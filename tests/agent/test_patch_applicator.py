import pytest
from agent.patch_applicator import apply_patches, _handle_insert, _handle_replace, _handle_delete_block
from pathlib import Path


def test_handle_insert(tmp_path):
    """Testa a aplicação de um patch INSERT."""
    file_path = tmp_path / 'test_file.txt'
    content = 'Original content\n'
    file_path.write_text(content)
    
    instruction = {'file_path': 'test_file.txt', 'operation': 'INSERT', 'line_number': 1, 'content': 'Inserted line\n'}
    success, updated_lines = _handle_insert(file_path, content.split('\n'), instruction, logging.getLogger())
    assert success
    assert 'Inserted line' in updated_lines[1]


def test_handle_replace(tmp_path):
    """Testa a aplicação de um patch REPLACE."""
    file_path = tmp_path / 'test_file.txt'
    content = 'Original content\n'
    file_path.write_text(content)
    
    instruction = {'file_path': 'test_file.txt', 'operation': 'REPLACE', 'block_to_replace': 'Original content', 'content': 'New content'}
    success, updated_lines = _handle_replace(file_path, content.split('\n'), instruction, logging.getLogger())
    assert success
    assert 'New content' in updated_lines


def test_handle_delete_block(tmp_path):
    """Testa a aplicação de um patch DELETE_BLOCK."""
    file_path = tmp_path / 'test_file.txt'
    content = 'Line 1\ndef obsolete_function():\n    pass\nLine 2\n'
    file_path.write_text(content)
    
    instruction = {'file_path': 'test_file.txt', 'operation': 'DELETE_BLOCK', 'block_to_delete': 'def obsolete_function():\n    pass'}
    success, updated_lines = _handle_delete_block(file_path, content.split('\n'), instruction, logging.getLogger())
    assert success
    assert 'obsolete_function()' not in '\n'.join(updated_lines)


def test_apply_patches_with_valid_instructions(tmp_path):
    """Testa a aplicação de múltiplos patches com instruções válidas."""
    file_path = tmp_path / 'test_file.txt'
    file_path.write_text('Initial content')
    
    instructions = [
        {'file_path': 'test_file.txt', 'operation': 'INSERT', 'line_number': 1, 'content': 'Inserted line'},
        {'file_path': 'test_file.txt', 'operation': 'REPLACE', 'block_to_replace': 'Initial content', 'content': 'Replaced content'}
    ]
    
    apply_patches(instructions, logging.getLogger(), base_path=str(tmp_path))
    assert file_path.read_text() == 'Inserted line\nReplaced content'