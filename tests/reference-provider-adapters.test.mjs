import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import test from 'node:test';
import { fileURLToPath } from 'node:url';

import {
  REFERENCE_PROVIDER_ADAPTER_ABI,
  REFERENCE_PROVIDER_ADAPTER_PACKAGE,
  ReferenceProviderAdapterContractError,
  runReferenceProviderAdapterStep,
} from '../runtime/reference-provider-adapters/index.ts';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const readJson = (relative) => JSON.parse(fs.readFileSync(path.join(ROOT, relative), 'utf8'));
const profile = readJson('contracts/reference-provider-adapters/scientific-metadata.json');
const registry = readJson('contracts/reference-provider-adapters/reference-provider-adapter-registry.json');

function provider(providerId) {
  return structuredClone(profile.providers.find((item) => item.provider_id === providerId));
}

function reference(overrides = {}) {
  return {
    id: 'ref-1',
    doi: null,
    pmid: null,
    pmcid: null,
    title: null,
    ...overrides,
  };
}

function build(providerId, inputReference, state) {
  return runReferenceProviderAdapterStep({
    surface_kind: 'opl_connect_reference_provider_adapter_step_request.v1',
    adapter_abi: REFERENCE_PROVIDER_ADAPTER_ABI,
    operation: 'build_request',
    provider: provider(providerId),
    reference: inputReference,
    ...(state ? { state } : {}),
  });
}

function parse(providerId, inputReference, requestResult, response) {
  assert.equal(requestResult.next.kind, 'request');
  return runReferenceProviderAdapterStep({
    surface_kind: 'opl_connect_reference_provider_adapter_step_request.v1',
    adapter_abi: REFERENCE_PROVIDER_ADAPTER_ABI,
    operation: 'parse_response',
    provider: provider(providerId),
    reference: inputReference,
    state: requestResult.next.state,
    response: {
      status: 200,
      ...response,
    },
  });
}

test('package manifest, profile, registry, and plugin expose the locked reference runtime module', () => {
  const manifest = readJson('contracts/opl_capability_package_manifest.json');
  const plugin = readJson('.codex-plugin/plugin.json');
  const binding = manifest.exports.runtime_module_bindings[0];
  assert.equal(manifest.version, '0.2.10');
  assert.equal(plugin.version, '0.2.10');
  assert.equal(manifest.content_lock.canonicalization, 'ordered_path_length_file_length_bytes');
  assert.equal(binding.module_id, 'mas-scholar-skills.reference-provider-adapters');
  assert.equal(binding.adapter_abi, REFERENCE_PROVIDER_ADAPTER_ABI);
  assert.deepEqual(binding.handler, {
    kind: 'typescript_export',
    file: 'runtime/reference-provider-adapters/index.ts',
    export: 'runReferenceProviderAdapterStep',
  });
  assert.deepEqual(binding.exports, [
    'runReferenceProviderAdapterStep',
    'build_request',
    'parse_response',
    'next_step',
  ]);
  assert.equal(binding.max_steps, 2);
  assert.equal(profile.adapter_abi, undefined);
  assert.equal(profile.adapter_package.adapter_abi, REFERENCE_PROVIDER_ADAPTER_ABI);
  assert.deepEqual(
    profile.adapter_package.adapter_ids,
    registry.adapters.map((item) => item.adapter_id),
  );
  assert.deepEqual(REFERENCE_PROVIDER_ADAPTER_PACKAGE.adapter_ids, profile.adapter_package.adapter_ids);
  const locked = new Set(manifest.content_lock.paths);
  for (const relative of [
    binding.profile_ref,
    binding.profile_schema_ref,
    binding.registry_ref,
    binding.registry_schema_ref,
    binding.step_schema_ref,
    ...binding.contained_implementation_files,
  ]) {
    assert.equal(locked.has(relative), true, `${relative} is content locked`);
  }
  assert.equal(Object.values(binding.authority_boundary).every((value) => value === false), true);
  assert.equal(Object.values(profile.no_authority_boundary).every((value) => value === false), true);
});

test('Crossref adapter builds a request and parses normalized metadata', () => {
  const input = reference({ doi: '10.1000/ABC', title: 'Expected title' });
  const request = build('crossref', input);
  assert.equal(request.next.kind, 'request');
  assert.match(request.next.request.url, /api\.crossref\.org\/works\/10\.1000%2FABC/i);
  const result = parse('crossref', input, request, {
    body: {
      message: {
        DOI: '10.1000/ABC',
        title: ['Expected title'],
        'container-title': ['Example Journal'],
        published: { 'date-parts': [[2024]] },
        relation: { 'is-retracted-by': [{ id: 'replacement' }] },
      },
    },
  });
  assert.equal(result.next.kind, 'complete');
  assert.equal(result.next.evidence.normalized.doi, '10.1000/abc');
  assert.equal(result.next.evidence.metadata.year, '2024');
  assert.equal(result.next.evidence.retraction_or_update_flags.retracted, true);
});

test('OpenAlex adapter parses DOI, PMID, PMCID, venue, and retraction signal', () => {
  const input = reference({ doi: '10.1000/openalex' });
  const request = build('openalex', input);
  const result = parse('openalex', input, request, {
    body: {
      id: 'https://openalex.org/W42',
      doi: 'https://doi.org/10.1000/OPENALEX',
      title: 'OpenAlex title',
      publication_year: 2023,
      is_retracted: true,
      ids: {
        pmid: 'https://pubmed.ncbi.nlm.nih.gov/12345/',
        pmcid: 'PMC999',
      },
      primary_location: { source: { display_name: 'OpenAlex Journal' } },
    },
  });
  assert.equal(result.next.kind, 'complete');
  assert.equal(result.next.evidence.provider_identifiers.pmid, '12345');
  assert.equal(result.next.evidence.normalized.pmcid, 'PMC999');
  assert.equal(result.next.evidence.retraction_or_update_flags.retracted, true);
});

test('PubMed eSummary adapter parses identifiers and authors without performing I/O', () => {
  const input = reference({ pmid: '31452104' });
  const request = build('pubmed', input);
  assert.equal(request.next.kind, 'request');
  assert.match(request.next.request.url, /esummary\.fcgi/);
  const result = parse('pubmed', input, request, {
    body: {
      result: {
        uids: ['31452104'],
        31452104: {
          title: 'PubMed title',
          pubdate: '2019 Aug 25',
          fulljournalname: 'PubMed Journal',
          authors: [{ name: 'Ada Lovelace' }, { name: 'Grace Hopper' }],
          articleids: [
            { idtype: 'doi', value: '10.1000/PUBMED' },
            { idtype: 'pmc', value: 'PMC1234' },
          ],
        },
      },
    },
  });
  assert.equal(result.next.kind, 'complete');
  assert.deepEqual(result.next.evidence.metadata.authors, ['Ada Lovelace', 'Grace Hopper']);
  assert.equal(result.next.evidence.normalized.doi, '10.1000/pubmed');
  assert.equal(result.next.evidence.verification_scope.full_text_available, true);
});

test('Europe PMC adapter performs exactly one bounded fullTextXML follow-up', () => {
  const input = reference({ pmcid: 'PMC7654' });
  const metadataRequest = build('pmc', input);
  const fullTextRequest = parse('pmc', input, metadataRequest, {
    body: {
      resultList: {
        result: [{
          id: '7654',
          pmid: '123456',
          pmcid: 'PMC7654',
          doi: '10.1000/PMC',
          title: 'Europe PMC title',
          pubYear: '2022',
          journalTitle: 'PMC Journal',
          authorList: { author: [{ fullName: 'Example Author' }] },
          inEPMC: 'Y',
        }],
      },
    },
  });
  assert.equal(fullTextRequest.next.kind, 'request');
  assert.equal(fullTextRequest.next.state.step, 'full_text_xml');
  assert.equal(fullTextRequest.next.state.step_index, 2);
  assert.equal(fullTextRequest.next.state.max_steps, 2);
  assert.match(fullTextRequest.next.request.url, /PMC7654\/fullTextXML$/);
  const completed = parse('pmc', input, fullTextRequest, {
    url: 'https://www.ebi.ac.uk/europepmc/webservices/rest/PMC7654/fullTextXML',
    headers: { 'content-type': 'application/xml' },
    body: '<?xml version="1.0"?><article><front/></article>',
  });
  assert.equal(completed.next.kind, 'complete');
  assert.equal(completed.next.evidence.verification_scope.full_text_body_verified, true);
  assert.equal(completed.next.evidence.verification_scope.full_text_probe_status, 'verified');
});

test('Semantic Scholar, Crossmark, and DOI landing adapters preserve provider-specific signals', () => {
  const semanticInput = reference({ doi: '10.1000/semantic' });
  const semantic = parse('semantic-scholar', semanticInput, build('semantic-scholar', semanticInput), {
    body: {
      paperId: 'paper-42',
      externalIds: { DOI: '10.1000/SEMANTIC', PMID: '2468', PMCID: 'PMC2468' },
      title: 'Semantic title',
      year: 2021,
      publicationVenue: { name: 'Semantic Journal' },
    },
  });
  assert.equal(semantic.next.kind, 'complete');
  assert.equal(semantic.next.evidence.provider_identifiers.semantic_scholar, 'paper-42');

  const crossmarkInput = reference({ doi: '10.1000/crossmark' });
  const crossmark = parse('crossmark', crossmarkInput, build('crossmark', crossmarkInput), {
    body: { message: { DOI: '10.1000/crossmark', title: ['Crossmark title'] } },
  });
  assert.equal(crossmark.next.kind, 'complete');
  assert.equal(crossmark.next.evidence.retraction_or_update_flags.crossmark_metadata_source, 'crossref_rest_api');

  const publisherInput = reference({ doi: '10.1000/publisher' });
  const publisher = parse('publisher', publisherInput, build('publisher', publisherInput), {
    url: 'https://publisher.example/article/42',
    headers: { 'content-type': 'text/html' },
    body: '<html><head><meta name="citation_title" content="Publisher title"><meta name="citation_publication_date" content="2020-04-01"><meta name="citation_journal_title" content="Publisher Journal"></head></html>',
  });
  assert.equal(publisher.next.kind, 'complete');
  assert.equal(publisher.next.evidence.metadata.title, 'Publisher title');
  assert.equal(publisher.next.evidence.provider_identifiers.publisher_landing_url, 'https://publisher.example/article/42');
  assert.equal(publisher.next.evidence.verification_scope.full_text_body_verified, false);
});

test('missing identifiers complete without requesting I/O', () => {
  const result = build('pubmed', reference({ title: 'No PMID' }));
  assert.equal(result.next.kind, 'complete');
  assert.equal(result.next.evidence.match_basis, 'none');
  assert.match(result.next.evidence.verification_scope.adapter_deferred_reason, /PMID/);
});

test('step cap, invalid state, and non-allowlisted origins fail closed', () => {
  const input = reference({ pmcid: 'PMC1' });
  assert.throws(
    () => build('pmc', input, {
      surface_kind: 'opl_connect_reference_provider_adapter_state.v1',
      adapter_id: 'europe_pmc_core',
      step: 'full_text_xml',
      step_index: 3,
      max_steps: 3,
      retained: {},
    }),
    (error) => error instanceof ReferenceProviderAdapterContractError
      && error.code === 'adapter_step_cap_exceeded',
  );
  assert.throws(
    () => build('pmc', input, {
      surface_kind: 'opl_connect_reference_provider_adapter_state.v1',
      adapter_id: 'europe_pmc_core',
      step: 'unexpected',
      step_index: 1,
      max_steps: 2,
    }),
    (error) => error instanceof ReferenceProviderAdapterContractError
      && error.code === 'adapter_state_invalid',
  );
  const untrusted = provider('crossref');
  untrusted.endpoint.base_url = 'https://untrusted.example';
  assert.throws(
    () => runReferenceProviderAdapterStep({
      surface_kind: 'opl_connect_reference_provider_adapter_step_request.v1',
      adapter_abi: REFERENCE_PROVIDER_ADAPTER_ABI,
      operation: 'build_request',
      provider: untrusted,
      reference: reference({ doi: '10.1000/untrusted' }),
    }),
    (error) => error instanceof ReferenceProviderAdapterContractError
      && error.code === 'adapter_provider_origin_not_allowed',
  );
});

test('runtime sources expose no direct network, environment, write, or spawn surface', () => {
  const forbiddenImports = /(?:from|import\s*)\s*['"](?:node:)?(?:fs|http|https|net|tls|child_process|worker_threads)/;
  const forbiddenTokens = [
    'fetch(',
    'XMLHttpRequest',
    'process.env',
    'Deno.',
    'Bun.',
    'request_json',
    'request_text',
    'writeFile(',
    'spawn(',
    'exec(',
  ];
  for (const relative of registry.contained_implementation_files) {
    const source = fs.readFileSync(path.join(ROOT, relative), 'utf8');
    assert.doesNotMatch(source, forbiddenImports, relative);
    for (const token of forbiddenTokens) assert.equal(source.includes(token), false, `${relative}: ${token}`);
  }
  assert.equal(Object.values(registry.sandbox).filter((value) => typeof value === 'boolean').every((value) => value === false), true);
  assert.equal(Object.values(registry.no_authority_boundary).every((value) => value === false), true);
});
