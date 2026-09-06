import {
  asRecord,
  asString,
  crossrefYear,
  firstString,
  normalizeDoi,
  normalizePmcid,
  yearFromText,
} from '../reference-provider-adapters/normalization.ts';
import {
  SCIENTIFIC_SEARCH_ADAPTER_ABI,
  ScientificSearchAdapterContractError,
  type PubmedSummaryState,
  type ScientificSearchAdapterState,
  type ScientificSearchAdapterStepResult,
  type ScientificSearchCandidate,
  type ScientificSearchHttpRequest,
  type ScientificSearchProviderAdapter,
  type ScientificSearchProviderDefinition,
} from './types.ts';

function providerUrl(provider: ScientificSearchProviderDefinition, relative: string): URL {
  const rawBase = provider.endpoint.base_url ?? provider.endpoint.default_base_url;
  let url: URL;
  try {
    const base = new URL(rawBase.endsWith('/') ? rawBase : `${rawBase}/`);
    url = new URL(relative.replace(/^\//, ''), base);
  } catch (error) {
    throw new ScientificSearchAdapterContractError(
      'search_adapter_provider_url_invalid',
      'Scientific search provider endpoint must be a valid absolute URL.',
      { provider_id: provider.provider_id, base_url: rawBase, cause: String(error) },
    );
  }
  if (!provider.endpoint.allowed_origins.includes(url.origin)) {
    throw new ScientificSearchAdapterContractError(
      'search_adapter_provider_origin_not_allowed',
      'Scientific search request origin is outside the profile allowlist.',
      {
        provider_id: provider.provider_id,
        request_origin: url.origin,
        allowed_origins: provider.endpoint.allowed_origins,
      },
    );
  }
  return url;
}

function requestResult(
  state: ScientificSearchAdapterState,
  request: ScientificSearchHttpRequest,
): ScientificSearchAdapterStepResult {
  return {
    surface_kind: 'opl_connect_scientific_search_adapter_step_result.v1',
    adapter_abi: SCIENTIFIC_SEARCH_ADAPTER_ABI,
    next: { kind: 'request', request, state },
  };
}

function completeResult(
  candidates: ScientificSearchCandidate[],
  providerTotal: number | null,
): ScientificSearchAdapterStepResult {
  return {
    surface_kind: 'opl_connect_scientific_search_adapter_step_result.v1',
    adapter_abi: SCIENTIFIC_SEARCH_ADAPTER_ABI,
    next: { kind: 'complete', candidates, provider_total: providerTotal },
  };
}

function getRequest(url: URL): ScientificSearchHttpRequest {
  return { method: 'GET', url: url.toString(), body: null };
}

function stableToken(value: string): string {
  let left = 0x811c9dc5;
  let right = 0x9e3779b9;
  for (let index = 0; index < value.length; index += 1) {
    const code = value.charCodeAt(index);
    left = Math.imul(left ^ code, 0x01000193) >>> 0;
    right = Math.imul(right ^ code, 0x85ebca6b) >>> 0;
  }
  return `${left.toString(16).padStart(8, '0')}${right.toString(16).padStart(8, '0')}`;
}

function asStringList(value: unknown): string[] {
  return (Array.isArray(value) ? value : [])
    .map(asString)
    .filter((entry): entry is string => Boolean(entry));
}

function nonNegativeInteger(value: unknown): number | null {
  const normalized = asString(value);
  if (normalized === null || !/^\d+$/.test(normalized)) return null;
  const parsed = Number(normalized);
  return Number.isSafeInteger(parsed) ? parsed : null;
}

function crossrefAuthors(item: Record<string, unknown>): string[] {
  return (Array.isArray(item.author) ? item.author : [])
    .map(asRecord)
    .map((author) => [asString(author.given), asString(author.family)].filter(Boolean).join(' '))
    .filter(Boolean);
}

function normalizeCrossrefCandidate(item: Record<string, unknown>): ScientificSearchCandidate | null {
  const doi = normalizeDoi(asString(item.DOI));
  const title = firstString(item.title);
  if (!doi && !title) return null;
  return {
    source_ref: doi ? `crossref:${doi}` : `crossref:query-result:${stableToken(JSON.stringify(item))}`,
    source_kind: 'literature_article',
    source_provider: 'Crossref',
    provider_id: 'crossref',
    doi,
    pmid: null,
    pmcid: null,
    openalex_id: null,
    title: title ?? '',
    journal: firstString(item['container-title']),
    publication_year: crossrefYear(item),
    authors: crossrefAuthors(item),
    article_types: [],
    source_urls: {
      doi: doi ? `https://doi.org/${doi}` : null,
      crossref: doi
        ? `https://api.crossref.org/works/${encodeURIComponent(doi)}`
        : asString(item.URL),
    },
  };
}

function openAlexShortId(value: string | null): string | null {
  return value?.replace(/^https?:\/\/openalex\.org\//i, '').trim() || null;
}

function normalizePmidUrl(value: string | null): string | null {
  return value
    ?.replace(/^https?:\/\/pubmed\.ncbi\.nlm\.nih\.gov\//i, '')
    .replace(/\/$/, '') || null;
}

function normalizeOpenAlexCandidate(item: Record<string, unknown>): ScientificSearchCandidate | null {
  const ids = asRecord(item.ids);
  const openAlexUrl = asString(item.id) ?? asString(ids.openalex);
  const openalexId = openAlexShortId(openAlexUrl);
  const doi = normalizeDoi(asString(item.doi) ?? asString(ids.doi));
  const pmid = normalizePmidUrl(asString(ids.pmid));
  const title = asString(item.title) ?? asString(item.display_name);
  if (!openalexId && !doi && !title) return null;
  const source = asRecord(asRecord(item.primary_location).source);
  const authors = (Array.isArray(item.authorships) ? item.authorships : [])
    .map(asRecord)
    .map((authorship) => asString(asRecord(authorship.author).display_name))
    .filter((name): name is string => Boolean(name));
  return {
    source_ref: openalexId
      ? `openalex:${openalexId}`
      : doi
        ? `openalex:doi:${doi}`
        : `openalex:query-result:${stableToken(JSON.stringify(item))}`,
    source_kind: 'literature_article',
    source_provider: 'OpenAlex',
    provider_id: 'openalex',
    doi,
    pmid,
    pmcid: null,
    openalex_id: openalexId,
    title: title ?? '',
    journal: asString(source.display_name),
    publication_year: asString(item.publication_year),
    authors,
    article_types: [],
    source_urls: {
      openalex: openAlexUrl,
      doi: doi ? `https://doi.org/${doi}` : null,
      pubmed: pmid ? `https://pubmed.ncbi.nlm.nih.gov/${pmid}/` : null,
      pmc: null,
    },
  };
}

function articleIdentifier(entry: Record<string, unknown>, ...types: string[]): string | null {
  const wanted = new Set(types.map((type) => type.toLowerCase()));
  for (const raw of Array.isArray(entry.articleids) ? entry.articleids : []) {
    const identifier = asRecord(raw);
    const type = asString(identifier.idtype)?.toLowerCase();
    const value = asString(identifier.value);
    if (type && value && wanted.has(type)) return value;
  }
  return null;
}

function normalizePubmedSummary(
  entry: Record<string, unknown>,
  requestedPmid: string,
): ScientificSearchCandidate | null {
  const title = asString(entry.title);
  if (!title) return null;
  const pmid = asString(entry.uid) ?? requestedPmid;
  if (!pmid) return null;
  const doi = normalizeDoi(articleIdentifier(entry, 'doi') ?? asString(entry.elocationid));
  const pmcid = normalizePmcid(articleIdentifier(entry, 'pmc', 'pmcid'));
  const authors = (Array.isArray(entry.authors) ? entry.authors : [])
    .map(asRecord)
    .map((author) => asString(author.name) ?? asString(author.collective_name))
    .filter((author): author is string => Boolean(author));
  return {
    source_ref: `pubmed:${pmid}`,
    source_kind: 'literature_article',
    source_provider: 'PubMed',
    provider_id: 'pubmed',
    doi,
    pmid,
    pmcid,
    openalex_id: null,
    title,
    journal: asString(entry.fulljournalname) ?? asString(entry.source),
    publication_year: yearFromText(asString(entry.pubdate)),
    authors,
    article_types: asStringList(entry.pubtype),
    source_urls: {
      doi: doi ? `https://doi.org/${doi}` : null,
      pubmed: `https://pubmed.ncbi.nlm.nih.gov/${pmid}/`,
      pmc: pmcid ? `https://pmc.ncbi.nlm.nih.gov/articles/${pmcid}/` : null,
      europe_pmc: null,
    },
  };
}

function normalizeEuropePmcCandidate(entry: Record<string, unknown>): ScientificSearchCandidate | null {
  const source = asString(entry.source)?.toUpperCase() ?? null;
  const providerId = asString(entry.id);
  const pmid = asString(entry.pmid)
    ?? (source === 'MED' ? providerId : null);
  const pmcid = normalizePmcid(
    asString(entry.pmcid)
      ?? (source === 'PMC' || providerId?.toUpperCase().startsWith('PMC') ? providerId : null),
  );
  const title = asString(entry.title);
  const sourceRef = pmcid ?? pmid ?? providerId;
  if (!sourceRef || !title) return null;
  const doi = normalizeDoi(asString(entry.doi));
  const europePmcType = pmid ? 'MED' : pmcid ? 'PMC' : source;
  const europePmcId = pmid ?? pmcid ?? providerId;
  return {
    source_ref: `pmc:${sourceRef}`,
    source_kind: 'literature_article',
    source_provider: 'Europe PMC',
    provider_id: 'pmc',
    doi,
    pmid,
    pmcid,
    openalex_id: null,
    title,
    journal: asString(entry.journalTitle),
    publication_year: yearFromText(asString(entry.pubYear) ?? asString(entry.firstPublicationDate)),
    authors: (Array.isArray(asRecord(entry.authorList).author) ? asRecord(entry.authorList).author : [])
      .map(asRecord)
      .map((author) => asString(author.fullName) ?? asString(author.collectiveName))
      .filter((author): author is string => Boolean(author)),
    article_types: asStringList(asRecord(entry.pubTypeList).pubType),
    source_urls: {
      doi: doi ? `https://doi.org/${doi}` : null,
      pubmed: pmid ? `https://pubmed.ncbi.nlm.nih.gov/${pmid}/` : null,
      pmc: pmcid ? `https://pmc.ncbi.nlm.nih.gov/articles/${pmcid}/` : null,
      europe_pmc: europePmcType && europePmcId
        ? `https://europepmc.org/article/${encodeURIComponent(europePmcType)}/${encodeURIComponent(europePmcId)}`
        : null,
    },
  };
}

const crossrefSearchAdapter: ScientificSearchProviderAdapter = {
  adapter_id: 'crossref_search_rest',
  provider_id: 'crossref',
  max_steps: 1,
  build_search_request({ provider, query, limit, state }) {
    const url = providerUrl(provider, 'works');
    url.searchParams.set('query', query);
    url.searchParams.set('rows', String(limit));
    return requestResult(state, getRequest(url));
  },
  parse_search_response({ limit, response }) {
    const message = asRecord(asRecord(response.body).message);
    if (!Array.isArray(message.items)) {
      throw new ScientificSearchAdapterContractError(
        'search_adapter_response_invalid',
        'Crossref search response must contain message.items.',
      );
    }
    return completeResult(
      message.items
        .map(asRecord)
        .map(normalizeCrossrefCandidate)
        .filter((candidate): candidate is ScientificSearchCandidate => Boolean(candidate))
        .slice(0, limit),
      nonNegativeInteger(message['total-results']),
    );
  },
};

const openAlexSearchAdapter: ScientificSearchProviderAdapter = {
  adapter_id: 'openalex_search_rest',
  provider_id: 'openalex',
  max_steps: 1,
  build_search_request({ provider, query, limit, state }) {
    const url = providerUrl(provider, 'works');
    url.searchParams.set('search', query);
    url.searchParams.set('per-page', String(limit));
    return requestResult(state, getRequest(url));
  },
  parse_search_response({ limit, response }) {
    const root = asRecord(response.body);
    if (!Array.isArray(root.results)) {
      throw new ScientificSearchAdapterContractError(
        'search_adapter_response_invalid',
        'OpenAlex search response must contain results.',
      );
    }
    return completeResult(
      root.results
        .map(asRecord)
        .map(normalizeOpenAlexCandidate)
        .filter((candidate): candidate is ScientificSearchCandidate => Boolean(candidate))
        .slice(0, limit),
      nonNegativeInteger(asRecord(root.meta).count),
    );
  },
};

const pubmedSearchAdapter: ScientificSearchProviderAdapter = {
  adapter_id: 'ncbi_pubmed_search',
  provider_id: 'pubmed',
  max_steps: 2,
  build_search_request({ provider, query, limit, state }) {
    const url = providerUrl(provider, state.step === 'summary' ? 'esummary.fcgi' : 'esearch.fcgi');
    url.searchParams.set('db', 'pubmed');
    url.searchParams.set('retmode', 'json');
    if (state.step === 'summary') {
      url.searchParams.set('id', state.ids.join(','));
    } else {
      url.searchParams.set('term', query);
      url.searchParams.set('retmax', String(limit));
    }
    return requestResult(state, getRequest(url));
  },
  parse_search_response({ provider, query, limit, state, response }) {
    if (state.step === 'search') {
      const searchResult = asRecord(asRecord(response.body).esearchresult);
      if (!Array.isArray(searchResult.idlist)) {
        throw new ScientificSearchAdapterContractError(
          'search_adapter_response_invalid',
          'PubMed ESearch response must contain esearchresult.idlist.',
        );
      }
      const ids = searchResult.idlist
        .map(asString)
        .filter((entry): entry is string => Boolean(entry))
        .slice(0, limit);
      const providerTotal = nonNegativeInteger(searchResult.count);
      if (ids.length === 0) return completeResult([], providerTotal);
      const summaryState: PubmedSummaryState = {
        surface_kind: 'opl_connect_scientific_search_adapter_state.v1',
        adapter_id: 'ncbi_pubmed_search',
        step: 'summary',
        step_index: 2,
        max_steps: 2,
        query,
        limit,
        ids,
        provider_total: providerTotal,
      };
      const summaryUrl = providerUrl(provider, 'esummary.fcgi');
      summaryUrl.searchParams.set('db', 'pubmed');
      summaryUrl.searchParams.set('id', ids.join(','));
      summaryUrl.searchParams.set('retmode', 'json');
      return requestResult(summaryState, getRequest(summaryUrl));
    }

    const result = asRecord(asRecord(response.body).result);
    if (!Array.isArray(result.uids)) {
      throw new ScientificSearchAdapterContractError(
        'search_adapter_response_invalid',
        'PubMed ESummary response must contain result.uids.',
      );
    }
    const candidates = state.ids
      .map((pmid) => normalizePubmedSummary(asRecord(result[pmid]), pmid))
      .filter((candidate): candidate is ScientificSearchCandidate => Boolean(candidate));
    return completeResult(candidates.slice(0, limit), state.provider_total);
  },
};

const europePmcSearchAdapter: ScientificSearchProviderAdapter = {
  adapter_id: 'europe_pmc_search',
  provider_id: 'pmc',
  max_steps: 1,
  build_search_request({ provider, query, limit, state }) {
    const url = providerUrl(provider, 'search');
    url.searchParams.set('query', query);
    url.searchParams.set('format', 'json');
    url.searchParams.set('resultType', 'core');
    url.searchParams.set('pageSize', String(limit));
    return requestResult(state, getRequest(url));
  },
  parse_search_response({ limit, response }) {
    const root = asRecord(response.body);
    const resultList = asRecord(root.resultList);
    if (!Array.isArray(resultList.result)) {
      throw new ScientificSearchAdapterContractError(
        'search_adapter_response_invalid',
        'Europe PMC search response must contain resultList.result.',
      );
    }
    return completeResult(
      resultList.result
        .map(asRecord)
        .map(normalizeEuropePmcCandidate)
        .filter((candidate): candidate is ScientificSearchCandidate => Boolean(candidate))
        .slice(0, limit),
      nonNegativeInteger(root.hitCount),
    );
  },
};

export const SCIENTIFIC_SEARCH_ADAPTERS: Record<string, ScientificSearchProviderAdapter> = {
  crossref_search_rest: crossrefSearchAdapter,
  openalex_search_rest: openAlexSearchAdapter,
  ncbi_pubmed_search: pubmedSearchAdapter,
  europe_pmc_search: europePmcSearchAdapter,
};
