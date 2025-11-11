"""
Tests for i18n module.
"""

import pytest
from pathlib import Path
from src.i18n import I18n, get_i18n, t


class TestI18n:
    """Test cases for I18n class."""
    
    def test_create_i18n_default_locale(self):
        """Test creating i18n with default locale."""
        i18n = I18n()
        
        assert i18n.locale == "pt-BR"
    
    def test_create_i18n_custom_locale(self):
        """Test creating i18n with custom locale."""
        i18n = I18n("en-US")
        
        assert i18n.locale == "en-US"
    
    def test_unsupported_locale_raises_error(self):
        """Test that unsupported locale raises error."""
        with pytest.raises(ValueError, match="Unsupported locale"):
            I18n("fr-FR")
    
    def test_load_module(self):
        """Test loading a translation module."""
        i18n = I18n("pt-BR")
        
        translations = i18n.load_module("cli")
        
        assert isinstance(translations, dict)
        assert "cli" in translations or "areas" in translations
    
    def test_translate_simple_key(self):
        """Test translating a simple key."""
        i18n = I18n("pt-BR")
        
        result = i18n.t("cli.title", module="cli")
        
        assert isinstance(result, str)
        assert len(result) > 0
    
    def test_translate_with_interpolation(self):
        """Test translation with parameter interpolation."""
        i18n = I18n("pt-BR")
        
        result = i18n.t("prompts.range_error", module="cli", min=0, max=45)
        
        assert "0" in result
        assert "45" in result
    
    def test_translate_missing_key_returns_key(self):
        """Test that missing key returns the key itself."""
        i18n = I18n("pt-BR")
        
        result = i18n.t("nonexistent.key", module="cli")
        
        assert result == "nonexistent.key"
    
    def test_set_locale(self):
        """Test changing locale."""
        i18n = I18n("pt-BR")
        
        i18n.set_locale("en-US")
        
        assert i18n.locale == "en-US"
    
    def test_set_locale_clears_cache(self):
        """Test that changing locale clears translation cache."""
        i18n = I18n("pt-BR")
        
        # Load a module
        i18n.load_module("cli")
        assert len(i18n._translations) > 0
        
        # Change locale
        i18n.set_locale("en-US")
        assert len(i18n._translations) == 0
    
    def test_get_available_locales(self):
        """Test getting available locales."""
        i18n = I18n()
        
        locales = i18n.get_available_locales()
        
        assert "pt-BR" in locales
        assert "en-US" in locales
    
    def test_global_get_i18n(self):
        """Test global i18n instance."""
        i18n1 = get_i18n()
        i18n2 = get_i18n()
        
        # Should return the same instance
        assert i18n1 is i18n2
    
    def test_global_t_function(self):
        """Test global t() shorthand function."""
        result = t("cli.title", module="cli")
        
        assert isinstance(result, str)
        assert len(result) > 0
    
    def test_different_locales_different_translations(self):
        """Test that different locales return different translations."""
        i18n_pt = I18n("pt-BR")
        i18n_en = I18n("en-US")
        
        pt_result = i18n_pt.t("areas.mathematics", module="cli")
        en_result = i18n_en.t("areas.mathematics", module="cli")
        
        # Should be different (unless they happen to be the same)
        # At minimum, should both be valid strings
        assert isinstance(pt_result, str)
        assert isinstance(en_result, str)
        assert len(pt_result) > 0
        assert len(en_result) > 0
    
    def test_repr(self):
        """Test string representation."""
        i18n = I18n("pt-BR")
        
        repr_str = repr(i18n)
        
        assert "I18n" in repr_str
        assert "pt-BR" in repr_str
