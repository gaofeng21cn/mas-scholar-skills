export const REFERENCE_PROVIDER_ADAPTER_ABI = 'opl-connect-reference-provider-adapter.v1' as const;

export type ReferenceRecord = {
  id: string;
  doi: string | null;
  pmid: string | null;
  pmcid: string | null;
  title: string | null;
};

export type ProviderDefinition = {
  provider_id: string;
  adapter_id: string;
  receipt_provider_name?: string;
  endpoint: {
    default_base_url: string;
    base_url?: string;
    allowed_origins: string[];
  };
  verification_scope?: Record<string, unknown>;
};

export type AdapterState = {
  surface_kind: 'opl_connect_reference_provider_adapter_state.v1';
  adapter_id: string;
  step: string;
  step_index: number;
  max_steps: number;
  retained?: Record<string, unknown>;
};

export type AdapterHttpRequest = {
  method: 'GET';
  url: string;
  headers?: Record<string, string>;
  body: null;
};

export type AdapterHttpResponse = {
  status: number;
  url?: string;
  headers?: Record<string, string>;
  body: unknown;
};

export type ReferenceMetadata = {
  title?: string;
  year?: string;
  journal?: string;
  authors?: string[];
  abstract?: string;
  article_types?: string[];
};

export type AdapterEvidence = {
  match_basis: 'doi' | 'pmid' | 'pmcid' | 'title' | 'none';
  provider_identifiers: Record<string, string>;
  metadata: ReferenceMetadata;
  retraction_or_update_flags: Record<string, unknown>;
  normalized: {
    doi: string | null;
    pmid: string | null;
    pmcid: string | null;
    title: string | null;
  };
  verification_scope?: Record<string, unknown>;
};

export type AdapterStepResult = {
  surface_kind: 'opl_connect_reference_provider_adapter_step_result.v1';
  adapter_abi: typeof REFERENCE_PROVIDER_ADAPTER_ABI;
  next:
    | {
      kind: 'request';
      request: AdapterHttpRequest;
      state: AdapterState;
    }
    | {
      kind: 'complete';
      evidence: AdapterEvidence;
    };
};

export type AdapterStepRequest = {
  surface_kind: 'opl_connect_reference_provider_adapter_step_request.v1';
  adapter_abi: typeof REFERENCE_PROVIDER_ADAPTER_ABI;
  operation: 'build_request' | 'parse_response';
  provider: ProviderDefinition;
  reference: ReferenceRecord;
  state?: AdapterState;
  response?: AdapterHttpResponse;
};

export type ParsedAdapterResponse = {
  surface_kind: 'opl_connect_reference_provider_adapter_parsed_response.v1';
  adapter_abi: typeof REFERENCE_PROVIDER_ADAPTER_ABI;
  adapter_id: string;
  provider: ProviderDefinition;
  reference: ReferenceRecord;
  state: AdapterState;
  parsed: Record<string, unknown>;
};

export class ReferenceProviderAdapterContractError extends Error {
  readonly code: string;
  readonly details: Record<string, unknown>;

  constructor(code: string, message: string, details: Record<string, unknown> = {}) {
    super(message);
    this.name = 'ReferenceProviderAdapterContractError';
    this.code = code;
    this.details = details;
  }
}

export type ProviderAdapter = {
  adapter_id: string;
  initial_step: string;
  max_steps: number;
  allowed_steps: Record<string, number>;
  build_request: (input: {
    provider: ProviderDefinition;
    reference: ReferenceRecord;
    state: AdapterState;
  }) => AdapterStepResult;
  parse_response: (input: {
    provider: ProviderDefinition;
    reference: ReferenceRecord;
    state: AdapterState;
    response: AdapterHttpResponse;
  }) => Record<string, unknown>;
  next_step: (input: ParsedAdapterResponse) => AdapterStepResult;
};
