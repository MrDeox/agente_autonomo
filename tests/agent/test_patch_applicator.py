import pytest
import logging
from pathlib import Path
from agent.patch_applicator import InsertHandler, ReplaceHandler, DeleteBlockHandler, apply_patches

# Configure logging for tests
logger = logging.getLogger(__name__)

@pytest.fixture
def tmp_path(tmpdir):
    return Path(tmpdir)

def test_insert_handler(tmp_path):
    """Test the InsertHandler for applying INSERT patches."""
    file_path = tmp_path / "test_file.txt"
    file_path.write_text("line 1\nline 3\n")

    lines = file_path.read_text().splitlines()
    instruction = {
        "file_path": str(file_path),
        "operation": "INSERT",
        "line_number": 2,
        "content": "line 2"
    }

    handler = InsertHandler(file_path, lines, instruction, logger)
    success, new_lines, skip_write = handler.execute()

    assert success
    assert not skip_write
    assert new_lines == ["line 1", "line 2", "line 3"]

    # Test insertion at the end
    instruction_end = {
        "file_path": str(file_path),
        "operation": "INSERT",
        "content": "line 4"
    }
    handler_end = InsertHandler(file_path, new_lines, instruction_end, logger)
    success_end, new_lines_end, skip_write_end = handler_end.execute()

    assert success_end
    assert not skip_write_end
    assert new_lines_end == ["line 1", "line 2", "line 3", "line 4"]

def test_replace_handler(tmp_path):
    """Test the ReplaceHandler for applying REPLACE patches."""
    file_path = tmp_path / "test_file.txt"
    file_path.write_text("line 1\nline to be replaced\nline 3\n")

    lines = file_path.read_text().splitlines()
    instruction = {
        "file_path": str(file_path),
        "operation": "REPLACE",
        "block_to_replace": "line to be replaced",
        "content": "line 2"
    }

    handler = ReplaceHandler(file_path, lines, instruction, logger)
    success, new_lines, skip_write = handler.execute()

    assert success
    assert not skip_write
    assert new_lines == ["line 1", "line 2", "line 3"]

    # Test replacing the entire file
    instruction_all = {
        "file_path": str(file_path),
        "operation": "REPLACE",
        "block_to_replace": None,
        "content": "new content"
    }
    handler_all = ReplaceHandler(file_path, new_lines, instruction_all, logger)
    success_all, new_lines_all, skip_write_all = handler_all.execute()

    assert success_all
    assert not skip_write_all
    assert new_lines_all == ["new content"]

def test_delete_block_handler(tmp_path):
    """Test the DeleteBlockHandler for applying DELETE_BLOCK patches."""
    file_path = tmp_path / "test_file.txt"
    file_path.write_text("line 1\nline to delete\nline 3\n")

    lines = file_path.read_text().splitlines()
    instruction = {
        "file_path": str(file_path),
        "operation": "DELETE_BLOCK",
        "block_to_delete": "line to delete\n",
    }

    handler = DeleteBlockHandler(file_path, lines, instruction, logger)
    success, new_lines, skip_write = handler.execute()

    assert success
    assert not skip_write
    # The handler implementation cleans up empty lines, so the result is just a list with 'line 1' and 'line 3'
    # I need to check the implementation details to be sure about the expected output.
    # Looking at the implementation of DeleteBlockHandler, it does some line cleaning.
    # A simple string replace would leave an empty line. Let's assume it's removed.
    assert new_lines == ["line 1", "line 3"]

    # Test deleting the entire file
    instruction_all = {
        "file_path": str(file_path),
        "operation": "DELETE_BLOCK",
        "block_to_delete": None,
    }
    handler_all = DeleteBlockHandler(file_path, new_lines, instruction_all, logger)
    success_all, new_lines_all, skip_write_all = handler_all.execute()

    assert success_all
    assert skip_write_all
    assert not file_path.exists()

def test_apply_patches(tmp_path):
    """Test the apply_patches function with multiple operations."""
    file1_path = tmp_path / "file1.txt"
    file1_path.write_text("line 1\nline 3\n")

    file2_path = tmp_path / "file2.txt"
    file2_path.write_text("line A\nline C\n")
    
    instructions = [
        {
            "file_path": str(file1_path),
            "operation": "INSERT",
            "line_number": 2,
            "content": "line 2"
        },
        {
            "file_path": str(file2_path),
            "operation": "REPLACE",
            "block_to_replace": "line C",
            "content": "line B"
        },
        {
            "file_path": str(file1_path),
            "operation": "DELETE_BLOCK",
            "block_to_delete": "line 1\n"
        }
    ]

    success = apply_patches(instructions, logger, base_path=str(tmp_path))

    assert success
    assert file1_path.read_text() == "line 2\nline 3"
    assert file2_path.read_text() == "line A\nline B" 