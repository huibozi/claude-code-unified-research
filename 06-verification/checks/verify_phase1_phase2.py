from __future__ import annotations

from pathlib import Path
import json
import sys

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]

REQUIRED_FILES = [
    "README.md",
    "06-verification/README.md",
    "04-diffs-and-indexes/provenance-index/provenance.md",
    "04-diffs-and-indexes/manifests/current-comparison-summary.md",
    "04-diffs-and-indexes/manifests/source-baseline.manifest.md",
    "04-diffs-and-indexes/manifests/source-leak.manifest.md",
    "04-diffs-and-indexes/manifests/kuberwastaken.manifest.md",
    "04-diffs-and-indexes/manifests/instructkr.manifest.md",
    "04-diffs-and-indexes/structure-diffs/source-vs-source-leak.md",
    "04-diffs-and-indexes/structure-diffs/source-vs-kuberwastaken.md",
    "04-diffs-and-indexes/structure-diffs/source-vs-instructkr.md",
    "04-diffs-and-indexes/symbol-index/runtime-capability-index.md",
    "03-specs-and-parity/module-matrices/repository-capability-matrix.md",
    "03-specs-and-parity/source-derived-spec/README.md",
    "03-specs-and-parity/source-derived-spec/2026-04-01-unified-claude-code-research-runtime-design.md",
    "03-specs-and-parity/source-derived-spec/mappings/source-to-spec.md",
    "03-specs-and-parity/source-derived-spec/mappings/kuber-to-spec.md",
    "03-specs-and-parity/source-derived-spec/mappings/instructkr-to-spec.md",
    "06-verification/reports/research-repo-health.md",
    "06-verification/reports/runtime-spec-health.md",
    "06-verification/reports/mapping-coverage.md",
    "06-verification/reports/parity-conflicts.md",
]

CONCEPT_NAMES = [
    "runtime",
    "session",
    "agent",
    "command",
    "tool",
    "skill",
    "task",
    "memory",
    "connector",
    "policy",
]

EXAMPLE_TO_SCHEMA = {
    "03-specs-and-parity/source-derived-spec/examples/openclaw-agent.example.json": "03-specs-and-parity/source-derived-spec/schemas/agent.schema.json",
    "03-specs-and-parity/source-derived-spec/examples/codex-skill.example.json": "03-specs-and-parity/source-derived-spec/schemas/skill.schema.json",
    "03-specs-and-parity/source-derived-spec/examples/task-lifecycle.example.json": "03-specs-and-parity/source-derived-spec/schemas/task.schema.json",
}


def fail(message: str) -> None:
    print(f"FAIL: {message}")
    raise SystemExit(1)


def check_required_files() -> None:
    missing = [rel for rel in REQUIRED_FILES if not (ROOT / rel).exists()]
    if missing:
        fail("missing required files:\n- " + "\n- ".join(missing))
    print(f"PASS: required files present ({len(REQUIRED_FILES)})")


def check_concepts() -> None:
    concept_dir = ROOT / "03-specs-and-parity/source-derived-spec/concepts"
    concept_files = sorted(p.stem for p in concept_dir.glob("*.md"))
    expected = sorted(CONCEPT_NAMES)
    if concept_files != expected:
        fail(f"concept coverage mismatch\nexpected={expected}\nactual={concept_files}")
    print("PASS: concept coverage complete (10 files)")


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def check_schemas() -> None:
    schema_dir = ROOT / "03-specs-and-parity/source-derived-spec/schemas"
    for name in CONCEPT_NAMES:
        schema_path = schema_dir / f"{name}.schema.json"
        if not schema_path.exists():
            fail(f"missing schema: {schema_path}")
        schema = load_json(schema_path)
        Draft202012Validator.check_schema(schema)
    print("PASS: schema files parse and satisfy Draft 2020-12")


def check_examples() -> None:
    for example_rel, schema_rel in EXAMPLE_TO_SCHEMA.items():
        example = load_json(ROOT / example_rel)
        schema = load_json(ROOT / schema_rel)
        Draft202012Validator(schema).validate(example)
    print(f"PASS: example payloads validate against target schemas ({len(EXAMPLE_TO_SCHEMA)})")


def check_mapping_count() -> None:
    mapping_dir = ROOT / "03-specs-and-parity/source-derived-spec/mappings"
    mappings = sorted(p.name for p in mapping_dir.glob("*.md"))
    expected = sorted(Path(rel).name for rel in [
        "03-specs-and-parity/source-derived-spec/mappings/source-to-spec.md",
        "03-specs-and-parity/source-derived-spec/mappings/kuber-to-spec.md",
        "03-specs-and-parity/source-derived-spec/mappings/instructkr-to-spec.md",
    ])
    if mappings != expected:
        fail(f"mapping coverage mismatch\nexpected={expected}\nactual={mappings}")
    print("PASS: mapping coverage complete (3 files)")


def main() -> None:
    check_required_files()
    check_concepts()
    check_schemas()
    check_examples()
    check_mapping_count()
    print("PASS: Phase 1 and Phase 2 verification complete")


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except Exception as exc:  # pragma: no cover
        fail(str(exc))
