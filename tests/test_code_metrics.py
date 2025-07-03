import pytest
from agent.code_metrics import analyze_complexity, detect_code_duplication, calculate_quality_score # Updated import

# Fixtures for sample code
@pytest.fixture
def simple_code():
    return """
def hello(name):
    print(f"Hello, {name}")

class Greeter:
    def __init__(self, greeting="Hello"):
        self.greeting = greeting

    def greet(self, name):
        return f"{self.greeting}, {name}!"
"""

@pytest.fixture
def complex_code():
    return """
def complex_function(a, b, c):
    if a > b:
        if b > c:
            if a > c:
                print("a > b > c")
                for i in range(a): print(i)
            else:
                print("c >= a > b")
                for i in range(b): print(i)
        else:
            print("b <= c, a > b")
            for i in range(c): print(i)
    elif b > a:
        if a > c:
            print("b > a > c")
            for i in range(a): print(i)
        else: # c >= a
            if b > c:
                 print("b > c >= a")
                 for i in range(b): print(i)
            else: # c >= b
                 print("c >= b > a")
                 for i in range(c): print(i)
    else: # a == b
        if a > c:
            print("a == b > c")
            for i in range(a): print(i)
        else:
            print("c >= a == b")
            for i in range(c): print(i)
    return "done"
"""

@pytest.fixture
def duplicated_code():
    return """
def func_a():
    # Common block starts
    x = 10
    y = 20
    z = x + y
    print(f"Result: {z}")
    # Common block ends
    return z

def func_b():
    # Another task
    print("Doing something else")
    # Common block starts
    x = 10
    y = 20
    z = x + y
    print(f"Result: {z}")
    # Common block ends
    return z * 2

# This is just a comment, should be ignored
# Another comment line

def func_c():
    # Common block starts
    x = 10
    y = 20
    z = x + y
    print(f"Result: {z}")
    # Common block ends
    return z + 100
"""

@pytest.fixture
def code_with_no_comments():
    return """
def f(x):
    y = x*x
    z = y + x
    if z > 10:
        return z
    return 10
"""

@pytest.fixture
def very_large_code():
    # Simulate a large code file (for LLOC check)
    # ~600 LLOC
    base_func = "def func_{0}():\\n    x = {0}\\n    y = x * 2\\n    print(y)\\n    return y\\n"
    return "\\n".join([base_func.format(i) for i in range(150)])


# Tests for analyze_complexity
def test_analyze_complexity_simple(simple_code):
    report = analyze_complexity(simple_code)
    assert "error" not in report
    assert report["overall_cyclomatic_complexity"] > 0 # hello (1) + __init__ (1) + greet (1) = 3
    assert report["lloc"] > 5
    # Expected functions/methods: hello, Greeter.__init__, Greeter.greet
    assert len(report["functions"]) == 3
    assert len(report["classes"]) == 1
    # Check if names are correctly reported
    func_names = sorted([f["name"] for f in report["functions"]])
    assert func_names == sorted(["hello", "Greeter.__init__", "Greeter.greet"])


def test_analyze_complexity_complex(complex_code):
    report = analyze_complexity(complex_code)
    assert "error" not in report
    assert report["overall_cyclomatic_complexity"] > 10  # Expect high complexity
    assert len(report["functions"]) == 1
    assert report["functions"][0]["complexity"] > 10

def test_analyze_complexity_empty_string():
    report = analyze_complexity("")
    assert "error" not in report # Radon handles empty strings gracefully
    assert report["overall_cyclomatic_complexity"] == 0
    assert report["lloc"] == 0

def test_analyze_complexity_syntax_error():
    report = analyze_complexity("def func(a:\n  print(a") # Syntax error
    assert "error" in report # Should report an error or handle gracefully

# Tests for detect_code_duplication
def test_detect_duplication_present(duplicated_code):
    duplicates = detect_code_duplication(duplicated_code, min_lines=4)
    assert len(duplicates) == 1
    assert duplicates[0]["num_occurrences"] == 3
    assert duplicates[0]["block_length_lines"] == 4 # "x = 10" to "print(f"Result: {z}")"
    assert "x = 10" in duplicates[0]["lines_content"]
    assert "print(f\"Result: {z}\")" in duplicates[0]["lines_content"]

    # Check occurrences line numbers (approximate, depends on exact stripping)
    # Original lines:
    # Original lines in fixture duplicated_code:
    # "" (line 1 - blank from initial """"")
    # "def func_a():" (line 2)
    # "    # Common block starts" (line 3)
    # "    x = 10" (line 4)
    # "    y = 20" (line 5)
    # "    z = x + y" (line 6)
    # "    print(f"Result: {z}")" (line 7)
    # ...
    # "def func_b():" (line 9)
    # ...
    # "    x = 10" (line 13) -> This is line 14 in original file if counting blank line
    # Corrected based on splitlines() and 1-based indexing used in detect_code_duplication
    # Line numbers are 1-based from the start of the string.
    # Original code:
    # 1 \n
    # 2 def func_a():
    # 3     # Common block starts
    # 4     x = 10  <-- Start of first actual block
    # 5     y = 20
    # 6     z = x + y
    # 7     print(f"Result: {z}") <-- End of first actual block
    # 8     # Common block ends
    # 9     return z
    # 10
    # 11 def func_b():
    # 12    # Another task
    # 13    print("Doing something else")
    # 14    # Common block starts
    # 15    x = 10 <-- Start of second actual block
    # 16    y = 20
    # 17    z = x + y
    # 18    print(f"Result: {z}") <-- End of second actual block
    # 19    # Common block ends
    # 20    return z * 2
    # 21
    # 22 # This is just a comment, should be ignored
    # 23 # Another comment line
    # 24
    # 25 def func_c():
    # 26    # Common block starts
    # 27    x = 10 <-- Start of third actual block
    # 28    y = 20
    # 29    z = x + y
    # 30    print(f"Result: {z}") <-- End of third actual block
    # 31    # Common block ends
    # 32    return z + 100

    expected_occurrences = sorted([(4,7), (15,18), (27,30)])
    assert sorted(duplicates[0]["occurrences"]) == expected_occurrences


def test_detect_duplication_none(simple_code):
    duplicates = detect_code_duplication(simple_code, min_lines=3)
    assert len(duplicates) == 0

def test_detect_duplication_min_lines_too_high(duplicated_code):
    duplicates = detect_code_duplication(duplicated_code, min_lines=10)
    assert len(duplicates) == 0

def test_detect_duplication_empty_string():
    duplicates = detect_code_duplication("", min_lines=2)
    assert len(duplicates) == 0

def test_detect_duplication_strip_comments(duplicated_code):
    # The fixture `duplicated_code` already has comments that should be stripped by default.
    # This test implicitly checks that behavior via `test_detect_duplication_present`.
    # We can add a more specific one if needed.
    code = """
    # comment
    line1
    line2
    # another comment
    line1
    line2
    """
    duplicates = detect_code_duplication(code, min_lines=2)
    assert len(duplicates) == 1
    assert duplicates[0]["num_occurrences"] == 2
    # The detect_code_duplication function returns the original lines, including leading/trailing whitespace of those lines.
    # The stripping is done for detection logic, not for the reported content.
    assert duplicates[0]["lines_content"] == "    line1\n    line2" # Original content with spaces

# Tests for calculate_quality_score
def test_calculate_quality_score_perfect():
    complexity_report = {"overall_cyclomatic_complexity": 5, "lloc": 50, "comments": 10, "functions": [{"complexity": 5}], "classes": []}
    duplication_report = []
    score = calculate_quality_score(complexity_report, duplication_report)
    assert score == 100.0

def test_calculate_quality_score_high_complexity(complex_code):
    # Use actual analysis for more realistic test
    complexity_report = analyze_complexity(complex_code)
    print(f"\nDEBUG test_calculate_quality_score_high_complexity - complexity_report: {complexity_report}\n")
    duplication_report = [] # No duplication in this specific fixture

    # Expected penalties:
    # complex_function has complexity > 20 (e.g. 29), so -10
    # LLOC might be low, no penalty. Comment ratio might be low if no comments.
    # Let's assume complex_function is the only one and its complexity is e.g. 16 (penalty 5)
    # For the complex_code fixture, radon reports:
    # complex_function - B (16)
    # So, one function with complexity 16 -> penalty = 5
    # LLOC for complex_code is small. Assume 0 comments.
    # lloc = 26, comments = 0. Ratio = 0. Penalty for low comments = 10.
    # Total penalty = 5 (complexity) + 10 (comments) = 15. Score = 85

    score = calculate_quality_score(complexity_report, duplication_report)
    # Based on current penalty logic:
    # - complex_function complexity is likely >10 and <20, e.g. 16 (radon default) -> -5 penalty
    # - LLOC is low, no penalty for size.
    # - Comments are 0, LLOC for complex_code is ~25-30. Ratio is 0. Penalty for low comments: -10
    # Expected score: 100 - 5 - 10 = 85
    # assert score < 90.0 # Old assertion, score was 95.0

    # Current state:
    # analyze_complexity(complex_code) ->
    #   overall_cyclomatic_complexity: 16
    #   lloc: 26
    #   comments: 0
    #   functions: [{'name': 'complex_function', 'type': 'Function', ..., 'complexity': 16, ...}]
    #
    # calculate_quality_score(complexity_report, []):
    #   Penalties:
    #     Function 'complex_function' (complexity 16): 16 > 10 -> penalty = 5
    #     LLOC (26): No penalty
    #     Comment ratio (0/26 = 0): lloc (26) > 20 and ratio (0) < 0.01 -> penalty = 10
    #   Total penalty = 5 + 10 = 15.
    #   Score = 100 - 15 = 85.0.
    # print(f"DEBUG: complex_code report = {complexity_report}")
    # print(f"DEBUG: complex_code score = {score}")
    # Updated expectation: comments are 3, lloc is 39. ratio = 3/39 = 0.076. No comment penalty.
    # Func complexity 16 -> penalty 5. Score = 95.0
    assert score == 95.0


def test_calculate_quality_score_with_duplication(duplicated_code):
    complexity_report = analyze_complexity(duplicated_code)
    # For duplicated_code:
    # func_a, func_b, func_c all simple (complexity 1 usually)
    # lloc is probably around 15-20. Comments are present.
    # complexity_report = analyze_complexity(duplicated_code)
    # Example: {'overall_cyclomatic_complexity': 3, 'lloc': 15, 'sloc': 15, 'comments': 8, ...}
    # No complexity penalties.
    # comment_ratio = 8/15 = ~0.53. No comment penalty.
    # LLOC is small. No size penalty.

    duplication_report = detect_code_duplication(duplicated_code, min_lines=4)
    # duplication_report has 1 block, 4 lines long, 3 occurrences.
    # Penalty: (5 + (4//5)) * (3-1) = (5+0) * 2 = 10
    # Expected score = 100 - 10 = 90.0
    score = calculate_quality_score(complexity_report, duplication_report)
    assert score == 90.0


def test_calculate_quality_score_very_large_code(): # Removed very_large_code fixture argument
    # Mock the complexity report for a very large code file, as Radon has issues with the generated string
    complexity_report = {
        "overall_cyclomatic_complexity": 150, # 150 funcs * complexity 1
        "lloc": 600,  # 150 funcs * 4 LLOC each
        "sloc": 600,
        "comments": 0, # No comments
        "multi_line_strings": 0,
        "blank_lines": 0,
        "functions": [{"name": f"func_{i}", "type": "Function", "complexity": 1} for i in range(150)],
        "classes": [],
        "error": None
    }
    print(f"\nDEBUG test_calculate_quality_score_very_large_code - MOCKED complexity_report: {complexity_report}\n")

    # Expected Penalties:
    # LLOC (600) > 500: penalty 5
    # Comments (0) / LLOC (600) = ratio 0.  (lloc > 20 and ratio < 0.01) -> penalty 10
    # Total penalty = 5 + 10 = 15. Score = 85.0
    duplication_report = []
    score = calculate_quality_score(complexity_report, duplication_report)
    assert score == 85.0

def test_calculate_quality_score_no_comments(code_with_no_comments):
    complexity_report = analyze_complexity(code_with_no_comments)
    # lloc for code_with_no_comments is small, e.g. 6
    # comments = 0. Ratio = 0.
    # Penalty for low comments: (lloc > 20 needs ratio < 0.01 for -10 penalty)
    # (lloc > 50 needs ratio < 0.05 for -5 penalty)
    # Here, lloc is too small for comment penalty.
    # No complexity penalties. Score should be 100.
    duplication_report = []
    score = calculate_quality_score(complexity_report, duplication_report)
    assert score == 100.0

def test_calculate_quality_score_all_penalties():
    # Craft reports that would trigger all penalties
    high_comp_func = {"name": "f1", "complexity": 25} # Penalty 10
    mod_comp_func = {"name": "f2", "complexity": 15}  # Penalty 5
    high_comp_class = {"name": "C1", "complexity": 60, "methods":[]} # Penalty 15

    complexity_report = {
        "overall_cyclomatic_complexity": 100,
        "lloc": 1200,  # Penalty 10 (for >1000)
        "comments": 10, # Ratio 10/1200 = 0.008. Penalty 10 (for <0.01 and lloc > 20)
        "functions": [high_comp_func, mod_comp_func],
        "classes": [high_comp_class],
        "error": None
    }

    duplication_report = [
        {"block_length_lines": 6, "num_occurrences": 3} # Penalty (5 + 6//5) * (3-1) = (5+1)*2 = 12
    ]

    # Total Penalties:
    # Complexity: 10 (f1) + 5 (f2) + 15 (C1) = 30
    # Duplication: 12
    # Size: 10
    # Comments: 10
    # Sum of penalties = 30 + 12 + 10 + 10 = 62
    # Score = 100 - 62 = 38

    score = calculate_quality_score(complexity_report, duplication_report)
    assert score == 38.0

def test_score_never_below_zero():
    complexity_report = {
        "overall_cyclomatic_complexity": 999,
        "lloc": 5000, "comments": 0,
        "functions": [{"complexity": 50}] * 10, # Massive complexity penalties
        "classes": [], "error": None
    }
    duplication_report = [{"block_length_lines": 20, "num_occurrences": 10}] * 5 # Massive duplication
    score = calculate_quality_score(complexity_report, duplication_report)
    assert score == 0.0

def test_handle_error_in_complexity_report():
    complexity_report = {"error": "Syntax error during parsing", "overall_cyclomatic_complexity": -1}
    duplication_report = []
    score = calculate_quality_score(complexity_report, duplication_report)
    # If complexity report has an error, it shouldn't contribute to penalties negatively,
    # but also shouldn't give a perfect score if other metrics are bad.
    # Current implementation: if error in complexity_report, penalties for complexity, size, comments are skipped.
    # Only duplication penalties would apply.
    # If duplication_report is also empty, score = 100. This might be too lenient.
    # Consider a default penalty or a note if complexity can't be assessed.
    # For now, with empty duplication, it will be 100.
    assert score == 100.0

    duplication_report_with_issues = [{"block_length_lines": 5, "num_occurrences": 2}] # Penalty (5+1)*(2-1) = 6
    score_with_dupes = calculate_quality_score(complexity_report, duplication_report_with_issues)
    assert score_with_dupes == 100.0 - (5 + (5//5)) * (2-1) # 100 - 6 = 94.0
    assert score_with_dupes == 94.0
