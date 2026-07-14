import {
  asRecord,
  asString,
  crossrefYear,
  firstString,
  normalizeDoi,
} from '../reference-provider-adapters/normalization.ts';
import {
  SCIENTIFIC_SEARCH_ADAPTER_ABI,
  ScientificSearchAdapterContractError,
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
    openalex_id: null,
    title: title ?? '',
    journal: firstString(item['container-title']),
    publication_year: crossrefYear(item),
    authors: crossrefAuthors(item),
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
    openalex_id: openalexId,
    title: title ?? '',
    journal: asString(source.display_name),
    publication_year: asString(item.publication_year),
    authors,
    source_urls: {
      openalex: openAlexUrl,
      doi: doi ? `https://doi.org/${doi}` : null,
      pubmed: pmid ? `https://pubmed.ncbi.nlm.nih.gov/${pmid}/` : null,
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
    return message.items
      .map(asRecord)
      .map(normalizeCrossrefCandidate)
      .filter((candidate): candidate is ScientificSearchCandidate => Boolean(candidate))
      .slice(0, limit);
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
    return root.results
      .map(asRecord)
      .map(normalizeOpenAlexCandidate)
      .filter((candidate): candidate is ScientificSearchCandidate => Boolean(candidate))
      .slice(0, limit);
  },
};

export const SCIENTIFIC_SEARCH_ADAPTERS: Record<string, ScientificSearchProviderAdapter> = {
  crossref_search_rest: crossrefSearchAdapter,
  openalex_search_rest: openAlexSearchAdapter,
};
