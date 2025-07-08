# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is **Hephaestus**, a Recursive Self-Improvement (RSI) agent designed to autonomously enhance its own capabilities. Unlike traditional software development agents, Hephaestus focuses on self-analysis, identifying limitations, and generating objectives to improve its architecture and efficiency.

**🎯 Recent Updates**: 
- **Real-Time Evolution Engine**: Implemented continuous evolution system that mutates and optimizes the system during runtime
- **Predictive Failure Engine**: AI-powered system that predicts failures before execution and applies preventive modifications
- **Meta-Intelligence Core**: Advanced systems for model optimization, knowledge acquisition, root cause analysis, and self-awareness
- **Agent consolidation**: Simplified to enhanced versions only (architect_enhanced.py, maestro_enhanced.py, etc.)
- **Startup optimization**: API server initialization reduced from 8-12s → 0.04s (99.7% improvement)
- **Enhanced inheritance**: Fixed multiple inheritance issues in EnhancedBaseAgent
- **Security fixes**: All API keys moved to .env file, removed hardcoded credentials
- **System health**: Monitoring dashboard with automatic agent registration

## Development Commands

### Package Management
```bash
# Install dependencies
poetry install

# The project is a proper Python package named 'hephaestus'
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

**Server Mode (API access):**
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

### Meta-Intelligence Systems

**Real-Time Evolution Engine** (`src/hephaestus/intelligence/real_time_evolution_engine.py`):
- Continuous evolution during execution (not just between cycles)
- 5 mutation types: prompt optimization, strategy adjustment, parameter tuning, workflow modification, agent behavior change
- Parallel testing with fitness evaluation and automatic deployment
- Anti-loop protection and emergency evolution triggers

**Predictive Failure Engine** (`src/hephaestus/intelligence/predictive_failure_engine.py`):
- Analyzes historical patterns to predict failure probability before execution
- Applies preventive modifications to high-risk objectives
- Continuous learning from execution feedback
- Pattern recognition for keyword-based, complexity-based, and async-related failures

**Meta-Intelligence Core Features**:
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
- `architect_enhanced.py`: Strategic planning and code architecture (ArchitectAgentEnhanced)
- `maestro_enhanced.py`: Strategy selection with weighted decisions (MaestroAgentEnhanced)
- `bug_hunter_enhanced.py`: Automated bug detection and fixing (BugHunterAgentEnhanced)
- `organizer_enhanced.py`: Project structure optimization (OrganizerAgentEnhanced)
- `enhanced_base.py`: Enhanced base class with proper MRO and automatic dashboard registration
- `base.py`: Base classes and interfaces for all agents
- `mixins.py`: Agent mixins for logging, caching, and LLM management

**Intelligence Layer (`src/hephaestus/intelligence/`)**
- `real_time_evolution_engine.py`: Continuous system evolution during runtime
- `predictive_failure_engine.py`: AI-powered failure prediction and prevention
- `model_optimizer.py`: LLM performance optimization and fine-tuning
- `knowledge_system.py`: Advanced web search and knowledge acquisition
- `root_cause_analyzer.py`: Deep causal analysis system
- `self_awareness.py`: System introspection and cognitive monitoring

**Services (`src/hephaestus/services/`)**
- `validation/`: Code and data validation systems
- `communication/`: Inter-agent communication
- `orchestration/`: Asynchronous task coordination
- `monitoring/`: Performance and health monitoring

**Monitoring (`src/hephaestus/monitoring/`)**
- `unified_dashboard.py`: Real-time system health monitoring with automatic agent registration
- `predictive_failure_dashboard.py`: Monitoring dashboard for failure prediction system

**API Interfaces (`src/hephaestus/api/`)**
- `rest/`: FastAPI server and endpoints
- `mcp/`: MCP server for IDE integration
- `cli/`: Command-line interface

**Utilities (`src/hephaestus/utils/`)**
- `llm_client.py`: LLM API communication with fallback support
- `llm_manager.py`: Centralized LLM call management with retry and caching
- `config_manager.py`: Configuration management with model fallback support
- `json_parser.py`: Robust JSON parsing with error correction
- `tool_executor.py`: External tool execution
- `git_utils.py`: Git operations
- `error_handling.py`: Error management
- `infrastructure_manager.py`: System infrastructure

### Execution Flow
1. **Objective Generation**: Brain module analyzes codebase and generates strategic objectives
2. **Failure Prediction**: Predictive engine analyzes objective and applies preventive modifications
3. **Agent Selection**: Maestro selects appropriate specialized agents
4. **Execution**: Agents execute with real-time monitoring and evolution
5. **Validation**: Multi-step validation including syntax, tests, and performance
6. **Meta-Analysis**: Root cause analysis and capability assessment
7. **Evolution**: Self-improvement based on performance data and continuous mutations

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
- Meta-functionalities memory: `data/memory/META_FUNCTIONALITIES_MEMORY.json`

### Testing Structure
- Unit tests: `tests/unit/`
- Integration tests: `tests/integration/`
- Test fixtures: `tests/fixtures/`
- Evolution engine tests: `test_real_time_evolution.py`, `test_predictive_engine.py`

## Development Guidelines

### Agent Development
When creating new agents, prefer inheriting from `EnhancedBaseAgent` in `src/hephaestus/agents/enhanced_base.py`:
- `execute()`: Main agent logic
- `get_capabilities()`: List of agent capabilities  
- `get_status()`: Current agent status
- Automatic logger setup, dashboard registration, and LLM management included

For basic agents, inherit from `BaseAgent` in `src/hephaestus/agents/base.py`.

### Meta-Intelligence Integration
The system includes advanced meta-intelligence capabilities:

**Real-Time Evolution**: 
- Register mutation callbacks for different types of system improvements
- Evolution runs continuously in background thread during execution
- Mutations are tested in parallel and deployed based on fitness scores

**Predictive Failure Prevention**:
- Integrate with failure prediction in objective generation pipeline
- System learns from execution feedback to improve predictions
- Risk factors and preventive modifications are automatically applied

### Import Patterns
```python
# Core components
from hephaestus.core import HephaestusAgent, Memory, CycleRunner
from hephaestus.core.brain import generate_next_objective

# Enhanced agents
from hephaestus.agents.architect_enhanced import ArchitectAgentEnhanced
from hephaestus.agents.maestro_enhanced import MaestroAgentEnhanced

# Intelligence systems
from hephaestus.intelligence.real_time_evolution_engine import get_real_time_evolution_engine
from hephaestus.intelligence.predictive_failure_engine import get_predictive_failure_engine

# Services
from hephaestus.services.validation import get_validation_step
from hephaestus.utils import call_llm_with_fallback
```

### Configuration Management
- Use Hydra configuration system
- Real-time evolution engine configuration in `config/default.yaml` under `real_time_evolution`
- Model configurations with intelligent distribution to avoid rate limiting
- Rate limiting and execution mode configurations for optimal performance

### Meta-Intelligence Features
- **Evolution Engine**: Continuously mutates and improves system during runtime
- **Predictive Engine**: Prevents failures by analyzing patterns and modifying objectives
- **Model Optimizer**: Automatically collects performance data for LLM fine-tuning
- **Knowledge System**: Intelligent web search with credibility ranking
- **Root Cause Analysis**: Deep causal analysis with 5-layer methodology

## Important Patterns

### Real-Time Evolution Integration
The system features a comprehensive evolution engine that:
- Runs in background thread during execution
- Generates 5 types of mutations (prompts, strategies, parameters, workflows, agent behaviors)
- Tests mutations in parallel with fitness evaluation
- Automatically deploys successful improvements
- Includes anti-loop protection and emergency evolution

### Predictive Failure Prevention
Integration with failure prediction system:
- Analyzes objectives before execution for failure probability
- Applies preventive modifications to high-risk objectives
- Learns from execution feedback to improve predictions
- Maintains patterns database for historical analysis

### Asynchronous Operations
Most agent operations are asynchronous. The API startup has been optimized with parallel initialization:
1. **Independent agents** (parallel): ErrorDetector, DependencyFixer, AgentExpansionCoordinator
2. **Dependent agents**: HephaestusAgent, CycleMonitor
3. **Evolution systems**: Real-time evolution and predictive failure engines
4. **Monitoring activation**: start_monitoring() and meta-intelligence systems

### Memory and Learning
All agents leverage the `Memory` system (`src/hephaestus/core/memory.py`) to:
- Store successful strategies and patterns
- Learn from failure patterns via predictive engine
- Maintain context across sessions
- Support meta-functionalities tracking

## Environment Setup
Set up API keys in `.env` file:
```bash
GEMINI_API_KEY="your_gemini_key_here"
OPENROUTER_API_KEY="your_openrouter_key_here"
```

## Troubleshooting

### Common Issues

**Evolution engine not working:**
- Check `config/default.yaml` - evolution may be disabled (`enabled: false`)
- Verify mutation callbacks are registered in agent initialization
- Check logs for evolution loop errors

**Predictive engine issues:**
- Verify failure patterns are loaded from `data/memory/HEPHAESTUS_MEMORY.json`
- Check prediction logs for analysis errors
- Ensure sufficient historical data for pattern recognition

**Agent initialization errors:**
- Enhanced agents use multiple inheritance - ensure proper MRO in `enhanced_base.py`
- Filter kwargs appropriately when calling parent constructors
- Check for missing dependencies in agent mixins

**MaestroAgent strategy selection errors:**
- Common issue: `'MaestroAgentEnhanced' object has no attribute 'choose_strategy'`
- Check method implementation in `maestro_enhanced.py`
- Verify strategy selection logic and configuration

### Key Log Files
- Main system: `data/logs/hephaestus_main.log`
- Individual agents: `data/logs/agents/<agent_name>_agent.log`
- Evolution engine: `data/reports/evolution_state_*.json`
- Error prevention: `data/logs/error_prevention.log`
- Evolution tracking: `logs/evolution_log.csv`

### Meta-Intelligence Monitoring
- Real-time evolution status via `get_evolution_status()` method
- Predictive failure dashboard with comprehensive reports
- Performance metrics collection and analysis
- Automatic state persistence and recovery mechanisms