"""
Unit tests for the Page-Level GEO/AEO/VEO Audit Engine.

This test suite covers:
- Signal extraction logic
- Configuration loading
- AI analyzer response parsing
- Error handling scenarios
"""

import json
import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

# Import modules to test
from config import Config, get_config
from audit_engine import PageSignals, PageFetcher, SignalExtractor, AIAnalyzer, AuditEngine


class TestPageSignals:
    """Test PageSignals dataclass functionality."""
    
    def test_create_page_signals(self):
        """Test creating PageSignals instance with default values."""
        signals = PageSignals(url="https://example.com")
        
        assert signals.url == "https://example.com"
        assert signals.title is None
        assert signals.word_count == 0
        assert signals.h1_tags == []
        assert signals.schema_types == []
    
    def test_create_page_signals_with_values(self):
        """Test creating PageSignals with populated values."""
        signals = PageSignals(
            url="https://example.com/page",
            title="Test Page",
            meta_description="Test description",
            h1_tags=["Main Heading"],
            h2_tags=["Section 1", "Section 2"],
            word_count=500,
            schema_types=["Article", "BreadcrumbList"]
        )
        
        assert signals.title == "Test Page"
        assert signals.title_length == 9
        assert len(signals.h1_tags) == 1
        assert len(signals.h2_tags) == 2
        assert signals.word_count == 500
    
    def test_to_analysis_dict(self):
        """Test conversion to analysis dictionary."""
        signals = PageSignals(
            url="https://example.com",
            title="Test",
            word_count=100,
            h1_tags=["Heading"],
            status_code=200
        )
        
        analysis_dict = signals.to_analysis_dict()
        
        assert "url" in analysis_dict
        assert "title" in analysis_dict
        assert "word_count" in analysis_dict
        assert "h1_count" in analysis_dict
        assert analysis_dict["h1_count"] == 1
        assert analysis_dict["status_code"] == 200


class TestSignalExtractor:
    """Test HTML signal extraction logic."""
    
    @pytest.fixture
    def sample_html(self):
        """Provide sample HTML for testing."""
        return """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <title>Test Page Title</title>
            <meta name="description" content="Test meta description">
            <link rel="canonical" href="https://example.com/page">
            <meta property="og:title" content="OG Title">
            <meta name="viewport" content="width=device-width">
            <script type="application/ld+json">
            {
                "@context": "https://schema.org",
                "@type": "Article",
                "headline": "Article Headline"
            }
            </script>
        </head>
        <body>
            <h1>Main Heading</h1>
            <h2>Section 1</h2>
            <h2>Section 2</h2>
            <h3>Subsection 1.1</h3>
            <p>This is a test paragraph with some content words.</p>
            <a href="/internal">Internal Link</a>
            <a href="https://external.com">External Link</a>
            <img src="image.jpg" alt="Test Image">
            <img src="image2.jpg">
        </body>
        </html>
        """
    
    def test_extract_title(self, sample_html):
        """Test title extraction from HTML."""
        extractor = SignalExtractor(sample_html, "https://example.com")
        signals = extractor.extract()
        
        assert signals.title == "Test Page Title"
        assert signals.title_length == 15
    
    def test_extract_meta_description(self, sample_html):
        """Test meta description extraction."""
        extractor = SignalExtractor(sample_html, "https://example.com")
        signals = extractor.extract()
        
        assert signals.meta_description == "Test meta description"
        assert signals.meta_description_length == 21
    
    def test_extract_headings(self, sample_html):
        """Test heading extraction."""
        extractor = SignalExtractor(sample_html, "https://example.com")
        signals = extractor.extract()
        
        assert len(signals.h1_tags) == 1
        assert signals.h1_tags[0] == "Main Heading"
        assert len(signals.h2_tags) == 2
        assert "Section 1" in signals.h2_tags
    
    def test_extract_schema_types(self, sample_html):
        """Test schema.org type extraction."""
        extractor = SignalExtractor(sample_html, "https://example.com")
        signals = extractor.extract()
        
        assert "Article" in signals.schema_types
    
    def test_extract_canonical(self, sample_html):
        """Test canonical URL extraction."""
        extractor = SignalExtractor(sample_html, "https://example.com")
        signals = extractor.extract()
        
        assert signals.canonical_url == "https://example.com/page"
    
    def test_count_links(self, sample_html):
        """Test internal and external link counting."""
        extractor = SignalExtractor(sample_html, "https://example.com")
        signals = extractor.extract()
        
        assert signals.internal_links_count >= 1
        assert signals.external_links_count >= 1
    
    def test_analyze_images(self, sample_html):
        """Test image analysis."""
        extractor = SignalExtractor(sample_html, "https://example.com")
        signals = extractor.extract()
        
        assert signals.images_count == 2
        assert signals.images_with_alt == 1
    
    def test_word_count(self, sample_html):
        """Test word counting."""
        extractor = SignalExtractor(sample_html, "https://example.com")
        signals = extractor.extract()
        
        assert signals.word_count > 0


class TestConfig:
    """Test configuration loading and validation."""
    
    @patch.dict('os.environ', {
        'OPENAI_API_KEY': 'test-key',
        'OPENAI_BASE_URL': 'https://api.test.com/v1',
        'OPENAI_MODEL': 'test-model'
    })
    def test_get_config_from_env(self):
        """Test loading config from environment variables."""
        config = get_config()
        
        assert config.openai_api_key == 'test-key'
        assert config.openai_base_url == 'https://api.test.com/v1'
        assert config.openai_model == 'test-model'
    
    @patch.dict('os.environ', {
        'OPENAI_API_KEY': 'test-key',
        'REQUEST_TIMEOUT': '60',
        'MAX_RETRIES': '5'
    })
    def test_config_optional_values(self):
        """Test optional config values with defaults."""
        config = get_config()
        
        assert config.request_timeout == 60
        assert config.max_retries == 5


class TestAIAnalyzer:
    """Test AI analyzer functionality."""
    
    @pytest.fixture
    def mock_config(self):
        """Create mock config for testing."""
        config = Mock(spec=Config)
        config.openai_api_key = 'test-key'
        config.openai_base_url = 'https://api.test.com/v1'
        config.openai_model = 'test-model'
        return config
    
    def test_analyze_valid_response(self, mock_config):
        """Test parsing valid JSON response from AI."""
        signals = PageSignals(url="https://example.com", title="Test")
        
        mock_response = {
            "geo_findings": ["Finding 1"],
            "aeo_findings": ["Finding 2"],
            "veo_findings": [],
            "critical_errors": [],
            "recommendations": ["Rec 1"],
            "priority_fixes": ["HIGH: Fix this"]
        }
        
        with patch('audit_engine.OpenAI') as mock_client:
            mock_client.return_value.chat.completions.create.return_value.choices[0].message.content = json.dumps(mock_response)
            
            analyzer = AIAnalyzer(mock_config)
            result = analyzer.analyze(signals)
            
            assert "geo_findings" in result
            assert len(result["geo_findings"]) == 1
            assert "priority_fixes" in result
    
    def test_analyze_missing_keys(self, mock_config):
        """Test handling of missing keys in AI response."""
        signals = PageSignals(url="https://example.com")
        
        # Response missing some required keys
        incomplete_response = {
            "geo_findings": ["Finding 1"]
            # Missing other required keys
        }
        
        with patch('audit_engine.OpenAI') as mock_client:
            mock_client.return_value.chat.completions.create.return_value.choices[0].message.content = json.dumps(incomplete_response)
            
            analyzer = AIAnalyzer(mock_config)
            result = analyzer.analyze(signals)
            
            # Should add empty lists for missing keys
            assert "aeo_findings" in result
            assert "veo_findings" in result
            assert isinstance(result["aeo_findings"], list)


class TestAuditEngine:
    """Test main audit engine orchestration."""
    
    @pytest.fixture
    def mock_config(self):
        """Create mock config."""
        config = Mock(spec=Config)
        config.openai_api_key = 'test-key'
        config.openai_base_url = 'https://api.test.com/v1'
        config.openai_model = 'test-model'
        config.request_timeout = 30
        config.max_retries = 3
        config.user_agent = 'TestBot/1.0'
        return config
    
    def test_run_audit_invalid_url(self, mock_config):
        """Test audit with invalid URL format."""
        engine = AuditEngine(mock_config)
        
        with pytest.raises(ValueError):
            engine.run_audit("not-a-valid-url")
    
    def test_run_audit_fetch_failure(self, mock_config):
        """Test audit when page fetch fails."""
        engine = AuditEngine(mock_config)
        
        with patch.object(engine.fetcher, 'fetch', return_value=(None, 404, None)):
            result = engine.run_audit("https://example.com")
            
            assert "error" in result or "critical_errors" in result
            assert result["url"] == "https://example.com"
    
    def test_run_audit_success(self, mock_config):
        """Test successful audit flow."""
        engine = AuditEngine(mock_config)
        
        sample_html = "<html><head><title>Test</title></head><body><h1>Heading</h1></body></html>"
        
        mock_ai_response = {
            "geo_findings": [],
            "aeo_findings": [],
            "veo_findings": [],
            "critical_errors": [],
            "recommendations": [],
            "priority_fixes": []
        }
        
        with patch.object(engine.fetcher, 'fetch', return_value=(sample_html, 200, 100)):
            with patch.object(engine.analyzer, 'analyze', return_value=mock_ai_response):
                result = engine.run_audit("https://example.com")
                
                assert result["url"] == "https://example.com"
                assert "page_signals" in result
                assert "geo_findings" in result


class TestErrorHandling:
    """Test error handling scenarios."""
    
    def test_extractor_handles_malformed_html(self):
        """Test signal extractor with malformed HTML."""
        malformed_html = "<html><head><title>Unclosed"
        
        # Should not raise exception
        extractor = SignalExtractor(malformed_html, "https://example.com")
        signals = extractor.extract()
        
        assert signals.url == "https://example.com"
    
    def test_extractor_handles_empty_html(self):
        """Test signal extractor with empty HTML."""
        extractor = SignalExtractor("", "https://example.com")
        signals = extractor.extract()
        
        assert signals.word_count == 0
        assert signals.h1_tags == []


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
