# Hephaestus: Um Agente de Aprimoramento Auto Recursivo (RSI)

**Hephaestus não é apenas um desenvolvedor de software autônomo; é um sistema projetado para melhorar a si mesmo.**

O objetivo principal deste projeto é explorar e construir um agente de IA capaz de **Aprimoramento Auto Recursivo (RSI)**. Isso significa que a principal diretriz do Hephaestus é analisar seu próprio código, identificar suas próprias limitações e gerar objetivos para aprimorar suas capacidades, arquitetura e eficiência.

---

## Visão do Projeto: O Foco em RSI

Em vez de simplesmente completar tarefas de desenvolvimento de software, o Hephaestus opera sob a seguinte hierarquia de prioridades:

1.  **Aprimorar Capacidades Fundamentais:** O agente busca ativamente expandir o que ele pode fazer. Isso é guiado pelo `CAPABILITIES.md`.
2.  **Melhorar a Eficiência e a Taxa de Sucesso:** Analisando seu histórico de performance (`evolution_log.csv`), o agente identifica por que falha e como pode ter mais sucesso no futuro.
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

## Como Funciona? O Ciclo de Auto-Aprimoramento

O Hephaestus opera em um ciclo contínuo, agora como um serviço em segundo plano, com foco em RSI:

1.  **Serviço em Segundo Plano:** O Hephaestus agora é executado como um servidor FastAPI, permitindo a submissão assíncrona de objetivos via API. Um thread worker dedicado processa os objetivos de uma fila.
2.  **Geração de Objetivo Estratégico:** O agente primeiro analisa o `CAPABILITIES.md` e seu `ROADMAP.md` para decidir qual capacidade aprimorar. Ele também revisa seu log de performance (`evolution_log.csv`) para encontrar padrões de falha a serem corrigidos. As métricas de código são usadas como um fator de desempate ou suporte. **Agora, o LLM é instruído a considerar a otimização de seus próprios prompts e estratégias com base na análise de performance.**
3.  **Planejamento Arquitetônico:** O `ArchitectAgent` cria um plano de modificação de código (patches) para alcançar o objetivo estratégico.
4.  **Decisão Estratégica:** O `MaestroAgent` analisa o plano e escolhe a melhor forma de validar as alterações. Se o plano for muito arriscado ou exigir uma capacidade que o agente não possui, ele pode solicitar um novo objetivo de "capacitação".
5.  **Execução e Validação:** As alterações são aplicadas em um ambiente seguro (sandbox) e validadas usando testes e verificação de sintaxe.
6.  **Meta-Análise de Falha:** Se o ciclo falhar, o `ErrorAnalysisAgent` é ativado. Sua nova função é questionar não apenas o código, mas também o objetivo e a estratégia. **Ele pode sugerir uma abordagem completamente nova ou um objetivo de meta-análise para entender a causa raiz da falha, que será processado pelo 'Planejador Estratégico Avançado'.**
7.  **Aplicação e Versionamento:** Se a validação for bem-sucedida, as alterações são aplicadas à base de código principal e um commit é feito automaticamente.

## Estrutura do Projeto

-   **`app.py`**: Aplicação FastAPI que expõe a API para submissão de objetivos e status, e inicia the agent em um thread worker.
-   **`agent/`**: Contém a lógica central do agente.
    -   `hephaestus_agent.py`: **Contém a classe principal `HephaestusAgent` (movida de `main.py`).**
    -   `brain.py`: Lógica de geração de objetivos e mensagens de commit. **Agora com lógica aprimorada para meta-análise e otimização de prompts.**
    -   `agents.py`: Define os agentes especializados (`Architect`, `Maestro`).
    -   `cycle_runner.py`: Orquestra o ciclo de auto-aprimoramento. **Agora interage com o `QueueManager`.**
    -   `error_analyzer.py`: Analisa falhas e realiza meta-análise. **Agora pode sugerir objetivos de meta-análise.**
    -   `queue_manager.py`: **Novo módulo para gerenciar a fila de objetivos.**
    -   `config_loader.py`: **Novo módulo para carregar a configuração do agente.**
    -   `utils/llm_client.py`: Gerencia a comunicação com as APIs de LLM (Gemini, OpenRouter).
    -   `validation_steps/`: Contém os passos de validação. **Agora inclui placeholders para `BenchmarkValidator`, `CheckFileExistenceValidator`, `ValidateJsonSyntax`.**
-   **`tests/`**: Testes unitários para o agente.
-   **Documentos de Estratégia:**
    -   `README.md`: (Este arquivo) Visão geral do projeto.
    -   `CAPABILITIES.md`: O manifesto de capacidades atuais e desejadas que guia o RSI.
    -   `ROADMAP.md`: O roadmap de desenvolvimento de alto nível.
    -   `MANIFESTO.md`: Os princípios de design do projeto.
    -   `AGENTS.md`: Documentação da arquitetura interna.
-   **Configuração e Logs:**
    -   `main.py`: **Ponto de entrada para iniciar o servidor FastAPI.**
    -   `config/`: Diretório contendo a configuração do agente, gerenciada pelo Hydra.
        -   `default.yaml`: Ponto de entrada principal da configuração Hydra.
        -   `base_config.yaml`: Configurações base (caminhos, thresholds, logging).
        -   `models/main.yaml`: Configurações dos modelos de LLM.
        -   `validation_strategies/main.yaml`: Estratégias de validação.
        -   `example_config.yaml`: Documentação e exemplo de como customizar a configuração Hydra.
    -   `hephaestus_config.json`: (Removido) A configuração agora é gerenciada via Hydra no diretório `config/`.
    -   `hephaestus.log`: Log detalhado de execução.
    -   `evolution_log.csv`: Log de alto nível sobre a performance de cada ciclo.

## Testes

```bash
poetry run pytest
```

## Contribuições

Contribuições são bem-vindas. Por favor, siga o guia em `CONTRIBUTING.md`.
