# 🔧 PROMPTS TÉCNICOS ESPECÍFICOS PARA HEPHAESTUS

## 🎯 BASEADO NA ANÁLISE ATUAL DO CÓDIGO

### 📋 COMPONENTES IDENTIFICADOS

**Agentes Ativos:**
- `HephaestusAgent` (core)
- `AsyncAgentOrchestrator` (coordenação)
- `InterAgentCommunication` (comunicação)
- `MetaIntelligenceCore` (meta-cognição)
- `BugHunterAgent` (detecção de bugs)
- `SwarmCoordinatorAgent` (coordenação de enxame)
- `ArchitectAgent`, `MaestroAgent`, `CodeReviewAgent`

**Sistemas Críticos:**
- `HotReloadManager` (auto-evolução)
- `PerformanceMonitor` (monitoramento)
- `ErrorPreventionSystem` (prevenção)
- `CoverageActivator` (ativação de features)

---

## 🚀 PROMPTS IMEDIATOS DE IMPLEMENTAÇÃO

### PROMPT T1: Otimização do AsyncAgentOrchestrator

```python
# CONTEXTO: agent/async_orchestrator.py linha 1-364
# PROBLEMA: Gargalos de performance em execução paralela

IMPLEMENTAR:
1. Pool de conexões LLM reutilizáveis
2. Batching de requests similares
3. Cache de resultados por hash de entrada
4. Timeout adaptativo baseado em complexidade
5. Métricas de performance por agente

CÓDIGO ESPECÍFICO:
- Modificar _execute_task() para usar connection pool
- Implementar _batch_similar_requests()
- Adicionar _adaptive_timeout_calculator()
- Criar metrics collector em _run_agent_task()
- Implementar circuit breaker pattern
```

### PROMPT T2: Evolução do InterAgentCommunication

```python
# CONTEXTO: agent/inter_agent_communication.py linha 1-467
# PROBLEMA: Comunicação pode ser mais inteligente

IMPLEMENTAR:
1. Sistema de priorização de mensagens
2. Detecção automática de loops de conversa
3. Compressão de mensagens grandes
4. Retry automático com backoff
5. Métricas de qualidade de comunicação

CÓDIGO ESPECÍFICO:
- Adicionar priority_queue no _process_message()
- Implementar _detect_conversation_loops()
- Criar _compress_large_messages()
- Adicionar _retry_with_backoff()
- Implementar _communication_quality_metrics()
```

### PROMPT T3: Upgrade do MetaIntelligenceCore

```python
# CONTEXTO: agent/meta_intelligence_core.py linha 1-1158
# PROBLEMA: Evolução de prompts pode ser mais sofisticada

IMPLEMENTAR:
1. A/B testing automático de prompts
2. Análise de sentimento das respostas
3. Detecção de padrões de falha
4. Otimização de temperatura por contexto
5. Versionamento de prompts

CÓDIGO ESPECÍFICO:
- Modificar evolve_prompt() para incluir A/B testing
- Implementar _analyze_response_sentiment()
- Criar _detect_failure_patterns()
- Adicionar _optimize_temperature()
- Implementar _version_control_prompts()
```

### PROMPT T4: Melhoria do BugHunterAgent

```python
# CONTEXTO: agent/agents/bug_hunter_agent.py linha 1-698
# PROBLEMA: Detecção pode ser mais proativa

IMPLEMENTAR:
1. Análise de código estática com AST
2. Detecção de code smells automatizada
3. Integração com ferramentas de linting
4. Predição de bugs com ML
5. Auto-correção com validação

CÓDIGO ESPECÍFICO:
- Adicionar _static_code_analysis()
- Implementar _detect_code_smells()
- Criar _integrate_linting_tools()
- Adicionar _predict_bugs_with_ml()
- Implementar _auto_fix_with_validation()
```

### PROMPT T5: Expansão do Sistema de Cache

```python
# CONTEXTO: Detectado uso de cache, mas pode ser otimizado

IMPLEMENTAR:
1. Cache multi-layer (L1: memory, L2: redis, L3: disk)
2. TTL inteligente baseado em padrões de uso
3. Invalidação seletiva por tags
4. Compressão automática de dados grandes
5. Métricas de hit/miss rate

CÓDIGO ESPECÍFICO:
- Criar MultiLayerCache class
- Implementar _intelligent_ttl_calculator()
- Adicionar _tag_based_invalidation()
- Criar _auto_compression_handler()
- Implementar _cache_metrics_collector()
```

---

## 🔧 PROMPTS PARA CORREÇÕES ESPECÍFICAS

### PROMPT FIX-1: Melhoria do HotReloadManager

```python
# CONTEXTO: agent/hot_reload_manager.py (referenciado no código)
# PROBLEMA: Hot reload pode causar instabilidade

IMPLEMENTAR:
1. Validação de sintaxe antes do reload
2. Backup automático antes de mudanças
3. Rollback automático em caso de erro
4. Teste de smoke após reload
5. Notificação de status para outros agentes

CÓDIGO ESPECÍFICO:
- Adicionar _validate_syntax_before_reload()
- Implementar _auto_backup_system()
- Criar _automatic_rollback()
- Adicionar _smoke_test_after_reload()
- Implementar _notify_other_agents()
```

### PROMPT FIX-2: Otimização da API FastAPI

```python
# CONTEXTO: tools/app.py linha 1-2658
# PROBLEMA: Muitos endpoints podem ser otimizados

IMPLEMENTAR:
1. Middleware de rate limiting por endpoint
2. Compressão automática de respostas
3. Pagination automática para listas grandes
4. Validação de entrada mais rigorosa
5. Logging estruturado com trace IDs

CÓDIGO ESPECÍFICO:
- Criar EndpointRateLimiter middleware
- Implementar _auto_response_compression()
- Adicionar _automatic_pagination()
- Criar _enhanced_input_validation()
- Implementar _structured_logging_with_trace()
```

### PROMPT FIX-3: Melhoria do Sistema de Monitoramento

```python
# CONTEXTO: Sistema de monitoramento distribuído pelo código

IMPLEMENTAR:
1. Alertas inteligentes baseados em ML
2. Correlação automática de eventos
3. Dashboards dinâmicos
4. Previsão de problemas
5. Auto-recovery para problemas conhecidos

CÓDIGO ESPECÍFICO:
- Criar IntelligentAlertSystem
- Implementar _auto_event_correlation()
- Adicionar _dynamic_dashboard_generator()
- Criar _problem_prediction_engine()
- Implementar _auto_recovery_system()
```

---

## 🎯 PROMPTS PARA NOVAS FUNCIONALIDADES

### PROMPT NEW-1: Sistema de Métricas Avançado

```python
# OBJETIVO: Criar sistema completo de métricas

IMPLEMENTAR:
1. Collector de métricas distribuído
2. Análise de trends em tempo real
3. Alertas baseados em anomalias
4. Dashboards personalizáveis
5. Exportação para sistemas externos

ESTRUTURA:
- MetricsCollector class
- TrendAnalyzer class
- AnomalyDetector class
- DashboardGenerator class
- ExternalExporter class
```

### PROMPT NEW-2: Sistema de Versionamento de Agentes

```python
# OBJETIVO: Controle de versão para agentes

IMPLEMENTAR:
1. Versionamento semântico automático
2. Rollback para versões anteriores
3. Teste de compatibilidade
4. Migração automática de dados
5. Changelog automático

ESTRUTURA:
- AgentVersionControl class
- CompatibilityTester class
- AutoMigrator class
- ChangelogGenerator class
- VersionManager class
```

### PROMPT NEW-3: Sistema de Aprendizado Contínuo

```python
# OBJETIVO: Aprendizado baseado em feedback

IMPLEMENTAR:
1. Coleta de feedback automatizada
2. Análise de padrões de sucesso/falha
3. Ajuste automático de parâmetros
4. Validação de melhorias
5. Distribuição de aprendizado

ESTRUTURA:
- FeedbackCollector class
- PatternAnalyzer class
- AutoParameterTuner class
- ImprovementValidator class
- LearningDistributor class
```

---

## 🔍 PROMPTS DE ANÁLISE E DIAGNÓSTICO

### PROMPT DIAG-1: Análise de Performance

```python
# OBJETIVO: Identificar gargalos de performance

ANALISAR:
1. Tempo de resposta por agente
2. Uso de CPU/memória por processo
3. Latência de chamadas LLM
4. Throughput de mensagens
5. Eficiência de cache

GERAR RELATÓRIO:
- Gráficos de performance
- Identificação de bottlenecks
- Sugestões de otimização
- Comparação com baseline
- Projeção de escalabilidade
```

### PROMPT DIAG-2: Análise de Qualidade

```python
# OBJETIVO: Avaliar qualidade das respostas

ANALISAR:
1. Taxa de sucesso por agente
2. Qualidade das soluções propostas
3. Tempo para resolução
4. Feedback dos usuários
5. Correlação entre métricas

GERAR RELATÓRIO:
- Score de qualidade geral
- Identificação de agentes problemáticos
- Sugestões de melhoria
- Trends de evolução
- Benchmarks de qualidade
```

### PROMPT DIAG-3: Análise de Segurança

```python
# OBJETIVO: Audit de segurança completo

ANALISAR:
1. Vulnerabilidades de código
2. Segurança de APIs
3. Proteção de dados
4. Controle de acesso
5. Auditoria de logs

GERAR RELATÓRIO:
- Lista de vulnerabilidades
- Classificação de riscos
- Plano de mitigação
- Compliance checklist
- Recomendações de segurança
```

---

## 🛠️ PROMPTS DE REFATORAÇÃO

### PROMPT REF-1: Refatoração do Core

```python
# OBJETIVO: Melhorar estrutura do código core

REFATORAR:
1. Separar responsabilidades
2. Implementar design patterns
3. Reduzir acoplamento
4. Melhorar testabilidade
5. Simplificar interfaces

FOCAR EM:
- HephaestusAgent class (muito grande)
- AsyncAgentOrchestrator (complexo)
- InterAgentCommunication (muitas responsabilidades)
- MetaIntelligenceCore (pode ser modularizado)
```

### PROMPT REF-2: Refatoração de Testes

```python
# OBJETIVO: Melhorar cobertura e qualidade dos testes

IMPLEMENTAR:
1. Testes unitários para cada agente
2. Testes de integração entre agentes
3. Testes de carga
4. Testes de falha
5. Testes de performance

CRIAR:
- TestUtils class para helpers
- MockAgents para testes isolados
- PerformanceTestSuite
- IntegrationTestSuite
- ChaosTestSuite
```

### PROMPT REF-3: Refatoração de Configuração

```python
# OBJETIVO: Melhorar sistema de configuração

IMPLEMENTAR:
1. Configuração hierárquica
2. Validação de configuração
3. Hot-reloading de configs
4. Profiles de ambiente
5. Documentação automática

CRIAR:
- ConfigValidator class
- ConfigHotReloader class
- ProfileManager class
- ConfigDocGenerator class
- EnvConfigLoader class
```

---

## 📊 PROMPTS DE MONITORAMENTO

### PROMPT MON-1: Dashboards Inteligentes

```python
# OBJETIVO: Criar dashboards que se adaptam

IMPLEMENTAR:
1. Layout dinâmico baseado em contexto
2. Widgets que se auto-organizam
3. Alertas visuais inteligentes
4. Drill-down automático
5. Personalizações que aprendem

FUNCIONALIDADES:
- Detecção de padrões visuais
- Sugestão de métricas relevantes
- Auto-refresh inteligente
- Exportação de insights
- Compartilhamento colaborativo
```

### PROMPT MON-2: Alertas Inteligentes

```python
# OBJETIVO: Sistema de alertas que evita ruído

IMPLEMENTAR:
1. Correlação de eventos
2. Supressão de alertas redundantes
3. Escalação automática
4. Contextualização de alertas
5. Sugestões de ação

FUNCIONALIDADES:
- Machine learning para padrões
- Feedback loop para melhorias
- Integração com sistemas externos
- Alertas preditivos
- Auto-resolução quando possível
```

---

## 🎯 IMPLEMENTAÇÃO PRÁTICA

### Fase 1: Otimizações Críticas (1-2 semanas)
```bash
# Prioridade máxima
1. PROMPT T1: AsyncAgentOrchestrator
2. PROMPT T2: InterAgentCommunication
3. PROMPT FIX-2: API FastAPI
4. PROMPT T5: Sistema de Cache
```

### Fase 2: Novas Funcionalidades (2-3 semanas)
```bash
# Funcionalidades que agregam valor
1. PROMPT NEW-1: Métricas Avançado
2. PROMPT NEW-3: Aprendizado Contínuo
3. PROMPT MON-1: Dashboards Inteligentes
4. PROMPT T3: MetaIntelligenceCore
```

### Fase 3: Qualidade e Manutenibilidade (1-2 semanas)
```bash
# Solidificar a base
1. PROMPT REF-1: Refatoração do Core
2. PROMPT REF-2: Refatoração de Testes
3. PROMPT DIAG-1: Análise de Performance
4. PROMPT DIAG-3: Análise de Segurança
```

---

## 📋 CHECKLIST DE EXECUÇÃO

### Para cada prompt:
- [ ] Analisar código existente
- [ ] Identificar dependências
- [ ] Criar branch específico
- [ ] Implementar incrementalmente
- [ ] Testar isoladamente
- [ ] Validar com métricas
- [ ] Documentar mudanças
- [ ] Fazer merge com validação

### Métricas de sucesso:
- [ ] Performance melhorou X%
- [ ] Qualidade de resposta melhorou
- [ ] Tempo de resposta reduziu
- [ ] Estabilidade aumentou
- [ ] Cobertura de testes aumentou

---

*Este documento contém prompts técnicos específicos baseados na análise real do código do projeto Hephaestus. Cada prompt foi criado considerando as implementações atuais e oportunidades de melhoria identificadas.*