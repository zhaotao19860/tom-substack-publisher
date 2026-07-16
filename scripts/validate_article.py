#!/usr/bin/env python3
"""Validate a prepared tom-substack-publisher article run."""

from __future__ import annotations

import argparse
from datetime import date, datetime, time, timedelta, timezone
import hashlib
import json
from pathlib import Path
import re
import sys
from typing import Any
from urllib.parse import urlparse


CJK_RE = re.compile(r"[\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]")
FRONTMATTER_RE = re.compile(r"\A---\s*\n(?P<meta>.*?)\n---\s*\n?", re.DOTALL)
IMAGE_RE = re.compile(r"!\[([^\]]*)\]\(([^)]+)\)")
FENCED_CODE_RE = re.compile(r"(?ms)^```[^\n]*\n.*?^```\s*$|^~~~[^\n]*\n.*?^~~~\s*$")
SOURCE_SECTION_RE = re.compile(
    r"(?ims)^#{2,6}\s*(?:参考来源|资料来源|来源|sources?|references?)\s*$.*\Z"
)
BEIJING = timezone(timedelta(hours=8))
REQUIRED_METADATA = ("title", "subtitle", "run_date", "window_start", "window_end")


def load_frontmatter(path: Path) -> tuple[dict[str, str], str]:
    text = path.read_text(encoding="utf-8")
    match = FRONTMATTER_RE.match(text)
    if not match:
        raise ValueError("article.md must start with YAML frontmatter")

    metadata: dict[str, str] = {}
    for line_number, raw_line in enumerate(match.group("meta").splitlines(), start=2):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" not in line:
            raise ValueError(f"invalid frontmatter line {line_number}: {raw_line}")
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
            value = value[1:-1]
        if not key:
            raise ValueError(f"empty frontmatter key on line {line_number}")
        metadata[key] = value
    return metadata, text[match.end() :]


def count_cjk(text: str) -> int:
    return len(CJK_RE.findall(text))


def readable_body(text: str) -> str:
    without_code = FENCED_CODE_RE.sub("", text)
    return SOURCE_SECTION_RE.sub("", without_code)


def estimate_reading_minutes(text: str) -> float:
    return round(count_cjk(readable_body(text)) / 450.0, 2)


def markdown_images(text: str) -> list[tuple[str, str]]:
    images: list[tuple[str, str]] = []
    for alt, raw_target in IMAGE_RE.findall(text):
        target = raw_target.strip()
        if target.startswith("<") and target.endswith(">"):
            target = target[1:-1]
        else:
            target = re.sub(r"\s+[\"'].*[\"']\s*$", "", target)
        images.append((alt.strip(), target.strip()))
    return images


def load_sources(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError("sources.json is missing") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"sources.json is invalid JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError("sources.json must contain a JSON object")
    return data


def _valid_http_url(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    parsed = urlparse(value)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def _parse_datetime(value: str, field: str, errors: list[str]) -> datetime | None:
    try:
        parsed = datetime.fromisoformat(value)
    except (TypeError, ValueError):
        errors.append(f"{field} must be an ISO 8601 datetime")
        return None
    if parsed.tzinfo is None:
        errors.append(f"{field} must include a timezone offset")
        return None
    return parsed


def _expected_window(run_date: date) -> tuple[datetime, datetime]:
    start_date = run_date - timedelta(days=2)
    end_date = run_date - timedelta(days=1)
    return (
        datetime.combine(start_date, time.min, tzinfo=BEIJING),
        datetime.combine(end_date, time(23, 59, 59), tzinfo=BEIJING),
    )


def compute_fingerprint(run_dir: Path) -> str:
    run_dir = run_dir.expanduser().resolve()
    digest = hashlib.sha256()
    paths = [
        run_dir / "article.md",
        run_dir / "article.html",
        run_dir / "sources.json",
    ]
    image_dir = run_dir / "images"
    if image_dir.is_dir():
        paths.extend(sorted(path for path in image_dir.rglob("*") if path.is_file()))

    for path in paths:
        relative = path.relative_to(run_dir).as_posix()
        digest.update(relative.encode("utf-8"))
        digest.update(b"\0")
        try:
            digest.update(path.read_bytes())
        except FileNotFoundError:
            digest.update(b"<missing>")
        digest.update(b"\0")
    return digest.hexdigest()


def validate_run(run_dir: Path) -> dict[str, Any]:
    run_dir = run_dir.expanduser().resolve()
    errors: list[str] = []
    warnings: list[str] = []
    article_path = run_dir / "article.md"
    article_html_path = run_dir / "article.html"
    sources_path = run_dir / "sources.json"
    metadata: dict[str, str] = {}
    body = ""

    if not run_dir.is_dir():
        errors.append(f"run directory does not exist: {run_dir}")
    if not article_path.is_file():
        errors.append("article.md is missing")
    if not article_html_path.is_file():
        errors.append("article.html is missing; run build_preview.py before validation")
    else:
        try:
            metadata, body = load_frontmatter(article_path)
        except (OSError, ValueError) as exc:
            errors.append(str(exc))

    for field in REQUIRED_METADATA:
        if not metadata.get(field):
            errors.append(f"frontmatter field is required: {field}")

    actual_start: datetime | None = None
    actual_end: datetime | None = None
    run_day: date | None = None
    if metadata.get("run_date"):
        try:
            run_day = date.fromisoformat(metadata["run_date"])
        except ValueError:
            errors.append("run_date must use YYYY-MM-DD")
    if metadata.get("window_start"):
        actual_start = _parse_datetime(metadata["window_start"], "window_start", errors)
    if metadata.get("window_end"):
        actual_end = _parse_datetime(metadata["window_end"], "window_end", errors)
    if run_day and actual_start and actual_end:
        expected_start, expected_end = _expected_window(run_day)
        if actual_start != expected_start:
            errors.append(
                f"window_start must be D-2 00:00:00+08:00 ({expected_start.isoformat()})"
            )
        if actual_end != expected_end:
            errors.append(
                f"window_end must be D-1 23:59:59+08:00 ({expected_end.isoformat()})"
            )

    cjk_chars = count_cjk(readable_body(body))
    reading_minutes = estimate_reading_minutes(body)
    if body and not 1800 <= cjk_chars <= 2600:
        errors.append(
            f"article body must contain 1,800-2,600 Chinese characters; found {cjk_chars}"
        )
    if body and not 4.0 <= reading_minutes <= 6.0:
        errors.append(
            f"estimated reading time must be 4-6 minutes; found {reading_minutes}"
        )

    image_entries = markdown_images(body)
    image_roles: set[str] = set()
    local_image_count = 0
    for alt, target in image_entries:
        if target.startswith(("http://", "https://")):
            errors.append(f"article image must be local before publication: {target}")
            continue
        image_path = (run_dir / target).resolve()
        try:
            image_path.relative_to(run_dir)
        except ValueError:
            errors.append(f"image path escapes the run directory: {target}")
            continue
        if not image_path.is_file() or image_path.stat().st_size == 0:
            errors.append(f"missing local image: {target}")
            continue
        local_image_count += 1
        role_text = f"{alt} {image_path.name}".lower()
        if "cover" in role_text:
            image_roles.add("cover")
        if "body-ai" in role_text or "body-hybrid" in role_text:
            image_roles.add("body-ai-or-hybrid")
        if "body-fact" in role_text:
            image_roles.add("body-fact")

    if local_image_count < 3:
        errors.append(f"at least three local images are required; found {local_image_count}")
    if "cover" not in image_roles:
        errors.append("an AI cover image role is required")
    if "body-ai-or-hybrid" not in image_roles:
        errors.append("an AI or hybrid body visual role is required")
    if "body-fact" not in image_roles:
        errors.append("a deterministic body-fact visual role is required")

    source_count = 0
    try:
        sources = load_sources(sources_path)
    except ValueError as exc:
        errors.append(str(exc))
        sources = {}

    candidates = sources.get("candidates", []) if isinstance(sources, dict) else []
    if not isinstance(candidates, list):
        errors.append("sources.json candidates must be an array")
        candidates = []
    verified = [
        candidate
        for candidate in candidates
        if isinstance(candidate, dict)
        and candidate.get("verification_status") == "verified"
    ]
    source_count = len(verified)
    if source_count < 2:
        errors.append(f"at least two verified sources are required; found {source_count}")
    if not any(candidate.get("source_class") == "primary" for candidate in verified):
        errors.append("at least one verified primary source is required")

    window = sources.get("window", {}) if isinstance(sources, dict) else {}
    if isinstance(window, dict) and metadata:
        if window.get("timezone") != "Asia/Shanghai":
            errors.append("sources.json window timezone must be Asia/Shanghai")
        if window.get("start") != metadata.get("window_start"):
            errors.append("sources.json window start must match article frontmatter")
        if window.get("end") != metadata.get("window_end"):
            errors.append("sources.json window end must match article frontmatter")

    verified_event_count = 0
    for index, candidate in enumerate(candidates, start=1):
        if not isinstance(candidate, dict):
            errors.append(f"source candidate {index} must be an object")
            continue
        if not _valid_http_url(candidate.get("url")):
            errors.append(f"source candidate {index} has an invalid canonical URL")
        published = candidate.get("published_at")
        published_at = _parse_datetime(
            published, f"source candidate {index} published_at", errors
        ) if isinstance(published, str) else None
        if published_at is None and not isinstance(published, str):
            errors.append(f"source candidate {index} published_at is required")
        if (
            published_at
            and actual_start
            and actual_end
            and candidate.get("source_role", "event") != "background"
        ):
            if not actual_start <= published_at <= actual_end:
                errors.append(f"source candidate {index} is outside the two-day window")
            elif candidate.get("verification_status") == "verified":
                verified_event_count += 1
        verification_urls = candidate.get("verification_urls", [])
        if not isinstance(verification_urls, list) or any(
            not _valid_http_url(url) for url in verification_urls
        ):
            errors.append(f"source candidate {index} has invalid verification URLs")

    if verified_event_count < 1:
        errors.append("at least one verified event source inside the two-day window is required")

    receipt = run_dir / "publish-receipt.json"
    if receipt.exists():
        errors.append(
            "publish-receipt.json must not exist during pre-publication validation"
        )

    if not candidates:
        warnings.append("sources.json contains no candidates")

    result = {
        "ok": not errors,
        "errors": errors,
        "warnings": warnings,
        "cjk_chars": cjk_chars,
        "reading_minutes": reading_minutes,
        "source_count": source_count,
        "image_count": local_image_count,
        "fingerprint": compute_fingerprint(run_dir),
        "run_dir": str(run_dir),
    }
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_dir", type=Path)
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args()

    result = validate_run(args.run_dir)
    if args.as_json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        status = "OK" if result["ok"] else "ERROR"
        print(f"[{status}] {result['run_dir']}")
        print(
            f"sources={result['source_count']} images={result['image_count']} "
            f"cjk={result['cjk_chars']} minutes={result['reading_minutes']}"
        )
        print(f"fingerprint={result['fingerprint']}")
        for message in result["errors"]:
            print(f"error: {message}", file=sys.stderr)
        for message in result["warnings"]:
            print(f"warning: {message}", file=sys.stderr)
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
