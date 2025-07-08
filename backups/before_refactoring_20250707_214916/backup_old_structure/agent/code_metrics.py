# This module contains functions for code complexity analysis,
# pattern repetition detection, and quality score calculation.

from radon.visitors import ComplexityVisitor
from radon.metrics import h_visit
from radon.raw import analyze

def analyze_complexity(code_string: str) -> dict:
    """
    Analyzes the cyclomatic complexity and other metrics of the given Python code string using Radon.
    Returns a dictionary with overall complexity, and a list of specific issues.
    """
    try:
        # Analyze raw metrics (LOC, LLOC, SLOC, comments, multi-line strings, blank lines)
        raw_analysis = analyze(code_string)
        # print(f"DEBUG raw_analysis for code string starting with '{code_string[:30].replace('\n', '')}...': {raw_analysis}")

        # Analyze cyclomatic complexity
        visitor = ComplexityVisitor.from_code(code_string)

        functions_and_methods_details = []
        # visitor.blocks contains all functions, methods, and closures.
        # Let's print to see what visitor.blocks contains for simple_code
        # print("DEBUG: visitor.blocks content:")
        # for b in visitor.blocks:
        #     print(f"  Type: {type(b).__name__}, Name: {getattr(b, 'name', 'N/A')}, Classname: {getattr(b, 'classname', 'N/A')}, Complexity: {getattr(b, 'complexity', 'N/A')}")

        for block in visitor.blocks:
            # We only want to add actual functions or methods to our list, not class blocks themselves if Radon includes them here.
            # Radon's Function, Method, Closure blocks are what we need.
            if type(block).__name__ in ('Function', 'Method', 'Closure'):
                if hasattr(block, 'name') and hasattr(block, 'complexity'):
                    name_to_report = block.name
                    if hasattr(block, 'classname') and block.classname:
                        name_to_report = f"{block.classname}.{block.name}"

                    functions_and_methods_details.append({
                        "name": name_to_report,
                        "type": type(block).__name__,
                        "lineno": block.lineno,
                        "col_offset": block.col_offset,
                        "complexity": block.complexity,
                        "rank": block.rank() if hasattr(block, 'rank') else 'N/A',
                    })

        # Extract class-specific details including their methods separately if needed for structure
        classes_details = []
        for cls_item in visitor.classes:
            method_details_for_class = []
            for method_item in cls_item.methods:
                method_details_for_class.append({
                    "name": method_item.name, # Method name is fine here, class context is from parent
                    "lineno": method_item.lineno,
                    "complexity": method_item.complexity,
                    "rank": method_item.rank() if hasattr(method_item, 'rank') else 'N/A',
                })
            classes_details.append({
                "name": cls_item.name,
                "lineno": cls_item.lineno,
                "complexity": cls_item.real_complexity, # Sum of methods' complexities
                "rank": cls_item.rank() if hasattr(cls_item, 'rank') else 'N/A',
                "methods": method_details_for_class
            })

        total_complexity = sum(block.complexity for block in visitor.blocks if hasattr(block, 'complexity'))

        # Halstead metrics (optional, can be intensive)
        # halstead_analysis = h_visit(code_string)

        return {
            "overall_cyclomatic_complexity": total_complexity,
            "loc": raw_analysis.loc,
            "lloc": raw_analysis.lloc,
            "sloc": raw_analysis.sloc,
            "comments": raw_analysis.comments,
            "multi_line_strings": raw_analysis.multi,
            "blank_lines": raw_analysis.blank,
            "functions": functions_and_methods_details, # Now includes all functions and methods
            "classes": classes_details, # Separate details for classes and their methods
            # "halstead": halstead_analysis.total._asdict() if halstead_analysis else None
        }
    except Exception as e:
        # Log error or handle gracefully
        # Ensure the error message is more informative if possible
        error_message = f"Radon analysis failed: {type(e).__name__} - {str(e)}"
        return {
            "error": str(e),
            "overall_cyclomatic_complexity": -1,
            "functions": [],
            "classes": []
        }


def calculate_quality_score(complexity_report: dict, duplication_report: list) -> float:
    """
    Calculates a quality score based on complexity, duplication, and other code metrics.

    The scoring is based on penalties deducted from a starting score of 100.
    - Cyclomatic Complexity:
        - Functions/methods with complexity > 10 incur penalties.
        - Higher penalties for complexity > 20.
    - Code Duplication:
        - Each duplicated block incurs a penalty.
        - Larger duplicated blocks might incur higher penalties (currently per block).
    - Code Size (LLOC - Logical Lines of Code):
        - Very large files might receive a small penalty (encouraging modularity).
    - Comment Density:
        - Very low comment-to-code ratio might incur a small penalty.
    """
    base_score = 100.0
    total_penalty = 0.0
    # print(f"Initial score: {base_score}, Initial penalty: {total_penalty}")
    # print(f"Complexity Report Received: {complexity_report}")
    # print(f"Duplication Report Received: {duplication_report}")


    # 1. Cyclomatic Complexity Penalties
    if complexity_report and not complexity_report.get("error"):
        # Penalize complex functions
        # print("Evaluating function complexity penalties...")
        for func in complexity_report.get("functions", []):
            # print(f"  Function: {func.get('name')}, Complexity: {func.get('complexity')}")
            if func.get("complexity", 0) > 20:
                total_penalty += 10  # Severe penalty
                # print(f"    Penalty +10 for {func.get('name')} (complexity > 20). Current total penalty: {total_penalty}")
            elif func.get("complexity", 0) > 10:
                total_penalty += 5   # Moderate penalty
                # print(f"    Penalty +5 for {func.get('name')} (complexity > 10). Current total penalty: {total_penalty}")

        # Penalize complex classes (based on sum of method complexities)
        # print("Evaluating class complexity penalties...")
        for cls in complexity_report.get("classes", []):
            # print(f"  Class: {cls.get('name')}, Complexity: {cls.get('complexity')}")
            if cls.get("complexity", 0) > 50:
                total_penalty += 15
                # print(f"    Penalty +15 for {cls.get('name')} (class complexity > 50). Current total penalty: {total_penalty}")
            elif cls.get("complexity", 0) > 25:
                total_penalty += 7
                # print(f"    Penalty +7 for {cls.get('name')} (class complexity > 25). Current total penalty: {total_penalty}")

    # 2. Code Duplication Penalties
    if duplication_report:
        # print("Evaluating duplication penalties...")
        for dupe_block in duplication_report:
            penalty_per_block = 5 + (dupe_block.get("block_length_lines", 0) // 5)
            # Penalize for each *extra* occurrence beyond the first one.
            num_extra_occurrences = dupe_block.get("num_occurrences", 1) - 1
            if num_extra_occurrences > 0:
                total_penalty += penalty_per_block * num_extra_occurrences
            # print(f"  Duplication block: length {dupe_block.get('block_length_lines',0)}, occurrences {dupe_block.get('num_occurrences',1)}. Penalty for this block: {penalty_per_block * num_extra_occurrences}. Current total penalty: {total_penalty}")

    # 3. Code Size Penalties (using LLOC from complexity_report)
    if complexity_report and not complexity_report.get("error"):
        lloc = complexity_report.get("lloc", 0)
        # print(f"Evaluating LLOC penalty: LLOC = {lloc}")
        if lloc > 1000: # Very large file
            total_penalty += 10
            # print(f"    Penalty +10 for LLOC > 1000. Current total penalty: {total_penalty}")
        elif lloc > 500: # Large file
            total_penalty += 5
            # print(f"    Penalty +5 for LLOC > 500. Current total penalty: {total_penalty}")

    # 4. Comment Density Penalties (using comments and LLOC from complexity_report)
    if complexity_report and not complexity_report.get("error"):
        comments = complexity_report.get("comments", 0)
        lloc = complexity_report.get("lloc", 0)
        comment_ratio = 0.0
        if lloc > 0 :
            comment_ratio = comments / lloc
        # print(f"Evaluating comment density: comments = {comments}, lloc = {lloc}, ratio = {comment_ratio:.4f}")

        # Penalize more strictly for very low comments first
        if lloc > 20 and comment_ratio < 0.01 :
            total_penalty += 10
            # print(f"    Penalty +10 for comment ratio < 0.01 and LLOC > 20. Current total penalty: {total_penalty}")
        elif lloc > 50 and comment_ratio < 0.05:
            total_penalty += 5
            # print(f"    Penalty +5 for comment ratio < 0.05 and LLOC > 50. Current total penalty: {total_penalty}")

    final_score = max(0.0, base_score - total_penalty)
    # print(f"Final score calculation: max(0.0, {base_score} - {total_penalty}) = {final_score}")
    return final_score

# Helper for duplication detection
def _get_code_lines(code_string: str, strip_comments_blanks: bool = True) -> list[tuple[int, str]]:
    """Returns a list of (original_line_number, line_content) tuples."""
    lines = []
    for i, line in enumerate(code_string.splitlines()):
        processed_line = line.strip()
        if strip_comments_blanks:
            if not processed_line or processed_line.startswith("#"):
                continue
        lines.append((i + 1, processed_line))
    return lines

def _find_duplicates_for_block(block_to_check: list[str], all_lines: list[tuple[int, str]], start_index: int, min_lines: int) -> list[tuple[int, int]]:
    """Finds occurrences of block_to_check in all_lines, starting after start_index."""
    duplicates = []
    block_len = len(block_to_check)
    if block_len < min_lines:
        return []

    for i in range(start_index, len(all_lines) - block_len + 1):
        current_block_lines = [line_content for _, line_content in all_lines[i : i + block_len]]
        if current_block_lines == block_to_check:
            duplicates.append((all_lines[i][0], all_lines[i + block_len - 1][0]))
    return duplicates


def detect_code_duplication(code_string: str, min_lines: int = 4, strip_comments_and_blanks: bool = True) -> list[dict]:
    """
    Detects duplicated code blocks in the given Python code string.
    A simple line-by-line comparison approach. More sophisticated methods exist (e.g., AST-based, token-based).

    Args:
        code_string (str): The source code to analyze.
        min_lines (int): The minimum number of consecutive lines to be considered a duplicate block.
        strip_comments_and_blanks (bool): If True, empty lines and comments are ignored.

    Returns:
        list[dict]: A list of dictionaries, where each dictionary represents a duplicated block
                    and contains 'lines' (the duplicated lines) and 'occurrences' (list of [start_line, end_line] tuples).
    """
    original_lines_with_numbers = code_string.splitlines()

    # Use processed lines for detection, but original line numbers for reporting
    processed_lines_for_detection = []
    line_map_processed_to_original = [] # Stores original line number for each processed line

    for i, line_text in enumerate(original_lines_with_numbers):
        original_line_num = i + 1
        stripped_line = line_text.strip()
        if strip_comments_and_blanks:
            if not stripped_line or stripped_line.startswith("#"):
                continue
        processed_lines_for_detection.append(stripped_line)
        line_map_processed_to_original.append(original_line_num)

    if not processed_lines_for_detection:
        return []

    num_processed_lines = len(processed_lines_for_detection)
    found_duplicates_info = []
    checked_blocks = set() # To avoid re-reporting subsets of already found larger duplicates

    for i in range(num_processed_lines - min_lines + 1):
        for length in range(min_lines, num_processed_lines - i + 1):
            current_block_processed_lines = tuple(processed_lines_for_detection[i : i + length])

            # Create a unique identifier for the block content to avoid re-checking
            block_content_id = hash(current_block_processed_lines)
            if block_content_id in checked_blocks:
                continue

            # Get original line numbers for the first occurrence
            original_start_line_first_occurrence = line_map_processed_to_original[i]
            original_end_line_first_occurrence = line_map_processed_to_original[i + length - 1]

            occurrences = [(original_start_line_first_occurrence, original_end_line_first_occurrence)]

            # Search for this block starting from the line after the current block ends
            # to avoid self-comparison and redundant checks.
            for j in range(i + length, num_processed_lines - length + 1):
                next_block_processed_lines = tuple(processed_lines_for_detection[j : j + length])
                if next_block_processed_lines == current_block_processed_lines:
                    original_start_line_next_occurrence = line_map_processed_to_original[j]
                    original_end_line_next_occurrence = line_map_processed_to_original[j + length - 1]

                    # Check if this new occurrence is already part of a reported duplicate
                    # This is a simple check; more robust would be interval overlap.
                    is_new_occurrence_covered = False
                    for dupe_info in found_duplicates_info:
                        for occ_start, occ_end in dupe_info["occurrences"]:
                            # If the new found block is entirely within an already reported occurrence for the same content
                            if dupe_info["lines_content_hash"] == block_content_id and \
                               original_start_line_next_occurrence >= occ_start and \
                               original_end_line_next_occurrence <= occ_end:
                                is_new_occurrence_covered = True
                                break
                        if is_new_occurrence_covered:
                            break

                    if not is_new_occurrence_covered:
                        occurrences.append((original_start_line_next_occurrence, original_end_line_next_occurrence))

            if len(occurrences) > 1:
                # Store the actual lines from the original code string for reporting
                # This uses the line numbers of the *first* occurrence to get the content.
                actual_duplicated_lines_content = original_lines_with_numbers[
                    original_start_line_first_occurrence - 1 : original_end_line_first_occurrence
                ]

                found_duplicates_info.append({
                    "lines_content": "\n".join(actual_duplicated_lines_content),
                    "lines_content_hash": block_content_id, # For internal checks
                    "occurrences": sorted(list(set(occurrences))), # Ensure unique occurrences
                    "num_occurrences": len(occurrences),
                    "block_length_lines": length
                })
                # Add this block and all its sub-blocks to checked_blocks to avoid redundant reports
                # This is a simplification. A more robust way would be to mark ranges.
                for k in range(length - min_lines + 1):
                    sub_block = tuple(current_block_processed_lines[k : k + min_lines])
                    checked_blocks.add(hash(sub_block))
                checked_blocks.add(block_content_id)


    # Filter out duplicates that are entirely contained within other, larger reported duplicates
    # This is a common post-processing step for duplication detectors.
    # For simplicity, we'll rely on the `checked_blocks` logic during detection,
    # but a more robust filtering could be done here by comparing occurrence ranges.
    # A simple filter: if two duplicate reports have the exact same set of occurrences, keep the one with more lines.
    # Or, if one report's occurrences are a subset of another's, and content is related, be careful.

    # For now, the current logic might over-report if not careful with checked_blocks.
    # The key is that `checked_blocks` should ideally mark ranges, not just content hashes of the *first* identified block.
    # However, the current implementation is a good starting point.

    # Let's refine: only add to found_duplicates_info if it's not a sub-block of an already found larger duplicate
    # This is tricky with the current loop structure. The `checked_blocks` helps, but might not be perfect.
    # A more robust approach would be to find all maximal duplicates.

    # The current approach is greedy and finds the first occurrence then searches for others.
    # It might report overlapping duplicates. Example:
    # A B C D E F
    # A B C
    #       C D E
    # If min_lines=3, it might find "A B C". Then, if min_lines=3, it might find "C D E".
    # If min_lines=2, it might find "A B", "B C", "C D", "D E", "E F".

    # The current implementation prioritizes finding *any* duplication.
    # Refinement can be added to merge overlapping/subsumed duplicates.
    # For now, we will return what's found, understanding there might be overlaps.

    return found_duplicates_info


if __name__ == '__main__':
    sample_code = """
def example_function(a, b):
    if a > b:
        for i in range(a):
            print(i)
    else:
        for j in range(b):
            print(j)
    return a + b

def another_function(x):
    if x > 0:
        for i in range(x): # Duplicated loop structure
            print(i)
    return x * 2
"""
    complexity = analyze_complexity(sample_code)
    print(f"Complexity Report: {complexity}")

    duplication = detect_code_duplication(sample_code)
    print(f"Duplication Report: {duplication}")

    quality_score = calculate_quality_score(complexity, duplication)
    print(f"Quality Score: {quality_score}")