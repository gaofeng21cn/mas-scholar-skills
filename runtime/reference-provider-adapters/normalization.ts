import {
  ReferenceProviderAdapterContractError,
  type AdapterEvidence,
  type ProviderDefinition,
  type ReferenceMetadata,
  type ReferenceRecord,
} from './types.ts';

export function asRecord(value: unknown): Record<string, unknown> {
  return typeof value === 'object' && value !== null && !Array.isArray(value)
    ? value as Record<string, unknown>
    : {};
}

export function asString(value: unknown): string | null {
  if (typeof value === 'number' && Number.isFinite(value)) return String(value);
  return typeof value === 'string' && value.trim() ? value.trim() : null;
}

export function firstString(value: unknown): string | null {
  if (Array.isArray(value)) return value.map(asString).find(Boolean) ?? null;
  return asString(value);
}

export function normalizeDoi(value: string | null): string | null {
  if (!value) return null;
  return value
    .replace(/^https?:\/\/(?:dx\.)?doi\.org\//i, '')
    .replace(/^doi:/i, '')
    .trim()
    .toLowerCase() || null;
}

export function normalizePmcid(value: string | null): string | null {
  const normalized = value?.trim().toUpperCase() || null;
  if (!normalized) return null;
  return normalized.startsWith('PMC') ? normalized : `PMC${normalized}`;
}

function normalizePmid(value: string | null): string | null {
  return value?.trim() || null;
}

function normalizeTitle(value: string | null): string | null {
  return value?.replace(/\s+/g, ' ').trim().toLowerCase() || null;
}

export function assessReferenceMatch(
  reference: ReferenceRecord,
  evidence: AdapterEvidence,
  providerId: string,
): NonNullable<AdapterEvidence['match_assessment']> {
  const fields = {
    doi: normalizeDoi,
    pmid: normalizePmid,
    pmcid: normalizePmcid,
    title: normalizeTitle,
  };
  const mismatchDetails: NonNullable<AdapterEvidence['match_assessment']>['mismatch_details'] = [];
  const matchedIdentifiers: Record<string, string> = {};
  for (const field of ['doi', 'pmid', 'pmcid', 'title'] as const) {
    const expected = reference[field];
    const actual = evidence.normalized[field];
    const normalizedExpected = fields[field](expected);
    const normalizedActual = fields[field](actual);
    if (!expected || !actual || !normalizedExpected || !normalizedActual) continue;
    if (normalizedExpected !== normalizedActual) {
      mismatchDetails.push({
        field, expected, actual,
        normalized_expected: normalizedExpected,
        normalized_actual: normalizedActual,
      });
    } else if (field !== 'title') {
      matchedIdentifiers[field] = normalizedActual;
    }
  }
  const matchStatus = mismatchDetails.length > 0
    ? 'metadata_conflict'
    : Object.keys(matchedIdentifiers).length > 0
      ? 'identifier_matched'
      : 'provider_found';
  return {
    match_status: matchStatus,
    matched_identifiers: matchStatus === 'identifier_matched'
      ? compactIdentifiers({
          ...matchedIdentifiers,
          ...Object.fromEntries(Object.entries(evidence.provider_identifiers)
            .filter(([key]) => key !== 'doi' && key !== 'pmid')),
        })
      : matchedIdentifiers,
    mismatch_details: mismatchDetails,
    ...(matchStatus === 'metadata_conflict' ? {
      deferred_reason: `${providerId} provider metadata conflicts with input reference`,
      deferred_code: 'provider_metadata_conflict' as const,
    } : matchStatus === 'provider_found' ? {
      deferred_reason: `${providerId} provider returned an item but no DOI/PMID/PMCID identifier matched the input reference`,
      deferred_code: 'provider_found_without_identifier_match' as const,
    } : {}),
  };
}

export function compactIdentifiers(
  input: Record<string, string | null | undefined>,
): Record<string, string> {
  return Object.fromEntries(
    Object.entries(input).filter((entry): entry is [string, string] => (
      typeof entry[1] === 'string' && entry[1].length > 0
    )),
  );
}

export function compactMetadata(input: {
  title?: string | null;
  year?: string | null;
  journal?: string | null;
  authors?: string[];
  abstract?: string | null;
  article_types?: string[];
}): ReferenceMetadata {
  return Object.fromEntries(
    Object.entries(input).filter(([, value]) => (
      Array.isArray(value) ? value.length > 0 : typeof value === 'string' && value.length > 0
    )),
  ) as ReferenceMetadata;
}

export function yearFromText(value: string | null): string | null {
  return value?.match(/\d{4}/)?.[0] ?? null;
}

export function crossrefYear(item: Record<string, unknown>): string | null {
  for (const key of ['published-print', 'published-online', 'published', 'created', 'deposited']) {
    const dateParts = asRecord(item[key])['date-parts'];
    if (!Array.isArray(dateParts) || !Array.isArray(dateParts[0])) continue;
    const year = asString(dateParts[0][0]);
    if (year) return yearFromText(year);
  }
  return null;
}

export function crossrefFlags(item: Record<string, unknown>): Record<string, unknown> {
  const relation = asRecord(item.relation);
  const flags: Record<string, unknown> = {};
  if (relation['is-retracted-by'] || relation['is-withdrawn-by']) flags.retracted = true;
  if (relation['is-corrected-by'] || relation['has-update']) flags.has_update = true;
  if (Array.isArray(item['update-to']) && item['update-to'].length > 0) flags.has_update = true;
  if (asString(item['update-policy'])) flags.crossmark_update_policy = true;
  return flags;
}

export function deferredEvidence(
  reference: ReferenceRecord,
  reason: string,
  verificationScope: Record<string, unknown> = {},
): AdapterEvidence {
  return {
    match_basis: 'none',
    provider_identifiers: {},
    metadata: {},
    retraction_or_update_flags: {},
    normalized: {
      doi: normalizeDoi(reference.doi),
      pmid: reference.pmid,
      pmcid: normalizePmcid(reference.pmcid),
      title: reference.title,
    },
    verification_scope: {
      ...verificationScope,
      adapter_deferred_reason: reason,
    },
  };
}

export function providerUrl(provider: ProviderDefinition, relative: string): URL {
  const rawBase = provider.endpoint.base_url ?? provider.endpoint.default_base_url;
  let base: URL;
  let url: URL;
  try {
    base = new URL(rawBase.endsWith('/') ? rawBase : `${rawBase}/`);
    url = new URL(relative.replace(/^\//, ''), base);
  } catch (error) {
    throw new ReferenceProviderAdapterContractError(
      'adapter_provider_url_invalid',
      'Reference provider endpoint must be a valid absolute URL.',
      { provider_id: provider.provider_id, base_url: rawBase, cause: String(error) },
    );
  }
  const allowedOrigins = provider.endpoint.allowed_origins;
  if (!Array.isArray(allowedOrigins) || !allowedOrigins.includes(url.origin)) {
    throw new ReferenceProviderAdapterContractError(
      'adapter_provider_origin_not_allowed',
      'Reference provider request origin is outside the profile allowlist.',
      { provider_id: provider.provider_id, request_origin: url.origin, allowed_origins: allowedOrigins },
    );
  }
  return url;
}

export function htmlMeta(html: string, ...names: string[]): string | null {
  const wanted = new Set(names.map((entry) => entry.toLowerCase()));
  for (const match of html.matchAll(/<meta\b[^>]*>/gi)) {
    const tag = match[0];
    const key = (htmlAttribute(tag, 'name') ?? htmlAttribute(tag, 'property'))?.toLowerCase();
    const content = htmlAttribute(tag, 'content');
    if (key && content && wanted.has(key)) return decodeHtmlText(content);
  }
  return null;
}

function htmlAttribute(tag: string, name: string): string | null {
  const escapedName = name.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  const match = tag.match(new RegExp(`\\b${escapedName}\\s*=\\s*("[^"]*"|'[^']*'|[^\\s>]+)`, 'i'));
  if (!match) return null;
  return match[1].replace(/^["']|["']$/g, '').trim() || null;
}

export function htmlTitle(html: string): string | null {
  const match = html.match(/<title\b[^>]*>([\s\S]*?)<\/title>/i);
  return match ? decodeHtmlText(match[1]).replace(/\s+/g, ' ').trim() || null : null;
}

function decodeHtmlText(value: string): string {
  return value
    .replace(/&amp;/g, '&')
    .replace(/&lt;/g, '<')
    .replace(/&gt;/g, '>')
    .replace(/&quot;/g, '"')
    .replace(/&#39;/g, "'");
}
