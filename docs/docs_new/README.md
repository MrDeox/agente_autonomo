# Hephaestus: Um Agente de Aprimoramento Auto Recursivo (RSI)

**Hephaestus não é apenas um desenvolvedor de software autônomo; é um sistema projetado para melhorar a si mesmo.**

O objetivo principal deste projeto é explorar e construir um agente de IA capaz de **Aprimoramento Auto Recursivo (RSI)**. Isso significa que a principal diretriz do Hephaestus é analisar seu próprio código, identificar suas próprias limitações e gerar objetivos para aprimorar suas capacidades, arquitetura e eficiência.

---

## Visão do Projeto: O Foco em RSI

Em vez de simplesmente completar tarefas de desenvolvimento de software, o Hephaestus opera sob a seguinte hierarquia de prioridades:

1.  **Aprimorar Capacidades Fundamentais:** O agente busca ativamente expandir o que ele pode fazer. Isso é guiado pelo `docs/CAPABILITIES.md`.
2.  **Melhorar a Eficiência e a Taxa de Sucesso:** Analisando seu histórico de performance (`logs/evolution_log.csv`), o agente identifica por que falha e como pode ter mais sucesso no futuro.
3.  **Refatorar com Propósito:** A refatoração do código não é feita apenas para melhorar métricas, mas para habilitar futuras capacidades ou corrigir falhas de performance.
4.  **Executar Tarefas de Desenvolvimento:** A modificação de código para tarefas externas é um resultado secundário e uma forma de testar as capacidades recém-adquiridas.

## Quick Start

1.  **Clone o repositório:**
    ```bash
    git clone [URL_DO_SEU_REPOSITORIO]
    cd hephaestus-agent
    ```

2.  **Instale o Poetry:**
    ```bash
    curl -sSL https://install.python-poetry.org | python3 -
    export PATH="/home/arthur/.local/bin:$PATH"
    ```

3.  **Instale as dependências:**
    ```bash
    poetry install
    ```

4.  **Configure suas Chaves de API:**
    Crie um arquivo `.env` na raiz do projeto e adicione suas chaves. O agente usará o Gemini como primário e o OpenRouter como fallback.
    ```
    GEMINI_API_KEY="sua_chave_gemini_aqui"
    OPENROUTER_API_KEY="sua_chave_openrouter_aqui"
    ```
    Ou exporte-as em seu terminal.

5.  **Escolha como executar o agente:**

    **Opção 1: Usando a CLI (recomendado)**
    ```bash
    # Iniciar o agente
    poetry run python cli.py run

    # Submeter um objetivo
    poetry run python cli.py submit "Seu objetivo aqui"

    # Verificar status
    poetry run python cli.py status
    ```

    **Opção 2: Executar o servidor FastAPI (para uso via API)**
    ```bash
    poetry run python main.py
    ```
    Após iniciar o servidor, você pode enviar objetivos via API (veja exemplos abaixo).

6.  **Exemplos de uso da API (se estiver executando o servidor):**
    Para enviar um novo objetivo ao agente, você pode usar o endpoint `/submit_objective`:
    ```bash
    curl -X POST "http://localhost:8000/submit_objective" -H "Content-Type: application/json" -d '{"objective": "Seu novo objetivo aqui"}'
    ```

    Para verificar o status do servidor e da fila de objetivos:
    ```bash
    curl "http://localhost:8000/status"
    ```

## Como Funciona? O Ciclo de Auto-Aprimoramento Avançado

O Hephaestus opera em um ciclo contínuo altamente sofisticado, com **sistemas avançados de meta-inteligência** que permitem verdadeira auto-otimização:

### 🧠 **Meta-Intelligence Core Expandido**

1.  **Serviço em Segundo Plano:** O Hephaestus é executado como um servidor FastAPI com thread worker dedicado para processamento assíncrono.
2.  **Enhanced Self-Assessment:** Análise profunda das capacidades cognitivas com identificação de blind spots e oportunidades de melhoria.
3.  **Advanced Root Cause Analysis:** Sistema multi-camada que identifica causas raiz sistêmicas usando metodologia "5 Whys" e análise temporal.
4.  **Intelligent Knowledge Acquisition:** Busca inteligente multi-fonte (web, GitHub, documentação) com otimização de queries por IA.
5.  **Model Performance Optimization:** Captura automática de dados de performance e geração de datasets para fine-tuning.
6.  **Enhanced Agent Creation:** Criação de novos agentes baseada em pesquisa de melhores práticas externas.

### 🎯 **Sistemas de Auto-Otimização**

- **🔧 Model Optimizer:** Coleta dados de performance (40% sucesso, 30% qualidade, 20% eficiência, 10% contexto) e gera datasets JSONL para fine-tuning automático. Aplica algoritmos genéticos para evolução de prompts.

- **🔍 Knowledge System:** Busca inteligente com ranking composto (50% relevância, 30% credibilidade, 20% recência). Cache TTL, análise semântica, e aprendizado contínuo baseado em feedback.

- **⚡ Root Cause Analyzer:** Análise em 5 camadas causais (Immediate → Proximate → Systemic → Cultural → Environmental). Detecção automática de padrões temporais, falhas em cascata, e degradação sistêmica.

### 🚀 **Ciclo Expandido de Meta-Cognição**

1.  **Planejamento Arquitetônico:** O `ArchitectAgent` cria planos com prompts otimizados por dados de performance histórica.
2.  **Decisão Estratégica Informada:** O `MaestroAgent` usa conhecimento externo pesquisado para escolher estratégias baseadas em evidências.
3.  **Execução com Monitoramento:** Captura automática de métricas de performance durante execução.
4.  **Meta-Análise Avançada:** Sistema de análise de causa raiz identifica problemas sistêmicos e gera recomendações acionáveis.
5.  **Auto-Otimização Contínua:** Datasets de fine-tuning são gerados automaticamente para treinar versões melhoradas do sistema.
6.  **Aplicação e Evolução:** Mudanças são aplicadas com versionamento Git e tracking de melhorias.

**Resultado:** O sistema literalmente treina versões melhores de si mesmo, expande conhecimento através de fontes externas, e previne problemas identificando causas raiz sistêmicas.

## Estrutura do Projeto

```
agente_autonomo/
├── README.md                    # Este arquivo - visão geral do projeto
├── main.py                      # Ponto de entrada para o servidor FastAPI
├── cli.py                       # Interface de linha de comando
├── pyproject.toml              # Configuração do Poetry
├── 
├── agent/                       # 🧠 Lógica central do agente
│   ├── brain.py                # Geração de objetivos e análise estratégica
│   ├── hephaestus_agent.py     # Classe principal do agente
│   ├── cycle_runner.py         # Orquestração do ciclo de auto-aprimoramento
│   ├── agents/                 # Agentes especializados
│   ├── validation_steps/       # Passos de validação
│   └── utils/                  # Utilitários e helpers
├── 
├── config/                      # ⚙️ Configurações (gerenciadas pelo Hydra)
│   ├── default.yaml            # Configuração principal
│   ├── base_config.yaml        # Configurações base
│   ├── models/                 # Configurações dos modelos LLM
│   └── validation_strategies/  # Estratégias de validação
├── 
├── tests/                       # 🧪 Testes unitários
├── 
├── docs/                        # 📚 Documentação completa
│   ├── README.md               # Índice da documentação
│   ├── ROADMAP.md              # Roadmap de desenvolvimento
│   ├── CAPABILITIES.md         # Capacidades atuais e desejadas
│   ├── ARCHITECTURE.md         # Arquitetura do sistema
│   ├── CONTRIBUTING.md         # Guia de contribuição
│   └── analysis/               # Análises técnicas e de performance
├── 
├── logs/                        # 📊 Logs do sistema
│   ├── hephaestus.log          # Log detalhado de execução
│   ├── evolution_log.csv       # Log de performance dos ciclos
│   └── night_agent.log         # Log do agente noturno
├── 
├── reports/                     # 📈 Relatórios e dados
│   ├── evolution/              # Relatórios de evolução
│   ├── night_work/             # Trabalho do agente noturno
│   └── memory/                 # Memória persistente
├── 
├── scripts/                     # 🔧 Scripts utilitários
│   ├── night_agent.py          # Agente de melhorias noturnas
│   ├── monitor_evolution.py    # Monitor de evolução
│   └── run_agent.py            # Runner alternativo
└── 
└── tools/                       # 🛠️ Ferramentas auxiliares
    ├── app.py                  # Aplicação FastAPI
    └── test_meta_intelligence.py
```

### Principais Componentes:

-   **`agent/`**: Contém a lógica central do agente.
    -   `hephaestus_agent.py`: Classe principal `HephaestusAgent`
    -   `brain.py`: Lógica de geração de objetivos e análise estratégica
    -   `cycle_runner.py`: Orquestra o ciclo de auto-aprimoramento
    -   `agents/`: Agentes especializados (`Architect`, `Maestro`, etc.)
    -   `validation_steps/`: Passos de validação (sintaxe, testes, etc.)
    -   `utils/`: Utilitários (LLM client, logging, etc.)

-   **`config/`**: Configurações gerenciadas pelo Hydra
    -   `default.yaml`: Ponto de entrada principal
    -   `base_config.yaml`: Configurações base
    -   `models/main.yaml`: Configurações dos modelos LLM
    -   `validation_strategies/main.yaml`: Estratégias de validação

-   **`docs/`**: Documentação completa do projeto
    -   `ROADMAP.md`: Roadmap de desenvolvimento
    -   `CAPABILITIES.md`: Capacidades atuais e desejadas
    -   `ARCHITECTURE.md`: Arquitetura detalhada do sistema
    -   `analysis/`: Análises técnicas e de performance

## Documentação

Para informações detalhadas, consulte:

- **[docs/README.md](docs/README.md)** - Índice completo da documentação
- **[docs/ROADMAP.md](docs/ROADMAP.md)** - Roadmap de desenvolvimento
- **[docs/CAPABILITIES.md](docs/CAPABILITIES.md)** - Capacidades do sistema
- **[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)** - Arquitetura detalhada
- **[docs/CONTRIBUTING.md](docs/CONTRIBUTING.md)** - Guia de contribuição

## Testes

```bash
poetry run pytest
```

## Contribuições

Contribuições são bem-vindas! Por favor, consulte o [Guia de Contribuição](docs/CONTRIBUTING.md) para detalhes sobre como contribuir para o projeto.

---

**Hephaestus**: Forjando o futuro da inteligência artificial auto-recursiva. 🔥⚒️
