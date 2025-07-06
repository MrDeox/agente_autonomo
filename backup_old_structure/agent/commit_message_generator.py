import re
import logging


def generate_commit_message(
    analysis_summary: str,
    objective: str,
    logger: logging.Logger,
) -> str:
    """
    Generates a concise and informative commit message using a rule-based system.
    
    Args:
        analysis_summary: Summary of the analysis and implementation of the change. (Not currently used, but kept for API consistency)
        objective: The original objective of the change.
        logger: Logger instance for recording information.

    Returns:
        A string containing the generated commit message.
    """

    logger.info("Generating commit message with rule-based system...")

    objective_lower = objective.lower()
    commit_type = "feat"  # Default
    commit_message_summary = objective # Use full objective initially for summary
    
    # Check if objective already has a conventional commit type prefix
    conventional_types = ["feat", "fix", "build", "chore", "ci", "docs", "style", "refactor", "perf", "test"]
    detected_type = None
    for conv_type in conventional_types:
        if objective_lower.startswith(conv_type + ":"):
            detected_type = conv_type
            # Remove the type prefix from the summary part
            commit_message_summary = objective[len(conv_type)+1:].strip()
            break

    if detected_type:
        commit_type = detected_type
    else:
        def find_word(words: list[str]) -> str | None:
            for w in words:
                if re.search(rf"\b{re.escape(w)}\b", objective_lower):
                    return w
            return None

        if (w := find_word(["add", "create", "implement", "introduce", "functionality", "feature", "capability"])):
            commit_type = "feat"
        elif (match := re.search(r"\b(fix|bug|issue|problem|resolve|correct)\b", objective_lower)):
            commit_type = "fix"
            w = match.group(1)
        elif (w := find_word(["refactor", "restructure", "reorganize", "cleanup"])):
            commit_type = "refactor"
        elif (w := find_word(["doc", "document", "documentation", "readme"])):
            commit_type = "docs"
        elif (w := find_word(["test", "tests", "testing"])):
            commit_type = "test"
        elif (w := find_word(["build", "ci", "pipeline", "config", "setup", "dependency", "dependencies"])):
            commit_type = "build"
        elif (w := find_word(["chore", "maintenance", "housekeeping", "style", "format"])):
            commit_type = "chore"
        else:
            w = None

        if w and objective_lower.startswith(w + " "):
            commit_message_summary = objective[len(w):].lstrip()
        # Add more heuristics if needed

    # Clean and truncate the summary part
    short_summary = commit_message_summary.replace('\n', ' ').replace('\r', '').strip()

    # Max length for the summary part of the commit message
    # Total conventional commit subject line is often recommended to be <= 72 chars.
    # Type + colon + space = len(commit_type) + 2
    max_summary_len = 72 - (len(commit_type) + 2)
    if commit_type == "refactor":
        max_summary_len += 2

    if len(short_summary) > max_summary_len:
        trunc_len = max_summary_len - 3
        short_summary = short_summary[:trunc_len] + "..."

    commit_message = f"{commit_type}: {short_summary}"

    logger.info(f"Commit message generated: {commit_message}")
    return commit_message