#!/usr/bin/env python3
"""Run the local PageIndex pipeline: index, restore, retrieve, and optionally answer."""

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
        "--question",
        default=None,
        help="Optional question. When set, the script retrieves relevant pages and generates an answer.",
    )
    parser.add_argument(
        "--qa-model",
        default=None,
        help="Model used for optional page selection and answer generation.",
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


def _normalize_pages(value: object, fallback: str) -> str:
    if isinstance(value, list):
        pages = [str(item).strip() for item in value if str(item).strip()]
        return ",".join(pages) or fallback
    if isinstance(value, str):
        return value.strip() or fallback
    return fallback


def _write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)


def run_qa_pipeline(
    client: object,
    doc_id: str,
    question: str,
    qa_model: str,
    fallback_pages: str,
    llm_func: object | None = None,
) -> dict[str, object]:
    if llm_func is None:
        from pageindex.utils import llm_completion

        llm_func = llm_completion

    structure = _load_json_string(client.get_document_structure(doc_id))
    selection_prompt = f"""
You are using a PageIndex document tree to retrieve context for a question.
Pick the tightest page range or comma-separated page list that is likely to answer the question.
Return JSON only, with this schema:
{{"thinking": "brief reason", "pages": "2-4"}}

Question:
{question}

PageIndex structure JSON:
{json.dumps(structure, ensure_ascii=False)}
""".strip()
    selection_raw = llm_func(qa_model, selection_prompt)
    selection = _load_json_string(selection_raw)

    selected_pages = fallback_pages
    if isinstance(selection, dict):
        selected_pages = _normalize_pages(
            selection.get("pages") or selection.get("page") or selection.get("selected_pages"),
            fallback_pages,
        )

    page_content = _load_json_string(client.get_page_content(doc_id, selected_pages))
    answer_prompt = f"""
Answer the question using only the retrieved page content below.
If the content is insufficient, say what is missing instead of guessing.
Cite page numbers inline when possible.

Question:
{question}

Retrieved page content JSON:
{json.dumps(page_content, ensure_ascii=False)}
""".strip()
    answer = llm_func(qa_model, answer_prompt)

    return {
        "question": question,
        "qa_model": qa_model,
        "selection": selection,
        "selected_pages": selected_pages,
        "page_content": page_content,
        "answer": answer,
    }


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

    qa_result = None
    qa_result_path = None
    if args.question:
        qa_model = args.qa_model or args.retrieve_model or args.model or restored.retrieve_model
        print("[QA] Selecting pages from the structure and generating an answer...")
        qa_result = run_qa_pipeline(
            client=restored,
            doc_id=doc_id,
            question=args.question,
            qa_model=qa_model,
            fallback_pages=args.pages,
        )
        qa_result_path = dump_dir / "qa_result.json"
        _write_json(qa_result_path, qa_result)

    result = {
        "doc_id": doc_id,
        "workspace": str(workspace),
        "meta_path": str(meta_path),
        "doc_path": str(doc_path),
        "dump_dir": str(dump_dir),
        "metadata": metadata,
    }
    if qa_result is not None:
        result["qa_result_path"] = str(qa_result_path)
        result["selected_pages"] = qa_result["selected_pages"]
        result["answer"] = qa_result["answer"]

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
