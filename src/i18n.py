"""
Internationalization (i18n) Module

Provides translation support for the ENEM TRI Calculator.
Supports pt-BR (Brazilian Portuguese) and en-US (English).
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional


class I18n:
    """
    Internationalization handler for loading and managing translations.
    """
    
    # Supported locales
    SUPPORTED_LOCALES = ["pt-BR", "en-US"]
    DEFAULT_LOCALE = "pt-BR"
    
    def __init__(self, locale: Optional[str] = None):
        """
        Initialize the i18n handler.
        
        Args:
            locale: Locale code (e.g., 'pt-BR', 'en-US'). 
                   If None, uses DEFAULT_LOCALE.
        """
        self.locale = locale or self.DEFAULT_LOCALE
        
        if self.locale not in self.SUPPORTED_LOCALES:
            raise ValueError(
                f"Unsupported locale: {self.locale}. "
                f"Supported: {', '.join(self.SUPPORTED_LOCALES)}"
            )
        
        # Get the locales directory path
        # Navigate from src/i18n.py to project root/locales
        self.locales_dir = Path(__file__).parent.parent / "locales"
        self.locale_dir = self.locales_dir / self.locale
        
        if not self.locale_dir.exists():
            raise FileNotFoundError(
                f"Locale directory not found: {self.locale_dir}. "
                f"Please ensure locales/{self.locale}/ exists."
            )
        
        # Cache for loaded translation files
        self._translations: Dict[str, Dict[str, Any]] = {}
    
    def load_module(self, module_name: str) -> Dict[str, Any]:
        """
        Load translations for a specific module.
        
        Args:
            module_name: Name of the module (e.g., 'cli', 'models', 'calculator')
            
        Returns:
            Dictionary with translations for the module
        """
        # Check cache first
        if module_name in self._translations:
            return self._translations[module_name]
        
        # Load from JSON file
        json_path = self.locale_dir / f"{module_name}.json"
        
        if not json_path.exists():
            # Try to provide helpful error message
            print(f"Warning: Translation file not found: {json_path}")
            return {}
        
        with open(json_path, 'r', encoding='utf-8') as f:
            translations = json.load(f)
        
        # Cache the translations
        self._translations[module_name] = translations
        
        return translations
    
    def t(self, key: str, module: str = "cli", **kwargs) -> str:
        """
        Translate a key with optional parameter interpolation.
        
        Args:
            key: Translation key in dot notation (e.g., 'cli.title')
            module: Module name to load translations from
            **kwargs: Parameters to interpolate in the translation
            
        Returns:
            Translated string with interpolated parameters
            
        Example:
            >>> i18n = I18n('pt-BR')
            >>> i18n.t('prompts.range_error', min=0, max=45)
            'Por favor, insira um valor entre 0 e 45'
        """
        # Load module translations
        translations = self.load_module(module)
        
        # Navigate through nested dictionary using dot notation
        keys = key.split('.')
        value = translations
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                # Return key itself if translation not found
                return key
        
        # If value is not a string, return the key
        if not isinstance(value, str):
            return key
        
        # Interpolate parameters
        if kwargs:
            try:
                return value.format(**kwargs)
            except KeyError:
                # Return unformatted string if parameter is missing
                return value
        
        return value
    
    def set_locale(self, locale: str) -> None:
        """
        Change the current locale.
        
        Args:
            locale: New locale code
        """
        if locale not in self.SUPPORTED_LOCALES:
            raise ValueError(
                f"Unsupported locale: {locale}. "
                f"Supported: {', '.join(self.SUPPORTED_LOCALES)}"
            )
        
        self.locale = locale
        self.locale_dir = self.locales_dir / self.locale
        
        # Clear cache when changing locale
        self._translations.clear()
    
    def get_available_locales(self) -> list[str]:
        """
        Get list of available locales.
        
        Returns:
            List of locale codes
        """
        return self.SUPPORTED_LOCALES.copy()
    
    def __repr__(self) -> str:
        """Return string representation."""
        return f"I18n(locale='{self.locale}')"


# Global instance for easy access
_global_i18n: Optional[I18n] = None


def get_i18n(locale: Optional[str] = None) -> I18n:
    """
    Get or create the global i18n instance.
    
    Args:
        locale: Optional locale to set. If None, uses existing or default.
        
    Returns:
        I18n instance
    """
    global _global_i18n
    
    if _global_i18n is None or locale is not None:
        _global_i18n = I18n(locale)
    
    return _global_i18n


def t(key: str, module: str = "cli", **kwargs) -> str:
    """
    Shorthand function for translation.
    
    Args:
        key: Translation key
        module: Module name
        **kwargs: Parameters to interpolate
        
    Returns:
        Translated string
    """
    return get_i18n().t(key, module, **kwargs)
