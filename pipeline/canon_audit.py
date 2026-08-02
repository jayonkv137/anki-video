"""Canon audit — the permanent consistency detector.

Built 2026-08-02 after three defects of the SAME SHAPE landed in one session:
  · a number living in two documents with different values (curriculum ~40-75
    words vs PEDAGOGY <=30 — caught by hand, one step before the lock);
  · a canon document superseded but still registry-pinned AND still injected
    (Characters-Main-Sheet, canon_blocks);
  · a canon rule with no code enforcing it (TREATMENT's 12-parameter shot spec).

None of these are stupidity — they are DRIFT BETWEEN LAYERS, and drift is
mechanically detectable. This module is the detector, so the answer to "how do we
not do that again" is a command rather than a promise.

    python -m pipeline canon-audit [-v]

Every check is either PASS or a FINDING with a file:line. Exit code 1 on any
ERROR finding, 0 when only WARNs remain (so it can gate a commit hook later).
"""

import json
import re
from dataclasses import dataclass, field
from pathlib import Path

from . import context as ctx
from .rcp import REPO, _parse_registry

CANON_DIR = REPO / "prompts" / "canon"


@dataclass
class Finding:
    level: str      # ERROR | WARN
    check: str
    where: str
    message: str


@dataclass
class Report:
    findings: list = field(default_factory=list)
    passed: list = field(default_factory=list)

    def err(self, check, where, msg):
        self.findings.append(Finding("ERROR", check, where, msg))

    def warn(self, check, where, msg):
        self.findings.append(Finding("WARN", check, where, msg))

    def ok(self, check, note=""):
        self.passed.append((check, note))

    @property
    def errors(self):
        return [f for f in self.findings if f.level == "ERROR"]


def _canon_files() -> dict[str, str]:
    return {p.name: p.read_text(encoding="utf-8") for p in sorted(CANON_DIR.glob("*.md"))
            if p.name != "REGISTRY.md"}


def _line_of(text: str, needle: str) -> int:
    idx = text.find(needle)
    return text[:idx].count("\n") + 1 if idx >= 0 else 0


# ── 1 · Registry integrity ───────────────────────────────────────

def check_registry(rep: Report):
    """Every pinned file exists and hashes; every canon file on disk is either
    pinned or provably retired (nothing may be live-but-unpinned)."""
    registry = _parse_registry()
    ctx._canon()  # raises on hash mismatch — that IS the check
    rep.ok("registry.hashes", f"{len(registry)} files verified")

    pinned = {Path(p).name for p in registry}
    on_disk = set(_canon_files())
    unpinned = on_disk - pinned
    for name in sorted(unpinned):
        text = (CANON_DIR / name).read_text(encoding="utf-8")
        retired = re.search(r"retired|superseded|RETIRED|SUPERSEDED", text[:1500])
        lvl = rep.warn if retired else rep.err
        lvl("registry.unpinned", f"prompts/canon/{name}",
            "on disk but NOT in REGISTRY — "
            + ("marked retired; delete it once the legacy wizard dies"
               if retired else "a live canon file that nothing verifies"))
    if not unpinned:
        rep.ok("registry.unpinned", "no unpinned canon files")


# ── 2 · Cross-reference resolution ───────────────────────────────

REF_RE = re.compile(r"`?(?P<doc>[A-Z_]{4,}|prompting_guidelines_\w+)(?:\.md)?`?\s*§\s*(?P<sec>\d+(?:\.\d+)*)")
DOC_ALIASES = {
    "MISSION": "MISSION.md", "SHOW_BIBLE": "SHOW_BIBLE.md",
    "STORY_SYSTEM": "STORY_SYSTEM.md", "PEDAGOGY": "PEDAGOGY.md",
    "TREATMENT": "TREATMENT.md", "PIPELINE": "PIPELINE.md",
    "prompting_guidelines_seedance": "prompting_guidelines_seedance.md",
    "prompting_guidelines_nanobanana": "prompting_guidelines_nanobanana.md",
}


def _sections(text: str) -> set[str]:
    """Both canon heading dialects: '## 4 · Title' and '## 4. Title'."""
    return set(re.findall(r"^#{2,4} (\d+(?:\.\d+)*)[.\s·]", text, re.M))


def check_cross_refs(rep: Report):
    """Every `DOC §N` reference in canon points at a section that exists.
    A dangling § is how a rule quietly stops being findable."""
    files = _canon_files()
    sections = {name: _sections(t) for name, t in files.items()}
    dangling = 0
    checked = 0
    for name, text in files.items():
        for m in REF_RE.finditer(text):
            target = DOC_ALIASES.get(m.group("doc"))
            if not target:
                continue
            # a bare "§N" inside its own doc resolves against itself
            if target not in sections:
                rep.err("xref.missing_doc", f"prompts/canon/{name}:{_line_of(text, m.group(0))}",
                        f"references {target}, which is not in canon")
                dangling += 1
                continue
            checked += 1
            sec = m.group("sec")
            if sec in sections[target]:
                continue
            # §6.1 may live inside a "### 6.1" or be a sub-point of "## 6"
            if sec.split(".")[0] in sections[target] and "." in sec:
                continue
            rep.err("xref.dangling", f"prompts/canon/{name}:{_line_of(text, m.group(0))}",
                    f"'{m.group(0).strip()}' → {target} has no section {sec}")
            dangling += 1
    if not dangling:
        rep.ok("xref", f"{checked} cross-references resolve")


# ── 3 · Single-source-of-truth for numbers ───────────────────────

def check_level_ceilings(rep: Report):
    """The A1/A2/B1 word + sentence ceilings must agree everywhere they appear:
    PEDAGOGY §2 (the authority) · curriculum.json guardrails · schemas.LEVEL_CEILINGS.
    This is the exact defect class of C1."""
    from .schemas import LEVEL_CEILINGS
    ped = (CANON_DIR / "PEDAGOGY.md").read_text(encoding="utf-8")
    # PEDAGOGY §2 table rows: "| Spoken words per block | ≤ 30 | ≤ 55 | ≤ 80 |"
    m = re.search(r"Spoken words per block\s*\|([^\n]+)", ped)
    if not m:
        rep.err("numbers.pedagogy", "prompts/canon/PEDAGOGY.md",
                "could not find the §2 'Spoken words per block' row — the ceiling "
                "authority moved; this audit must be updated with it")
        return
    ped_words = [int(x) for x in re.findall(r"(\d+)", m.group(1))]
    cur = ctx.curriculum()["guardrails"]
    cur_words = [cur[l]["max_words"] for l in ("A1", "A2", "B1")]
    code_words = [LEVEL_CEILINGS[l][0] for l in ("A1", "A2", "B1")]
    if ped_words == cur_words == code_words:
        rep.ok("numbers.word_ceilings", f"A1/A2/B1 = {ped_words} in all three layers")
    else:
        rep.err("numbers.word_ceilings", "PEDAGOGY §2 / curriculum.json / schemas.py",
                f"disagree — PEDAGOGY {ped_words} · curriculum {cur_words} · code {code_words}")

    m = re.search(r"Max sentence length\s*\|([^\n]+)", ped)
    if m:
        ped_sent = [int(x) for x in re.findall(r"(\d+)", m.group(1))]
        cur_sent = [cur[l]["max_sentence_words"] for l in ("A1", "A2", "B1")]
        code_sent = [LEVEL_CEILINGS[l][1] for l in ("A1", "A2", "B1")]
        if ped_sent == cur_sent == code_sent:
            rep.ok("numbers.sentence_ceilings", f"A1/A2/B1 = {ped_sent} in all three layers")
        else:
            rep.err("numbers.sentence_ceilings", "PEDAGOGY §2 / curriculum.json / schemas.py",
                    f"disagree — PEDAGOGY {ped_sent} · curriculum {cur_sent} · code {code_sent}")


def check_subtitle_colours(rep: Report):
    """PEDAGOGY §5.3 owns the colour key; the subtitle engine must render it."""
    from . import subtitles
    ped = (CANON_DIR / "PEDAGOGY.md").read_text(encoding="utf-8")
    want = {}
    for label, name in (("der", "Masculine"), ("die", "Feminine"), ("das", "Neuter")):
        m = re.search(rf"{name} noun.*?`(#[0-9A-Fa-f]{{6}})`", ped)
        if m:
            want[label] = m.group(1).upper()
    m = re.search(r"target structure.*?`(#[0-9A-Fa-f]{6})`", ped)
    if m:
        want["grammar"] = m.group(1).upper()
    bad = {k: (v, subtitles.COLORS[k][0].upper())
           for k, v in want.items() if subtitles.COLORS[k][0].upper() != v}
    if bad:
        for k, (canon_hex, code_hex) in bad.items():
            rep.err("numbers.subtitle_colour", "pipeline/subtitles.py:COLORS",
                    f"'{k}' is {code_hex} in code but {canon_hex} in PEDAGOGY §5.3")
    else:
        rep.ok("numbers.subtitle_colours", f"{len(want)} colours match PEDAGOGY §5.3")

    # PEDAGOGY §5.2 resolved the subtitle conflict to STATIC colour-coded clauses:
    # keep the colour key (the retention win), drop the word-by-word reveal (which
    # destroys the reader's perceptual span). ASS \k is exactly that reveal.
    src = (REPO / "pipeline" / "subtitles.py").read_text(encoding="utf-8")
    if re.search(r'\\\\k\{?\d*\}?', src) or "\\\\k" in src:
        rep.err("numbers.subtitle_format", "pipeline/subtitles.py:render_ass",
                "emits ASS \\k (word-by-word karaoke) — PEDAGOGY §5.2 requires "
                "STATIC colour-coded clauses; the reveal costs the perceptual span")
    else:
        rep.ok("numbers.subtitle_format", "static clauses, per PEDAGOGY §5.2")


# ── 4 · Canon rule → enforcing code ──────────────────────────────

# Each entry: a HARD canon rule and the code symbol that enforces it. A rule with
# no enforcer is a rule the pipeline only *hopes* is followed.
ENFORCEMENT = [
    ("TREATMENT §5 light = named source + ratio", "pipeline/schemas.py", "light_ratio"),
    ("TREATMENT §3.1 depth of field per shot", "pipeline/schemas.py", "DOF_VALUES"),
    ("TREATMENT §8.1 atmosphere layers", "pipeline/schemas.py", "ATMOSPHERE_VALUES"),
    ("TREATMENT §6.5 tonal mode per segment", "pipeline/schemas.py", "tonal_mode"),
    ("TREATMENT §8.2 contact / blocking references", "pipeline/schemas.py", "contact_shot"),
    ("TREATMENT §1 Live-Action Integration Rule", "pipeline/schemas.py", "banned_medium"),
    ("PEDAGOGY §2 level ceilings", "pipeline/schemas.py", "LEVEL_CEILINGS"),
    ("PEDAGOGY §7 no pedagogical fourth wall", "pipeline/schemas.py", "DEFAULT_BANNED_TOKENS"),
    ("PIPELINE §6 dependency graph decides recompiles", "pipeline/overseer.py", "_describe_recompile"),
    ("REGISTRY hash verification aborts a run", "pipeline/rcp.py", "verify_canon"),
]


def check_enforcement(rep: Report):
    missing = []
    for rule, path, symbol in ENFORCEMENT:
        src = (REPO / path).read_text(encoding="utf-8")
        if symbol not in src:
            missing.append((rule, path, symbol))
            rep.err("enforcement.missing", path,
                    f"'{rule}' has no enforcer — expected symbol '{symbol}'")
    if not missing:
        rep.ok("enforcement", f"{len(ENFORCEMENT)} HARD rules have enforcing code")


# ── 5 · Retired material must be dead ────────────────────────────

RETIRED = {
    "prompting_guidelines_omni.md": "deleted 2026-08-02",
    "canon_blocks.md": "folded into TREATMENT §10 (2026-08-02)",
    "Characters-Main-Sheet.md": "superseded by SHOW_BIBLE §6 (2026-08-02)",
}
# canon_audit.py itself is excluded: naming the retired documents is its job.
LIVE_CODE = ["pipeline/context.py", "pipeline/llm.py", "pipeline/schemas.py",
             "pipeline/universe_state.py", "pipeline/subtitles.py"]


def check_retired(rep: Report):
    """No V4 module may reference a retired document. (stages.py/rcp.py are the
    legacy wizard's, exempt until Phase 3.5 deletes them.)"""
    hits = 0
    for path in LIVE_CODE:
        src = (REPO / path).read_text(encoding="utf-8")
        for name in RETIRED:
            stem = name.replace(".md", "")
            for m in re.finditer(re.escape(stem), src):
                line = src[:m.start()].count("\n") + 1
                if re.search(r"^\s*#", src.splitlines()[line - 1]):
                    continue  # a comment explaining the retirement is fine
                rep.err("retired.referenced", f"{path}:{line}",
                        f"references retired '{name}' ({RETIRED[name]})")
                hits += 1
    if not hits:
        rep.ok("retired", f"{len(RETIRED)} retired docs unreferenced by V4 code")


# ── 6 · Curriculum integrity ─────────────────────────────────────

def check_curriculum(rep: Report):
    cur = ctx.curriculum()
    meta = cur["meta"]
    import hashlib
    live = hashlib.sha256((REPO / meta["source"]).read_text(encoding="utf-8")
                          .encode("utf-8")).hexdigest()
    if live != meta["source_sha256"]:
        rep.err("curriculum.drift", meta["source"],
                "the markdown source changed since the lock — re-run "
                "scripts/build_curriculum.py and re-pin the registry")
    else:
        rep.ok("curriculum.source", "markdown unchanged since the lock")

    ids = [a["id"] for m in cur["modules"] for a in m["atoms"]]
    if len(ids) != len(set(ids)):
        rep.err("curriculum.ids", "resources/curriculum.json", "duplicate atom ids")
    elif len(ids) != meta["totals"]["atoms"]:
        rep.err("curriculum.count", "resources/curriculum.json",
                f"{len(ids)} atoms but meta says {meta['totals']['atoms']}")
    else:
        rep.ok("curriculum.atoms", f"{len(ids)} unique ids match the declared totals")

    # every level named in guardrails is a level some module actually uses
    levels = {m["level"] for m in cur["modules"]}
    if levels - set(cur["guardrails"]):
        rep.err("curriculum.guardrails", "resources/curriculum.json",
                f"levels without guardrails: {sorted(levels - set(cur['guardrails']))}")
    else:
        rep.ok("curriculum.guardrails", f"guardrails cover {sorted(levels)}")


# ── 7 · Phase context contracts ──────────────────────────────────

def check_phase_contracts(rep: Report):
    """Every phase's canon list resolves, every station contract extracts, and the
    scoping map (if non-empty) carries a written justification."""
    bad = 0
    for phase in ctx.PHASES:
        for doc in ctx.PHASE_CANON[phase]:
            if doc not in ctx.CANON_PATHS:
                rep.err("phase.unknown_doc", f"context.PHASE_CANON[{phase}]",
                        f"'{doc}' is not a canon path")
                bad += 1
        sc = ctx.station_contract(phase)
        if len(sc) < 200:
            rep.err("phase.contract_empty", f"context.station_contract('{phase}')",
                    "extracted station contract is suspiciously short — a PIPELINE "
                    "heading probably moved")
            bad += 1
    if ctx.DOC_SECTIONS:
        src = (REPO / "pipeline" / "context.py").read_text(encoding="utf-8")
        if "PIPELINE §" not in src.split("DOC_SECTIONS")[0][-2000:]:
            rep.warn("phase.scoping_unjustified", "pipeline/context.py:DOC_SECTIONS",
                     "canon is being section-scoped without a station-contract "
                     "justification recorded beside it")
    if not bad:
        rep.ok("phase.contracts", f"{len(ctx.PHASES)} phases resolve their canon + contract")


# ── Runner ───────────────────────────────────────────────────────

CHECKS = [check_registry, check_cross_refs, check_level_ceilings, check_subtitle_colours,
          check_enforcement, check_retired, check_curriculum, check_phase_contracts]


def run() -> Report:
    rep = Report()
    for fn in CHECKS:
        try:
            fn(rep)
        except Exception as e:
            rep.err("audit.crashed", fn.__name__, f"{type(e).__name__}: {e}")
    return rep


def main(verbose: bool = False) -> int:
    rep = run()
    if verbose:
        for check, note in rep.passed:
            print(f"  ✓ {check:32s} {note}")
    for f in rep.findings:
        icon = "✗" if f.level == "ERROR" else "!"
        print(f"  {icon} [{f.level}] {f.check}\n      {f.where}\n      {f.message}")
    n_err = len(rep.errors)
    n_warn = len(rep.findings) - n_err
    print(f"\ncanon audit: {len(rep.passed)} passed · {n_err} error(s) · {n_warn} warning(s)")
    return 1 if n_err else 0
