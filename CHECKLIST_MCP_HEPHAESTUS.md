# ✅ Checklist: Servidor MCP Hephaestus

## 📋 Verificação Rápida - Siga Esta Ordem!

### 1. ✅ Arquivos Criados
- [ ] `hephaestus_mcp_server.py` - Servidor principal
- [ ] `cursor_mcp_config.json` - Configuração Cursor
- [ ] `MCP_SETUP_GUIDE.md` - Guia detalhado
- [ ] `README_MCP_HEPHAESTUS.md` - Instruções finais
- [ ] `pyproject.toml` - Atualizado com dependências MCP

### 2. ✅ Ambiente Python
- [ ] Python 3.10+ instalado (`python3 --version`)
- [ ] Está na raiz do projeto Hephaestus
- [ ] Poetry instalado OU pip3 funcionando

### 3. ✅ Dependências MCP
```bash
# Escolha UMA opção:

# Opção 1 - Poetry (recomendado)
poetry install

# Opção 2 - pip3
pip3 install mcp httpx websockets pydantic
```
- [ ] Dependências instaladas sem erro

### 4. ✅ Teste Rápido do Servidor
```bash
# Teste se o servidor pode iniciar
python3 hephaestus_mcp_server.py stdio
```
- [ ] Servidor inicia sem erro fatal
- [ ] Vê mensagem "🚀 Iniciando Servidor MCP Hephaestus"
- [ ] Vê "✅ HephaestusAgent inicializado" (pode demorar)

### 5. ✅ Configuração Cursor IDE

#### A. Abrir Configuração
- [ ] Cursor IDE aberto
- [ ] Settings (Ctrl+,) → Procurar "MCP"
- [ ] Clicar "Add MCP Server"

#### B. Adicionar Configuração
Cole exatamente isso:
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
- [ ] Configuração adicionada
- [ ] Salvou configuração
- [ ] Reiniciou o Cursor

### 6. ✅ Teste no Cursor

#### A. Iniciar Servidor
```bash
python3 hephaestus_mcp_server.py stdio
```
- [ ] Servidor rodando em terminal

#### B. Testar no Cursor
- [ ] Abriu chat no Cursor
- [ ] Digitou `@` e viu "hephaestus" na lista
- [ ] Selecionou "hephaestus"
- [ ] Testou `@hephaestus system_status`

### 7. ✅ Teste de Ferramentas

Teste cada ferramenta:
- [ ] `@hephaestus system_status` - Status do sistema
- [ ] `@hephaestus analyze_code` - Cole um código simples
- [ ] `@hephaestus generate_objective "teste"` - Gerar objetivo
- [ ] `@hephaestus meta_intelligence_report` - Relatório meta

## 🚨 Se Algo Der Errado

### ❌ Servidor não inicia
```bash
# Verifique imports
python3 -c "import sys; sys.path.insert(0, '.'); import agent.hephaestus_agent"
```
- Se der erro: dependências faltando
- Se OK: continue

### ❌ Cursor não vê servidor
1. Servidor está rodando?
2. Configuração JSON está correta?
3. Reiniciou o Cursor após configurar?

### ❌ Ferramentas não respondem
1. Aguarde inicialização completa (pode demorar 1-2 min)
2. Use `@hephaestus system_status` primeiro
3. Se persistir, reinicie servidor

## 🎯 Teste Final de Sucesso

Se conseguir fazer isto, está 100% funcionando:

1. **Servidor rodando** em um terminal
2. **Digite no chat do Cursor:**
   ```
   @hephaestus analyze_code
   ```
3. **Cole este código:**
   ```python
   def fibonacci(n):
       if n <= 1:
           return n
       return fibonacci(n-1) + fibonacci(n-2)
   ```
4. **Recebeu análise RSI completa?** ✅ **SUCESSO!**

## 🎉 Próximos Passos

Após passar no checklist:
1. 📖 Leia `README_MCP_HEPHAESTUS.md` para exemplos avançados
2. 🧪 Experimente todas as 7 ferramentas disponíveis
3. 🚀 Explore capacidades de auto-aprimoramento recursivo!

---

**🔥 Bem-vindo ao futuro da IA com auto-aprimoramento recursivo!**