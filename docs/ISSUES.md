# Histórico de Issues Relevantes

*Nota: Para o rastreamento de issues atuais e novas, por favor, utilize o sistema de Issues do GitHub deste repositório.*

## Corrigir teste `test_update_project_manifest_happy_path`

**Descrição:**  
O teste `test_update_project_manifest_happy_path` estava falhando porque o arquivo `utils.py` estava sendo incluído na seção de conteúdo completo do manifesto, mesmo não sendo um arquivo alvo. Foi necessário ajustar a lógica do scanner para incluir apenas os arquivos especificados em `target_files`.

**Passos para reproduzir (histórico):**
1. Executar `pytest tests/test_project_scanner.py::test_update_project_manifest_happy_path` (antes da correção).
2. Observava-se que o teste falhava porque o conteúdo de `utils.py` aparecia na seção 3 do manifesto.

**Comportamento esperado (e atual):**
Apenas os arquivos especificados em `target_files` (no caso do teste, `main.py` e `data.json`) devem aparecer na seção "CONTEÚDO COMPLETO DOS ARQUIVOS ALVO" do manifesto gerado para o teste.

**Prioridade:** Alta (no momento da ocorrência)
**Status:** Fechado
**Atribuído a:** N/A (resolvido no desenvolvimento)
**Rótulos:** bug, testes, project-scanner

---
