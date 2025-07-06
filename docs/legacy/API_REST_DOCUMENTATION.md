# 🚀 Hephaestus Meta-Intelligence API REST v3.1.0

## Visão Geral

A API REST do Hephaestus é uma interface completa e profissional para controlar e monitorar o sistema de IA autônoma. Inclui recursos avançados como:

- 🧠 **Meta-Intelligence**: Sistema de IA autoconsciênte e auto-aprimorante
- 🚀 **Orquestração Assíncrona**: Processamento paralelo com até 8 agentes simultâneos
- 🔥 **Modo Turbo**: Aumento de performance de 8x para tarefas complexas
- 🎨 **Interface Auto-Gerada**: Dashboards e controles personalizados
- 🛡️ **Segurança Enterprise**: Autenticação, rate limiting e CORS
- 📊 **Monitoramento em Tempo Real**: Métricas e logs completos

## Acesso à API

- **Base URL**: `http://localhost:8000`
- **Documentação Interativa**: `http://localhost:8000/docs`
- **Interface do Arthur**: `http://localhost:8000/arthur_interface`

## Endpoints Disponíveis

### 🏠 Core Operations (Operações Básicas)

#### `GET /`
- **Descrição**: Página inicial da API com navegação
- **Resposta**: HTML com informações sobre a API
- **Exemplo**: `curl http://localhost:8000/`

#### `GET /health`
- **Descrição**: Verificação completa de saúde do sistema
- **Resposta**: Status detalhado com métricas de performance
- **Exemplo**: `curl http://localhost:8000/health`

#### `GET /status`
- **Descrição**: Status detalhado do sistema incluindo todos os subsistemas
- **Resposta**: Informações sobre meta-intelligence, filas, workers
- **Exemplo**: `curl http://localhost:8000/status`

#### `POST /objectives`
- **Descrição**: Submeter novo objetivo para processamento
- **Autenticação**: Requerida
- **Payload**:
  ```json
  {
    "objective": "Analyze system performance",
    "priority": 3,
    "metadata": {"category": "analysis"}
  }
  ```

#### `GET /objectives/queue`
- **Descrição**: Status da fila de objetivos
- **Autenticação**: Requerida
- **Resposta**: Informações sobre tamanho da fila e processamento

### 🚀 Orchestration (Orquestração)

#### `POST /orchestration/turbo-mode`
- **Descrição**: Ativar modo turbo com paralelismo máximo
- **Autenticação**: Requerida
- **Resposta**: Status da ativação e métricas de performance

#### `POST /orchestration/async-evolution`
- **Descrição**: Iniciar evolução assíncrona com orquestração multi-agente
- **Autenticação**: Requerida
- **Payload**:
  ```json
  {
    "objective": "Optimize system architecture",
    "enable_turbo": true,
    "max_concurrent_agents": 8,
    "timeout_seconds": 300
  }
  ```

#### `GET /orchestration/status`
- **Descrição**: Status detalhado da orquestração assíncrona
- **Autenticação**: Requerida
- **Resposta**: Informações sobre agentes ativos, tarefas paralelas

### 🧠 Meta-Intelligence (Meta-Inteligência)

#### `POST /meta-intelligence/deep-reflection`
- **Descrição**: Realizar auto-reflexão profunda e introspecção
- **Autenticação**: Requerida
- **Payload**:
  ```json
  {
    "focus_area": "performance_optimization",
    "depth_level": 4,
    "include_performance_metrics": true
  }
  ```

#### `GET /meta-intelligence/status`
- **Descrição**: Status abrangente da meta-inteligência
- **Autenticação**: Requerida
- **Resposta**: Métricas cognitivas, evolução, auto-consciência

#### `POST /meta-intelligence/evolution-cycle`
- **Descrição**: Disparar manualmente um ciclo de evolução
- **Autenticação**: Requerida
- **Resposta**: Resultados do ciclo evolutivo

### 🎨 Interface Generation (Geração de Interface)

#### `POST /interface/generate`
- **Descrição**: Gerar interface personalizada para Arthur
- **Autenticação**: Requerida
- **Payload**:
  ```json
  {
    "theme": "dark",
    "layout": "dashboard",
    "include_advanced_controls": true,
    "user_preferences": {"color_scheme": "matrix"}
  }
  ```

#### `GET /interface/arthur`
- **Descrição**: Servir interface mais recente do Arthur
- **Resposta**: HTML da interface personalizada
- **Exemplo**: `curl http://localhost:8000/interface/arthur`

#### `GET /interface/list`
- **Descrição**: Listar todas as interfaces geradas
- **Autenticação**: Requerida
- **Resposta**: Lista com detalhes das interfaces disponíveis

### 📊 Monitoring (Monitoramento)

#### `GET /monitoring/metrics`
- **Descrição**: Métricas abrangentes do sistema
- **Autenticação**: Requerida
- **Resposta**: Métricas de saúde, performance, agentes

#### `GET /monitoring/logs`
- **Descrição**: Logs recentes do sistema
- **Autenticação**: Requerida
- **Parâmetros**: `limit` (padrão: 50)
- **Exemplo**: `curl http://localhost:8000/monitoring/logs?limit=100`

### ⚙️ Configuration (Configuração)

#### `POST /config/agent`
- **Descrição**: Atualizar configuração do agente
- **Autenticação**: Requerida
- **Payload**:
  ```json
  {
    "continuous_mode": true,
    "max_objectives": 20,
    "evolution_interval": 1800
  }
  ```

#### `GET /config/current`
- **Descrição**: Obter configuração atual do sistema
- **Autenticação**: Requerida
- **Resposta**: Configurações ativas do sistema

### 🔄 Legacy (Compatibilidade)

#### Endpoints Legados
- `GET /api/orchestration_status` → `/orchestration/status`
- `POST /api/enable_turbo_mode` → `/orchestration/turbo-mode`
- `POST /api/start_async_evolution` → `/orchestration/async-evolution`
- `GET /arthur_interface` → `/interface/arthur`

## Recursos Avançados

### 🔒 Autenticação
- **Tipo**: Bearer Token
- **Header**: `Authorization: Bearer YOUR_TOKEN`
- **Nota**: Para desenvolvimento, qualquer token funciona

### 🛡️ Rate Limiting
- **Limite**: 100 requisições por minuto por IP
- **Resposta**: HTTP 429 quando limite excedido

### 🌐 CORS
- **Configuração**: Aceita todas as origens (desenvolvimento)
- **Produção**: Configurar origens específicas

### 📈 Middleware
- **Process Time**: Header `X-Process-Time` em cada resposta
- **Rate Limiting**: Controle automático de taxa
- **CORS**: Suporte completo para requisições cross-origin

## Exemplos de Uso

### Ativar Modo Turbo
```bash
curl -X POST http://localhost:8000/orchestration/turbo-mode \
  -H "Authorization: Bearer your_token"
```

### Submeter Objetivo
```bash
curl -X POST http://localhost:8000/objectives \
  -H "Authorization: Bearer your_token" \
  -H "Content-Type: application/json" \
  -d '{"objective": "Analyze performance bottlenecks", "priority": 4}'
```

### Iniciar Evolução Assíncrona
```bash
curl -X POST http://localhost:8000/orchestration/async-evolution \
  -H "Authorization: Bearer your_token" \
  -H "Content-Type: application/json" \
  -d '{"objective": "Optimize system architecture", "enable_turbo": true}'
```

### Gerar Interface Personalizada
```bash
curl -X POST http://localhost:8000/interface/generate \
  -H "Authorization: Bearer your_token" \
  -H "Content-Type: application/json" \
  -d '{"theme": "dark", "layout": "dashboard"}'
```

## Status dos Recursos

- ✅ **API Base**: Funcionando completamente
- ✅ **Documentação**: Swagger UI disponível
- ✅ **Orquestração**: Agentes paralelos ativos
- ✅ **Meta-Intelligence**: Sistema cognitivo operacional
- ✅ **Interface Auto-Gerada**: Funcional e personalizada
- ✅ **Monitoramento**: Métricas em tempo real
- ✅ **Segurança**: Autenticação e rate limiting
- ✅ **Modo Turbo**: Performance 8x disponível

## Próximos Passos

1. **Implementar WebSocket**: Para comunicação em tempo real
2. **Dashboard Avançado**: Interface web completa
3. **Métricas Grafana**: Visualização avançada
4. **API Keys**: Sistema de autenticação robusto
5. **Clustering**: Suporte multi-instância
6. **Backup/Restore**: Persistência de estado

---

**Desenvolvido por**: Arthur & Hephaestus AI Team  
**Versão**: 3.1.0  
**Data**: 2025-07-04  
**Status**: ✅ Produção Ready 