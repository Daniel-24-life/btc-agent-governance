from pathlib import Path
from shutil import copyfile
import sys

repository = Path(__file__).resolve().parents[1]
out = Path(sys.argv[1])
files = {
    "index.html": "demo/index.html",
    "styles.css": "demo/styles.css",
    "app.js": "demo/app.js",
    "sample.fake.json": "sample.fake.json"
}

for output_path, input_path in files.items():
    target = out / output_path
    target.parent.mkdir(parents=True, exist_ok=True)
    copyfile(repository / input_path, target)

source = out / "index.html"
source.write_text(source.read_text(encoding="utf-8").replace('href="../README.md"', 'href="https://github.com/Daniel-24-life/btc-agent-governance#readme"'), encoding="utf-8")
app = out / "app.js"
text = app.read_text(encoding="utf-8")
if '"../sample.fake.json"' not in text:
    raise ValueError("Record viewer fixture path changed")
app.write_text(text.replace('"../sample.fake.json"', '"./sample.fake.json"'), encoding="utf-8")
