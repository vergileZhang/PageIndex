#!/usr/bin/env python3
"""Run the local PageIndex pipeline: index, persist workspace, restore, read back."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path


LLM_KEY_ENV_VARS = (
    "OPENAI_API_KEY",
    "CHATGPT_API_KEY",
    "ANTHROPIC_API_KEY",
    "GEMINI_API_KEY",
    "GOOGLE_API_KEY",
    "AZURE_API_KEY",
    "LITELLM_API_KEY",
)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Run PageIndex without the PageIndex cloud API: build a local "
            "workspace index, reload it, and retrieve structure/page content."
        )
    )
    parser.add_argument("--source", required=True, help="PDF or Markdown file to index.")
    parser.add_argument(
        "--workspace",
        default="./pageindex_workspace",
        help="Directory where PageIndex writes _meta.json and per-doc JSON files.",
    )
    parser.add_argument(
        "--repo-root",
        default=".",
        help="Path to a local PageIndex repo checkout. Defaults to the current directory.",
    )
    parser.add_argument("--model", default=None, help="Indexing model passed to PageIndexClient.")
    parser.add_argument(
        "--retrieve-model",
        default=None,
        help="Retrieve model passed to PageIndexClient. This script does not run an agent.",
    )
    parser.add_argument(
        "--pages",
        default="1-3",
        help='Page range to read after restore, e.g. "1-3", "3,8", or "12".',
    )
    parser.add_argument(
        "--dump-dir",
        default=None,
        help="Optional directory for restored metadata/structure/page-content JSON dumps.",
    )
    parser.add_argument(
        "--skip-key-check",
        action="store_true",
        help="Skip the LLM API key preflight for custom LiteLLM/local provider setups.",
    )
    return parser.parse_args(argv)


def _has_llm_key() -> bool:
    return any(os.getenv(name) for name in LLM_KEY_ENV_VARS)


def validate_args(args: argparse.Namespace) -> None:
    source = Path(args.source).expanduser()
    if not source.is_file():
        raise SystemExit(f"Source file not found: {source}")

    suffix = source.suffix.lower()
    if suffix not in {".pdf", ".md", ".markdown"}:
        raise SystemExit("Source must be a .pdf, .md, or .markdown file")

    if not args.skip_key_check and not _has_llm_key():
        keys = ", ".join(LLM_KEY_ENV_VARS)
        raise SystemExit(
            "Missing LLM API key. Set one of "
            f"{keys}, or pass --skip-key-check for a custom local LiteLLM setup."
        )

    repo_root = Path(args.repo_root).expanduser()
    if not (repo_root / "pageindex").is_dir():
        raise SystemExit(
            f"PageIndex package not found under repo root: {repo_root}. "
            "Run this from the PageIndex repo or pass --repo-root."
        )


def _load_json_string(payload: str) -> object:
    try:
        return json.loads(payload)
    except json.JSONDecodeError:
        return {"raw": payload}


def _write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)


def run_pipeline(args: argparse.Namespace) -> dict[str, object]:
    repo_root = Path(args.repo_root).expanduser().resolve()
    source = Path(args.source).expanduser().resolve()
    workspace = Path(args.workspace).expanduser().resolve()
    dump_dir = Path(args.dump_dir).expanduser().resolve() if args.dump_dir else workspace / "_pipeline_dump"

    sys.path.insert(0, str(repo_root))
    try:
        from pageindex import PageIndexClient
    except ModuleNotFoundError as exc:
        raise SystemExit(
            "Install dependencies first: "
            f"python3 -m pip install -r {repo_root / 'requirements.txt'} "
            f"(missing module: {exc.name})"
        ) from exc

    print(f"[1/5] Source: {source}")
    print(f"[2/5] Workspace: {workspace}")

    client = PageIndexClient(
        workspace=str(workspace),
        model=args.model,
        retrieve_model=args.retrieve_model,
    )
    print("[3/5] Building index and writing workspace JSON...")
    doc_id = client.index(str(source))

    meta_path = workspace / "_meta.json"
    doc_path = workspace / f"{doc_id}.json"
    if not meta_path.is_file():
        raise RuntimeError(f"Expected workspace meta file was not created: {meta_path}")
    if not doc_path.is_file():
        raise RuntimeError(f"Expected document index file was not created: {doc_path}")

    print("[4/5] Restoring from workspace in a fresh client...")
    restored = PageIndexClient(
        workspace=str(workspace),
        model=args.model,
        retrieve_model=args.retrieve_model,
    )

    metadata = _load_json_string(restored.get_document(doc_id))
    structure = _load_json_string(restored.get_document_structure(doc_id))
    page_content = _load_json_string(restored.get_page_content(doc_id, args.pages))

    print("[5/5] Dumping restored readback artifacts...")
    _write_json(dump_dir / "metadata.json", metadata)
    _write_json(dump_dir / "structure.json", structure)
    _write_json(dump_dir / "page_content.json", page_content)

    result = {
        "doc_id": doc_id,
        "workspace": str(workspace),
        "meta_path": str(meta_path),
        "doc_path": str(doc_path),
        "dump_dir": str(dump_dir),
        "metadata": metadata,
    }

    print("\nPipeline completed.")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return result


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    validate_args(args)
    run_pipeline(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
