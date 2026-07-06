import importlib.util
import json
import unittest
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "examples" / "pageindex_pipeline_demo.py"


def load_script():
    spec = importlib.util.spec_from_file_location("pageindex_pipeline_demo", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class FakeClient:
    def __init__(self):
        self.requested_pages = None

    def get_document_structure(self, doc_id):
        return json.dumps([
            {"title": "Intro", "node_id": "0001", "start_index": 1, "end_index": 1},
            {"title": "Method", "node_id": "0002", "start_index": 2, "end_index": 3},
        ])

    def get_page_content(self, doc_id, pages):
        self.requested_pages = pages
        return json.dumps([
            {"page": 2, "content": "The method uses a tree index."},
            {"page": 3, "content": "The answer should cite these pages."},
        ])


class PipelineDemoTests(unittest.TestCase):
    def test_question_and_qa_model_arguments_are_parsed(self):
        script = load_script()
        args = script.parse_args([
            "--source",
            "doc.pdf",
            "--question",
            "What is the method?",
            "--qa-model",
            "gpt-4o-mini",
        ])

        self.assertEqual(args.question, "What is the method?")
        self.assertEqual(args.qa_model, "gpt-4o-mini")

    def test_normalize_pages_accepts_lists_and_ranges(self):
        script = load_script()

        self.assertEqual(script._normalize_pages(["2", "5-6", 3], "1-2"), "2,5-6,3")
        self.assertEqual(script._normalize_pages("", "1-2"), "1-2")

    def test_qa_pipeline_selects_pages_and_generates_answer(self):
        script = load_script()
        client = FakeClient()
        calls = []

        def fake_llm(model, prompt):
            calls.append(prompt)
            if len(calls) == 1:
                return '{"thinking": "Method spans these pages", "pages": "2-3"}'
            return "The method uses a tree index. [pages 2-3]"

        result = script.run_qa_pipeline(
            client=client,
            doc_id="doc-1",
            question="What is the method?",
            qa_model="test-model",
            fallback_pages="1-2",
            llm_func=fake_llm,
        )

        self.assertEqual(client.requested_pages, "2-3")
        self.assertEqual(result["selected_pages"], "2-3")
        self.assertIn("tree index", result["answer"])


if __name__ == "__main__":
    unittest.main()
