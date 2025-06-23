# Issues

## Corrigir teste test_update_project_manifest_happy_path

**Descrição:**  
O teste `test_update_project_manifest_happy_path` está falhando porque o arquivo `utils.py` está sendo incluído na seção de conteúdo completo do manifesto, mesmo não sendo um arquivo alvo. Precisamos ajustar a lógica do scanner para incluir apenas os arquivos especificados em `target_files`.

**Passos para reproduzir:**
1. Executar `pytest tests/test_project_scanner.py::test_update_project_manifest_happy_path`
2. Observar que o teste falha porque o conteúdo de `utils.py` aparece na seção 3 do manifesto

**Comportamento esperado:**  
Apenas os arquivos especificados em `target_files` (neste caso `main.py` e `data.json`) devem aparecer na seção "CONTEÚDO COMPLETO DOS ARQUIVOS ALVO".

**Prioridade:** Alta
**Status:** Aberto
**Atribuído a:** 
**Labels:** bug, tests, project-scanner

---
