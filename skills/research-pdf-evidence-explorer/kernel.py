"""Deterministic refs-only helpers for research PDF evidence exploration.

No provider calls, credentials, OCR service, or MAS authority writes live here.
PDF parser imports are optional and never required for the self-check.
"""

from __future__ import annotations

import hashlib
import os
import re
from collections import Counter
from typing import Iterable, Mapping


STOPWORDS = frozenset(
    "the a an and or of to in on for with from by as at is are be this that "
    "these those it its into via using used we our their they them than also "
    "between within across paper figure table supplement".split()
)


def path_fingerprint(path: str) -> dict[str, object]:
    """Return a stable file fingerprint for a PDF or extracted text file."""
    full = os.path.abspath(os.path.expanduser(path))
    digest = hashlib.sha256()
    with open(full, "rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    stat = os.stat(full)
    return {
        "path": full,
        "sha256": digest.hexdigest(),
        "size_bytes": stat.st_size,
        "mtime_ns": stat.st_mtime_ns,
    }


def normalize_page_texts(pages: Iterable[object]) -> list[dict[str, object]]:
    """Normalize page text inputs to [{page, text, n_chars}]."""
    out: list[dict[str, object]] = []
    for index, item in enumerate(pages, start=1):
        if isinstance(item, Mapping):
            page = int(item.get("page") or index)
            text = str(item.get("text") or "")
        else:
            page = index
            text = str(item or "")
        text = text.replace("\r\n", "\n").replace("\r", "\n")
        text = re.sub(r"[ \t]+", " ", text)
        out.append({"page": page, "text": text.strip(), "n_chars": len(text.strip())})
    return out


def read_pdf_text_pages(path: str) -> list[dict[str, object]]:
    """Best-effort text extraction with optional local PDF parsers."""
    full = os.path.abspath(os.path.expanduser(path))
    try:
        from pypdf import PdfReader  # type: ignore
    except ImportError:
        PdfReader = None  # type: ignore
    if PdfReader is not None:
        reader = PdfReader(full)
        return normalize_page_texts(
            {"page": i + 1, "text": page.extract_text() or ""}
            for i, page in enumerate(reader.pages)
        )
    try:
        import fitz  # type: ignore
    except ImportError as exc:
        raise ImportError("read_pdf_text_pages requires optional pypdf or pymupdf") from exc
    with fitz.open(full) as doc:
        return normalize_page_texts(
            {"page": i + 1, "text": doc.load_page(i).get_text("text") or ""}
            for i in range(doc.page_count)
        )


def guess_outline(pages: Iterable[object]) -> list[dict[str, object]]:
    """Guess section headings from extracted page text."""
    outline: list[dict[str, object]] = []
    heading_re = re.compile(
        r"^(abstract|introduction|methods?|results?|discussion|conclusion|references|"
        r"supplement(?:ary)?|appendix|[0-9]+(?:\.[0-9]+)*\s+[A-Z][^\n]{2,80})$",
        re.I,
    )
    for page in normalize_page_texts(pages):
        for line in page["text"].splitlines():
            candidate = line.strip()
            word_count = len(candidate.split())
            if heading_re.match(candidate) and (word_count == 1 or 2 <= word_count <= 14):
                outline.append({"page": page["page"], "heading": candidate, "level": 1})
                break
    return outline


def lexical_scan(pages: Iterable[object], query: str, top_k: int = 5) -> dict[str, object]:
    """Return deterministic page candidates by term overlap and density."""
    if not query.strip():
        raise ValueError("query must be non-empty")
    terms = {t for t in re.findall(r"[a-z0-9]+", query.lower()) if len(t) > 2 and t not in STOPWORDS}
    phrase = query.lower().strip()
    denom = len(terms) or 1
    hits: list[dict[str, object]] = []
    for page in normalize_page_texts(pages):
        words = re.findall(r"[a-z0-9]+", str(page["text"]).lower())
        counts = Counter(words)
        matched = sorted(t for t in terms if counts.get(t))
        density = sum(counts.get(t, 0) for t in terms) / (len(words) or 1) * 1000
        score = len(matched) / denom + min(density, 5.0) / 10.0
        if len(phrase) > 8 and phrase in str(page["text"]).lower():
            score += 1.0
        hits.append({"page": page["page"], "score": round(score, 3), "matched": matched, "text": page["text"]})
    hits.sort(key=lambda item: (-float(item["score"]), int(item["page"])))
    return {"hits": [h for h in hits if h["score"] > 0][:top_k] or hits[:top_k], "n_scanned": len(hits)}


def regex_grep(pages: Iterable[object], pattern: str | re.Pattern[str], flags: int = re.I, context: bool = False) -> list[dict[str, object]]:
    """Regex sweep across normalized page text."""
    rx = re.compile(pattern, flags) if isinstance(pattern, str) else pattern
    rows: list[dict[str, object]] = []
    for page in normalize_page_texts(pages):
        text = str(page["text"])
        matches = [match.group(0) for match in rx.finditer(text)]
        if not matches:
            continue
        row: dict[str, object] = {"page": page["page"], "matches": matches}
        if context:
            row["lines"] = [line for line in text.splitlines() if rx.search(line)]
        rows.append(row)
    return rows


def page_evidence_ref(source_ref: str, page: int, quote_or_reason: str = "") -> dict[str, object]:
    """Create a refs-only page evidence skeleton."""
    return {
        "pdf_source_ref": source_ref,
        "page": int(page),
        "evidence_text_or_reason": quote_or_reason,
        "extraction_limitations_ref": "",
        "owner_gate_handoff_ref": "",
    }


def crop_ref_skeleton(source_ref: str, page: int, bbox: tuple[float, float, float, float] | None = None) -> dict[str, object]:
    """Create a refs-only crop reference skeleton."""
    return {
        "pdf_source_ref": source_ref,
        "page": int(page),
        "bbox": bbox,
        "pdf_crop_ref": "",
        "purpose": "",
        "owner_gate_handoff_ref": "",
    }


def _self_check() -> None:
    pages = normalize_page_texts(
        [
            "Abstract\nThis paper reports alpha beta findings.",
            {"page": 2, "text": "Methods\nWe measured beta and gamma.\nDOI 10.1000/XYZ"},
        ]
    )
    assert pages[0]["page"] == 1
    assert guess_outline(pages)[0]["heading"] == "Abstract"
    assert lexical_scan(pages, "beta gamma", top_k=1)["hits"][0]["page"] == 2
    assert regex_grep(pages, r"10\.\d{4,9}/[^\s]+")[0]["matches"] == ["10.1000/XYZ"]
    assert path_fingerprint(__file__)["sha256"]
    assert page_evidence_ref("pdf:demo", 2)["page"] == 2
    assert crop_ref_skeleton("pdf:demo", 1)["bbox"] is None


if __name__ == "__main__":
    _self_check()
    print("research-pdf-evidence-explorer kernel self-check passed")
