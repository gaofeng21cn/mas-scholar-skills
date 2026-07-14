import { REFERENCE_PROVIDER_ADAPTERS } from './provider-adapters.ts';
import {
  REFERENCE_PROVIDER_ADAPTER_ABI,
  ReferenceProviderAdapterContractError,
  type AdapterHttpResponse,
  type AdapterState,
  type AdapterStepRequest,
  type AdapterStepResult,
  type ParsedAdapterResponse,
  type ProviderAdapter,
  type ProviderDefinition,
  type ReferenceRecord,
} from './types.ts';

export {
  REFERENCE_PROVIDER_ADAPTER_ABI,
  ReferenceProviderAdapterContractError,
} from './types.ts';
export type {
  AdapterEvidence,
  AdapterHttpRequest,
  AdapterHttpResponse,
  AdapterState,
  AdapterStepRequest,
  AdapterStepResult,
  ParsedAdapterResponse,
  ProviderDefinition,
  ReferenceRecord,
} from './types.ts';

function contractError(
  code: string,
  message: string,
  details: Record<string, unknown> = {},
): never {
  throw new ReferenceProviderAdapterContractError(code, message, details);
}

function adapterFor(provider: ProviderDefinition): ProviderAdapter {
  if (!provider || typeof provider !== 'object') {
    contractError('adapter_provider_invalid', 'Reference provider definition must be an object.');
  }
  const adapter = REFERENCE_PROVIDER_ADAPTERS[provider.adapter_id];
  if (!adapter) {
    contractError(
      'adapter_not_exported',
      'Reference provider selects an adapter that is not exported by this module.',
      { adapter_id: provider.adapter_id, exported_adapter_ids: Object.keys(REFERENCE_PROVIDER_ADAPTERS) },
    );
  }
  if (typeof provider.provider_id !== 'string' || !provider.provider_id) {
    contractError('adapter_provider_invalid', 'Reference provider id must be a non-empty string.');
  }
  const endpoint = provider.endpoint;
  if (!endpoint || typeof endpoint.default_base_url !== 'string') {
    contractError(
      'adapter_provider_invalid',
      'Reference provider endpoint must declare default_base_url.',
      { provider_id: provider.provider_id },
    );
  }
  if (!Array.isArray(endpoint.allowed_origins) || endpoint.allowed_origins.length === 0) {
    contractError(
      'adapter_provider_invalid',
      'Reference provider endpoint must declare at least one allowed origin.',
      { provider_id: provider.provider_id },
    );
  }
  return adapter;
}

function validateReference(reference: ReferenceRecord): void {
  if (!reference || typeof reference !== 'object' || typeof reference.id !== 'string' || !reference.id) {
    contractError('adapter_reference_invalid', 'Reference adapter input must include a stable reference id.');
  }
  for (const field of ['doi', 'pmid', 'pmcid', 'title'] as const) {
    if (reference[field] !== null && typeof reference[field] !== 'string') {
      contractError(
        'adapter_reference_invalid',
        'Reference identifiers and title must be strings or null.',
        { reference_id: reference.id, field },
      );
    }
  }
}

function initialState(adapter: ProviderAdapter): AdapterState {
  return {
    surface_kind: 'opl_connect_reference_provider_adapter_state.v1',
    adapter_id: adapter.adapter_id,
    step: adapter.initial_step,
    step_index: 1,
    max_steps: adapter.max_steps,
  };
}

function validateState(adapter: ProviderAdapter, state: AdapterState): void {
  if (!state || state.surface_kind !== 'opl_connect_reference_provider_adapter_state.v1') {
    contractError(
      'adapter_state_invalid',
      'Reference provider adapter state has the wrong surface kind.',
      { adapter_id: adapter.adapter_id },
    );
  }
  if (state.adapter_id !== adapter.adapter_id) {
    contractError(
      'adapter_state_invalid',
      'Reference provider adapter state belongs to a different adapter.',
      { adapter_id: adapter.adapter_id, state_adapter_id: state.adapter_id },
    );
  }
  if (!Number.isInteger(state.step_index) || state.step_index < 1) {
    contractError(
      'adapter_state_invalid',
      'Reference provider adapter step index must be a positive integer.',
      { adapter_id: adapter.adapter_id, step_index: state.step_index },
    );
  }
  if (state.step_index > adapter.max_steps || state.max_steps > adapter.max_steps) {
    contractError(
      'adapter_step_cap_exceeded',
      'Reference provider adapter state exceeds its declared step cap.',
      {
        adapter_id: adapter.adapter_id,
        step_index: state.step_index,
        state_max_steps: state.max_steps,
        adapter_max_steps: adapter.max_steps,
      },
    );
  }
  if (state.max_steps !== adapter.max_steps || adapter.allowed_steps[state.step] !== state.step_index) {
    contractError(
      'adapter_state_invalid',
      'Reference provider adapter state has an invalid step or step index.',
      {
        adapter_id: adapter.adapter_id,
        step: state.step,
        step_index: state.step_index,
        max_steps: state.max_steps,
      },
    );
  }
}

function validateEnvelope(request: AdapterStepRequest): ProviderAdapter {
  if (!request || request.surface_kind !== 'opl_connect_reference_provider_adapter_step_request.v1') {
    contractError(
      'adapter_request_invalid',
      'Reference provider adapter request has the wrong surface kind.',
    );
  }
  if (request.adapter_abi !== REFERENCE_PROVIDER_ADAPTER_ABI) {
    contractError(
      'adapter_abi_mismatch',
      'Reference provider adapter request uses an unsupported ABI.',
      { expected: REFERENCE_PROVIDER_ADAPTER_ABI, actual: request.adapter_abi },
    );
  }
  validateReference(request.reference);
  return adapterFor(request.provider);
}

function validateResponse(response: AdapterHttpResponse | undefined): AdapterHttpResponse {
  if (!response || !Number.isInteger(response.status) || response.status < 100 || response.status > 599) {
    contractError(
      'adapter_response_invalid',
      'Reference provider adapter response must include a valid HTTP status.',
    );
  }
  if (response.headers !== undefined && (
    typeof response.headers !== 'object' || response.headers === null || Array.isArray(response.headers)
  )) {
    contractError(
      'adapter_response_invalid',
      'Reference provider adapter response headers must be a string map.',
    );
  }
  return response;
}

export function build_request(request: AdapterStepRequest): AdapterStepResult {
  const adapter = validateEnvelope(request);
  if (request.operation !== 'build_request') {
    contractError(
      'adapter_operation_invalid',
      'build_request received a different adapter operation.',
      { operation: request.operation },
    );
  }
  const state = request.state ?? initialState(adapter);
  validateState(adapter, state);
  return adapter.build_request({ provider: request.provider, reference: request.reference, state });
}

export function parse_response(request: AdapterStepRequest): ParsedAdapterResponse {
  const adapter = validateEnvelope(request);
  if (request.operation !== 'parse_response') {
    contractError(
      'adapter_operation_invalid',
      'parse_response received a different adapter operation.',
      { operation: request.operation },
    );
  }
  if (!request.state) {
    contractError(
      'adapter_state_invalid',
      'parse_response requires the exact state returned with its HTTP request.',
      { adapter_id: adapter.adapter_id },
    );
  }
  validateState(adapter, request.state);
  const response = validateResponse(request.response);
  return {
    surface_kind: 'opl_connect_reference_provider_adapter_parsed_response.v1',
    adapter_abi: REFERENCE_PROVIDER_ADAPTER_ABI,
    adapter_id: adapter.adapter_id,
    provider: request.provider,
    reference: request.reference,
    state: request.state,
    parsed: adapter.parse_response({
      provider: request.provider,
      reference: request.reference,
      state: request.state,
      response,
    }),
  };
}

export function next_step(parsed: ParsedAdapterResponse): AdapterStepResult {
  if (!parsed || parsed.surface_kind !== 'opl_connect_reference_provider_adapter_parsed_response.v1') {
    contractError(
      'adapter_parsed_response_invalid',
      'next_step requires a parsed reference provider adapter response.',
    );
  }
  if (parsed.adapter_abi !== REFERENCE_PROVIDER_ADAPTER_ABI) {
    contractError(
      'adapter_abi_mismatch',
      'Parsed reference provider adapter response uses an unsupported ABI.',
      { expected: REFERENCE_PROVIDER_ADAPTER_ABI, actual: parsed.adapter_abi },
    );
  }
  validateReference(parsed.reference);
  const adapter = adapterFor(parsed.provider);
  if (parsed.adapter_id !== adapter.adapter_id) {
    contractError(
      'adapter_parsed_response_invalid',
      'Parsed response adapter id does not match its provider declaration.',
      { parsed_adapter_id: parsed.adapter_id, provider_adapter_id: adapter.adapter_id },
    );
  }
  validateState(adapter, parsed.state);
  return adapter.next_step(parsed);
}

export function runReferenceProviderAdapterStep(request: AdapterStepRequest): AdapterStepResult {
  if (request.operation === 'build_request') return build_request(request);
  if (request.operation === 'parse_response') return next_step(parse_response(request));
  contractError(
    'adapter_operation_invalid',
    'Reference provider adapter operation must be build_request or parse_response.',
    { operation: (request as { operation?: unknown }).operation },
  );
}

export const REFERENCE_PROVIDER_ADAPTER_PACKAGE = {
  surface_kind: 'opl_connect_reference_provider_adapter_package.v1',
  package_id: 'mas-scholar-skills',
  module_id: 'mas-scholar-skills.reference-provider-adapters',
  adapter_abi: REFERENCE_PROVIDER_ADAPTER_ABI,
  adapter_ids: Object.keys(REFERENCE_PROVIDER_ADAPTERS),
  max_steps: 2,
  handler_export: 'runReferenceProviderAdapterStep',
  state_machine_exports: ['build_request', 'parse_response', 'next_step'],
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
