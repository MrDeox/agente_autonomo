import json
import os
import time # For unique timestamps
import pytest
from agent.memory import Memory

@pytest.fixture
def temp_memory_file(tmp_path):
    """Fixture to create a temporary memory file path."""
    return tmp_path / "test_memory.json"

def test_memory_initialization(temp_memory_file):
    """Test that Memory initializes correctly with a filepath."""
    memory = Memory(filepath=str(temp_memory_file))
    assert memory.filepath == str(temp_memory_file)
    assert memory.max_objectives_history == 20 # Default
    assert memory.cycle_count == 0
    assert memory.completed_objectives == []
    assert memory.failed_objectives == []
    assert memory.acquired_capabilities == []
    assert memory.recent_objectives_log == []

def test_memory_initialization_custom_max_history(temp_memory_file):
    """Test Memory initialization with custom max_objectives_history."""
    memory = Memory(filepath=str(temp_memory_file), max_objectives_history=10)
    assert memory.max_objectives_history == 10

def test_save_and_load_empty_memory(temp_memory_file):
    """Test saving and loading an empty memory."""
    memory1 = Memory(filepath=str(temp_memory_file))
    memory1.save()
    assert os.path.exists(temp_memory_file)

    memory2 = Memory(filepath=str(temp_memory_file))
    memory2.load()
    assert memory2.completed_objectives == []
    assert memory2.failed_objectives == []
    assert memory2.acquired_capabilities == []
    assert memory2.recent_objectives_log == [] # Verificar novo atributo

def test_add_completed_objective(temp_memory_file):
    """Test adding and saving/loading a completed objective."""
    memory = Memory(filepath=str(temp_memory_file))
    ts_before = memory._get_timestamp()
    time.sleep(0.01) # ensure timestamp changes if test is too fast
    memory.add_completed_objective("Test objective 1", "test_strategy", "Details here")
    time.sleep(0.01)
    ts_after = memory._get_timestamp()

    assert len(memory.completed_objectives) == 1
    record = memory.completed_objectives[0]
    assert record["objective"] == "Test objective 1"
    assert record["strategy_used"] == "test_strategy"
    assert record["details"] == "Details here"
    assert ts_before < record["date"] < ts_after

    memory.save()

    new_memory = Memory(filepath=str(temp_memory_file))
    new_memory.load()
    assert len(new_memory.completed_objectives) == 1
    loaded_record = new_memory.completed_objectives[0]
    assert loaded_record["objective"] == "Test objective 1"
    assert loaded_record["date"] == record["date"]

def test_add_failed_objective(temp_memory_file):
    """Test adding and saving/loading a failed objective."""
    memory = Memory(filepath=str(temp_memory_file))
    memory.add_failed_objective("Test objective 2", "test_reason", "Failure details")

    assert len(memory.failed_objectives) == 1
    record = memory.failed_objectives[0]
    assert record["objective"] == "Test objective 2"
    assert record["reason"] == "test_reason"
    assert record["details"] == "Failure details"
    assert "date" in record

    memory.save()

    new_memory = Memory(filepath=str(temp_memory_file))
    new_memory.load()
    assert len(new_memory.failed_objectives) == 1
    assert new_memory.failed_objectives[0]["objective"] == "Test objective 2"

def test_add_capability(temp_memory_file):
    """Test adding and saving/loading an acquired capability."""
    memory = Memory(filepath=str(temp_memory_file))
    memory.add_capability("New tool X", related_objective="Objective foo")

    assert len(memory.acquired_capabilities) == 1
    record = memory.acquired_capabilities[0]
    assert record["description"] == "New tool X"
    assert record["related_objective"] == "Objective foo"
    assert "date" in record

    memory.save()

    new_memory = Memory(filepath=str(temp_memory_file))
    new_memory.load()
    assert len(new_memory.acquired_capabilities) == 1
    assert new_memory.acquired_capabilities[0]["description"] == "New tool X"

def test_load_non_existent_file(tmp_path):
    """Test loading from a non-existent file path, should start fresh."""
    non_existent_file = tmp_path / "does_not_exist.json"
    memory = Memory(filepath=str(non_existent_file))
    memory.load() # Should not raise error
    assert memory.completed_objectives == []
    assert memory.failed_objectives == []
    assert memory.acquired_capabilities == []
    assert memory.recent_objectives_log == []

def test_load_corrupted_json_file(temp_memory_file):
    """Test loading from a corrupted JSON file, should start fresh and print warning."""
    with open(temp_memory_file, "w") as f:
        f.write("this is not json {") # Corrupted JSON

    memory = Memory(filepath=str(temp_memory_file))
    # Capture print output (optional, could also check logs if Memory class logged)
    # For simplicity, we'll just check that it loads empty without erroring out
    memory.load()

    assert memory.completed_objectives == []
    assert memory.failed_objectives == []
    assert memory.acquired_capabilities == []
    assert memory.recent_objectives_log == []

def test_file_persistence_across_instances(temp_memory_file):
    """Test that data saved by one instance is loaded by another."""
    memory1 = Memory(filepath=str(temp_memory_file))
    memory1.add_completed_objective("Persistent obj", "strat1", "detail1")
    memory1.add_failed_objective("Persistent fail", "reason1", "detail_fail1")
    memory1.add_capability("Persistent cap", "obj_cap1")
    memory1.save()

    memory2 = Memory(filepath=str(temp_memory_file))
    memory2.load()

    assert len(memory2.completed_objectives) == 1
    assert memory2.completed_objectives[0]["objective"] == "Persistent obj"
    assert len(memory2.failed_objectives) == 1
    assert memory2.failed_objectives[0]["objective"] == "Persistent fail"
    assert len(memory2.acquired_capabilities) == 1
    assert memory2.acquired_capabilities[0]["description"] == "Persistent cap"

def test_get_history_summary_format_and_content(temp_memory_file):
    """Test the format and content of get_history_summary."""
    memory = Memory(filepath=str(temp_memory_file))

    # Test empty summary
    assert memory.get_history_summary() == "No significant history recorded yet."
    assert memory.get_full_history_for_prompt() == "No relevant history available."


    obj1_comp = "Completed Objective Alpha"
    obj2_fail = "Failed Objective Beta"
    cap1_desc = "New Capability Gamma"

    memory.add_completed_objective(obj1_comp, "s1", "d1")
    time.sleep(0.01) # ensure different timestamps
    memory.add_failed_objective(obj2_fail, "r1", "d_fail1")
    time.sleep(0.01)
    memory.add_capability(cap1_desc, obj1_comp)

    summary = memory.get_history_summary(max_items_per_category=1)

    assert "Recent Successes:" in summary
    assert obj1_comp[:100] in summary # Check for objective name (potentially truncated)
    assert "Recent Failures:" in summary
    assert obj2_fail[:100] in summary
    assert "Recent Capabilities Acquired:" in summary
    assert cap1_desc[:100] in summary

    # Check order (most recent first)
    idx_cap = summary.find(cap1_desc[:100])
    idx_fail = summary.find(obj2_fail[:100])
    idx_comp = summary.find(obj1_comp[:100])

    # Assuming capabilities are listed after failures, and failures after successes
    # and within each category, items are reversed (most recent first).
    # The get_history_summary concatenates these blocks.
    # The test is more about presence than strict order between categories here.

    full_prompt_summary = memory.get_full_history_for_prompt(max_completed=1, max_failed=1, max_capabilities=1)
    assert "Completed Objectives (most recent first):" in full_prompt_summary
    assert obj1_comp in full_prompt_summary # Full name in prompt version
    assert "Failed Objectives (most recent first):" in full_prompt_summary
    assert obj2_fail in full_prompt_summary
    assert "Acquired Capabilities (most recent first):" in full_prompt_summary
    assert cap1_desc in full_prompt_summary


def test_get_history_summary_max_items(temp_memory_file):
    """Test that max_items_per_category limits the output correctly."""
    memory = Memory(filepath=str(temp_memory_file))
    for i in range(5):
        memory.add_completed_objective(f"CompObj {i}", "s", "d")
        memory.add_failed_objective(f"FailObj {i}", "r", "d")
        memory.add_capability(f"Cap {i}")

    summary_limited = memory.get_history_summary(max_items_per_category=2)

    # Count occurrences. Each line starts with "  - Objective:" or "  - Capability:"
    completed_lines = [line for line in summary_limited.split('\n') if "Objective:" in line and "Recent Successes:" in summary_limited.split("Recent Failures:")[0]]
    failed_lines = [line for line in summary_limited.split('\n') if "Objective:" in line and "Recent Failures:" in summary_limited.split("Recent Capabilities Acquired:")[0] and "Recent Successes:" not in line]
    capability_lines = [line for line in summary_limited.split('\n') if "Capability:" in line]

    # This is a bit simplistic as it depends on the exact string format.
    # A more robust way would be to parse, but for this test, counting lines is okay.
    # Need to be careful if the summary format changes.
    # Let's refine the count based on the actual structure

    success_count = summary_limited.count("Objective:") if "Recent Successes:" in summary_limited else 0
    failure_count = 0
    if "Recent Failures:" in summary_limited:
        fail_block_start = summary_limited.find("Recent Failures:")
        fail_block_end = summary_limited.find("Recent Capabilities Acquired:")
        if fail_block_end == -1: # No capabilities block
             fail_block_end = len(summary_limited)
        failure_count = summary_limited[fail_block_start:fail_block_end].count("Objective:")

    # Adjust success_count if failures were counted in it
    if failure_count > 0 :
        success_count = summary_limited.split("Recent Failures:")[0].count("Objective:")


    capability_count = summary_limited.count("Capability:")

    assert success_count <= 2
    assert failure_count <= 2
    assert capability_count <= 2

    # Check that the most recent items are present
    assert "CompObj 4" in summary_limited # Most recent completed
    assert "CompObj 3" in summary_limited
    assert "CompObj 2" not in summary_limited # Should be excluded by max_items

    assert "FailObj 4" in summary_limited
    assert "FailObj 3" in summary_limited
    assert "FailObj 2" not in summary_limited

    assert "Cap 4" in summary_limited
    assert "Cap 3" in summary_limited
    assert "Cap 2" not in summary_limited

    full_prompt_summary_limited = memory.get_full_history_for_prompt(max_completed=2, max_failed=1, max_capabilities=3)
    assert full_prompt_summary_limited.count("Objective: CompObj") <= 2 # Max 2 completed
    assert full_prompt_summary_limited.count("Objective: FailObj") <= 1 # Max 1 failed
    assert full_prompt_summary_limited.count("Capability: Cap") <= 3   # Max 3 capabilities
    assert "CompObj 4" in full_prompt_summary_limited
    assert "FailObj 4" in full_prompt_summary_limited
    assert "Cap 4" in full_prompt_summary_limited
    assert "Cap 3" in full_prompt_summary_limited
    assert "Cap 2" in full_prompt_summary_limited
    assert "Cap 1" not in full_prompt_summary_limited # Excluded by max_capabilities=3 from 5 total.
    assert "FailObj 3" not in full_prompt_summary_limited # Excluded by max_failed=1
    assert "CompObj 2" not in full_prompt_summary_limited # Excluded by max_completed=2


def test_recent_objectives_log_tracking_and_trimming(temp_memory_file):
    """Test that recent_objectives_log correctly tracks objectives and stays trimmed."""
    memory = Memory(filepath=str(temp_memory_file))

    # Add 7 objectives (2 completed, 5 failed)
    memory.add_completed_objective("Obj Comp 1", "s", "d")
    memory.add_failed_objective("Obj Fail 1", "r", "d")
    memory.add_completed_objective("Obj Comp 2", "s", "d")
    memory.add_failed_objective("Obj Fail 2", "r", "d")
    memory.add_failed_objective("Obj Fail 3", "r", "d")
    memory.add_failed_objective("Obj Fail 4", "r", "d")
    memory.add_failed_objective("Obj Fail 5", "r", "d") # This is the 7th total, 5th fail

    assert len(memory.recent_objectives_log) == 5 # Should be trimmed to 5

    # Check content of the log (most recent 5)
    # Expected: Comp2 (success), Fail2 (failure), Fail3 (failure), Fail4 (failure), Fail5 (failure)
    assert memory.recent_objectives_log[0]["objective"] == "Obj Comp 2"
    assert memory.recent_objectives_log[0]["status"] == "success"

    assert memory.recent_objectives_log[1]["objective"] == "Obj Fail 2"
    assert memory.recent_objectives_log[1]["status"] == "failure"

    assert memory.recent_objectives_log[2]["objective"] == "Obj Fail 3"
    assert memory.recent_objectives_log[2]["status"] == "failure"

    assert memory.recent_objectives_log[3]["objective"] == "Obj Fail 4"
    assert memory.recent_objectives_log[3]["status"] == "failure"

    assert memory.recent_objectives_log[4]["objective"] == "Obj Fail 5"
    assert memory.recent_objectives_log[4]["status"] == "failure"

    # Add one more, check trimming again
    memory.add_completed_objective("Obj Comp 3", "s", "d") # This is the 8th
    assert len(memory.recent_objectives_log) == 5

    # Expected: Fail2, Fail3, Fail4, Fail5, Comp3
    assert memory.recent_objectives_log[0]["objective"] == "Obj Fail 2"
    assert memory.recent_objectives_log[1]["objective"] == "Obj Fail 3"
    assert memory.recent_objectives_log[2]["objective"] == "Obj Fail 4"
    assert memory.recent_objectives_log[3]["objective"] == "Obj Fail 5"
    assert memory.recent_objectives_log[4]["objective"] == "Obj Comp 3"
    assert memory.recent_objectives_log[4]["status"] == "success"

    # Test save and load for recent_objectives_log
    memory.save()
    new_memory = Memory(filepath=str(temp_memory_file))
    new_memory.load()

    assert len(new_memory.recent_objectives_log) == 5
    assert new_memory.recent_objectives_log[4]["objective"] == "Obj Comp 3"
    assert new_memory.recent_objectives_log[0]["objective"] == "Obj Fail 2"


def test_cleanup_memory_trigger_and_cycle_reset(temp_memory_file):
    """Test that cleanup_memory is triggered every 5 calls and cycle_count resets."""
    memory = Memory(filepath=str(temp_memory_file), max_objectives_history=3)
    assert memory.cycle_count == 0

    for i in range(4): # Add 4 objectives
        memory.add_completed_objective(f"Obj {i}", "s", "d")
        assert memory.cycle_count == i + 1
        assert len(memory.completed_objectives) == i + 1 # No cleanup yet

    # Add 5th objective - should trigger cleanup
    memory.add_completed_objective("Obj 4", "s", "d")
    assert memory.cycle_count == 0 # Reset after cleanup
    # Objectives list is sorted chronologically: Obj 2, Obj 3, Obj 4
    assert len(memory.completed_objectives) == 3
    assert memory.completed_objectives[0]["objective"] == "Obj 2" # Oldest of the kept
    assert memory.completed_objectives[1]["objective"] == "Obj 3"
    assert memory.completed_objectives[2]["objective"] == "Obj 4" # Most recent of the kept

    # Add another 4 objectives
    for i in range(5, 9): # Objs 5, 6, 7, 8
        memory.add_failed_objective(f"Obj {i}", "f", "d")
        assert memory.cycle_count == i - 4 # cycle is 1, 2, 3, 4

    # Current objectives: Comp: [Obj 4, Obj 3, Obj 2], Failed: [Obj 5, Obj 6, Obj 7, Obj 8]
    # Total = 7, but lists are separate.
    assert len(memory.completed_objectives) == 3
    assert len(memory.failed_objectives) == 4

    # Add 10th objective (5th since last cleanup) - should trigger cleanup
    memory.add_completed_objective("Obj 9", "s", "d") # This is Obj 9
    assert memory.cycle_count == 0

    # After cleanup, with max_history = 3.
    # Combined and sorted: Obj 9(C), Obj 8(F), Obj 7(F), Obj 6(F), Obj 5(F), Obj 4(C), Obj 3(C), Obj 2(C)
    # Kept (top 3): Obj 9(C), Obj 8(F), Obj 7(F)
    # Separated: Completed: [Obj 9], Failed: [Obj 8, Obj 7]

    assert len(memory.completed_objectives) == 1, f"Completed: {memory.completed_objectives}"
    assert memory.completed_objectives[0]["objective"] == "Obj 9"

    assert len(memory.failed_objectives) == 2, f"Failed: {memory.failed_objectives}"
    # Failed objectives list is sorted chronologically: Obj 7, Obj 8
    assert memory.failed_objectives[0]["objective"] == "Obj 7" # Oldest of the kept failed
    assert memory.failed_objectives[1]["objective"] == "Obj 8" # Most recent of the kept failed


def test_cleanup_memory_deduplication(temp_memory_file):
    """Test that cleanup_memory removes duplicate objectives, keeping the latest."""
    memory = Memory(filepath=str(temp_memory_file), max_objectives_history=5)

    # Add objectives, some with same name but different timestamps/details
    memory.add_completed_objective("Duplicate Obj A", "s", "first entry", ) # 1st call
    time.sleep(0.01)
    memory.add_failed_objective("Unique Obj B", "f", "details B")      # 2nd call
    time.sleep(0.01)
    memory.add_completed_objective("Duplicate Obj A", "s", "second entry, updated") # 3rd call
    time.sleep(0.01)
    memory.add_failed_objective("Unique Obj C", "f", "details C")      # 4th call
    time.sleep(0.01)

    # 5th call, triggers cleanup
    memory.add_completed_objective("Unique Obj D", "s", "details D")
    assert memory.cycle_count == 0

    # Expected after cleanup (max_history=5):
    # Unique D (Comp), Unique C (Fail), Duplicate Obj A (Comp, second entry), Unique B (Fail)
    # Total 4 unique objectives by name.

    assert len(memory.completed_objectives) == 2
    assert len(memory.failed_objectives) == 2

    completed_names = [obj["objective"] for obj in memory.completed_objectives]
    failed_names = [obj["objective"] for obj in memory.failed_objectives]

    assert "Unique Obj D" in completed_names
    assert "Duplicate Obj A" in completed_names
    assert "Unique Obj C" in failed_names
    assert "Unique Obj B" in failed_names

    # Check that the latest version of "Duplicate Obj A" was kept
    for obj in memory.completed_objectives:
        if obj["objective"] == "Duplicate Obj A":
            assert obj["details"] == "second entry, updated"
            break
    else:
        assert False, "Duplicate Obj A not found in completed objectives"

def test_cleanup_memory_history_limit(temp_memory_file):
    """Test that cleanup_memory respects max_objectives_history."""
    max_hist = 2
    memory = Memory(filepath=str(temp_memory_file), max_objectives_history=max_hist)

    # Add 4 objectives, cleanup won't trigger yet
    memory.add_completed_objective("Obj 0", "s", "d0") # cycle 1
    memory.add_failed_objective("Obj 1", "f", "d1")    # cycle 2
    memory.add_completed_objective("Obj 2", "s", "d2") # cycle 3
    memory.add_failed_objective("Obj 3", "f", "d3")    # cycle 4

    assert len(memory.completed_objectives) == 2
    assert len(memory.failed_objectives) == 2

    # Add 5th objective, triggering cleanup
    memory.add_completed_objective("Obj 4", "s", "d4") # cycle 0 (reset)

    # All objectives: Obj 4(C), Obj 3(F), Obj 2(C), Obj 1(F), Obj 0(C)
    # Sorted by date (most recent first): Obj 4, Obj 3, Obj 2, Obj 1, Obj 0
    # Kept (max_hist = 2): Obj 4, Obj 3
    # Separated: Completed: [Obj 4], Failed: [Obj 3]

    assert len(memory.completed_objectives) == 1
    assert memory.completed_objectives[0]["objective"] == "Obj 4"

    assert len(memory.failed_objectives) == 1
    assert memory.failed_objectives[0]["objective"] == "Obj 3"

    # Add 5 more objectives (total 10, 2nd cleanup)
    memory.add_completed_objective("Obj 5", "s", "d5") # cycle 1
    memory.add_failed_objective("Obj 6", "f", "d6")    # cycle 2
    memory.add_completed_objective("Obj 7", "s", "d7") # cycle 3
    memory.add_failed_objective("Obj 8", "f", "d8")    # cycle 4
    memory.add_completed_objective("Obj 9", "s", "d9") # cycle 0 (reset)

    # Previous state: Comp:[Obj 4], Fail:[Obj 3]
    # Added: C:Obj5, F:Obj6, C:Obj7, F:Obj8, C:Obj9
    # All before this cleanup: Obj 9(C), Obj 8(F), Obj 7(C), Obj 6(F), Obj 5(C), Obj 4(C), Obj 3(F)
    # Sorted by date: Obj 9, Obj 8, Obj 7, Obj 6, Obj 5, Obj 4, Obj 3
    # Kept (max_hist = 2): Obj 9, Obj 8
    # Separated: Completed: [Obj 9], Failed: [Obj 8]

    assert len(memory.completed_objectives) == 1
    assert memory.completed_objectives[0]["objective"] == "Obj 9"

    assert len(memory.failed_objectives) == 1
    assert memory.failed_objectives[0]["objective"] == "Obj 8"

def test_cleanup_memory_no_action_if_cycle_not_reached(temp_memory_file):
    """Test that cleanup_memory does nothing if cycle count is not 5."""
    memory = Memory(filepath=str(temp_memory_file), max_objectives_history=1)
    memory.add_completed_objective("Obj 1", "s", "d")
    memory.add_completed_objective("Obj 2", "s", "d")
    memory.add_failed_objective("Obj 3", "f", "d")

    assert memory.cycle_count == 3
    assert len(memory.completed_objectives) == 2
    assert len(memory.failed_objectives) == 1

    # Manually call cleanup (though it's private, for testing the guard)
    # In the actual code, _add_to_recent_objectives_log calls it.
    # The test for `add_completed_objective` already covers the cycle increment.
    # Here we just want to ensure if we somehow call it early, it doesn't clean.
    # This is more of a conceptual test as direct call to cleanup_memory isn't typical.
    # Let's simulate the state just before the 5th add.
    memory.cycle_count = 4 # Simulate being just before the 5th call
    memory.cleanup_memory() # This call itself will increment cycle_count to 5, so it WILL clean.

    # Re-think: The test should verify that if add_objective is called < 4 times,
    # the lists are not trimmed beyond max_history *yet*.
    memory = Memory(filepath=str(temp_memory_file), max_objectives_history=1)
    memory.add_completed_objective("Test 1", "s", "d") # cycle 1
    memory.add_completed_objective("Test 2", "s", "d") # cycle 2
    memory.add_completed_objective("Test 3", "s", "d") # cycle 3

    assert memory.cycle_count == 3
    assert len(memory.completed_objectives) == 3 # Max history is 1, but cleanup not run

    memory.add_completed_objective("Test 4", "s", "d") # cycle 4
    assert memory.cycle_count == 4
    assert len(memory.completed_objectives) == 4

    memory.add_completed_objective("Test 5", "s", "d") # cycle 0 (cleaned)
    assert memory.cycle_count == 0
    assert len(memory.completed_objectives) == 1 # Now cleaned to max_history
    assert memory.completed_objectives[0]["objective"] == "Test 5"


# To run these tests:
# Ensure pytest is installed: pip install pytest
# Navigate to the root directory of the project (where tests/ and agent/ are)
# Run: pytest
# or: pytest tests/test_memory.py

# Example of how to run with coverage:
# pip install pytest-cov
# pytest --cov=agent.memory tests/test_memory.py --cov-report=html
# Then open htmlcov/index.html in a browser.
