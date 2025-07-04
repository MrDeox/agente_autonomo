"""Tests for the UXEnhancer utility"""
import pytest

from agent.utils.ux_enhancer import UXEnhancer


class TestUXEnhancer:
    """Test class for UXEnhancer utility"""
    
    def test_format_welcome_message(self):
        """Test the format_welcome_message function"""
        enhancer = UXEnhancer()
        result = enhancer.format_welcome_message("Arthur")
        assert "Arthur" in result
        assert "welcome" in result.lower()
        assert isinstance(result, str)