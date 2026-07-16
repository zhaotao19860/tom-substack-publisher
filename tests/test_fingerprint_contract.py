import importlib.util
from pathlib import Path
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "validate_article.py"


def load_validator():
    spec = importlib.util.spec_from_file_location("tom_substack_validator", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


validator = load_validator()


class FingerprintContractTests(unittest.TestCase):
    def test_compiled_html_is_required_and_part_of_fingerprint(self):
        with tempfile.TemporaryDirectory() as temp:
            run_dir = Path(temp)
            article_html = run_dir / "article.html"
            article_html.write_text("<p>first build</p>\n", encoding="utf-8")

            before = validator.compute_fingerprint(run_dir)
            article_html.write_text("<p>changed build</p>\n", encoding="utf-8")
            after = validator.compute_fingerprint(run_dir)
            self.assertNotEqual(before, after)

            article_html.unlink()
            result = validator.validate_run(run_dir)
            self.assertIn("article.html is missing", " ".join(result["errors"]))


if __name__ == "__main__":
    unittest.main()
