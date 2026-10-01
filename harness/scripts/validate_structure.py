#!/usr/bin/env python3
"""
validate_structure.py — BA Spec Harness structure checker.

Usage:
    python3 harness/scripts/validate_structure.py <path-to-output-file.md>

Exit code 0 = no FAIL-level issues (WARNs may still be printed).
Exit code 1 = at least one FAIL-level issue found.

This script only reads the file — it never modifies it. The AI that wrote
the file is responsible for reading this report, fixing the file directly,
and re-running this script until it passes. See ORCHESTRATOR.md, "Choosing
and running a step", steps 9-10, for when this must run.

Stdlib only (re, sys, os) — no dependencies, so it runs the same way on
Kiro, Claude Code, and Gemini CLI's shell/execute tool.
"""
import os
import re
import sys

SECTION_TITLES = [
    (1, "Metadata"),
    (2, "Overview"),
    (3, "Defined Scope"),
    (4, "Features and Behaviors"),
    (5, "Edge Cases and Error States"),
    (6, "Auth and Permissions"),
    (7, "Data Model"),
    (8, "Integrations"),
    (9, "UI/UX Notes"),
    (10, "Success Metrics"),
]

PERSONA_HEADINGS = [
    "Backend Engineering",
    "Frontend Engineering",
    "QA / Testing",
    "Design / UX",
    "Product / Data",
]

STRUCTURED_TYPES = {
    "rewrite", "ba-review-draft", "team-review-draft", "final",
}

# Matches [OPEN: ...] or [OPEN (Persona): ...]. Assumes the question text
# itself doesn't contain literal [ or ] characters.
OPEN_TAG_RE = re.compile(r"\[OPEN(?:\s*\([^)]*\))?\s*:[^\[\]]*\]")
# Only a clean "### FR-NNN — <title>" (or "### FR-NNN - <title>") counts as
# an FR *definition* heading. Edge-case headings like
# "### FR-005/FR-006-E1 — ..." must NOT match here — they reference FRs,
# they don't define one.
FR_HEADING_RE = re.compile(r"^###\s+FR-(\d{3})\s*[—\-–]\s+\S", re.MULTILINE)
FR_EDGE_RE = re.compile(r"\bFR-(\d{3})-E(\d+)\b")
SECTION_SPLIT_RE = re.compile(r"^##\s+4\.", re.MULTILINE)
SECTION5_SPLIT_RE = re.compile(r"^##\s+5\.", re.MULTILINE)
MD_LINK_RE = re.compile(r"\[([^\]]*)\]\(([^)]+)\)")


def detect_type(filename):
    name = os.path.basename(filename)
    m = re.match(r"^\[([a-zA-Z0-9\-]+)\]-", name)
    return m.group(1) if m else None


def fail(issues, msg):
    issues.append(("FAIL", msg))


def warn(issues, msg):
    issues.append(("WARN", msg))


def check_sections(text, issues):
    for num, title_fragment in SECTION_TITLES:
        keyword = title_fragment.split()[0]
        pattern = re.compile(
            r"^##\s+" + str(num) + r"\.\s+.*" + re.escape(keyword),
            re.MULTILINE | re.IGNORECASE,
        )
        if not pattern.search(text):
            fail(
                issues,
                f"Missing or misnumbered heading for Section {num} "
                f"({title_fragment}) — expected a line like "
                f"'## {num}. {title_fragment}...'",
            )


def check_toc(text, issues):
    sec1 = re.search(
        r"^##\s+1\..*?(?=^##\s+2\.|\Z)", text, re.MULTILINE | re.DOTALL
    )
    block = sec1.group(0) if sec1 else text
    links = MD_LINK_RE.findall(block)
    anchor_links = [l for l in links if l[1].startswith("#")]
    if len(anchor_links) < 8:
        fail(
            issues,
            "Table of Contents in Section 1 must be a real linked list "
            f"(one link per section) — found only {len(anchor_links)} "
            "anchor link(s). A placeholder sentence is not acceptable.",
        )


def _section4_text(text):
    """Return only the Section 4 body (Features and Behaviors), so FR
    definition headings aren't confused with edge-case headings in
    Section 5 that merely *reference* one or more FR IDs."""
    start_m = SECTION_SPLIT_RE.search(text)
    if not start_m:
        return text
    end_m = SECTION5_SPLIT_RE.search(text, start_m.end())
    return text[start_m.end(): end_m.start() if end_m else len(text)]


def check_fr_ids(text, issues):
    ids = [int(m.group(1)) for m in FR_HEADING_RE.finditer(_section4_text(text))]
    if not ids:
        return ids
    seen, dupes = set(), set()
    for i in ids:
        (dupes if i in seen else seen).add(i)
    if dupes:
        fail(
            issues,
            "Duplicate FR IDs found: "
            f"{sorted('FR-%03d' % d for d in dupes)} — FR IDs must never "
            "be reused.",
        )
    if ids != sorted(ids):
        warn(
            issues,
            "FR IDs do not appear in ascending order — verify none were "
            "renumbered out of sequence.",
        )
    first = sorted(set(ids))[0]
    if first != 1:
        warn(
            issues,
            f"First FR ID is FR-{first:03d}, not FR-001 — confirm this is "
            "intentional (e.g. a re-run continuing an existing document).",
        )
    return ids


def check_edge_cases(text, fr_ids, issues):
    fr_set = set(fr_ids)
    for m in FR_EDGE_RE.finditer(text):
        fr_num = int(m.group(1))
        if fr_num not in fr_set:
            fail(
                issues,
                f"Edge case FR-{fr_num:03d}-E{m.group(2)} references "
                f"FR-{fr_num:03d}, which has no matching FR heading in "
                "Section 4.",
            )


def check_open_tag_emphasis(text, issues):
    bad = []
    for m in OPEN_TAG_RE.finditer(text):
        start, end = m.span()
        before = text[start - 1] if start > 0 else ""
        after = text[end] if end < len(text) else ""
        if before != "`" or after != "`":
            bad.append(m.group(0)[:60])
    if bad:
        fail(
            issues,
            f"{len(bad)} open-question tag(s) are not wrapped in "
            "backticks (must read like `[OPEN: ...]` with backticks on "
            f"both sides). First example: {bad[0]}...",
        )


def check_traceability_groups(text, issues):
    groups = re.findall(
        r"^##\s+Resolved Questions\s*—\s*(\S+)", text, re.MULTILINE
    )
    if not groups:
        fail(
            issues,
            "'final' documents must have at least one traceability group "
            "('## Resolved Questions — <step> (<timestamp>)') — none "
            "found. See ORCHESTRATOR.md, 'The final document'.",
        )
    return [g.rstrip("(") for g in groups]


def check_final_team_review_carryover(text, issues, step_names):
    """If a 'final' document's traceability shows team_review has run at
    least once, the 5 persona sections and Overall Verdict must be carried
    into the final document too (03-team-review.md, Phase C) — they must
    never be silently dropped when the document is finalized/updated."""
    if not any("team_review" in s for s in step_names):
        return
    check_personas(text, issues)
    check_verdict(text, issues)


def check_open_tag_count_vs_list(text, issues):
    inline_count = len(OPEN_TAG_RE.findall(text))
    if inline_count == 0:
        return
    list_match = re.search(r"^##\s+Open (Questions|Items).*", text, re.MULTILINE)
    if not list_match:
        fail(
            issues,
            f"Found {inline_count} inline open-question tag(s) but no "
            "'Open Questions' / 'Open Items' section at the end of the "
            "document.",
        )
        return
    tail = text[list_match.end():]
    entries = re.findall(r"^\s*(?:\d+\.|-)\s+", tail, re.MULTILINE)
    if len(entries) < inline_count:
        warn(
            issues,
            f"{inline_count} inline open-question tag(s) found, but only "
            f"{len(entries)} entries in the Open Questions/Items list — "
            "verify every tag has a matching list entry (principles.md §2).",
        )


def check_rewrite_no_open_tags(text, issues):
    count = len(OPEN_TAG_RE.findall(text))
    if count > 0:
        fail(
            issues,
            "'rewrite' must never write [OPEN: ...] tags (principles.md "
            f"§5), but {count} were found.",
        )


def check_personas(text, issues):
    for persona in PERSONA_HEADINGS:
        pattern = re.compile(r"^##\s+" + re.escape(persona) + r"\s*$", re.MULTILINE)
        if not pattern.search(text):
            fail(
                issues,
                f"Missing required persona section: '## {persona}' — "
                "team_review must include all 5 persona headings, even if "
                "a persona has no findings.",
            )


def check_verdict(text, issues):
    if not re.search(r"Overall Verdict", text, re.IGNORECASE):
        fail(issues, "Missing 'Overall Verdict' section.")
    elif not re.search(r"🔴|🟡|🟢", text):
        warn(issues, "Overall Verdict section found, but no 🔴/🟡/🟢 marker detected.")


def check_estimation(text, issues):
    if not re.search(r"\|\s*FR\s*\|", text, re.IGNORECASE):
        fail(
            issues,
            "Missing the required sizing table (columns: FR | Size | Key "
            "assumption | Key risk/unknown).",
        )
    if not re.search(
        r"Rough estimate.*pre-technical-design.*not a commitment",
        text,
        re.IGNORECASE,
    ):
        fail(
            issues,
            "Missing the required disclaimer label: \"Rough estimate, "
            "pre-technical-design — not a commitment.\"",
        )


HEDGE_WORDS = [
    "generally", "typically", "usually", "in most cases", "often",
    "nói chung", "phần lớn", "hầu hết",
    # NOTE: "thường" was removed — it's a substring of "chữ thường"
    # (lowercase, a normal field value in this domain, e.g. "chữ
    # hoa/thường"), so a plain substring match on it alone produced
    # constant false positives. If a genuine standalone hedge word
    # ("thường thì", "thông thường") needs catching later, add a more
    # specific phrase here instead of the bare word.
]
FILLER_WORDS = [
    "basically", "simply", "in order to", "there is a need for",
    "is able to",
]
SPELLED_NUMBER_NEAR_UNIT_RE = re.compile(
    r"\b(one|two|three|four|five|six|seven|eight|nine|ten|a couple of)\s+"
    r"(megabyte|kilobyte|gigabyte|mb|kb|gb|second|minute|hour|day|week)s?\b",
    re.IGNORECASE,
)


def check_sentence_craft_hints(text, issues):
    """WARN-only, best-effort hints for reference_structure.md's Sentence
    craft section. This cannot judge prose quality — it only flags
    specific word choices the AI is expected to review by hand
    (review-checklist.md item 15). Never FAILs; a flagged word may be
    legitimate depending on context (e.g. quoted from source, or already
    inside an [OPEN: ...] tag)."""
    open_spans = [m.span() for m in OPEN_TAG_RE.finditer(text)]

    def inside_open_tag(pos):
        return any(start <= pos < end for start, end in open_spans)

    for word in HEDGE_WORDS:
        for m in re.finditer(r"\b" + re.escape(word) + r"\b", text, re.IGNORECASE):
            if not inside_open_tag(m.start()):
                warn(
                    issues,
                    f"Hedge word '{m.group(0)}' found outside an "
                    "`[OPEN: ...]` tag — per Sentence craft, either state "
                    "the rule plainly or flag it open (review manually; "
                    "not auto-fixable).",
                )
                break  # one WARN per word type is enough signal

    for phrase in FILLER_WORDS:
        if re.search(r"\b" + re.escape(phrase) + r"\b", text, re.IGNORECASE):
            warn(
                issues,
                f"Filler phrase '{phrase}' found — Sentence craft asks to "
                "cut this (review manually).",
            )

    if SPELLED_NUMBER_NEAR_UNIT_RE.search(text):
        warn(
            issues,
            "A number appears spelled out next to a unit (e.g. 'five "
            "megabytes') — Sentence craft asks for numerals near units "
            "(review manually).",
        )


def check_relative_links(text, issues):
    for _, path in MD_LINK_RE.findall(text):
        if path.startswith("http"):
            continue
        if path.startswith("/") or re.match(r"^[A-Za-z]:\\", path):
            warn(
                issues,
                f"Link to '{path}' looks like an absolute path — project "
                "file links should be relative.",
            )


def main():
    if len(sys.argv) != 2:
        print("Usage: python3 validate_structure.py <path-to-output-file.md>")
        sys.exit(2)

    path = sys.argv[1]
    if not os.path.isfile(path):
        print(f"File not found: {path}")
        sys.exit(2)

    with open(path, "r", encoding="utf-8") as f:
        text = f.read()

    filetype = detect_type(path)
    issues = []

    if filetype in STRUCTURED_TYPES:
        check_sections(text, issues)
        check_toc(text, issues)
        fr_ids = check_fr_ids(text, issues)
        check_edge_cases(text, fr_ids, issues)
        check_relative_links(text, issues)

    if filetype in STRUCTURED_TYPES or filetype == "estimation":
        check_sentence_craft_hints(text, issues)

    check_open_tag_emphasis(text, issues)

    if filetype == "rewrite":
        check_rewrite_no_open_tags(text, issues)
    elif filetype in STRUCTURED_TYPES:
        check_open_tag_count_vs_list(text, issues)

    if filetype == "team-review-draft":
        check_personas(text, issues)
        check_verdict(text, issues)

    if filetype == "final":
        step_names = check_traceability_groups(text, issues)
        check_final_team_review_carryover(text, issues, step_names)

    if filetype == "estimation":
        check_estimation(text, issues)

    if filetype is None:
        print(
            f"WARN: could not detect step type from filename "
            f"'{os.path.basename(path)}' — expected it to start with "
            "'[<label>]-'. Ran only generic checks.\n"
        )

    fails = [m for lvl, m in issues if lvl == "FAIL"]
    warns = [m for lvl, m in issues if lvl == "WARN"]

    print(f"Structure check: {os.path.basename(path)}  (type: {filetype or 'unknown'})")
    print(f"  {len(fails)} FAIL, {len(warns)} WARN\n")
    for lvl, msg in issues:
        print(f"[{lvl}] {msg}")
    if not issues:
        print("All checks passed.")

    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
