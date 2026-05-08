# Page-Level GEO/AEO/VEO Audit Engine

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code Style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A production-grade, page-level search visibility audit tool for **GEO** (Generative Engine Optimization), **AEO** (Answer Engine Optimization), and **VEO** (Voice Engine Optimization). This tool extracts on-page signals, analyzes them via an OpenAI-compatible API, and returns a structured JSON report with actionable, prioritized fixes.

---

## 🔧 Features

- **On-Page Signal Extraction**: Title, meta description, H1/H2 hierarchy, word count, schema markup, canonical URL.
- **AI-Powered Analysis**: Sends extracted data to any OpenAI-compatible API endpoint for structured findings.
- **Structured JSON Output**: Returns findings in a strict schema: `geo_findings`, `aeo_findings`, `veo_findings`, `critical_errors`, `recommendations`, `priority_fixes`.
- **Terminal Summary**: Rich-formatted table output for quick review.
- **Pipeline-Ready**: Designed for integration with n8n, cron jobs, CI/CD pipelines, or internal dashboards.
- **Error Handling**: Comprehensive try/except blocks with clear error messages and graceful degradation.
- **Type Safety**: Full type hints for IDE support and static analysis.

---

## 📁 Repository Structure

```
page-audit-engine/
├── .env.example           # Environment variable template
├── .gitignore             # Git ignore rules
├── config.py              # Configuration loader
├── audit_engine.py        # Core extraction and analysis logic
├── main.py                # CLI entry point
├── requirements.txt       # Python dependencies
├── README.md              # This file
└── reports/               # Output directory for JSON reports
```

---

## 🚀 Quick Start

### 1. Clone & Install

```bash
git clone <YOUR_REPO_URL>
cd page-audit-engine
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` with your API credentials:

```env
OPENAI_API_KEY=your_api_key_here
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4o-mini
REQUEST_TIMEOUT=30
MAX_RETRIES=3
```

### 3. Run Audit

```bash
python main.py --url "https://example.com/page" --output my-audit-report
```

Output:
- Terminal: Formatted summary table
- File: `reports/my-audit-report.json`

---

## 📊 Output Schema

The generated JSON report follows this strict structure:

```json
{
  "url": "https://example.com/page",
  "geo_findings": ["..."],
  "aeo_findings": ["..."],
  "veo_findings": ["..."],
  "critical_errors": ["..."],
  "recommendations": ["..."],
  "priority_fixes": ["..."]
}
```

| Key | Description |
|-----|-------------|
| `url` | Audited page URL |
| `geo_findings` | Generative engine optimization insights |
| `aeo_findings` | Answer engine optimization insights |
| `veo_findings` | Voice search optimization insights |
| `critical_errors` | Blocking issues requiring immediate attention |
| `recommendations` | Actionable improvement suggestions |
| `priority_fixes` | Ranked list of fixes by impact/effort |

---

## ⚙️ Technical Details

### Extraction Logic (`audit_engine.py`)

- **HTTP Fetch**: Custom headers (User-Agent, Accept-Language), timeout handling, retry logic.
- **HTML Parsing**: BeautifulSoup4 for DOM traversal, schema.org detection via JSON-LD.
- **Signal Metrics**:
  - Title length & keyword presence
  - Meta description quality
  - Heading hierarchy (H1 → H2 → H3)
  - Word count & content density
  - Schema markup types (Article, Product, FAQ, etc.)
  - Canonical URL validation

### AI Analysis Prompt

The system prompt enforces JSON-only output with strict key requirements. Example:

```
You are a search visibility auditor. Analyze the provided on-page signals for GEO, AEO, and VEO compliance.
Return ONLY valid JSON with these keys: geo_findings, aeo_findings, veo_findings, critical_errors, recommendations, priority_fixes.
Each value must be a list of strings. Be specific, actionable, and technical.
```

### CLI Arguments (`main.py`)

| Argument | Required | Description |
|----------|----------|-------------|
| `--url` | Yes | Target page URL |
| `--output` | No | Report filename (default: `audit-report-{timestamp}`) |
| `--verbose` | No | Enable debug logging |

---

## 🔄 Automation Integration

### Cron Job (Linux/macOS)

```bash
# Run daily at 3 AM
0 3 * * * /path/to/venv/bin/python /path/to/main.py --url "https://example.com" --output daily-audit >> /var/log/audit.log 2>&1
```

### n8n Workflow

Use the **Execute Command** node:

```json
{
  "command": "python main.py --url={{ $json.url }} --output={{ $json.report_name }}"
}
```

### GitHub Actions

```yaml
name: Page Audit
on: [workflow_dispatch]
jobs:
  audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.10'
      - run: pip install -r requirements.txt
      - run: python main.py --url "${{ secrets.AUDIT_URL }}" --output ci-audit
      - name: Upload Report
        uses: actions/upload-artifact@v4
        with:
          name: audit-report
          path: reports/*.json
```

---

## 🛠️ Development

### Running Tests

```bash
pytest tests/ -v
```

### Code Formatting

```bash
black .
flake8 .
mypy .
```

### Adding New Extractors

Extend `PageSignals` dataclass in `audit_engine.py`:

```python
@dataclass
class PageSignals:
    url: str
    title: Optional[str] = None
    meta_description: Optional[str] = None
    # Add new fields here
```

---

## 📝 License

MIT License. See [LICENSE](LICENSE) for details.

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feat/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feat/amazing-feature`)
5. Open a Pull Request

---

## 📞 Support

For issues, questions, or contributions, open an issue on GitHub.
