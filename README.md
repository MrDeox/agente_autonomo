# Hephaestus Agent

Autonomous AI agent for software development

## Quick Start

1. Clone this repository
2. Install dependencies: `pip install -r requirements.txt`
3. Set the `OPENROUTER_API_KEY` environment variable with your OpenRouter key
   (you can place it in a `.env` file or export it directly).
4. Optionally adjust `hephaestus_config.json` for model and runtime settings.
5. Run the agent: `python main.py`

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
