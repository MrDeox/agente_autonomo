# 🚀 Servidor MCP Hephaestus - Setup para Cursor IDE

## ✨ O que é isso?

O **Servidor MCP Hephaestus** expõe todas as capacidades avançadas do agente de auto-aprimoramento recursivo (RSI) via Model Context Protocol, permitindo usar as funcionalidades do Hephaestus diretamente no Cursor IDE.

## 🎯 Capacidades Principais

- **🔄 Auto-aprimoramento recursivo (RSI)** - Ciclos completos de evolução automática
- **🧠 Meta-inteligência** - Sistema de meta-cognição com algoritmos genéticos
- **🔍 Análise de código avançada** - Insights profundos com sugestões RSI
- **🎯 Geração inteligente de objetivos** - Sistema Brain contextualizado
- **📊 Análise de performance** - Métricas e otimizações múltiplas
- **🧬 Evolução de capacidades** - Criação automática de novos agentes

## 📦 Instalação Rápida

### 1. Instalar Dependências MCP

```bash
# Via Poetry (recomendado)
poetry install

# Ou via pip
pip install mcp httpx websockets pydantic
```

### 2. Configurar Cursor IDE

1. **Abra o Cursor IDE**
2. **Vá em Settings** (Ctrl+, ou File > Preferences > Settings)
3. **Procure por "MCP"** na barra de pesquisa
4. **Clique em "Add MCP Server"**
5. **Cole esta configuração:**

```json
{
  "mcpServers": {
    "hephaestus": {
      "command": "python3",
      "args": ["hephaestus_mcp_server.py", "stdio"],
      "env": {
        "PYTHONPATH": ".",
        "PYTHONIOENCODING": "utf-8"
      }
    }
  }
}
```

6. **Salve e reinicie o Cursor**

### 3. Iniciar o Servidor

```bash
python3 hephaestus_mcp_server.py stdio
```

## 🚀 Como Usar no Cursor

1. **Digite `@` no chat do Cursor**
2. **Selecione "hephaestus"** na lista
3. **Use as ferramentas disponíveis:**

### 🛠️ Ferramentas Disponíveis

#### `analyze_code` - Análise RSI de Código
```
@hephaestus analyze_code
```
Depois cole seu código para análise completa com insights de auto-aprimoramento.

#### `generate_objective` - Geração Inteligente de Objetivos
```
@hephaestus generate_objective "Melhorar performance do algoritmo"
```

#### `execute_rsi_cycle` - Auto-Aprimoramento Completo
```
@hephaestus execute_rsi_cycle "Otimizar função de ordenação"
```

#### `meta_intelligence_report` - Relatório de Meta-Inteligência
```
@hephaestus meta_intelligence_report
```

#### `performance_analysis` - Análise Profunda de Performance
```
@hephaestus performance_analysis
```

#### `evolve_capabilities` - Evolução de Capacidades
```
@hephaestus evolve_capabilities "code_analysis"
```

#### `system_status` - Status do Sistema
```
@hephaestus system_status
```

## 🎯 Exemplos Práticos

### Analisar Código Python
1. Use `@hephaestus analyze_code`
2. Cole seu código
3. Receba análise RSI completa com sugestões de melhorias

### Gerar Objetivo de Melhoria
1. Use `@hephaestus generate_objective "Problema ou contexto"`
2. Receba objetivo inteligente gerado pelo sistema Brain

### Executar Auto-Aprimoramento
1. Use `@hephaestus execute_rsi_cycle "Objetivo específico"`
2. Veja o sistema se aprimorar automaticamente

## 🔧 Solução de Problemas

### ❌ Servidor não inicia
- Verifique se está na raiz do projeto Hephaestus
- Instale todas as dependências
- Verifique logs para erros específicos

### ❌ Cursor não reconhece servidor
- Verifique a configuração MCP
- Reinicie o Cursor após configurar
- Confirme que o servidor está rodando

### ❌ Ferramentas não respondem
- Use `system_status` para verificar estado
- Reinicie o servidor se necessário
- Verifique se todas as dependências estão instaladas

## 🎉 Pronto!

Agora você tem acesso completo às capacidades de **auto-aprimoramento recursivo** do Hephaestus diretamente no Cursor IDE!

### 🔥 Recursos Únicos do Hephaestus MCP:

- **RSI Real**: Verdadeiro auto-aprimoramento recursivo
- **Meta-Inteligência**: Sistema que evolui a si mesmo
- **Algoritmos Genéticos**: Evolução automática de prompts
- **Criação de Agentes**: Gera novos agentes automaticamente
- **Análise Profunda**: Insights únicos de código e performance

**Divirta-se explorando o futuro da IA! 🚀**