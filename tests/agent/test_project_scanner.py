import pytest
from pathlib import Path
from unittest.mock import patch, mock_open

from agent.project_scanner import (
    _extract_elements,
    _extract_skeleton,
    update_project_manifest,
    analyze_code_metrics
)

# Test data
SAMPLE_CODE = '''
import os

class MyClass:
    """Sample class docstring"""
    def __init__(self):
        pass

def sample_func(arg1, arg2):
    """Sample function docstring"""
    return arg1 + arg2
'''

# Tests for _extract_elements
class TestExtractElements:
    def test_extract_elements_success(self):
        """Test _extract_elements with valid code."""
        result = _extract_elements(SAMPLE_CODE)
        assert len(result) == 3
        assert result[0][0] == 'import'
        assert result[1][0] == 'class'
        assert result[2][0] == 'function'

    def test_extract_elements_error(self):
        """Test _extract_elements with invalid code."""
        result = _extract_elements('invalid python code')
        assert result[0][0] == 'error'

# Tests for _extract_skeleton
class TestExtractSkeleton:
    def test_extract_skeleton_success(self):
        """Test _extract_skeleton with valid code."""
        result = _extract_skeleton(SAMPLE_CODE)
        assert 'class MyClass' in result
        assert 'def sample_func' in result

    def test_extract_skeleton_error(self):
        """Test _extract_skeleton with invalid code."""
        result = _extract_skeleton('invalid python code')
        assert result.startswith('# Erro na análise AST')

# Tests for update_project_manifest
class TestUpdateProjectManifest:
    @patch('os.walk')
    @patch('builtins.open', new_callable=mock_open)
    def test_update_project_manifest(self, mock_file, mock_walk):
        """Test update_project_manifest basic functionality."""
        mock_walk.return_value = [
            ('/root', ['dir1'], ['file1.py']),
            ('/root/dir1', [], ['file2.py'])
        ]
        
        with patch('pathlib.Path.resolve', return_value=Path('/root')):
            update_project_manifest('/root', ['file1.py'])
            
        assert mock_file.called

# Tests for analyze_code_metrics
class TestAnalyzeCodeMetrics:
    @patch('os.walk')
    def test_analyze_code_metrics(self, mock_walk):
        """Test analyze_code_metrics basic functionality."""
        mock_walk.return_value = [
            ('/root', ['dir1'], ['file1.py']),
            ('/root/dir1', [], ['file2.py'])
        ]
        
        with patch('pathlib.Path.resolve', return_value=Path('/root')), \
             patch('agent.project_scanner.analyze_raw'), \
             patch('agent.project_scanner.ComplexityVisitor.from_ast'):
            result = analyze_code_metrics('/root')
            
        assert 'metrics' in result
        assert 'summary' in result