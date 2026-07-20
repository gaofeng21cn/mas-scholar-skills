#!/usr/bin/env python3
"""Verify the built-in medical publication layout catalog and selector."""

from __future__ import annotations

import importlib.util
import json
import re
import xml.etree.ElementTree as ET
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = ROOT / "packs/medical-publication-layouts/publication_layout_catalog.json"
SCHEMA_PATH = ROOT / "contracts/publication-layout-profile.schema.json"
KERNEL_PATH = ROOT / "skills/medical-submission-prep/kernel.py"
EXPECTED_OUTPUTS = ["paper.pdf", "paper_with_supplementary.pdf"]
EXPECTED_JOURNAL_PROFILES = {
    "jama-network-research.v1",
    "nejm-original-article.v1",
    "lancet-research-article.v1",
    "bmj-research.v1",
    "nature-medicine-article.v1",
    "diabetes-care-original-article.v1",
    "cardiovascular-diabetology-research.v1",
    "bmc-medicine-research.v1",
    "frontiers-research-article.v1",
}


def fail(message: str) -> None:
    raise SystemExit(f"publication layout verification failed: {message}")


def read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail(f"cannot read {path.relative_to(ROOT)}: {exc}")
    if not isinstance(value, dict):
        fail(f"{path.relative_to(ROOT)} must contain an object")
    return value


def contained_file(relative: str) -> Path:
    if relative.startswith("/") or ".." in Path(relative).parts:
        fail(f"asset ref escapes package root: {relative}")
    path = ROOT / relative
    if not path.is_file() or path.is_symlink():
        fail(f"asset ref must resolve to a regular package file: {relative}")
    return path


def normalize_alias(value: object) -> str:
    return re.sub(r"[^a-z0-9]+", " ", str(value or "").strip().lower()).strip()


def load_kernel() -> Any:
    spec = importlib.util.spec_from_file_location("medical_submission_prep_kernel", KERNEL_PATH)
    if spec is None or spec.loader is None:
        fail("cannot load medical-submission-prep kernel")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    schema = read_json(SCHEMA_PATH)
    catalog = read_json(CATALOG_PATH)
    if schema.get("$schema") != "https://json-schema.org/draft/2020-12/schema":
        fail("profile schema must use JSON Schema Draft 2020-12")
    if schema.get("additionalProperties") is not False:
        fail("profile schema must reject unknown top-level fields")
    if catalog.get("surface_kind") != "mas_scholar_publication_layout_catalog.v1":
        fail("catalog surface kind mismatch")
    if catalog.get("schema_ref") != "contracts/publication-layout-profile.schema.json":
        fail("catalog schema ref mismatch")
    if catalog.get("schema_version") != 1:
        fail("catalog schema version mismatch")

    outputs = catalog.get("core_pdf_outputs") or []
    if [item.get("file_name") for item in outputs] != EXPECTED_OUTPUTS:
        fail("catalog must expose exactly paper.pdf and paper_with_supplementary.pdf")
    if [item.get("includes_supplementary") for item in outputs] != [False, True]:
        fail("core PDF supplementary roles are inverted")
    policy = catalog.get("selection_policy") or {}
    if policy.get("network_policy") != "offline_first_no_network_for_ordinary_authoring":
        fail("ordinary authoring must remain offline-first")
    if policy.get("output_policy") != "exactly_two_core_pdfs_no_third_reader_edition":
        fail("catalog must forbid a third reader edition")

    profiles = catalog.get("profiles") or []
    profile_ids = [profile.get("profile_id") for profile in profiles]
    if len(profile_ids) != len(set(profile_ids)):
        fail("profile ids must be unique")
    if catalog.get("default_profile_id") not in profile_ids:
        fail("default profile does not exist")
    journal_ids = {
        profile["profile_id"]
        for profile in profiles
        if profile.get("mode") == "journal_adaptation"
    }
    if journal_ids != EXPECTED_JOURNAL_PROFILES:
        fail("built-in journal profile set differs from the supported baseline")

    aliases: dict[str, str] = {}
    prefixes: dict[str, str] = {}
    for profile in profiles:
        profile_id = profile.get("profile_id")
        if not re.fullmatch(r"[a-z0-9][a-z0-9.-]+\.v[0-9]+", str(profile_id or "")):
            fail(f"invalid profile id: {profile_id}")
        contained_file(profile["template_assets"]["header_tex_ref"])
        contained_file(profile["template_assets"]["lua_filter_ref"])
        citation_ref = profile["template_assets"].get("citation_style_ref")
        if citation_ref:
            contained_file(citation_ref)
        for raw_alias in profile.get("aliases") or []:
            alias = normalize_alias(raw_alias)
            if not alias:
                fail(f"blank alias in {profile_id}")
            if alias in aliases and aliases[alias] != profile_id:
                fail(f"alias collision: {alias}")
            aliases[alias] = profile_id
        for raw_prefix in profile.get("alias_prefixes") or []:
            prefix = normalize_alias(raw_prefix)
            if len(prefix.split()) < 2:
                fail(f"journal-family prefix must contain at least two tokens: {profile_id}")
            if prefix in prefixes and prefixes[prefix] != profile_id:
                fail(f"alias prefix collision: {prefix}")
            prefixes[prefix] = profile_id
        freshness = profile.get("freshness_policy") or {}
        if profile.get("mode") == "journal_adaptation":
            reviewed_on = freshness.get("reviewed_on")
            try:
                date.fromisoformat(reviewed_on)
            except (TypeError, ValueError):
                fail(f"journal profile lacks a valid review date: {profile_id}")
            if freshness.get("formal_submission_refresh_required") is not True:
                fail(f"formal submission refresh must be required: {profile_id}")
            sources = profile.get("official_sources") or []
            if not sources or any(not source.get("url", "").startswith("https://") for source in sources):
                fail(f"journal profile lacks an official HTTPS source: {profile_id}")
            dynamic = profile.get("authoring_rules", {}).get(
                "dynamic_fields_requiring_official_refresh"
            ) or []
            if not dynamic:
                fail(f"journal profile must identify dynamic fields: {profile_id}")

    header = contained_file(
        "packs/medical-publication-layouts/templates/general-medical-reader/header.tex"
    ).read_text(encoding="utf-8")
    lua_filter = contained_file(
        "packs/medical-publication-layouts/templates/general-medical-reader/layout.lua"
    ).read_text(encoding="utf-8")
    if "MedicalInk" not in header or "widowpenalty" not in header or "microtype" not in header:
        fail("default header lacks publication-grade typography guards")
    forbidden_study_tokens = ["DM003", "Table 1", "F1.png", "Supplementary Figure S1"]
    if any(token in lua_filter for token in forbidden_study_tokens):
        fail("generic Lua filter contains study-specific layout rules")
    frontiers_csl = contained_file(
        "packs/medical-publication-layouts/styles/frontiers.csl"
    )
    try:
        frontiers_style = ET.parse(frontiers_csl).getroot()
    except ET.ParseError as exc:
        fail(f"Frontiers CSL is not valid XML: {exc}")
    csl_namespace = {"csl": "http://purl.org/net/xbiblio/csl"}
    frontiers_rights = frontiers_style.find("csl:info/csl:rights", csl_namespace)
    frontiers_category = frontiers_style.find("csl:info/csl:category", csl_namespace)
    if (
        frontiers_rights is None
        or frontiers_rights.get("license")
        != "http://creativecommons.org/licenses/by-sa/3.0/"
    ):
        fail("Frontiers CSL must retain its CC BY-SA 3.0 attribution")
    if (
        frontiers_category is None
        or frontiers_category.get("citation-format") != "author-date"
    ):
        fail("Frontiers CSL must retain the author-date citation family")

    kernel = load_kernel()
    default = kernel.select_publication_layout(as_of_date="2026-07-20")
    if default["selected_profile_id"] != "general-medical-reader.v1":
        fail("unnamed journal did not select the default reader profile")
    if default["core_pdf_outputs"] != EXPECTED_OUTPUTS:
        fail("selector changed the two-output contract")
    jama = kernel.select_publication_layout("JAMA Network Open", as_of_date="2026-07-20")
    if jama["selected_profile_id"] != "jama-network-research.v1":
        fail("known journal alias did not resolve locally")
    frontiers_cardiology = kernel.select_publication_layout(
        "Frontiers in Cardiology", as_of_date="2026-07-20"
    )
    frontiers_endocrinology = kernel.select_publication_layout(
        "Frontiers in Endocrinology", as_of_date="2026-07-20"
    )
    if {
        frontiers_cardiology["selected_profile_id"],
        frontiers_endocrinology["selected_profile_id"],
    } != {"frontiers-research-article.v1"}:
        fail("Frontiers journal family prefix did not resolve to one shared profile")
    frontier_false_positive = kernel.select_publication_layout(
        "Frontier Medicine", as_of_date="2026-07-20"
    )
    if frontier_false_positive["resolution_status"] != "journal_profile_pending_official_mapping":
        fail("singular Frontier journal name must not match the Frontiers family prefix")
    unknown = kernel.select_publication_layout("Example Future Journal", as_of_date="2026-07-20")
    if unknown["resolution_status"] != "journal_profile_pending_official_mapping":
        fail("unknown journal must remain pending without blocking ordinary authoring")
    if unknown["authoring_may_continue"] is not True:
        fail("unknown journal incorrectly blocked ordinary authoring")
    stale = kernel.select_publication_layout("BMJ", as_of_date="2027-01-20")
    if stale["profile_freshness"] != "stale" or stale["authoring_may_continue"] is not True:
        fail("stale local profile must remain usable for ordinary authoring")
    formal = kernel.select_publication_layout(
        "NEJM", formal_submission=True, as_of_date="2026-07-20"
    )
    if formal["official_refresh_required"] is not True:
        fail("formal submission must require official instruction refresh")
    if formal["can_claim_journal_compliance"] is not False:
        fail("selector must not claim journal compliance")

    print(
        json.dumps(
            {
                "ok": True,
                "profiles": len(profiles),
                "journal_profiles": len(journal_ids),
                "core_pdf_outputs": EXPECTED_OUTPUTS,
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
