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

## Configuration

See `hephaestus_config.json` for available options.

## Testing

Run the test suite with [pytest](https://docs.pytest.org/):

```bash
pytest
```

Ensure the `OPENROUTER_API_KEY` variable is set when executing tests, as many
tests rely on its presence.

## Troubleshooting

Check `hephaestus.log` for detailed execution logs.
