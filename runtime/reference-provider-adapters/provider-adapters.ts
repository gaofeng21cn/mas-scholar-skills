import {
  asRecord,
  asString,
  compactIdentifiers,
  compactMetadata,
  crossrefFlags,
  crossrefYear,
  deferredEvidence,
  firstString,
  htmlMeta,
  htmlTitle,
  normalizeDoi,
  normalizePmcid,
  providerUrl,
  yearFromText,
} from './normalization.ts';
import {
  REFERENCE_PROVIDER_ADAPTER_ABI,
  ReferenceProviderAdapterContractError,
  type AdapterEvidence,
  type AdapterHttpRequest,
  type AdapterHttpResponse,
  type AdapterState,
  type AdapterStepResult,
  type ParsedAdapterResponse,
  type ProviderAdapter,
  type ProviderDefinition,
  type ReferenceRecord,
} from './types.ts';

type CandidateRecord = {
  identifiers: Record<string, string | null>;
  evidence: AdapterEvidence;
  full_text_available?: boolean;
};

function requestResult(state: AdapterState, request: AdapterHttpRequest): AdapterStepResult {
  return {
    surface_kind: 'opl_connect_reference_provider_adapter_step_result.v1',
    adapter_abi: REFERENCE_PROVIDER_ADAPTER_ABI,
    next: { kind: 'request', request, state },
  };
}

function getRequest(url: URL, headers?: Record<string, string>): AdapterHttpRequest {
  return {
    method: 'GET',
    url: url.toString(),
    ...(headers && Object.keys(headers).length > 0 ? { headers } : {}),
    body: null,
  };
}

function completeResult(evidence: AdapterEvidence): AdapterStepResult {
  return {
    surface_kind: 'opl_connect_reference_provider_adapter_step_result.v1',
    adapter_abi: REFERENCE_PROVIDER_ADAPTER_ABI,
    next: { kind: 'complete', evidence },
  };
}

function deferredResult(
  reference: ReferenceRecord,
  provider: ProviderDefinition,
  reason: string,
): AdapterStepResult {
  return completeResult(deferredEvidence(reference, reason, provider.verification_scope));
}

function parsedCandidate(evidence: AdapterEvidence, extra: Record<string, unknown> = {}) {
  return { kind: 'candidate', evidence, ...extra };
}

function parsedDeferred(reason: string) {
  return { kind: 'deferred', reason };
}

function finishParsed(input: ParsedAdapterResponse): AdapterStepResult {
  if (input.parsed.kind === 'deferred') {
    return deferredResult(
      input.reference,
      input.provider,
      asString(input.parsed.reason) ?? 'provider returned no usable metadata',
    );
  }
  if (input.parsed.kind !== 'candidate') {
    throw new ReferenceProviderAdapterContractError(
      'adapter_parsed_response_invalid',
      'Reference provider parser returned an unsupported transition.',
      { adapter_id: input.adapter_id, parsed_kind: input.parsed.kind },
    );
  }
  const evidence = input.parsed.evidence;
  if (!isEvidence(evidence)) {
    throw new ReferenceProviderAdapterContractError(
      'adapter_evidence_invalid',
      'Reference provider parser did not return normalized evidence.',
      { adapter_id: input.adapter_id },
    );
  }
  return completeResult(evidence);
}

function isEvidence(value: unknown): value is AdapterEvidence {
  const record = asRecord(value);
  return typeof record.match_basis === 'string'
    && typeof record.provider_identifiers === 'object'
    && typeof record.metadata === 'object'
    && typeof record.retraction_or_update_flags === 'object'
    && typeof record.normalized === 'object';
}

function parsePubmedSummary(payload: unknown, requestedPmid: string): CandidateRecord | null {
  const result = asRecord(asRecord(payload).result);
  const uids = Array.isArray(result.uids) ? result.uids.map(asString).filter(Boolean) : [];
  const uid = uids.find((entry) => entry === requestedPmid) ?? uids[0] ?? requestedPmid;
  const entry = asRecord(result[uid]);
  const title = asString(entry.title);
  if (Object.keys(entry).length === 0 || !title) return null;
  const articleIds = Array.isArray(entry.articleids) ? entry.articleids : [];
  const identifier = (...types: string[]) => {
    const wanted = new Set(types.map((type) => type.toLowerCase()));
    for (const raw of articleIds) {
      const item = asRecord(raw);
      const type = asString(item.idtype)?.toLowerCase();
      const value = asString(item.value);
      if (type && value && wanted.has(type)) return value;
    }
    return null;
  };
  const doi = normalizeDoi(identifier('doi') ?? asString(entry.elocationid));
  const pmcid = normalizePmcid(identifier('pmc', 'pmcid'));
  const authors = (Array.isArray(entry.authors) ? entry.authors : [])
    .map((author) => asString(asRecord(author).name))
    .filter((author): author is string => Boolean(author));
  const identifiers = { doi, pmid: uid, pmcid, pubmed: uid };
  return {
    identifiers,
    full_text_available: Boolean(pmcid),
    evidence: {
      match_basis: 'pmid',
      provider_identifiers: compactIdentifiers(identifiers),
      metadata: compactMetadata({
        title,
        year: yearFromText(asString(entry.pubdate)),
        journal: asString(entry.fulljournalname) ?? asString(entry.source),
        authors,
      }),
      retraction_or_update_flags: {},
      normalized: { doi, pmid: uid, pmcid, title },
      verification_scope: {
        evidence_source: 'ncbi_pubmed_esummary',
        full_text_available: Boolean(pmcid),
        full_text_body_verified: false,
      },
    },
  };
}

function parseEuropePmcSearch(payload: unknown, reference: ReferenceRecord): CandidateRecord | null {
  const resultList = asRecord(asRecord(payload).resultList);
  const results = Array.isArray(resultList.result) ? resultList.result : [];
  const entry = asRecord(results[0]);
  if (Object.keys(entry).length === 0) return null;
  const doi = normalizeDoi(asString(entry.doi));
  const pmid = asString(entry.pmid) ?? asString(entry.id);
  const pmcid = normalizePmcid(asString(entry.pmcid));
  const title = asString(entry.title);
  const authorList = asRecord(entry.authorList);
  const authors = (Array.isArray(authorList.author) ? authorList.author : [])
    .map((author) => asString(asRecord(author).fullName) ?? asString(asRecord(author).collectiveName))
    .filter((author): author is string => Boolean(author));
  const fullTextAvailable = entry.inEPMC === 'Y'
    || entry.isOpenAccess === 'Y'
    || entry.inEPMC === true
    || entry.isOpenAccess === true
    || pmcid !== null;
  const identifiers = { doi, pmid, pmcid, europe_pmc: asString(entry.id) };
  return {
    identifiers,
    full_text_available: fullTextAvailable,
    evidence: {
      match_basis: reference.pmcid ? 'pmcid' : reference.pmid ? 'pmid' : 'doi',
      provider_identifiers: compactIdentifiers(identifiers),
      metadata: compactMetadata({
        title,
        year: yearFromText(asString(entry.pubYear) ?? asString(entry.firstPublicationDate)),
        journal: asString(entry.journalTitle),
        authors,
        abstract: asString(entry.abstractText),
      }),
      retraction_or_update_flags: {},
      normalized: { doi, pmid, pmcid, title },
      verification_scope: {
        evidence_source: 'europe_pmc_core_metadata',
        full_text_available: fullTextAvailable,
        full_text_body_verified: false,
        full_text_probe_status: fullTextAvailable ? 'pending' : 'not_available',
      },
    },
  };
}

const crossrefAdapter: ProviderAdapter = {
  adapter_id: 'crossref_rest',
  initial_step: 'metadata',
  max_steps: 1,
  allowed_steps: { metadata: 1 },
  build_request({ provider, reference, state }) {
    if (!reference.doi && !reference.title) {
      return deferredResult(reference, provider, 'crossref provider needs a DOI or title');
    }
    const url = reference.doi
      ? providerUrl(provider, `works/${encodeURIComponent(reference.doi)}`)
      : providerUrl(provider, 'works');
    if (!reference.doi && reference.title) {
      url.searchParams.set('query.title', reference.title);
      url.searchParams.set('rows', '1');
    }
    return requestResult(state, getRequest(url));
  },
  parse_response({ reference, response }) {
    const message = asRecord(asRecord(response.body).message);
    const item = reference.doi
      ? message
      : asRecord((Array.isArray(message.items) ? message.items : [])[0]);
    if (Object.keys(item).length === 0) return parsedDeferred('crossref returned no matching item');
    const doi = normalizeDoi(asString(item.DOI));
    const title = firstString(item.title);
    return parsedCandidate({
      match_basis: reference.doi ? 'doi' : 'title',
      provider_identifiers: compactIdentifiers({ doi }),
      metadata: compactMetadata({
        title,
        year: crossrefYear(item),
        journal: firstString(item['container-title']),
      }),
      retraction_or_update_flags: crossrefFlags(item),
      normalized: { doi, pmid: null, pmcid: null, title },
    });
  },
  next_step: finishParsed,
};

const crossmarkAdapter: ProviderAdapter = {
  ...crossrefAdapter,
  adapter_id: 'crossref_crossmark_signal',
  build_request({ provider, reference, state }) {
    if (!reference.doi) {
      return deferredResult(reference, provider, 'crossmark signal lookup needs a DOI');
    }
    return requestResult(
      state,
      getRequest(providerUrl(provider, `works/${encodeURIComponent(reference.doi)}`)),
    );
  },
  parse_response(input) {
    const parsed = crossrefAdapter.parse_response(input);
    const evidence = asRecord(parsed.evidence);
    if (parsed.kind === 'candidate' && isEvidence(evidence)) {
      return parsedCandidate({
        ...evidence,
        retraction_or_update_flags: {
          ...evidence.retraction_or_update_flags,
          crossmark_metadata_source: 'crossref_rest_api',
        },
      });
    }
    return parsed;
  },
};

const openAlexAdapter: ProviderAdapter = {
  adapter_id: 'openalex_rest',
  initial_step: 'metadata',
  max_steps: 1,
  allowed_steps: { metadata: 1 },
  build_request({ provider, reference, state }) {
    if (!reference.doi && !reference.title) {
      return deferredResult(reference, provider, 'OpenAlex provider needs a DOI or title');
    }
    const url = reference.doi
      ? providerUrl(provider, `works/${encodeURIComponent(`https://doi.org/${reference.doi}`)}`)
      : providerUrl(provider, 'works');
    if (!reference.doi && reference.title) {
      url.searchParams.set('search', reference.title);
      url.searchParams.set('per-page', '1');
    }
    return requestResult(state, getRequest(url));
  },
  parse_response({ reference, response }) {
    const root = asRecord(response.body);
    const item = Array.isArray(root.results) ? asRecord(root.results[0]) : root;
    if (!asString(item.id)) return parsedDeferred('OpenAlex returned no matching work');
    const ids = asRecord(item.ids);
    const source = asRecord(asRecord(item.primary_location).source);
    const doi = normalizeDoi(asString(item.doi) ?? asString(ids.doi));
    const pmid = asString(ids.pmid)
      ?.replace(/^https?:\/\/pubmed\.ncbi\.nlm\.nih\.gov\//i, '')
      .replace(/\/$/, '') || null;
    const pmcid = normalizePmcid(asString(ids.pmcid) ?? asString(ids.pmc));
    const title = asString(item.title) ?? asString(item.display_name);
    return parsedCandidate({
      match_basis: reference.doi ? 'doi' : 'title',
      provider_identifiers: compactIdentifiers({ doi, pmid, pmcid, openalex: asString(item.id) }),
      metadata: compactMetadata({
        title,
        year: asString(item.publication_year),
        journal: asString(source.display_name),
      }),
      retraction_or_update_flags: item.is_retracted === true ? { retracted: true } : {},
      normalized: { doi, pmid, pmcid, title },
    });
  },
  next_step: finishParsed,
};

const pubmedAdapter: ProviderAdapter = {
  adapter_id: 'ncbi_pubmed_esummary',
  initial_step: 'metadata',
  max_steps: 1,
  allowed_steps: { metadata: 1 },
  build_request({ provider, reference, state }) {
    if (!reference.pmid) {
      return deferredResult(reference, provider, 'PubMed eSummary lookup needs a PMID');
    }
    const url = providerUrl(provider, 'esummary.fcgi');
    url.searchParams.set('db', 'pubmed');
    url.searchParams.set('id', reference.pmid);
    url.searchParams.set('retmode', 'json');
    url.searchParams.set('tool', 'one-person-lab');
    return requestResult(state, getRequest(url));
  },
  parse_response({ reference, response }) {
    const candidate = parsePubmedSummary(response.body, reference.pmid!);
    return candidate
      ? parsedCandidate(candidate.evidence)
      : parsedDeferred('PubMed returned no matching summary');
  },
  next_step: finishParsed,
};

const europePmcAdapter: ProviderAdapter = {
  adapter_id: 'europe_pmc_core',
  initial_step: 'metadata',
  max_steps: 2,
  allowed_steps: { metadata: 1, full_text_xml: 2 },
  build_request({ provider, reference, state }) {
    if (state.step === 'full_text_xml') {
      const retained = asRecord(state.retained);
      const evidence = asRecord(retained.evidence);
      const normalized = asRecord(evidence.normalized);
      const pmcid = normalizePmcid(asString(normalized.pmcid));
      if (!pmcid) {
        throw new ReferenceProviderAdapterContractError(
          'adapter_state_invalid',
          'Europe PMC full-text step requires retained normalized PMCID evidence.',
          { adapter_id: state.adapter_id, step: state.step },
        );
      }
      return requestResult(
        state,
        getRequest(
          providerUrl(provider, `${encodeURIComponent(pmcid)}/fullTextXML`),
          { accept: 'application/xml,text/xml;q=0.9' },
        ),
      );
    }
    if (!reference.pmcid && !reference.pmid && !reference.doi) {
      return deferredResult(reference, provider, 'Europe PMC lookup needs a PMCID, PMID, or DOI');
    }
    const url = providerUrl(provider, 'search');
    const query = reference.pmcid
      ? `PMCID:${reference.pmcid}`
      : reference.pmid
        ? `EXT_ID:${reference.pmid} AND SRC:MED`
        : `DOI:"${reference.doi}"`;
    url.searchParams.set('query', query);
    url.searchParams.set('format', 'json');
    url.searchParams.set('resultType', 'core');
    url.searchParams.set('pageSize', '1');
    return requestResult(state, getRequest(url));
  },
  parse_response({ reference, state, response }) {
    if (state.step === 'full_text_xml') {
      if (typeof response.body !== 'string') {
        throw new ReferenceProviderAdapterContractError(
          'adapter_response_invalid',
          'Europe PMC full-text response body must be text.',
          { adapter_id: state.adapter_id, step: state.step },
        );
      }
      return {
        kind: 'full_text_probe',
        verified: /<article\b/i.test(response.body),
        response_url: response.url ?? null,
      };
    }
    const candidate = parseEuropePmcSearch(response.body, reference);
    return candidate
      ? parsedCandidate(candidate.evidence, { full_text_available: candidate.full_text_available === true })
      : parsedDeferred('Europe PMC returned no matching record');
  },
  next_step(input) {
    if (input.parsed.kind === 'deferred') return finishParsed(input);
    if (input.state.step === 'metadata') {
      const evidence = input.parsed.evidence;
      if (!isEvidence(evidence)) {
        throw new ReferenceProviderAdapterContractError(
          'adapter_evidence_invalid',
          'Europe PMC metadata response did not contain normalized evidence.',
          { adapter_id: input.adapter_id },
        );
      }
      const fullTextAvailable = input.parsed.full_text_available === true;
      if (!fullTextAvailable || !evidence.normalized.pmcid) {
        return completeResult({
          ...evidence,
          verification_scope: {
            ...evidence.verification_scope,
            full_text_probe_status: 'not_available',
          },
        });
      }
      if (input.state.step_index >= input.state.max_steps) {
        return completeResult({
          ...evidence,
          verification_scope: {
            ...evidence.verification_scope,
            full_text_probe_status: 'step_cap_reached',
          },
        });
      }
      const nextState: AdapterState = {
        surface_kind: 'opl_connect_reference_provider_adapter_state.v1',
        adapter_id: input.adapter_id,
        step: 'full_text_xml',
        step_index: input.state.step_index + 1,
        max_steps: input.state.max_steps,
        retained: { evidence },
      };
      return europePmcAdapter.build_request({
        provider: input.provider,
        reference: input.reference,
        state: nextState,
      });
    }
    const retainedEvidence = asRecord(input.state.retained).evidence;
    if (!isEvidence(retainedEvidence) || input.parsed.kind !== 'full_text_probe') {
      throw new ReferenceProviderAdapterContractError(
        'adapter_state_invalid',
        'Europe PMC full-text completion requires retained metadata and a probe response.',
        { adapter_id: input.adapter_id, step: input.state.step },
      );
    }
    const verified = input.parsed.verified === true;
    return completeResult({
      ...retainedEvidence,
      verification_scope: {
        ...retainedEvidence.verification_scope,
        full_text_body_verified: verified,
        full_text_probe_status: verified ? 'verified' : 'invalid_payload',
        ...(asString(input.parsed.response_url)
          ? { full_text_response_url: asString(input.parsed.response_url) }
          : {}),
      },
    });
  },
};

const semanticScholarAdapter: ProviderAdapter = {
  adapter_id: 'semantic_scholar_graph',
  initial_step: 'metadata',
  max_steps: 1,
  allowed_steps: { metadata: 1 },
  build_request({ provider, reference, state }) {
    if (!reference.doi && !reference.title) {
      return deferredResult(reference, provider, 'Semantic Scholar lookup needs a DOI or title');
    }
    const url = reference.doi
      ? providerUrl(provider, `paper/${encodeURIComponent(`DOI:${reference.doi}`)}`)
      : providerUrl(provider, 'paper/search');
    url.searchParams.set('fields', 'paperId,externalIds,title,year,venue,publicationVenue');
    if (!reference.doi && reference.title) {
      url.searchParams.set('query', reference.title);
      url.searchParams.set('limit', '1');
    }
    return requestResult(state, getRequest(url));
  },
  parse_response({ reference, response }) {
    const root = asRecord(response.body);
    const item = Array.isArray(root.data) ? asRecord(root.data[0]) : root;
    if (!asString(item.paperId)) return parsedDeferred('Semantic Scholar returned no matching paper');
    const externalIds = asRecord(item.externalIds);
    const publicationVenue = asRecord(item.publicationVenue);
    const doi = normalizeDoi(asString(externalIds.DOI) ?? asString(externalIds.doi));
    const pmid = asString(externalIds.PMID) ?? asString(externalIds.PubMed);
    const pmcid = normalizePmcid(asString(externalIds.PMCID) ?? asString(externalIds.PMC));
    const title = asString(item.title);
    return parsedCandidate({
      match_basis: reference.doi ? 'doi' : 'title',
      provider_identifiers: compactIdentifiers({
        doi,
        pmid,
        pmcid,
        semantic_scholar: asString(item.paperId),
      }),
      metadata: compactMetadata({
        title,
        year: asString(item.year),
        journal: asString(publicationVenue.name) ?? asString(item.venue),
      }),
      retraction_or_update_flags: {},
      normalized: { doi, pmid, pmcid, title },
    });
  },
  next_step: finishParsed,
};

const publisherAdapter: ProviderAdapter = {
  adapter_id: 'doi_resolver_landing',
  initial_step: 'landing',
  max_steps: 1,
  allowed_steps: { landing: 1 },
  build_request({ provider, reference, state }) {
    if (!reference.doi) {
      return deferredResult(reference, provider, 'DOI resolver landing lookup needs a DOI');
    }
    return requestResult(
      state,
      getRequest(
        providerUrl(provider, encodeURIComponent(reference.doi)),
        { accept: 'text/html,application/xhtml+xml,text/plain;q=0.8,*/*;q=0.5' },
      ),
    );
  },
  parse_response({ reference, response }) {
    if (typeof response.body !== 'string') {
      throw new ReferenceProviderAdapterContractError(
        'adapter_response_invalid',
        'DOI resolver landing response body must be text.',
        { adapter_id: 'doi_resolver_landing' },
      );
    }
    const title = htmlMeta(response.body, 'citation_title', 'dc.title', 'og:title')
      ?? htmlTitle(response.body)
      ?? reference.title;
    const contentType = response.headers?.['content-type'] ?? response.headers?.['Content-Type'] ?? null;
    return parsedCandidate({
      match_basis: 'doi',
      provider_identifiers: compactIdentifiers({
        doi: normalizeDoi(reference.doi),
        publisher_landing_url: response.url ?? null,
      }),
      metadata: compactMetadata({
        title,
        year: yearFromText(htmlMeta(response.body, 'citation_publication_date', 'dc.date')),
        journal: htmlMeta(response.body, 'citation_journal_title', 'citation_publisher'),
      }),
      retraction_or_update_flags: {
        publisher_landing_resolved: true,
        publisher_lookup_source: 'doi_resolver_landing_metadata',
        full_text_body_verified: false,
        ...(contentType ? { content_type: contentType } : {}),
      },
      normalized: {
        doi: normalizeDoi(reference.doi),
        pmid: null,
        pmcid: null,
        title,
      },
      verification_scope: {
        evidence_source: 'doi_resolver_landing_metadata',
        landing_metadata_only: true,
        full_text_body_verified: false,
      },
    });
  },
  next_step: finishParsed,
};

export const REFERENCE_PROVIDER_ADAPTERS: Record<string, ProviderAdapter> = {
  crossref_rest: crossrefAdapter,
  openalex_rest: openAlexAdapter,
  ncbi_pubmed_esummary: pubmedAdapter,
  europe_pmc_core: europePmcAdapter,
  semantic_scholar_graph: semanticScholarAdapter,
  crossref_crossmark_signal: crossmarkAdapter,
  doi_resolver_landing: publisherAdapter,
};
