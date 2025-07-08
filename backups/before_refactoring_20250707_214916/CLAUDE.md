# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is **Hephaestus**, a Recursive Self-Improvement (RSI) agent designed to autonomously enhance its own capabilities. Unlike traditional software development agents, Hephaestus focuses on self-analysis, identifying limitations, and generating objectives to improve its architecture and efficiency.

**🎯 Recent Update**: The project has been completely reorganized into a professional Python package structure and startup initialization has been optimized with parallel agent loading, reducing initialization time from 8-12 seconds to 0.04 seconds (99.7% improvement).

## Development Commands

### Package Management
```bash
# Install dependencies with new structure
poetry install

# The project is now a proper Python package named 'hephaestus'
# located in src/hephaestus/
```

### Testing
```bash
# Run all tests
poetry run pytest

# Run tests with coverage
poetry run pytest --cov=src/hephaestus --cov-report=html

# Run specific test file
poetry run pytest tests/unit/core/test_brain.py
```

### Linting and Code Quality
```bash
# Run linter (Ruff)
poetry run ruff check .

# Format code
poetry run ruff format .
```

### Running the System

**CLI Mode (Recommended for development):**
```bash
# Main CLI entry point
poetry run python cli.py run

# Run in continuous mode
poetry run python cli.py run --continuous

# Run with cycle limit
poetry run python cli.py run --max-cycles 5

# Submit objective via CLI
poetry run python cli.py submit "Your objective here"

# Check system status
poetry run python cli.py status
```

**Server Mode (API access - OPTIMIZED startup):**
```bash
# Start FastAPI server with optimized parallel initialization
poetry run python main.py
# Then access API at http://localhost:8000/docs
```

**MCP Server Mode:**
```bash
# Start MCP server for Cursor/Claude integration
poetry run python hephaestus_mcp_server.py
```

**Alternative scripts:**
```bash
# Use poetry scripts (defined in pyproject.toml)
poetry run hephaestus run
poetry run hephaestus-server
poetry run hephaestus-mcp
```

## High-Level Architecture

### Core Philosophy: Recursive Self-Improvement (RSI)
The system operates on a hierarchy of priorities:
1. **Enhance Core Capabilities** - Expand what the agent can do
2. **Improve Efficiency** - Analyze performance data to increase success rates
3. **Refactor with Purpose** - Code changes enable future capabilities
4. **Execute Development Tasks** - External tasks test new capabilities

### Meta-Intelligence Core
The system features advanced meta-cognitive capabilities:

- **Model Optimizer**: Collects performance data and generates JSONL datasets for fine-tuning
- **Knowledge System**: Intelligent web search with credibility ranking and semantic analysis
- **Root Cause Analyzer**: 5-layer causal analysis (Immediate → Environmental) with pattern detection
- **Self-Awareness Core**: Deep introspection and cognitive state monitoring

### Key Components

**Core System (`src/hephaestus/core/`)**
- `agent.py`: Main HephaestusAgent class that coordinates all subsystems
- `cycle_runner.py`: Asynchronous execution loop manager
- `memory.py`: Persistent storage with semantic clustering
- `brain.py`: Decision-making and objective generation
- `state.py`: Agent state management

**Specialized Agents (`src/hephaestus/agents/`)**
- `architect.py`: Strategic planning and code architecture
- `maestro.py`: Strategy selection with weighted decisions
- `bug_hunter.py`: Automated bug detection and fixing
- `organizer.py`: Project structure optimization
- `error_detector_agent.py`: Real-time error monitoring and detection
- `dependency_fixer_agent.py`: Automated dependency resolution
- `cycle_monitor_agent.py`: Performance and cycle tracking
- `agent_expansion_coordinator.py`: Dynamic agent creation and coordination
- `base.py`: Base classes and interfaces for all agents

**Meta-Intelligence (`src/hephaestus/intelligence/`)**
- `model_optimizer.py`: LLM performance optimization and fine-tuning
- `knowledge_system.py`: Advanced web search and knowledge acquisition
- `root_cause_analyzer.py`: Deep causal analysis system
- `self_awareness.py`: System introspection and cognitive monitoring

**Services (`src/hephaestus/services/`)**
- `validation/`: Code and data validation systems
- `communication/`: Inter-agent communication
- `orchestration/`: Asynchronous task coordination
- `monitoring/`: Performance and health monitoring

**API Interfaces (`src/hephaestus/api/`)**
- `rest/`: FastAPI server and endpoints
- `mcp/`: MCP server for IDE integration
- `cli/`: Command-line interface

**Utilities (`src/hephaestus/utils/`)**
- `llm_client.py`: LLM API communication
- `tool_executor.py`: External tool execution
- `git_utils.py`: Git operations
- `error_handling.py`: Error management
- `infrastructure_manager.py`: System infrastructure

**Configuration (`config/`)**
- `default.yaml`: Main configuration entry point
- `base_config.yaml`: Base system settings
- `models/main.yaml`: LLM model configurations
- `validation_strategies/main.yaml`: Validation settings

### Execution Flow
1. **Objective Generation**: Brain module analyzes codebase and generates strategic objectives
2. **Agent Selection**: Maestro selects appropriate specialized agents
3. **Execution**: Agents execute with real-time monitoring
4. **Validation**: Multi-step validation including syntax, tests, and performance
5. **Meta-Analysis**: Root cause analysis and capability assessment
6. **Evolution**: Self-improvement based on performance data

## Key Files and Patterns

### Entry Points
- CLI: `cli.py` (main CLI interface)
- Server: `main.py` (FastAPI server)
- MCP Server: `hephaestus_mcp_server.py` (Cursor/Claude integration)

### Configuration Management
- Main config: `config/default.yaml`
- Model configs: `config/models/main.yaml`
- Base configs: `config/base_config.yaml`
- Runtime config: `hephaestus_config.json` (in root)

### Data and State
- Agent memory: `data/memory/HEPHAESTUS_MEMORY.json`
- System logs: `data/logs/`
- Reports and analysis: `data/reports/`
- Performance metrics: `data/reports/model_performance.db`
- Evolution tracking: `logs/evolution_log.csv`
- Backup files: `src/hephaestus/api/rest/main.py.backup` (startup optimization backup)

### Testing Structure (Reorganized)
- Unit tests: `tests/unit/`
- Integration tests: `tests/integration/`
- Test fixtures: `tests/fixtures/`

### Scripts Organization
- Setup scripts: `scripts/setup/`
- Monitoring: `scripts/monitoring/`
- Analysis tools: `scripts/analysis/`
- Demos: `scripts/demos/`

## Development Guidelines

### Agent Development
When creating new agents, inherit from `BaseAgent` in `src/hephaestus/agents/base.py` and implement:
- `execute()`: Main agent logic
- `get_capabilities()`: List of agent capabilities
- `get_status()`: Current agent status

### Import Patterns (New Structure)
```python
# Core components
from hephaestus.core import HephaestusAgent, Memory, CycleRunner
from hephaestus.core.brain import generate_next_objective

# Agents
from hephaestus.agents import ArchitectAgent, MaestroAgent
from hephaestus.agents.base import BaseAgent

# Intelligence
from hephaestus.intelligence import ModelOptimizer, get_knowledge_system

# Services
from hephaestus.services.validation import get_validation_step
from hephaestus.utils import call_llm_with_fallback
```

### Configuration Changes
- Use Hydra configuration system
- Add new models to `config/models/`
- Main configuration in `config/default.yaml`
- Base settings in `config/base_config.yaml`

### Error Handling
- The system has comprehensive error detection and recovery
- Use the `ErrorPreventionSystem` for critical components
- All agents should report errors to the central error detector

### Performance Optimization
- The `ModelOptimizer` automatically collects performance data
- Use `@optimize_llm_call` decorator for LLM calls
- Monitor metrics through the performance monitoring system

## Important Patterns

### Dependency Injection
The system uses a comprehensive dependency injection pattern via `DependencyResolver` in the services layer.

### Asynchronous Operations
Most agent operations are asynchronous. Use the `AsyncAgentOrchestrator` in `src/hephaestus/services/orchestration/` for coordinating multiple agents.

**Important**: The API startup has been optimized with parallel initialization. Agents are loaded in phases:
1. **Independent agents** (parallel): ErrorDetector, DependencyFixer, AgentExpansionCoordinator, InterfaceGenerator
2. **Dependent agents**: HephaestusAgent, CycleMonitor
3. **Monitoring activation**: start_monitoring() and meta-intelligence systems

### Hot Reload and Self-Modification
The system can modify its own code at runtime through components in the intelligence layer:
- `HotReloadManager`: Real-time code reloading
- `FlowSelfModifier`: Dynamic LLM call optimization  
- `SelfEvolutionEngine`: Automated system evolution

### Memory and Learning
All agents should leverage the `Memory` system (`src/hephaestus/core/memory.py`) to:
- Store successful strategies
- Learn from failure patterns
- Maintain context across sessions

### Package Structure Benefits
The new structure provides:
- **Clear separation of concerns**: Core, agents, intelligence, services, API
- **Better testability**: Isolated components with clear dependencies
- **Improved maintainability**: Logical grouping of related functionality
- **Standard Python packaging**: Follows PEP standards for distribution

## Security Considerations

- API endpoints are protected with JWT authentication (`src/hephaestus/api/rest/`)
- Rate limiting is implemented
- All configuration is validated before use
- Error prevention system monitors for security issues

## Project Structure Reorganization

**✅ COMPLETED**: The project has been successfully reorganized from a chaotic structure to a professional Python package.

### What Changed:
- **Before**: 74 files cluttered in root directory
- **After**: Clean root with only 5 essential files
- **Package**: Code now organized in `src/hephaestus/` following Python standards
- **Backup**: Old structure preserved in `backup_old_structure/`

### Current Structure:
```
agente_autonomo/
├── 📄 main.py                    # FastAPI server entry point
├── 📄 cli.py                     # CLI interface
├── 📄 hephaestus_mcp_server.py   # MCP server for IDE integration
├── 📄 README.md                  # Project documentation
├── 📄 CLAUDE.md                  # This file
├── 📁 src/hephaestus/            # Main Python package
│   ├── core/                     # Core system components
│   ├── agents/                   # Specialized agents
│   ├── intelligence/             # Meta-intelligence systems
│   ├── services/                 # Shared services
│   ├── api/                      # API interfaces
│   └── utils/                    # Utility functions
├── 📁 config/                    # Configuration files
├── 📁 scripts/                   # Organized scripts
├── 📁 docs/                      # Documentation
├── 📁 data/                      # Data, logs, reports
└── 📁 tests/                     # Test suites
```

## Development Best Practices

### Working with the New Structure
1. **Always use the package imports**: Import from `hephaestus.*` rather than direct file paths
2. **Respect the layer separation**: Core → Agents → Intelligence → Services → Utils
3. **Follow the naming conventions**: Clear, descriptive names in English
4. **Use the organized test structure**: Place tests in appropriate `tests/unit/` or `tests/integration/`
5. **Keep the root clean**: Add new Python files to appropriate packages, not the root

### Important Notes
- This system is designed to be self-modifying and autonomous
- The reorganized structure follows Python packaging best practices
- All core functionality has been preserved during reorganization
- The system maintains extensive logs in `data/logs/` for debugging
- Memory is persistent across sessions in `data/memory/`
- Legacy backup is available in `backup_old_structure/` if needed

### Getting Started
1. Ensure all dependencies are installed: `poetry install`
2. Test basic functionality: `poetry run python cli.py --help`
3. Start the system: `poetry run python main.py` (server) or `poetry run python cli.py run` (CLI)
4. Monitor logs in `data/logs/` for system behavior
5. Check memory state in `data/memory/HEPHAESTUS_MEMORY.json`

### Performance Optimizations
- **Startup optimization**: API server initialization reduced from 8-12 seconds to 0.04 seconds through parallel agent loading
- **Backup available**: Original startup code backed up in `src/hephaestus/api/rest/main.py.backup`
- **Monitoring**: Use `⚡ Initialization time: X.XXs` log messages to verify optimization is working

### Environment Setup
Set up API keys in `.env` file:
```bash
GEMINI_API_KEY="your_gemini_key_here"
OPENROUTER_API_KEY="your_openrouter_key_here"
```

### API Usage Examples
```bash
# Submit objective via API
curl -X POST "http://localhost:8000/submit_objective" -H "Content-Type: application/json" -d '{"objective": "Your objective here"}'

# Check system status
curl "http://localhost:8000/status"

# Access interactive documentation
# Open http://localhost:8000/docs in browser
```