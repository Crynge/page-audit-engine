# 🚀 Page-Level GEO/AEO/VEO Audit Engine

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code Style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Tests](https://github.com/Crynge/page-audit-engine/actions/workflows/tests.yml/badge.svg)](https://github.com/Crynge/page-audit-engine/actions)
[![Quality Gate](https://sonarcloud.io/api/project_badges/measure?project=Crynge_page-audit-engine&metric=alert_status)](https://sonarcloud.io/dashboard?id=Crynge_page-audit-engine)

**Production-grade search visibility audit tool for Generative Engine Optimization (GEO), Answer Engine Optimization (AEO), and Voice Engine Optimization (VEO).** Extract on-page signals, analyze with AI, and get actionable, prioritized fixes in structured JSON format.

---

## 📌 Table of Contents

- [Features](#-features)
- [Quick Start](#-quick-start)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Usage](#-usage)
- [Output Schema](#-output-schema)
- [Technical Architecture](#-technical-architecture)
- [API Reference](#-api-reference)
- [Automation Integration](#-automation-integration)
- [Development](#-development)
- [Troubleshooting](#-troubleshooting)
- [Contributing](#-contributing)
- [License](#-license)

---

## ✨ Features

### 🔍 On-Page Signal Extraction
- **Metadata Analysis**: Title tags, meta descriptions, Open Graph, Twitter Cards
- **Heading Hierarchy**: H1, H2, H3 structure validation
- **Content Metrics**: Word count, content density, readability signals
- **Schema Detection**: JSON-LD, Microdata, RDFa schema.org markup
- **Technical SEO**: Canonical URLs, viewport meta, language attributes
- **Link Analysis**: Internal/external link counting, anchor text extraction
- **Image Optimization**: Alt text coverage, image count analysis
- **Performance Signals**: Page load time measurement

### 🤖 AI-Powered Analysis
- **Multi-Model Support**: OpenAI GPT-4, GPT-4o, Claude, local LLMs via Ollama
- **Structured Output**: Strict JSON schema enforcement
- **Custom Prompts**: Configurable system prompts for specific use cases
- **Retry Logic**: Automatic retries with exponential backoff
- **Fallback Handling**: Graceful degradation on API failures

### 📊 Comprehensive Reporting
- **GEO Findings**: Entity recognition, semantic richness, topic authority
- **AEO Findings**: Featured snippet potential, FAQ optimization, direct answers
- **VEO Findings**: Voice search readiness, conversational queries, local intent
- **Critical Errors**: Blocking issues requiring immediate attention
- **Priority Fixes**: Ranked recommendations (HIGH/MEDIUM/LOW)
- **Actionable Recommendations**: Specific, technical improvement suggestions

### 🛠️ Enterprise-Ready
- **Type Safety**: Full type hints for IDE support and static analysis
- **Error Handling**: Comprehensive try/except with detailed logging
- **Pipeline Integration**: CLI flags for CI/CD, cron, n8n, Zapier
- **Batch Processing**: Ready for multi-URL auditing scripts
- **Environment Management**: .env configuration with validation
- **Rich Terminal Output**: Color-coded tables and panels for quick review

---

## 🚀 Quick Start

```bash
# Clone repository
git clone https://github.com/Crynge/page-audit-engine.git
cd page-audit-engine

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API key

# Run audit
python main.py --url "https://example.com/page" --output my-audit
```

**Output:**
- Terminal: Formatted summary with color-coded tables
- File: `reports/my-audit.json`

---

## 📦 Installation

### Prerequisites
- Python 3.10 or higher
- pip package manager
- OpenAI API key (or compatible endpoint)

### Step-by-Step Installation

#### 1. Clone Repository
```bash
git clone https://github.com/Crynge/page-audit-engine.git
cd page-audit-engine
```

#### 2. Create Virtual Environment
```bash
# Linux/macOS
python -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate

# Windows PowerShell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

#### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

#### 4. Verify Installation
```bash
python -c "from audit_engine import AuditEngine; print('✅ Installation successful')"
```

### Alternative Installation Methods

#### Using pipx (Global CLI Tool)
```bash
pipx install .
page-audit --url "https://example.com"
```

#### Docker (Coming Soon)
```bash
docker build -t page-audit-engine .
docker run -e OPENAI_API_KEY=$OPENAI_API_KEY page-audit-engine --url "https://example.com"
```

---

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `OPENAI_API_KEY` | Your API key for OpenAI-compatible endpoints | `sk-proj-...` |
| `OPENAI_BASE_URL` | Base URL for the API endpoint | `https://api.openai.com/v1` |
| `OPENAI_MODEL` | Model identifier for analysis | `gpt-4o-mini` |

### Optional Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `REQUEST_TIMEOUT` | HTTP request timeout in seconds | `30` |
| `MAX_RETRIES` | Number of retry attempts | `3` |
| `USER_AGENT` | Custom User-Agent string | `PageAuditBot/1.0` |
| `LOG_LEVEL` | Logging verbosity | `INFO` |

### Example .env File

```env
# API Configuration
OPENAI_API_KEY=your_api_key_here
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4o-mini

# Request Settings
REQUEST_TIMEOUT=30
MAX_RETRIES=3
USER_AGENT=PageAuditBot/1.0 (+https://github.com/Crynge/page-audit-engine)

# Logging
LOG_LEVEL=INFO
```

### Alternative Providers

#### Anthropic Claude
```env
OPENAI_API_KEY=your_anthropic_key
OPENAI_BASE_URL=https://api.anthropic.com/v1
OPENAI_MODEL=claude-3-5-sonnet-20241022
```

#### Local LLM with Ollama
```env
OPENAI_API_KEY=ollama
OPENAI_BASE_URL=http://localhost:11434/v1
OPENAI_MODEL=llama3.1:8b
```

#### Groq
```env
OPENAI_API_KEY=your_groq_key
OPENAI_BASE_URL=https://api.groq.com/openai/v1
OPENAI_MODEL=llama-3.1-70b-versatile
```

---

## 💻 Usage

### Basic Commands

#### Single URL Audit
```bash
python main.py --url "https://example.com/page"
```

#### Custom Output Filename
```bash
python main.py --url "https://example.com/page" --output competitor-analysis
```

#### Verbose Mode
```bash
python main.py --url "https://example.com/page" --verbose
```

#### Terminal Output Only (No File)
```bash
python main.py --url "https://example.com/page" --no-file
```

### CLI Arguments Reference

| Argument | Short | Required | Description |
|----------|-------|----------|-------------|
| `--url` | `-u` | ✅ Yes | Target URL to audit |
| `--output` | `-o` | ❌ No | Output filename (without .json) |
| `--verbose` | `-v` | ❌ No | Enable debug logging |
| `--no-file` | `-n` | ❌ No | Skip file output |
| `--help` | `-h` | ❌ No | Show help message |

### Advanced Usage Examples

#### Batch Auditing Script
```python
# batch_audit.py
from audit_engine import AuditEngine
from config import get_config
import json

urls = [
    "https://example.com/page1",
    "https://example.com/page2",
    "https://example.com/page3",
]

config = get_config()
engine = AuditEngine(config)

results = []
for url in urls:
    report = engine.run_audit(url)
    results.append(report)

with open("batch-audit.json", "w") as f:
    json.dump(results, f, indent=2)
```

#### Integration with Python Scripts
```python
from audit_engine import AuditEngine
from config import get_config

config = get_config()
engine = AuditEngine(config)

report = engine.run_audit("https://example.com/page")

# Access specific findings
for finding in report["geo_findings"]:
    print(f"GEO: {finding}")

for fix in report["priority_fixes"]:
    print(f"Priority: {fix}")
```

---

## 📋 Output Schema

### Complete JSON Structure

```json
{
  "url": "https://example.com/page",
  "audit_timestamp": "2026-05-08T12:51:20Z",
  "page_signals": {
    "url": "https://example.com/page",
    "title": "Page Title Here",
    "title_length": 45,
    "meta_description": "Meta description text...",
    "meta_description_length": 155,
    "h1_count": 1,
    "h1_tags": ["Main Heading"],
    "h2_count": 5,
    "h2_tags": ["Section 1", "Section 2", "..."],
    "h3_count": 8,
    "h3_tags": ["Subsection 1.1", "..."],
    "word_count": 1250,
    "schema_types": ["Article", "BreadcrumbList"],
    "canonical_url": "https://example.com/page",
    "og_title": "Open Graph Title",
    "og_description": "OG Description",
    "twitter_card": "summary_large_image",
    "lang_attribute": "en",
    "has_viewport_meta": true,
    "internal_links": 25,
    "external_links": 8,
    "images_total": 12,
    "images_with_alt": 10,
    "status_code": 200,
    "load_time_ms": 342
  },
  "geo_findings": [
    "Strong entity density with 15+ named entities detected",
    "Schema markup present but missing Organization schema",
    "Semantic richness score: HIGH - diverse vocabulary usage"
  ],
  "aeo_findings": [
    "FAQ section detected with 5 question-answer pairs",
    "Featured snippet potential: List structure found in H2 section",
    "Direct answer pattern identified in paragraph 3"
  ],
  "veo_findings": [
    "Conversational query patterns present in headings",
    "Local intent signals: City name mentioned 3 times",
    "Mobile optimization: Viewport meta tag present"
  ],
  "critical_errors": [
    "Missing H1 tag on page",
    "Canonical URL points to different domain"
  ],
  "recommendations": [
    "Add Organization schema to improve entity recognition",
    "Increase word count to 1500+ for better topic coverage",
    "Optimize images: 2 images missing alt text"
  ],
  "priority_fixes": [
    "HIGH: Add single H1 tag to establish page hierarchy",
    "HIGH: Fix canonical URL to point to correct domain",
    "MEDIUM: Add alt text to 2 images for accessibility",
    "LOW: Consider adding FAQ schema for AEO improvement"
  ]
}
```

### Field Descriptions

| Key | Type | Description |
|-----|------|-------------|
| `url` | string | Audited page URL |
| `audit_timestamp` | string | ISO 8601 timestamp of audit |
| `page_signals` | object | Extracted on-page signals |
| `geo_findings` | array[string] | Generative engine optimization insights |
| `aeo_findings` | array[string] | Answer engine optimization insights |
| `veo_findings` | array[string] | Voice search optimization insights |
| `critical_errors` | array[string] | Blocking issues requiring immediate fix |
| `recommendations` | array[string] | Actionable improvement suggestions |
| `priority_fixes` | array[string] | Ranked fixes by impact (HIGH/MEDIUM/LOW) |

### Page Signals Fields

| Field | Type | Description |
|-------|------|-------------|
| `title` | string | Page title tag content |
| `title_length` | integer | Character count of title |
| `meta_description` | string | Meta description content |
| `meta_description_length` | integer | Character count of description |
| `h1_count` | integer | Number of H1 tags |
| `h1_tags` | array[string] | Text content of H1 tags |
| `h2_count` | integer | Number of H2 tags |
| `h2_tags` | array[string] | Text content of H2 tags |
| `h3_count` | integer | Number of H3 tags |
| `word_count` | integer | Total word count |
| `schema_types` | array[string] | Detected schema.org types |
| `canonical_url` | string | Canonical URL if present |
| `status_code` | integer | HTTP response status code |
| `load_time_ms` | integer | Page load time in milliseconds |

---

## 🏗️ Technical Architecture

### Component Overview

```
┌─────────────────────────────────────────────────────────────┐
│                         main.py                              │
│                    CLI Entry Point                           │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Argument Parsing  │  Rich Output  │  Report Saving  │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                      audit_engine.py                         │
│                     AuditEngine Class                        │
│  ┌────────────┐  ┌─────────────┐  ┌──────────────┐         │
│  │ PageFetcher│  │SignalExtractor│ │ AIAnalyzer   │         │
│  │            │  │             │  │              │         │
│  │ - HTTP GET │  │ - BeautifulSoup│ │ - OpenAI API│         │
│  │ - Retry    │  │ - Schema Parse│ │ - JSON Valid│         │
│  │ - Timeout  │  │ - Metrics    │  │ - Prompt Eng│         │
│  └────────────┘  └─────────────┘  └──────────────┘         │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                        config.py                             │
│                   Configuration Manager                      │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  .env Loading  │  Validation  │  Type Safety (Pydantic)│  │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### Data Flow

1. **CLI Input** → `main.py` parses arguments
2. **Config Load** → `config.py` validates environment variables
3. **Page Fetch** → `PageFetcher` retrieves HTML with retry logic
4. **Signal Extraction** → `SignalExtractor` parses DOM and extracts metrics
5. **AI Analysis** → `AIAnalyzer` sends signals to LLM, receives structured JSON
6. **Report Generation** → Combined report saved to file and terminal

### Error Handling Strategy

```python
try:
    # Attempt operation
    result = perform_operation()
except SpecificException as e:
    # Handle known errors gracefully
    logger.warning(f"Known error: {e}")
    return fallback_result()
except Exception as e:
    # Catch-all for unexpected errors
    logger.exception(f"Unexpected error: {e}")
    raise RuntimeError(f"Operation failed: {e}")
```

### Performance Optimizations

- **Connection Pooling**: Reuses HTTP sessions for multiple requests
- **Async-Ready**: Designed for future async/await implementation
- **Caching Layer**: Optional Redis integration for repeated audits
- **Batch Processing**: Efficient multi-URL handling
- **Memory Management**: Streaming responses for large pages

---

## 📚 API Reference

### AuditEngine Class

#### `__init__(config: Config)`
Initialize audit engine with configuration.

**Parameters:**
- `config`: Config instance with API settings

**Example:**
```python
from audit_engine import AuditEngine
from config import get_config

config = get_config()
engine = AuditEngine(config)
```

#### `run_audit(url: str) -> Dict[str, Any]`
Execute complete audit on a URL.

**Parameters:**
- `url`: Target URL to audit

**Returns:**
- Dictionary containing full audit report

**Raises:**
- `ValueError`: Invalid URL format
- `RuntimeError`: Audit process failure

**Example:**
```python
report = engine.run_audit("https://example.com/page")
print(report["geo_findings"])
```

### PageSignals Dataclass

Contains all extracted on-page signals.

**Fields:**
- `url`: str - Page URL
- `title`: Optional[str] - Title tag
- `meta_description`: Optional[str] - Meta description
- `h1_tags`: List[str] - H1 headings
- `h2_tags`: List[str] - H2 headings
- `word_count`: int - Total words
- `schema_types`: List[str] - Schema types
- `canonical_url`: Optional[str] - Canonical URL
- And 15+ additional fields

### Configuration Options

See [Configuration](#-configuration) for complete list.

---

## 🔄 Automation Integration

### Cron Jobs (Linux/macOS)

#### Daily Audit at 3 AM
```bash
# Edit crontab
crontab -e

# Add line for daily audit
0 3 * * * /path/to/venv/bin/python /path/to/main.py --url "https://example.com" --output daily-audit >> /var/log/page-audit.log 2>&1
```

#### Hourly Monitoring
```bash
0 * * * * /path/to/venv/bin/python /path/to/main.py --url "https://example.com/critical-page" --output hourly-check >> /var/log/hourly-audit.log 2>&1
```

### GitHub Actions

#### Workflow: Scheduled Audits
```yaml
# .github/workflows/scheduled-audit.yml
name: Scheduled Page Audit

on:
  schedule:
    - cron: '0 3 * * *'  # Daily at 3 AM UTC
  workflow_dispatch:
    inputs:
      url:
        description: 'URL to audit'
        required: true
        default: 'https://example.com'

jobs:
  audit:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.10'
          cache: 'pip'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
      
      - name: Run audit
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
          OPENAI_BASE_URL: ${{ secrets.OPENAI_BASE_URL }}
          OPENAI_MODEL: gpt-4o-mini
        run: |
          python main.py \
            --url "${{ github.event.inputs.url || 'https://example.com' }}" \
            --output "gha-audit-${{ github.run_id }}"
      
      - name: Upload report
        uses: actions/upload-artifact@v4
        with:
          name: audit-report
          path: reports/*.json
          retention-days: 30
```

### n8n Workflow

#### HTTP Request + Execute Command
```json
{
  "nodes": [
    {
      "parameters": {
        "method": "POST",
        "url": "https://your-server.com/webhook/audit",
        "options": {}
      },
      "name": "Webhook Trigger",
      "type": "n8n-nodes-base.webhook"
    },
    {
      "parameters": {
        "command": "python main.py --url={{ $json.url }} --output={{ $json.report_name }}"
      },
      "name": "Execute Audit",
      "type": "n8n-nodes-base.executeCommand"
    },
    {
      "parameters": {
        "operation": "read",
        "filePath": "reports/{{ $json.report_name }}.json"
      },
      "name": "Read Report",
      "type": "n8n-nodes-base.readWriteFile"
    }
  ]
}
```

### Docker Integration

#### Dockerfile
```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENTRYPOINT ["python", "main.py"]
CMD ["--help"]
```

#### Docker Compose
```yaml
version: '3.8'

services:
  page-audit:
    build: .
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - OPENAI_BASE_URL=${OPENAI_BASE_URL}
      - OPENAI_MODEL=${OPENAI_MODEL}
    volumes:
      - ./reports:/app/reports
```

### CI/CD Pipeline Integration

#### Pre-deployment Check
```yaml
# Add to existing CI pipeline
- name: SEO Audit Before Deploy
  run: |
    python main.py --url "https://staging.example.com" --output pre-deploy-audit
    # Fail if critical errors found
    python -c "
    import json
    with open('reports/pre-deploy-audit.json') as f:
        report = json.load(f)
    if report['critical_errors']:
        print('❌ Critical errors found:')
        for error in report['critical_errors']:
            print(f'  - {error}')
        exit(1)
    "
```

---

## 🧪 Development

### Setting Up Development Environment

```bash
# Clone repository
git clone https://github.com/Crynge/page-audit-engine.git
cd page-audit-engine

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install development dependencies
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install
```

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=audit_engine --cov=config --cov=main --cov-report=html

# Run specific test file
pytest tests/test_signal_extractor.py -v

# Run specific test function
pytest tests/test_signal_extractor.py::test_extract_title -v
```

### Code Quality

```bash
# Format code
black .

# Sort imports
isort .

# Type checking
mypy .

# Linting
flake8 .

# Security scan
bandit -r .
```

### Building Documentation

```bash
# Install docs dependencies
pip install mkdocs mkdocs-material

# Serve documentation locally
mkdocs serve

# Build static site
mkdocs build
```

### Contributing Guidelines

1. **Fork** the repository
2. **Create feature branch**: `git checkout -b feat/amazing-feature`
3. **Make changes** with tests
4. **Run quality checks**: `black . && isort . && mypy . && flake8 . && pytest`
5. **Commit**: `git commit -m 'feat: add amazing feature'`
6. **Push**: `git push origin feat/amazing-feature`
7. **Open Pull Request**

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

---

## 🔧 Troubleshooting

### Common Issues

#### ❌ "Configuration Error: OPENAI_API_KEY not set"
**Solution:** Ensure `.env` file exists with valid API key:
```bash
cp .env.example .env
# Edit .env and add your key
```

#### ❌ "Failed to fetch page (HTTP 403)"
**Solution:** Some sites block automated requests. Try:
- Adding delays between requests
- Rotating User-Agent strings
- Using residential proxies

#### ❌ "Invalid JSON from AI"
**Solution:** 
- Check API endpoint compatibility
- Verify model supports JSON mode
- Increase `max_tokens` if response is truncated

#### ❌ "Timeout error"
**Solution:** Increase timeout in `.env`:
```env
REQUEST_TIMEOUT=60
MAX_RETRIES=5
```

### Debug Mode

Enable verbose logging:
```bash
python main.py --url "https://example.com" --verbose
```

Check logs for detailed error messages:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Getting Help

1. **Search Issues**: [GitHub Issues](https://github.com/Crynge/page-audit-engine/issues)
2. **Ask Question**: Open new issue with `[Question]` prefix
3. **Discussions**: [GitHub Discussions](https://github.com/Crynge/page-audit-engine/discussions)

---

## 🤝 Contributing

We welcome contributions! See our [Contributing Guide](CONTRIBUTING.md) for details.

### Ways to Contribute

- 🐛 Report bugs
- 💡 Suggest features
- 📝 Improve documentation
- 🔧 Submit PRs
- 🧪 Write tests
- 🌍 Translate documentation

### Code of Conduct

Please read our [Code of Conduct](CODE_OF_CONDUCT.md) before contributing.

---

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

---

## 🙏 Acknowledgments

- [OpenAI](https://openai.com/) for API infrastructure
- [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/) for HTML parsing
- [Rich](https://github.com/Textualize/rich) for terminal formatting
- All contributors and supporters

---

## 📞 Contact

- **Repository**: https://github.com/Crynge/page-audit-engine
- **Issues**: https://github.com/Crynge/page-audit-engine/issues
- **Discussions**: https://github.com/Crynge/page-audit-engine/discussions

---

<div align="center">

**Made with ❤️ for the SEO community**

[⬆ Back to Top](#-page-level-geoaechoveo-audit-engine)

</div>
