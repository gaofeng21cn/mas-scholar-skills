export const SCIENTIFIC_SEARCH_ADAPTER_ABI = 'opl-connect-scientific-search-adapter.v1' as const;

export type ScientificSearchProviderId = 'crossref' | 'openalex' | 'pubmed' | 'pmc';
export type ScientificSearchAdapterId =
  | 'crossref_search_rest'
  | 'openalex_search_rest'
  | 'ncbi_pubmed_search'
  | 'europe_pmc_search';

export type ScientificSearchProviderDefinition = {
  provider_id: ScientificSearchProviderId;
  adapter_id: ScientificSearchAdapterId;
  source_provider: 'Crossref' | 'OpenAlex' | 'PubMed' | 'Europe PMC';
  endpoint: {
    default_base_url: string;
    base_url?: string;
    allowed_origins: string[];
  };
};

type OneStepScientificSearchAdapterState = {
  surface_kind: 'opl_connect_scientific_search_adapter_state.v1';
  adapter_id: Exclude<ScientificSearchAdapterId, 'ncbi_pubmed_search'>;
  step: 'search';
  step_index: 1;
  max_steps: 1;
  query: string;
  limit: number;
};

type PubmedSearchState = {
  surface_kind: 'opl_connect_scientific_search_adapter_state.v1';
  adapter_id: 'ncbi_pubmed_search';
  step: 'search';
  step_index: 1;
  max_steps: 2;
  query: string;
  limit: number;
};

export type PubmedSummaryState = {
  surface_kind: 'opl_connect_scientific_search_adapter_state.v1';
  adapter_id: 'ncbi_pubmed_search';
  step: 'summary';
  step_index: 2;
  max_steps: 2;
  query: string;
  limit: number;
  ids: string[];
  provider_total: number | null;
};

export type ScientificSearchAdapterState =
  | OneStepScientificSearchAdapterState
  | PubmedSearchState
  | PubmedSummaryState;

export type ScientificSearchHttpRequest = {
  method: 'GET';
  url: string;
  headers?: Record<string, string>;
  body: null;
};

export type ScientificSearchHttpResponse = {
  status: number;
  url?: string;
  headers?: Record<string, string>;
  body: unknown;
};

export type ScientificSearchCandidate = {
  source_ref: string;
  source_kind: 'literature_article';
  source_provider: 'Crossref' | 'OpenAlex' | 'PubMed' | 'Europe PMC';
  provider_id: ScientificSearchProviderId;
  doi: string | null;
  pmid: string | null;
  pmcid: string | null;
  openalex_id: string | null;
  title: string;
  journal: string | null;
  publication_year: string | null;
  authors: string[];
  article_types: string[];
  source_urls: Record<string, string | null>;
};

export type ScientificSearchAdapterStepRequest = {
  surface_kind: 'opl_connect_scientific_search_adapter_step_request.v1';
  adapter_abi: typeof SCIENTIFIC_SEARCH_ADAPTER_ABI;
  operation: 'build_search_request' | 'parse_search_response';
  provider: ScientificSearchProviderDefinition;
  query: string;
  limit: number;
  state?: ScientificSearchAdapterState;
  response?: ScientificSearchHttpResponse;
};

export type ScientificSearchAdapterStepResult = {
  surface_kind: 'opl_connect_scientific_search_adapter_step_result.v1';
  adapter_abi: typeof SCIENTIFIC_SEARCH_ADAPTER_ABI;
  next:
    | {
        kind: 'request';
        request: ScientificSearchHttpRequest;
        state: ScientificSearchAdapterState;
      }
    | {
        kind: 'complete';
        candidates: ScientificSearchCandidate[];
        provider_total: number | null;
      };
};

export type ScientificSearchProviderAdapter = {
  adapter_id: ScientificSearchAdapterId;
  provider_id: ScientificSearchProviderId;
  max_steps: 1 | 2;
  build_search_request(input: {
    provider: ScientificSearchProviderDefinition;
    query: string;
    limit: number;
    state: ScientificSearchAdapterState;
  }): ScientificSearchAdapterStepResult;
  parse_search_response(input: {
    provider: ScientificSearchProviderDefinition;
    query: string;
    limit: number;
    state: ScientificSearchAdapterState;
    response: ScientificSearchHttpResponse;
  }): ScientificSearchAdapterStepResult;
};

export class ScientificSearchAdapterContractError extends Error {
  readonly code: string;
  readonly details: Record<string, unknown>;

  constructor(code: string, message: string, details: Record<string, unknown> = {}) {
    super(message);
    this.name = 'ScientificSearchAdapterContractError';
    this.code = code;
    this.details = details;
  }
}
