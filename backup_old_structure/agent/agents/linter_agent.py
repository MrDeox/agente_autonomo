import logging
import subprocess
import tempfile
import shutil
from pathlib import Path
from typing import Optional

import git

class LinterAgent:
    """
    An agent that uses a static linter (ruff) to find, fix, and safely propose
    code quality improvements.
    """
    def __init__(self, logger: logging.Logger):
        self.logger = logger

    def run_linter_and_propose_objective(self) -> Optional[str]:
        """
        Runs the ruff linter in a sandbox, generates a diff patch, and proposes
        an objective if changes were made.

        Returns:
            A string containing an objective to apply the linting fixes, or None if
            no changes were made.
        """
        self.logger.info("🧹 Linter Agent: Starting secure linting process...")

        # Create a temporary sandbox directory
        with tempfile.TemporaryDirectory(prefix="hephaestus_linter_") as sandbox_dir:
            sandbox_path = Path(sandbox_dir)
            project_root = Path(".")
            
            try:
                # Copy project to sandbox, ignoring git directory
                shutil.copytree(project_root, sandbox_path, dirs_exist_ok=True, ignore=shutil.ignore_patterns('.git'))
                self.logger.info(f"Linter Agent: Project copied to sandbox: {sandbox_path}")

                # Run ruff with --fix in the sandbox
                command = ['ruff', 'check', '--fix', '--exit-non-zero-on-fix', '.']
                result = subprocess.run(command, capture_output=True, text=True, cwd=sandbox_path)

                if result.returncode != 1:
                    self.logger.info("Linter Agent: No auto-fixable issues found by ruff.")
                    return None

                # Generate a diff patch
                repo = git.Repo(sandbox_path)
                repo.git.add(A=True) # Stage all changes made by ruff
                
                # Check if there are actual changes to diff
                if not repo.is_dirty():
                    self.logger.info("Linter Agent: Ruff indicated fixes, but no changes were detected by git.")
                    return None

                diff = repo.git.diff(repo.head.commit)

                if not diff:
                    self.logger.info("Linter Agent: No diff generated, no changes to propose.")
                    return None

                self.logger.info("Linter Agent: `ruff` found and fixed issues. Generating patch...")
                
                # Create a structured objective with the patch
                objective = f"""
[CHORE] Apply and validate automated linting fixes.

The LinterAgent (using ruff) has automatically fixed style and quality issues. Please apply and validate the following patch.

```diff
{diff}
```
"""
                return objective.strip()

            except FileNotFoundError:
                self.logger.error("Linter Agent: `ruff` or `git` command not found. Please ensure they are installed and in the PATH.")
                return None
            except Exception as e:
                self.logger.error(f"An unexpected error occurred during linting: {e}", exc_info=True)
                return None 