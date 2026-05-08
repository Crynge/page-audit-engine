"""
Core audit engine for page-level GEO, AEO, and VEO analysis.

This module handles:
- HTML fetching with proper headers and timeout handling
- On-page signal extraction (title, meta, headings, schema, etc.)
- AI-powered analysis via OpenAI-compatible APIs
- Structured JSON report generation
"""

import json
import logging
import re
import time
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup, Tag
from openai import OpenAI

from config import Config

logger = logging.getLogger(__name__)


@dataclass
class PageSignals:
    """Extracted on-page signals for search visibility analysis."""

    url: str
    title: Optional[str] = None
    title_length: int = 0
    meta_description: Optional[str] = None
    meta_description_length: int = 0
    h1_tags: List[str] = field(default_factory=list)
    h2_tags: List[str] = field(default_factory=list)
    h3_tags: List[str] = field(default_factory=list)
    word_count: int = 0
    schema_types: List[str] = field(default_factory=list)
    canonical_url: Optional[str] = None
    og_title: Optional[str] = None
    og_description: Optional[str] = None
    twitter_card: Optional[str] = None
    lang_attribute: Optional[str] = None
    has_viewport_meta: bool = False
    internal_links_count: int = 0
    external_links_count: int = 0
    images_count: int = 0
    images_with_alt: int = 0
    load_time_ms: Optional[int] = None
    status_code: Optional[int] = None
    content_html: str = ""

    def to_analysis_dict(self) -> Dict[str, Any]:
        """Convert signals to a dictionary suitable for AI analysis."""
        return {
            "url": self.url,
            "title": self.title,
            "title_length": self.title_length,
            "meta_description": self.meta_description,
            "meta_description_length": self.meta_description_length,
            "h1_count": len(self.h1_tags),
            "h1_tags": self.h1_tags,
            "h2_count": len(self.h2_tags),
            "h2_tags": self.h2_tags,
            "h3_count": len(self.h3_tags),
            "h3_tags": self.h3_tags,
            "word_count": self.word_count,
            "schema_types": self.schema_types,
            "canonical_url": self.canonical_url,
            "og_title": self.og_title,
            "og_description": self.og_description,
            "twitter_card": self.twitter_card,
            "lang_attribute": self.lang_attribute,
            "has_viewport_meta": self.has_viewport_meta,
            "internal_links": self.internal_links_count,
            "external_links": self.external_links_count,
            "images_total": self.images_count,
            "images_with_alt": self.images_with_alt,
            "status_code": self.status_code,
        }


class PageFetcher:
    """Handles HTTP requests with retry logic and proper error handling."""

    def __init__(self, config: Config):
        self.config = config
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": config.user_agent,
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate, br",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
            }
        )

    def fetch(self, url: str) -> tuple[Optional[str], int, Optional[int]]:
        """
        Fetch HTML content from URL with retry logic.

        Args:
            url: Target URL to fetch.

        Returns:
            Tuple of (html_content, status_code, load_time_ms).
            Returns (None, status_code, None) on failure.
        """
        last_exception = None

        for attempt in range(self.config.max_retries):
            try:
                start_time = time.time()
                response = self.session.get(
                    url, timeout=self.config.request_timeout, allow_redirects=True
                )
                load_time_ms = int((time.time() - start_time) * 1000)

                if response.status_code >= 400:
                    logger.warning(
                        f"HTTP {response.status_code} for {url} (attempt {attempt + 1})"
                    )
                    if attempt < self.config.max_retries - 1:
                        time.sleep(2**attempt)
                        continue
                    return None, response.status_code, load_time_ms

                return response.text, response.status_code, load_time_ms

            except requests.exceptions.Timeout as e:
                last_exception = e
                logger.warning(f"Timeout on attempt {attempt + 1}: {e}")
            except requests.exceptions.TooManyRedirects as e:
                last_exception = e
                logger.error(f"Too many redirects: {e}")
                break
            except requests.exceptions.RequestException as e:
                last_exception = e
                logger.warning(f"Request error on attempt {attempt + 1}: {e}")

            if attempt < self.config.max_retries - 1:
                time.sleep(2**attempt)

        logger.error(f"All retries exhausted for {url}. Last error: {last_exception}")
        return None, 0, None


class SignalExtractor:
    """Extracts on-page SEO signals from HTML content."""

    def __init__(self, html: str, url: str):
        self.html = html
        self.url = url
        self.base_domain = urlparse(url).netloc
        self.soup = BeautifulSoup(html, "lxml")

    def extract(self) -> PageSignals:
        """Extract all on-page signals and return PageSignals instance."""
        signals = PageSignals(url=self.url, content_html=self.html)

        # Basic metadata
        signals.title = self._extract_title()
        signals.title_length = len(signals.title) if signals.title else 0
        signals.meta_description = self._extract_meta_description()
        signals.meta_description_length = (
            len(signals.meta_description) if signals.meta_description else 0
        )
        signals.lang_attribute = self._extract_lang()
        signals.canonical_url = self._extract_canonical()

        # Headings
        signals.h1_tags = self._extract_headings("h1")
        signals.h2_tags = self._extract_headings("h2")
        signals.h3_tags = self._extract_headings("h3")

        # Content analysis
        signals.word_count = self._count_words()

        # Schema markup
        signals.schema_types = self._extract_schema_types()

        # Social meta tags
        signals.og_title = self._extract_og_tag("og:title")
        signals.og_description = self._extract_og_tag("og:description")
        signals.twitter_card = self._extract_twitter_card()

        # Technical SEO
        signals.has_viewport_meta = self._has_viewport_meta()

        # Links and images
        signals.internal_links_count, signals.external_links_count = (
            self._count_links()
        )
        signals.images_count, signals.images_with_alt = self._analyze_images()

        return signals

    def _extract_title(self) -> Optional[str]:
        title_tag = self.soup.find("title")
        if title_tag:
            return title_tag.get_text(strip=True)
        return None

    def _extract_meta_description(self) -> Optional[str]:
        meta = self.soup.find("meta", attrs={"name": "description"})
        if meta and meta.get("content"):
            return meta["content"].strip()
        return None

    def _extract_lang(self) -> Optional[str]:
        html_tag = self.soup.find("html")
        if html_tag and html_tag.get("lang"):
            return html_tag["lang"]
        return None

    def _extract_canonical(self) -> Optional[str]:
        link = self.soup.find("link", rel="canonical")
        if link and link.get("href"):
            return link["href"]
        return None

    def _extract_headings(self, tag_name: str) -> List[str]:
        headings = self.soup.find_all(tag_name)
        return [h.get_text(strip=True) for h in headings if h.get_text(strip=True)]

    def _count_words(self) -> int:
        # Remove script and style elements
        for element in self.soup(["script", "style", "noscript"]):
            element.decompose()

        text = self.soup.get_text(separator=" ")
        words = re.findall(r"\b\w+\b", text.lower())
        return len(words)

    def _extract_schema_types(self) -> List[str]:
        schema_types = []

        # JSON-LD schemas
        for script in self.soup.find_all("script", type="application/ld+json"):
            try:
                schema_data = json.loads(script.string or "")
                if isinstance(schema_data, dict):
                    schema_type = schema_data.get("@type")
                    if schema_type:
                        if isinstance(schema_type, list):
                            schema_types.extend(schema_type)
                        else:
                            schema_types.append(str(schema_type))
                    # Check nested @graph
                    graph = schema_data.get("@graph", [])
                    if isinstance(graph, list):
                        for item in graph:
                            if isinstance(item, dict) and "@type" in item:
                                item_type = item["@type"]
                                if isinstance(item_type, list):
                                    schema_types.extend(item_type)
                                else:
                                    schema_types.append(str(item_type))
            except (json.JSONDecodeError, TypeError):
                continue

        # Microdata schemas
        for item in self.soup.find_all(attrs={"itemtype": True}):
            itemtype = item.get("itemtype", "")
            if itemtype:
                schema_types.append(itemtype.split("/")[-1])

        return list(set(schema_types))

    def _extract_og_tag(self, property_name: str) -> Optional[str]:
        meta = self.soup.find("meta", attrs={"property": property_name})
        if meta and meta.get("content"):
            return meta["content"].strip()
        return None

    def _extract_twitter_card(self) -> Optional[str]:
        meta = self.soup.find("meta", attrs={"name": "twitter:card"})
        if meta and meta.get("content"):
            return meta["content"].strip()
        return None

    def _has_viewport_meta(self) -> bool:
        meta = self.soup.find("meta", attrs={"name": "viewport"})
        return meta is not None

    def _count_links(self) -> tuple[int, int]:
        internal = 0
        external = 0

        for link in self.soup.find_all("a", href=True):
            href = link["href"]
            if href.startswith("#") or href.startswith("tel:") or href.startswith(
                "mailto:"
            ):
                continue

            parsed = urlparse(href)
            if parsed.netloc == "" or parsed.netloc == self.base_domain:
                internal += 1
            else:
                external += 1

        return internal, external

    def _analyze_images(self) -> tuple[int, int]:
        images = self.soup.find_all("img")
        total = len(images)
        with_alt = sum(1 for img in images if img.get("alt"))
        return total, with_alt


class AIAnalyzer:
    """Sends extracted signals to AI for GEO/AEO/VEO analysis."""

    SYSTEM_PROMPT = """You are an expert search visibility auditor specializing in GEO (Generative Engine Optimization), AEO (Answer Engine Optimization), and VEO (Voice Engine Optimization).

Analyze the provided on-page signals and return ONLY valid JSON with exactly these keys:
- geo_findings: List of findings related to generative engine optimization (LLM discoverability, entity recognition, context richness)
- aeo_findings: List of findings related to answer engine optimization (direct answers, FAQ structure, featured snippet potential)
- veo_findings: List of findings related to voice search optimization (conversational queries, local intent, natural language)
- critical_errors: List of blocking issues that must be fixed immediately
- recommendations: List of actionable improvement suggestions
- priority_fixes: List of fixes ranked by impact (format: "HIGH/MEDIUM/LOW: description")

Requirements:
1. Return ONLY valid JSON - no markdown, no explanations, no code blocks
2. Each value must be a list of strings (can be empty if no findings)
3. Be specific, technical, and actionable
4. Reference actual values from the input data
5. Consider industry best practices for each optimization type

Analysis criteria:
- GEO: Entity density, semantic richness, structured data, topic authority signals
- AEO: Question-answer patterns, concise definitions, list structures, statistics
- VEO: Conversational phrasing, local modifiers, long-tail keywords, mobile optimization"""

    def __init__(self, config: Config):
        self.config = config
        self.client = OpenAI(
            api_key=config.openai_api_key, base_url=config.openai_base_url
        )

    def analyze(self, signals: PageSignals) -> Dict[str, Any]:
        """
        Send signals to AI for analysis.

        Args:
            signals: Extracted page signals.

        Returns:
            Dictionary containing analysis results.

        Raises:
            ValueError: If API response cannot be parsed.
            RuntimeError: If API call fails.
        """
        analysis_input = signals.to_analysis_dict()

        try:
            response = self.client.chat.completions.create(
                model=self.config.openai_model,
                messages=[
                    {"role": "system", "content": self.SYSTEM_PROMPT},
                    {
                        "role": "user",
                        "content": f"Analyze this page for GEO/AEO/VEO optimization:\n{json.dumps(analysis_input, indent=2)}",
                    },
                ],
                temperature=0.3,
                max_tokens=2000,
            )

            content = response.choices[0].message.content
            if not content:
                raise ValueError("Empty response from AI")

            # Clean up potential markdown formatting
            content = re.sub(r"^```json\s*|\s*```$", "", content.strip(), flags=re.MULTILINE)
            
            result = json.loads(content)
            
            # Validate required keys
            required_keys = [
                "geo_findings",
                "aeo_findings",
                "veo_findings",
                "critical_errors",
                "recommendations",
                "priority_fixes",
            ]
            for key in required_keys:
                if key not in result:
                    result[key] = []
                elif not isinstance(result[key], list):
                    result[key] = [str(result[key])]

            return result

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse AI response: {e}")
            logger.debug(f"Raw response: {content}")
            raise ValueError(f"Invalid JSON from AI: {e}")
        except Exception as e:
            logger.error(f"AI analysis failed: {e}")
            raise RuntimeError(f"AI analysis error: {e}")


class AuditEngine:
    """Main orchestration class for the page audit process."""

    def __init__(self, config: Config):
        self.config = config
        self.fetcher = PageFetcher(config)
        self.analyzer = AIAnalyzer(config)

    def run_audit(self, url: str) -> Dict[str, Any]:
        """
        Run complete audit on a URL.

        Args:
            url: Target URL to audit.

        Returns:
            Complete audit report as dictionary.

        Raises:
            ValueError: If URL is invalid.
            RuntimeError: If audit process fails.
        """
        # Validate URL
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            raise ValueError(f"Invalid URL format: {url}")

        logger.info(f"Starting audit for: {url}")

        try:
            # Fetch page
            html, status_code, load_time = self.fetcher.fetch(url)
            
            if html is None:
                return {
                    "url": url,
                    "error": f"Failed to fetch page (status: {status_code})",
                    "geo_findings": [],
                    "aeo_findings": [],
                    "veo_findings": [],
                    "critical_errors": [f"Page could not be fetched (HTTP {status_code})"],
                    "recommendations": ["Verify the URL is accessible"],
                    "priority_fixes": ["HIGH: Fix server or network issues preventing page access"],
                }

            # Extract signals
            extractor = SignalExtractor(html, url)
            signals = extractor.extract()
            signals.status_code = status_code
            signals.load_time_ms = load_time

            logger.info(
                f"Extracted signals: {signals.word_count} words, "
                f"{len(signals.h1_tags)} H1s, {len(signals.schema_types)} schema types"
            )

            # Analyze with AI
            analysis = self.analyzer.analyze(signals)

            # Build final report
            report = {
                "url": url,
                "audit_timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "page_signals": signals.to_analysis_dict(),
                **analysis,
            }

            logger.info(f"Audit completed successfully for: {url}")
            return report

        except Exception as e:
            logger.exception(f"Audit failed for {url}: {e}")
            return {
                "url": url,
                "error": str(e),
                "geo_findings": [],
                "aeo_findings": [],
                "veo_findings": [],
                "critical_errors": [f"Audit process failed: {str(e)}"],
                "recommendations": ["Retry the audit or check logs for details"],
                "priority_fixes": ["HIGH: Investigate and resolve the error"],
            }
