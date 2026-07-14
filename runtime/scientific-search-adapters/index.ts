import { SCIENTIFIC_SEARCH_ADAPTERS } from './search-adapters.ts';
import {
  SCIENTIFIC_SEARCH_ADAPTER_ABI,
  ScientificSearchAdapterContractError,
  type ScientificSearchAdapterState,
  type ScientificSearchAdapterStepRequest,
  type ScientificSearchAdapterStepResult,
  type ScientificSearchHttpResponse,
  type ScientificSearchProviderAdapter,
  type ScientificSearchProviderDefinition,
} from './types.ts';

export {
  SCIENTIFIC_SEARCH_ADAPTER_ABI,
  ScientificSearchAdapterContractError,
} from './types.ts';
export type {
  ScientificSearchAdapterState,
  ScientificSearchAdapterStepRequest,
  ScientificSearchAdapterStepResult,
  ScientificSearchCandidate,
  ScientificSearchHttpRequest,
  ScientificSearchHttpResponse,
  ScientificSearchProviderDefinition,
} from './types.ts';

function contractError(
  code: string,
  message: string,
  details: Record<string, unknown> = {},
): never {
  throw new ScientificSearchAdapterContractError(code, message, details);
}

function adapterFor(provider: ScientificSearchProviderDefinition): ScientificSearchProviderAdapter {
  if (!provider || typeof provider !== 'object') {
    contractError('search_adapter_provider_invalid', 'Scientific search provider must be an object.');
  }
  const adapter = SCIENTIFIC_SEARCH_ADAPTERS[provider.adapter_id];
  if (!adapter || adapter.provider_id !== provider.provider_id) {
    contractError(
      'search_adapter_not_exported',
      'Scientific search provider selects an adapter that is not exported for that provider.',
      {
        provider_id: provider.provider_id,
        adapter_id: provider.adapter_id,
        exported_adapter_ids: Object.keys(SCIENTIFIC_SEARCH_ADAPTERS),
      },
    );
  }
  const endpoint = provider.endpoint;
  if (!endpoint || typeof endpoint.default_base_url !== 'string'
    || (endpoint.base_url !== undefined && typeof endpoint.base_url !== 'string')
    || !Array.isArray(endpoint.allowed_origins) || endpoint.allowed_origins.length === 0
    || endpoint.allowed_origins.some((origin) => typeof origin !== 'string')) {
    contractError(
      'search_adapter_provider_invalid',
      'Scientific search provider must declare a default endpoint and allowed origins.',
      { provider_id: provider.provider_id },
    );
  }
  return adapter;
}

function validateEnvelope(request: ScientificSearchAdapterStepRequest): ScientificSearchProviderAdapter {
  if (!request || request.surface_kind !== 'opl_connect_scientific_search_adapter_step_request.v1') {
    contractError('search_adapter_request_invalid', 'Scientific search request has the wrong surface kind.');
  }
  if (request.adapter_abi !== SCIENTIFIC_SEARCH_ADAPTER_ABI) {
    contractError('search_adapter_abi_mismatch', 'Scientific search request uses an unsupported ABI.', {
      expected: SCIENTIFIC_SEARCH_ADAPTER_ABI,
      actual: request.adapter_abi,
    });
  }
  if (typeof request.query !== 'string' || !request.query.trim()) {
    contractError('search_adapter_query_invalid', 'Scientific search query must be a non-empty string.');
  }
  if (!Number.isSafeInteger(request.limit) || request.limit < 1) {
    contractError('search_adapter_limit_invalid', 'Scientific search limit must be a positive integer.', {
      limit: request.limit,
    });
  }
  return adapterFor(request.provider);
}

function initialState(
  adapter: ScientificSearchProviderAdapter,
  query: string,
  limit: number,
): ScientificSearchAdapterState {
  return {
    surface_kind: 'opl_connect_scientific_search_adapter_state.v1',
    adapter_id: adapter.adapter_id,
    step: 'search',
    step_index: 1,
    max_steps: 1,
    query,
    limit,
  };
}

function validateState(
  adapter: ScientificSearchProviderAdapter,
  request: ScientificSearchAdapterStepRequest,
  state: ScientificSearchAdapterState,
): void {
  if (!state || state.surface_kind !== 'opl_connect_scientific_search_adapter_state.v1'
    || state.adapter_id !== adapter.adapter_id
    || state.step !== 'search'
    || state.step_index !== 1
    || state.max_steps !== 1
    || state.query !== request.query
    || state.limit !== request.limit) {
    contractError('search_adapter_state_invalid', 'Scientific search state does not match its request.', {
      provider_id: request.provider.provider_id,
      adapter_id: adapter.adapter_id,
    });
  }
}

function validateResponse(response: ScientificSearchHttpResponse | undefined): ScientificSearchHttpResponse {
  if (!response || !Number.isInteger(response.status) || response.status < 100 || response.status > 599) {
    contractError('search_adapter_response_invalid', 'Scientific search response must include a valid HTTP status.');
  }
  if (response.status < 200 || response.status > 299) {
    contractError('search_adapter_response_unsuccessful', 'Scientific search response must have a successful status.', {
      status: response.status,
    });
  }
  if (response.headers !== undefined
    && (typeof response.headers !== 'object' || response.headers === null || Array.isArray(response.headers)
      || Object.values(response.headers).some((value) => typeof value !== 'string'))) {
    contractError('search_adapter_response_invalid', 'Scientific search response headers must be a string map.');
  }
  if (response.url !== undefined && typeof response.url !== 'string') {
    contractError('search_adapter_response_invalid', 'Scientific search response URL must be a string when present.');
  }
  return response;
}

export function build_search_request(
  request: ScientificSearchAdapterStepRequest,
): ScientificSearchAdapterStepResult {
  const adapter = validateEnvelope(request);
  if (request.operation !== 'build_search_request') {
    contractError('search_adapter_operation_invalid', 'build_search_request received a different operation.', {
      operation: request.operation,
    });
  }
  const state = request.state ?? initialState(adapter, request.query, request.limit);
  validateState(adapter, request, state);
  return adapter.build_search_request({
    provider: request.provider,
    query: request.query,
    limit: request.limit,
    state,
  });
}

export function parse_search_response(
  request: ScientificSearchAdapterStepRequest,
): ScientificSearchAdapterStepResult {
  const adapter = validateEnvelope(request);
  if (request.operation !== 'parse_search_response') {
    contractError('search_adapter_operation_invalid', 'parse_search_response received a different operation.', {
      operation: request.operation,
    });
  }
  if (!request.state) {
    contractError(
      'search_adapter_state_invalid',
      'parse_search_response requires the exact state returned with its HTTP request.',
      { adapter_id: adapter.adapter_id },
    );
  }
  validateState(adapter, request, request.state);
  const candidates = adapter.parse_search_response({
    provider: request.provider,
    query: request.query,
    limit: request.limit,
    state: request.state,
    response: validateResponse(request.response),
  });
  return {
    surface_kind: 'opl_connect_scientific_search_adapter_step_result.v1',
    adapter_abi: SCIENTIFIC_SEARCH_ADAPTER_ABI,
    next: { kind: 'complete', candidates },
  };
}

export function runScientificSearchAdapterStep(
  request: ScientificSearchAdapterStepRequest,
): ScientificSearchAdapterStepResult {
  if (!request || typeof request !== 'object') {
    contractError('search_adapter_request_invalid', 'Scientific search request must be an object.');
  }
  if (request.operation === 'build_search_request') return build_search_request(request);
  if (request.operation === 'parse_search_response') return parse_search_response(request);
  contractError(
    'search_adapter_operation_invalid',
    'Scientific search operation must be build_search_request or parse_search_response.',
    { operation: (request as { operation?: unknown }).operation },
  );
}

export const SCIENTIFIC_SEARCH_ADAPTER_PACKAGE = {
  surface_kind: 'opl_connect_scientific_search_adapter_package.v1',
  package_id: 'mas-scholar-skills',
  module_id: 'mas-scholar-skills.scientific-search-adapters',
  module_kind: 'opl_connect_scientific_search_adapter',
  adapter_abi: SCIENTIFIC_SEARCH_ADAPTER_ABI,
  adapter_ids: Object.keys(SCIENTIFIC_SEARCH_ADAPTERS),
  max_steps: 1,
  handler_export: 'runScientificSearchAdapterStep',
  state_machine_exports: ['build_search_request', 'parse_search_response'],
  authority_boundary: {
    can_perform_network_io: false,
    can_read_environment: false,
    can_write_files: false,
    can_spawn_processes: false,
    can_write_domain_truth: false,
    can_sign_owner_receipt: false,
    can_create_typed_blocker: false,
    can_claim_reference_truth: false,
    can_claim_quality_verdict: false,
    can_claim_domain_ready: false,
    can_claim_production_ready: false,
  },
} as const;
