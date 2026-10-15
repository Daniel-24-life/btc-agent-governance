import json
import subprocess
from html.parser import HTMLParser
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEMO = ROOT / "demo"


def test_record_matches_public_runner_except_dynamic_timestamps():
    from public_demo import build_demo

    def stable(value):
        if isinstance(value, dict):
            return {key: stable(item) for key, item in value.items() if key not in {"generated_at", "created_at"}}
        if isinstance(value, (list, tuple)):
            return [stable(item) for item in value]
        return value

    saved = json.loads((ROOT / "sample.fake.json").read_text(encoding="utf-8"))
    assert stable(saved) == stable(build_demo())


class DemoHTMLParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = set()
        self.buttons = []
        self.landmarks = []
        self.document_language = None

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        if tag == "html":
            self.document_language = attributes.get("lang")
        if "id" in attributes:
            self.ids.add(attributes["id"])
        if tag == "button":
            self.buttons.append(attributes)
        if tag in {"header", "nav", "main", "article", "footer"}:
            self.landmarks.append(tag)


def test_demo_has_semantic_static_entrypoint():
    parser = DemoHTMLParser()
    parser.feed((DEMO / "index.html").read_text(encoding="utf-8"))

    assert parser.document_language == "zh-CN"
    assert {"record", "scenarios", "scenario-title", "raw-record"} <= parser.ids
    assert {"header", "nav", "main", "article", "footer"} <= set(
        parser.landmarks
    )


def test_demo_uses_local_assets_and_root_sample_path():
    html = (DEMO / "index.html").read_text(encoding="utf-8")
    script = (DEMO / "app.js").read_text(encoding="utf-8")

    assert 'href="styles.css"' in html
    assert 'src="app.js"' in html
    assert "http://" not in html
    assert "https://" not in html
    assert 'const DATA_URL = "../sample.fake.json"' in script
    assert "fetch(DATA_URL" in script
    assert "该场景没有证据分类记录" in script
    assert "路由结果请以“路由决定”阶段为准" in script


def test_demo_style_contract_and_responsive_floor():
    css = (DEMO / "styles.css").read_text(encoding="utf-8")

    assert "--page: #f3f6f8" in css
    assert "--ink: #102536" in css
    assert "--accent: #12685f" in css
    assert "font-size: 16px" in css
    assert "font-size: 0.8125rem" in css
    assert ":focus-visible" in css
    assert "@media (max-width: 420px)" in css
    assert "prefers-reduced-motion: reduce" in css
    assert "word-break: break-all" not in css


def test_demo_behavior_distinguishes_not_run_and_blocked():
    node_program = r"""
const fs = require('fs');
const viewer = require('./demo/app.js');
const payload = JSON.parse(fs.readFileSync('./sample.fake.json', 'utf8'));
viewer.validatePayload(payload);
if (viewer.DEFAULT_SCENARIO !== 'dry_run_lifecycle') process.exit(1);
const byName = Object.fromEntries(payload.scenarios.map(item => [item.scenario, item]));
if (viewer.stageState(byName.research_candidate, 'lifecycle') !== 'not-run') process.exit(2);
if (viewer.stageState(byName.live_request, 'lifecycle') !== 'not-run') process.exit(3);
if (viewer.stageState(byName.promotion_request, 'promotion') !== 'blocked') process.exit(4);
if (viewer.stageState(byName.dry_run_lifecycle, 'lifecycle') !== 'complete') process.exit(5);
const unsafe = JSON.parse(JSON.stringify(payload));
unsafe.scenarios[0].release.execution_authority = true;
let rejected = false;
try { viewer.validatePayload(unsafe); } catch (_) { rejected = true; }
if (!rejected) process.exit(6);
"""
    result = subprocess.run(
        ["node", "-e", node_program],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr


def test_public_sample_keeps_non_trading_boundary_for_viewer():
    payload = json.loads((ROOT / "sample.fake.json").read_text(encoding="utf-8"))

    assert payload["contains_real_data"] is False
    assert payload["summary"]["real_orders_submitted"] == 0
    assert payload["summary"]["real_fills_recorded"] == 0
    assert all(
        scenario["release"]["execution_authority"] is False
        for scenario in payload["scenarios"]
    )
