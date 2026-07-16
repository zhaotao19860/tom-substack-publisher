from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class ReadmeContractTests(unittest.TestCase):
    def test_readme_documents_public_usage_and_safety(self):
        text = (ROOT / "README.md").read_text(encoding="utf-8")
        for required in (
            "# tom-substack-publisher",
            "## 工作流",
            "## 安装",
            "https://github.com/zhaotao19860/tom-substack-publisher.git",
            "${HOME}/.comate/skills/tom-substack-publisher",
            "ian-xiaohei-illustrations",
            "content fingerprint",
            "send_email=false",
            "## 开发与验证",
            "python3 -m unittest discover -s tests -v",
            "## 已知限制",
        ):
            self.assertIn(required, text)

    def test_gitignore_excludes_local_and_sensitive_artifacts(self):
        text = (ROOT / ".gitignore").read_text(encoding="utf-8")
        for required in (
            "__pycache__/",
            ".env*",
            "*cookie*",
            "*token*",
            "/candidates.md",
            "/sources.json",
            "/article.md",
            "/article.html",
            "/preview.html",
            "/images/",
            "/publish-receipt.json",
            "/latest-article-path.txt",
        ):
            self.assertIn(required, text)
