# 🚀 Guia de Configuração MCP no Cursor IDE

Este guia explica como configurar e usar o Servidor MCP Hephaestus no Cursor IDE para ter acesso às capacidades de auto-aprimoramento recursivo (RSI) e meta-inteligência.

## 📋 Pré-requisitos

- Cursor IDE instalado
- Python 3.8+ instalado
- Dependências do projeto instaladas
- Servidor MCP Hephaestus funcionando

## 🔧 Configuração Passo a Passo

### 1. Verificar Dependências MCP

```bash
# Instalar dependências MCP se necessário
pip install mcp fastmcp

# Verificar se o servidor funciona
python3 test_mcp_simple.py
```

### 2. Configurar o Cursor IDE

#### Opção A: Configuração via Settings (Recomendado)

1. **Abra o Cursor IDE**
2. **Vá para Settings** (`Ctrl+,` ou `Cmd+,`)
3. **Procure por "MCP"** na barra de pesquisa
4. **Adicione a configuração do servidor**:

```json
{
  "mcpServers": {
    "hephaestus": {
      "command": "python3",
      "args": [
        "/home/arthur/projects/agente_autonomo/hephaestus_mcp_server.py",
        "stdio"
      ],
      "env": {
        "PYTHONPATH": "/home/arthur/projects/agente_autonomo",
        "HEPHAESTUS_MODE": "mcp"
      }
    }
  }
}
```

#### Opção B: Configuração via Arquivo

1. **Crie/edite o arquivo de configuração do Cursor**:
   - Linux: `~/.cursor/mcp_settings.json`
   - macOS: `~/Library/Application Support/Cursor/mcp_settings.json`
   - Windows: `%APPDATA%\Cursor\mcp_settings.json`

2. **Adicione a configuração**:
```json
{
  "mcpServers": {
    "hephaestus": {
      "command": "python3",
      "args": [
        "/home/arthur/projects/agente_autonomo/hephaestus_mcp_server.py",
        "stdio"
      ],
      "env": {
        "PYTHONPATH": "/home/arthur/projects/agente_autonomo",
        "HEPHAESTUS_MODE": "mcp"
      }
    }
  }
}
```

### 3. Reiniciar o Cursor IDE

Após configurar, reinicie o Cursor IDE para carregar as configurações MCP.

## 🎯 Como Usar as Ferramentas MCP

### Ferramentas Disponíveis

O servidor MCP Hephaestus expõe as seguintes ferramentas:

#### 🔍 `analyze_code` - Análise de Código com RSI
```
Analisa código usando capacidades de auto-aprimoramento recursivo
Parâmetros:
- code: Código a ser analisado
- context: Contexto adicional (opcional)
```

#### 🎯 `generate_objective` - Geração Inteligente de Objetivos
```
Gera objetivos usando o sistema Brain do Hephaestus
Parâmetros:
- context: Contexto ou problema a resolver
- type: Tipo de objetivo (standard, capacitation)
```

#### 🔄 `execute_rsi_cycle` - Ciclo de Auto-Aprimoramento
```
Executa um ciclo completo de auto-aprimoramento recursivo
Parâmetros:
- objective: Objetivo a ser executado
- area: Área de foco (opcional)
```

#### 🧠 `meta_intelligence_report` - Relatório de Meta-Inteligência
```
Gera relatório completo da meta-inteligência do sistema
Sem parâmetros
```

#### 📊 `performance_analysis` - Análise de Performance
```
Análise profunda de performance usando múltiplos sistemas
Sem parâmetros
```

#### 🧬 `evolve_capabilities` - Evolução de Capacidades
```
Evolui as capacidades do sistema usando meta-inteligência
Parâmetros:
- focus_area: Área de foco para evolução (opcional)
```

#### 🔧 `system_status` - Status do Sistema
```
Status geral do sistema Hephaestus
Sem parâmetros
```

### Recursos Disponíveis

#### 📄 `hephaestus://status` - Status Detalhado
Status completo do sistema em tempo real

#### 🎯 `hephaestus://capabilities` - Capacidades do Sistema
Lista detalhada de todas as capacidades disponíveis

#### 🧠 `hephaestus://memory` - Memória do Sistema
Acesso à memória e histórico do sistema

## 💡 Exemplos de Uso no Cursor

### Exemplo 1: Analisar Código Python

1. **Selecione um código Python no editor**
2. **Abra o chat do Cursor** (`Ctrl+L` ou `Cmd+L`)
3. **Use o comando**:
```
@hephaestus analyze_code com o código selecionado
```

### Exemplo 2: Gerar Objetivo para Otimização

**No chat do Cursor**:
```
@hephaestus generate_objective para otimizar performance de algoritmos recursivos
```

### Exemplo 3: Executar Ciclo RSI

**No chat do Cursor**:
```
@hephaestus execute_rsi_cycle para melhorar análise de código
```

### Exemplo 4: Obter Relatório de Meta-Inteligência

**No chat do Cursor**:
```
@hephaestus meta_intelligence_report
```

## 🔍 Verificação da Configuração

### Teste Rápido

1. **Abra o chat do Cursor**
2. **Digite**: `@hephaestus system_status`
3. **Você deve ver**: Status detalhado do sistema Hephaestus

### Teste Completo

1. **Use o comando**: `@hephaestus analyze_code`
2. **Cole um código simples**:
```python
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
```
3. **Você deve receber**: Análise detalhada com insights RSI

## 🚨 Solução de Problemas

### Problema: Servidor não conecta
**Solução**:
```bash
# Verificar se o servidor está rodando
python3 test_mcp_simple.py

# Reiniciar servidor se necessário
python3 run_mcp.py stdio
```

### Problema: Ferramentas não aparecem
**Solução**:
1. Verificar configuração MCP no Cursor
2. Reiniciar o Cursor IDE
3. Verificar logs do servidor

### Problema: Erros de dependências
**Solução**:
```bash
# Instalar dependências
pip install -r requirements_mcp.txt

# Verificar instalação
python3 -c "import mcp.server.fastmcp; print('MCP OK')"
```

## 🎉 Capacidades Avançadas

### Auto-Aprimoramento Recursivo (RSI)
- Análise de código com insights evolutivos
- Otimização automática de algoritmos
- Sugestões de melhorias baseadas em IA

### Meta-Inteligência
- Sistema de auto-reflexão cognitiva
- Evolução de prompts por algoritmos genéticos
- Criação automática de novos agentes

### Análise Profunda
- Métricas de complexidade avançadas
- Detecção de padrões e anti-padrões
- Recomendações contextualizadas

## 📚 Recursos Adicionais

- [Documentação MCP](https://modelcontextprotocol.io/)
- [Guia do Cursor IDE](https://docs.cursor.com/)
- [Capacidades do Hephaestus](docs/CAPABILITIES.md)

## 🔗 Links Úteis

- **Repositório**: [Hephaestus Agent](https://github.com/MrDeox/agente_autonomo)
- **Issues**: [Reportar Problemas](https://github.com/MrDeox/agente_autonomo/issues)
- **Documentação**: [Docs Completa](docs/)

---

🚀 **Agora você tem acesso às capacidades de auto-aprimoramento recursivo e meta-inteligência diretamente no Cursor IDE!** 