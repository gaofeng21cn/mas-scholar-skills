import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import test from 'node:test';
import { fileURLToPath } from 'node:url';

import {
  SCIENTIFIC_SEARCH_ADAPTER_ABI,
  SCIENTIFIC_SEARCH_ADAPTER_PACKAGE,
  ScientificSearchAdapterContractError,
  runScientificSearchAdapterStep,
} from '../runtime/scientific-search-adapters/index.ts';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const readJson = (relative) => JSON.parse(fs.readFileSync(path.join(ROOT, relative), 'utf8'));
const profile = readJson('contracts/scientific-search-adapters/scientific-search.json');
const registry = readJson('contracts/scientific-search-adapters/scientific-search-adapter-registry.json');

function provider(providerId) {
  return structuredClone(profile.providers.find((item) => item.provider_id === providerId));
}

function build(providerId, query, limit = 10, state) {
  return runScientificSearchAdapterStep({
    surface_kind: 'opl_connect_scientific_search_adapter_step_request.v1',
    adapter_abi: SCIENTIFIC_SEARCH_ADAPTER_ABI,
    operation: 'build_search_request',
    provider: provider(providerId),
    query,
    limit,
    ...(state ? { state } : {}),
  });
}

function parse(providerId, query, limit, requestResult, body) {
  assert.equal(requestResult.next.kind, 'request');
  return runScientificSearchAdapterStep({
    surface_kind: 'opl_connect_scientific_search_adapter_step_request.v1',
    adapter_abi: SCIENTIFIC_SEARCH_ADAPTER_ABI,
    operation: 'parse_search_response',
    provider: provider(providerId),
    query,
    limit,
    state: requestResult.next.state,
    response: { status: 200, body },
  });
}

test('manifest, profile, registry, and descriptor expose the locked search runtime module', () => {
  const manifest = readJson('contracts/opl_capability_package_manifest.json');
  const plugin = readJson('.codex-plugin/plugin.json');
  const descriptor = readJson('contracts/domain_descriptor.json');
  const binding = manifest.exports.runtime_module_bindings.find(
    (item) => item.module_id === 'mas-scholar-skills.scientific-search-adapters',
  );
  assert.equal(manifest.version, '0.2.29');
  assert.equal(plugin.version, '0.2.29');
  assert.equal(manifest.content_lock.canonicalization, 'ordered_path_length_file_length_bytes');
  assert.ok(binding);
  assert.equal(binding.adapter_abi, SCIENTIFIC_SEARCH_ADAPTER_ABI);
  assert.deepEqual(binding.handler, {
    kind: 'typescript_export',
    file: 'runtime/scientific-search-adapters/index.ts',
    export: 'runScientificSearchAdapterStep',
  });
  assert.deepEqual(binding.exports, [
    'runScientificSearchAdapterStep',
    'build_search_request',
    'parse_search_response',
  ]);
  assert.equal(binding.max_steps, 2);
  assert.deepEqual(profile.adapter_package.adapter_ids, registry.adapters.map((item) => item.adapter_id));
  assert.deepEqual(profile.provider_scope, {
    role: 'package_owned_primary_biomedical_and_generic_metadata_search',
    provider_ids: ['crossref', 'openalex', 'pubmed', 'pmc'],
    framework_core_provider_ids: [],
  });
  assert.deepEqual(
    profile.providers.map((item) => [item.provider_id, item.adapter_id]),
    registry.adapters.map((item) => [item.provider_id, item.adapter_id]),
  );
  assert.deepEqual(SCIENTIFIC_SEARCH_ADAPTER_PACKAGE.adapter_ids, profile.adapter_package.adapter_ids);
  assert.deepEqual(
    descriptor.capability_pack.runtime_module_ids,
    manifest.exports.runtime_module_bindings.map((item) => item.module_id),
  );
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

test('Crossref search builds one bounded request and preserves every normalized candidate field', () => {
  const request = build('crossref', 'diabetes cardiovascular risk', 2);
  assert.equal(request.next.kind, 'request');
  const url = new URL(request.next.request.url);
  assert.equal(url.origin, 'https://api.crossref.org');
  assert.equal(url.pathname, '/works');
  assert.equal(url.searchParams.get('query'), 'diabetes cardiovascular risk');
  assert.equal(url.searchParams.get('rows'), '2');
  assert.equal(request.next.state.step_index, 1);
  assert.equal(request.next.state.max_steps, 1);

  const result = parse('crossref', 'diabetes cardiovascular risk', 2, request, {
    message: {
      items: [
        {
          DOI: '10.1000/FIRST',
          title: ['First article'],
          'container-title': ['Clinical Journal'],
          published: { 'date-parts': [[2025, 2, 1]] },
          author: [{ given: 'Ada', family: 'Lovelace' }, { family: 'Hopper' }],
        },
        {
          title: ['Second article without DOI'],
          URL: 'https://example.org/second',
          author: [],
        },
        { DOI: '10.1000/OMITTED', title: ['Beyond limit'] },
      ],
    },
  });
  assert.equal(result.next.kind, 'complete');
  assert.equal(result.next.candidates.length, 2);
  assert.deepEqual(result.next.candidates[0], {
    source_ref: 'crossref:10.1000/first',
    source_kind: 'literature_article',
    source_provider: 'Crossref',
    provider_id: 'crossref',
    doi: '10.1000/first',
    pmid: null,
    pmcid: null,
    openalex_id: null,
    title: 'First article',
    journal: 'Clinical Journal',
    publication_year: '2025',
    authors: ['Ada Lovelace', 'Hopper'],
    article_types: [],
    source_urls: {
      doi: 'https://doi.org/10.1000/first',
      crossref: 'https://api.crossref.org/works/10.1000%2Ffirst',
    },
  });
  assert.match(result.next.candidates[1].source_ref, /^crossref:query-result:[0-9a-f]{16}$/);
  assert.equal(result.next.candidates[1].source_urls.crossref, 'https://example.org/second');
});

test('OpenAlex search preserves DOI, PMID, OpenAlex id, authors, journal, year, and source URLs', () => {
  const request = build('openalex', 'heart failure', 3);
  assert.equal(request.next.kind, 'request');
  const url = new URL(request.next.request.url);
  assert.equal(url.origin, 'https://api.openalex.org');
  assert.equal(url.pathname, '/works');
  assert.equal(url.searchParams.get('search'), 'heart failure');
  assert.equal(url.searchParams.get('per-page'), '3');

  const result = parse('openalex', 'heart failure', 3, request, {
    results: [{
      doi: 'https://doi.org/10.1000/OPENALEX',
      display_name: 'OpenAlex result',
      publication_year: 2024,
      ids: {
        openalex: 'https://openalex.org/W123',
        pmid: 'https://pubmed.ncbi.nlm.nih.gov/12345/',
      },
      primary_location: { source: { display_name: 'OpenAlex Journal' } },
      authorships: [
        { author: { display_name: 'First Author' } },
        { author: { display_name: 'Second Author' } },
      ],
    }],
  });
  assert.equal(result.next.kind, 'complete');
  assert.deepEqual(result.next.candidates[0], {
    source_ref: 'openalex:W123',
    source_kind: 'literature_article',
    source_provider: 'OpenAlex',
    provider_id: 'openalex',
    doi: '10.1000/openalex',
    pmid: '12345',
    pmcid: null,
    openalex_id: 'W123',
    title: 'OpenAlex result',
    journal: 'OpenAlex Journal',
    publication_year: '2024',
    authors: ['First Author', 'Second Author'],
    article_types: [],
    source_urls: {
      openalex: 'https://openalex.org/W123',
      doi: 'https://doi.org/10.1000/openalex',
      pubmed: 'https://pubmed.ncbi.nlm.nih.gov/12345/',
      pmc: null,
    },
  });
});

test('PubMed search uses an explicit ESearch to ESummary next-step state', () => {
  const request = build('pubmed', 'CONSORT randomized trial', 2);
  assert.equal(request.next.kind, 'request');
  const searchUrl = new URL(request.next.request.url);
  assert.equal(searchUrl.origin, 'https://eutils.ncbi.nlm.nih.gov');
  assert.equal(searchUrl.pathname, '/entrez/eutils/esearch.fcgi');
  assert.equal(searchUrl.searchParams.get('db'), 'pubmed');
  assert.equal(searchUrl.searchParams.get('term'), 'CONSORT randomized trial');
  assert.equal(searchUrl.searchParams.get('retmode'), 'json');
  assert.equal(searchUrl.searchParams.get('retmax'), '2');
  assert.deepEqual(request.next.state, {
    surface_kind: 'opl_connect_scientific_search_adapter_state.v1',
    adapter_id: 'ncbi_pubmed_search',
    step: 'search',
    step_index: 1,
    max_steps: 2,
    query: 'CONSORT randomized trial',
    limit: 2,
  });

  const summaryRequest = parse('pubmed', 'CONSORT randomized trial', 2, request, {
    esearchresult: {
      count: '2',
      idlist: ['20332509', '12345'],
    },
  });
  assert.equal(summaryRequest.next.kind, 'request');
  const summaryUrl = new URL(summaryRequest.next.request.url);
  assert.equal(summaryUrl.pathname, '/entrez/eutils/esummary.fcgi');
  assert.equal(summaryUrl.searchParams.get('db'), 'pubmed');
  assert.equal(summaryUrl.searchParams.get('id'), '20332509,12345');
  assert.equal(summaryRequest.next.state.step, 'summary');
  assert.equal(summaryRequest.next.state.step_index, 2);
  assert.equal(summaryRequest.next.state.max_steps, 2);
  assert.deepEqual(summaryRequest.next.state.ids, ['20332509', '12345']);
  assert.equal(summaryRequest.next.state.provider_total, 2);

  const result = parse('pubmed', 'CONSORT randomized trial', 2, summaryRequest, {
    result: {
      uids: ['20332509', '12345'],
      '20332509': {
        uid: '20332509',
        title: 'CONSORT 2010 statement',
        pubdate: '2010 Mar 23',
        fulljournalname: 'BMJ',
        authors: [{ name: 'Schulz KF' }],
        pubtype: ['Journal Article', 'Randomized Controlled Trial'],
        articleids: [
          { idtype: 'doi', value: '10.1136/bmj.c332' },
          { idtype: 'pmc', value: 'PMC2844940' },
        ],
      },
      '12345': {
        uid: '12345',
        title: 'Second article',
        pubdate: '2024',
        source: 'Clinical Journal',
        authors: [{ name: 'Second Author' }],
      },
    },
  });
  assert.equal(result.next.kind, 'complete');
  assert.equal(result.next.provider_total, 2);
  assert.deepEqual(result.next.candidates[0], {
    source_ref: 'pubmed:20332509',
    source_kind: 'literature_article',
    source_provider: 'PubMed',
    provider_id: 'pubmed',
    doi: '10.1136/bmj.c332',
    pmid: '20332509',
    pmcid: 'PMC2844940',
    openalex_id: null,
    title: 'CONSORT 2010 statement',
    journal: 'BMJ',
    publication_year: '2010',
    authors: ['Schulz KF'],
    article_types: ['Journal Article', 'Randomized Controlled Trial'],
    source_urls: {
      doi: 'https://doi.org/10.1136/bmj.c332',
      pubmed: 'https://pubmed.ncbi.nlm.nih.gov/20332509/',
      pmc: 'https://pmc.ncbi.nlm.nih.gov/articles/PMC2844940/',
      europe_pmc: null,
    },
  });
});

test('PubMed empty ESearch response completes without an ESummary request', () => {
  const request = build('pubmed', 'no matches', 5);
  const result = parse('pubmed', 'no matches', 5, request, {
    esearchresult: { count: '0', idlist: [] },
  });
  assert.equal(result.next.kind, 'complete');
  assert.deepEqual(result.next.candidates, []);
  assert.equal(result.next.provider_total, 0);
});

test('Europe PMC search builds and parses a one-step PMC candidate response', () => {
  const request = build('pmc', 'OPEN_ACCESS:Y AND CONSORT', 1);
  assert.equal(request.next.kind, 'request');
  const url = new URL(request.next.request.url);
  assert.equal(url.origin, 'https://www.ebi.ac.uk');
  assert.equal(url.pathname, '/europepmc/webservices/rest/search');
  assert.equal(url.searchParams.get('query'), 'OPEN_ACCESS:Y AND CONSORT');
  assert.equal(url.searchParams.get('format'), 'json');
  assert.equal(url.searchParams.get('resultType'), 'core');
  assert.equal(url.searchParams.get('pageSize'), '1');
  assert.equal(request.next.state.max_steps, 1);

  const result = parse('pmc', 'OPEN_ACCESS:Y AND CONSORT', 1, request, {
    hitCount: 3,
    resultList: {
      result: [{
        id: '20332509',
        source: 'MED',
        pmid: '20332509',
        pmcid: 'PMC2844940',
        doi: '10.1136/bmj.c332',
        title: 'CONSORT 2010 statement',
        pubYear: '2010',
        journalTitle: 'BMJ',
        authorList: { author: [{ fullName: 'Schulz KF' }] },
        pubTypeList: { pubType: ['journal article', 'guideline'] },
        inEPMC: 'Y',
      }],
    },
  });
  assert.equal(result.next.kind, 'complete');
  assert.equal(result.next.provider_total, 3);
  assert.deepEqual(result.next.candidates[0], {
    source_ref: 'pmc:PMC2844940',
    source_kind: 'literature_article',
    source_provider: 'Europe PMC',
    provider_id: 'pmc',
    doi: '10.1136/bmj.c332',
    pmid: '20332509',
    pmcid: 'PMC2844940',
    openalex_id: null,
    title: 'CONSORT 2010 statement',
    journal: 'BMJ',
    publication_year: '2010',
    authors: ['Schulz KF'],
    article_types: ['journal article', 'guideline'],
    source_urls: {
      doi: 'https://doi.org/10.1136/bmj.c332',
      pubmed: 'https://pubmed.ncbi.nlm.nih.gov/20332509/',
      pmc: 'https://pmc.ncbi.nlm.nih.gov/articles/PMC2844940/',
      europe_pmc: 'https://europepmc.org/article/MED/20332509',
    },
  });
});

test('query, limit, adapter state, response, and endpoint drift fail closed', () => {
  const request = build('crossref', 'stable query', 4);
  assert.equal(request.next.kind, 'request');
  const baseParse = {
    surface_kind: 'opl_connect_scientific_search_adapter_step_request.v1',
    adapter_abi: SCIENTIFIC_SEARCH_ADAPTER_ABI,
    operation: 'parse_search_response',
    provider: provider('crossref'),
    query: 'stable query',
    limit: 4,
    state: request.next.state,
    response: { status: 200, body: { message: { items: [] } } },
  };
  for (const changed of [
    { ...baseParse, query: 'changed query' },
    { ...baseParse, limit: 5 },
    { ...baseParse, state: { ...baseParse.state, step_index: 2 } },
  ]) {
    assert.throws(
      () => runScientificSearchAdapterStep(changed),
      (error) => error instanceof ScientificSearchAdapterContractError
        && error.code === 'search_adapter_state_invalid',
    );
  }
  assert.throws(
    () => runScientificSearchAdapterStep({ ...baseParse, response: undefined }),
    (error) => error instanceof ScientificSearchAdapterContractError
      && error.code === 'search_adapter_response_invalid',
  );
  assert.throws(
    () => runScientificSearchAdapterStep({
      ...baseParse,
      response: { status: 200, headers: { invalid: 42 }, body: { message: { items: [] } } },
    }),
    (error) => error instanceof ScientificSearchAdapterContractError
      && error.code === 'search_adapter_response_invalid',
  );
  assert.throws(
    () => runScientificSearchAdapterStep({
      ...baseParse,
      response: { status: 429, body: { message: { items: [] } } },
    }),
    (error) => error instanceof ScientificSearchAdapterContractError
      && error.code === 'search_adapter_response_unsuccessful',
  );
  for (const malformed of [
    { ...baseParse, response: { status: 200, body: { message: {} } } },
    {
      ...baseParse,
      provider: provider('openalex'),
      state: { ...baseParse.state, adapter_id: 'openalex_search_rest' },
      response: { status: 200, body: {} },
    },
  ]) {
    assert.throws(
      () => runScientificSearchAdapterStep(malformed),
      (error) => error instanceof ScientificSearchAdapterContractError
      && error.code === 'search_adapter_response_invalid',
    );
  }
  const empty = runScientificSearchAdapterStep(baseParse);
  assert.equal(empty.next.kind, 'complete');
  assert.deepEqual(empty.next.candidates, []);
  assert.equal(empty.next.provider_total, null);
  const untrusted = provider('openalex');
  untrusted.endpoint.base_url = 'https://untrusted.example';
  assert.throws(
    () => runScientificSearchAdapterStep({
      surface_kind: 'opl_connect_scientific_search_adapter_step_request.v1',
      adapter_abi: SCIENTIFIC_SEARCH_ADAPTER_ABI,
      operation: 'build_search_request',
      provider: untrusted,
      query: 'bounded query',
      limit: 5,
    }),
    (error) => error instanceof ScientificSearchAdapterContractError
      && error.code === 'search_adapter_provider_origin_not_allowed',
  );
});

test('invalid operations, queries, limits, and provider/adapter pairs fail closed', () => {
  const base = {
    surface_kind: 'opl_connect_scientific_search_adapter_step_request.v1',
    adapter_abi: SCIENTIFIC_SEARCH_ADAPTER_ABI,
    operation: 'build_search_request',
    provider: provider('crossref'),
    query: 'query',
    limit: 1,
  };
  const cases = [
    [null, 'search_adapter_request_invalid'],
    [{ ...base, operation: 'unknown' }, 'search_adapter_operation_invalid'],
    [{ ...base, query: '   ' }, 'search_adapter_query_invalid'],
    [{ ...base, limit: 0 }, 'search_adapter_limit_invalid'],
    [{ ...base, limit: 1.5 }, 'search_adapter_limit_invalid'],
    [{ ...base, provider: { ...base.provider, provider_id: 'openalex' } }, 'search_adapter_not_exported'],
    [{ ...base, provider: { ...base.provider, endpoint: { ...base.provider.endpoint, base_url: 42 } } }, 'search_adapter_provider_invalid'],
  ];
  for (const [input, code] of cases) {
    assert.throws(
      () => runScientificSearchAdapterStep(input),
      (error) => error instanceof ScientificSearchAdapterContractError && error.code === code,
    );
  }
});

test('scientific search runtime sources expose no direct network, environment, write, or spawn surface', () => {
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
    assert.equal(forbiddenImports.test(source), false, relative);
    for (const token of forbiddenTokens) assert.equal(source.includes(token), false, `${relative}: ${token}`);
  }
});
