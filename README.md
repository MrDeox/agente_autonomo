# Hephaestus Agent

Autonomous AI agent for software development.

*For more detailed documentation in Portuguese, please see the `MANIFESTO.md` and other `.md` files in this repository.*

## Quick Start

1.  **Clone the repository:**
    Clone your local or remote repository. For example:
    ```bash
    git clone [URL_DO_SEU_REPOSITORIO]
    cd hephaestus-agent
    ```
2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
3.  **Set up your API Key:**
    Set the `OPENROUTER_API_KEY` environment variable. You can add it to a `.env` file in the project root:
    ```
    OPENROUTER_API_KEY="your_openrouter_api_key_here"
    ```
    Or export it in your terminal session:
    ```bash
    export OPENROUTER_API_KEY="your_openrouter_api_key_here"
    ```
4.  **Configure the Agent (Optional):**
    Review and optionally adjust `hephaestus_config.json` for model selection, validation strategies, and other runtime settings. For example, to focus on a specific objective, you might set an initial objective (though typically objectives are self-generated based on documents like `MANIFESTO.md` or `ROADMAP.md` in more advanced use).

5.  **Run the agent:**
    ```bash
    python main.py
    ```
    The agent will start its operational cycle, analyzing the project, potentially generating a new objective if none is set, and attempting to achieve it.

## Illustrative Usage Example

Let's imagine you want Hephaestus to add a new utility function to `agent/utils/llm_client.py`.

**1. Defining an Objective (Conceptual):**

While Hephaestus often generates its own objectives, you could conceptually guide it or have an initial objective in mind. For this example, let's say the objective is:

*"Create a new utility function in `agent/utils/llm_client.py` called `estimate_token_count` that takes a string and returns an estimated token count (e.g., by words / 0.75). Add a basic test for this function in a new test file `tests/agent/utils/test_llm_client_extra.py`."*

**2. Agent's Approach (Simplified):**

-   **Analysis:** Hephaestus would analyze `agent/utils/llm_client.py` and the `tests/` directory.
-   **Planning:** It would determine the changes needed:
    -   Add the `estimate_token_count` function to `llm_client.py`.
    -   Create `tests/agent/utils/test_llm_client_extra.py`.
    -   Write one or more test cases for `estimate_token_count` within the new test file.
-   **Code Generation:** The `ArchitectAgent` would generate the Python code for the new function and the new test file.
-   **Validation:**
    -   `SyntaxValidator` would check the new code for syntax errors.
    -   `PytestNewFileValidator` (or a similar strategy) would run `pytest` on the newly created test file to ensure the new tests pass and cover the new function.
-   **Patch Application:** If validation is successful, the changes are written to disk.
-   **Committing (if git integration is fully active for this):** A commit message would be generated and the changes committed.

**3. Configuration (`hephaestus_config.json`):**

No specific changes to `hephaestus_config.json` would necessarily be required for this specific task if default models and strategies are suitable. The agent would use a strategy like `CREATE_NEW_TEST_FILE_STRATEGY` or similar when it detects a new test file creation task.

**4. Running the Agent:**

```bash
python main.py
```

The agent would then proceed through its cycles, logging its progress in `hephaestus.log`. You would monitor this log to see its actions and any potential errors.

This is a simplified illustration. The agent's actual internal reasoning, patch generation, and validation steps can be quite detailed.

## Features

- Autonomous code generation and modification
- Project analysis and documentation
- Self-improvement capabilities
- Internet search via `web_search` helper

## Configuration

See `hephaestus_config.json` for available options.

## Web Search Helper

The `web_search` helper provides quick internet lookup using DuckDuckGo's instant answer API. No API key is required, but DuckDuckGo imposes request rate limits. Excessive queries may lead to temporary blocking, so keep usage moderate.

```python
from agent.tool_executor import web_search

success, results = web_search("python unit testing")
if success:
    print(results)
```

## Testing

Install dependencies and run the test suite with [pytest](https://docs.pytest.org/):

```bash
pip install -r requirements.txt
pytest
```

Ensure the `OPENROUTER_API_KEY` variable is set when executing tests, as many
tests rely on its presence.

## Troubleshooting

Check `hephaestus.log` for detailed execution logs.

## Project Structure Overview

The project is primarily organized into two main directories:

- **`agent/`**: Contains the core logic of the Hephaestus agent.
    - `brain.py`: Decision-making and LLM interactions.
    - `cycle_runner.py`: Manages the agent's operational cycles.
    - `tool_executor.py`: Executes tools like `pytest` and `web_search`.
    - `project_scanner.py`: Analyzes the project structure and code.
    - `patch_applicator.py`: Applies code modifications.
    - `validation_steps/`: Various steps for validating changes (syntax, tests, etc.).
    - `utils/`: Utility functions, including LLM client.
- **`tests/`**: Contains all tests for the agent, mirroring the `agent/` structure.

Key files in the root directory:
- `main.py`: Entry point to run the agent.
- `hephaestus_config.json`: Main configuration for the agent.
- `AGENTS.md`: A summary of the project's code structure and internal APIs (mostly in Portuguese).
- `MANIFESTO.md`: The project's principles and high-level architecture (in Portuguese).
- `ROADMAP.md`: The development roadmap for new features (in Portuguese).

## Contributing

Contributions are welcome! We are working on a `CONTRIBUTING.md` file with detailed guidelines. In the meantime:

1.  **Fork the Repository:** If you are working with a remote Git server, fork the main repository first. For local development, you can skip this step.
2.  **Clone Your Fork/Repository:**
    Clone your fork or your primary local repository to your development machine.
    ```bash
    git clone [URL_DO_SEU_FORK_OU_REPOSITORIO_PRINCIPAL]
    cd hephaestus-agent
    ```
3.  **Create a Feature Branch:**
    ```bash
    git checkout -b my-new-feature
    ```
4.  **Make Your Changes:** Implement your feature or bug fix.
5.  **Test Your Changes:** Ensure all tests pass.
    ```bash
    pytest
    ```
    Add new tests for new functionality.
6.  **Commit Your Changes:**
    ```bash
    git commit -am 'Add some amazing feature'
    ```
7.  **Push to Your Branch:**
    ```bash
    git push origin my-new-feature
    ```
8.  **Submit a Pull Request:** Go to the original repository on GitHub and click 'New pull request'.

Please ensure your code adheres to general Python best practices and that new functionality is accompanied by tests.
