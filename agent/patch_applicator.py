"""Utilities for applying textual patches to files.

The functions here are used by the agent to modify project files.  Each
instruction describes an ``INSERT``, ``REPLACE`` or ``DELETE_BLOCK``
operation and this module executes them.
"""

import os
import re
import logging
from pathlib import Path


def _handle_insert(full_path: Path, lines: list[str], instruction: dict,
                   logger: logging.Logger) -> tuple[bool, list[str]]:
    """Apply an INSERT patch and return ``(success, updated_lines)``."""
    content = instruction.get("content", "")
    if not isinstance(content, list):
        insert_lines = content.splitlines()
    else:
        insert_lines = [str(line) for line in content]

    line_number = instruction.get("line_number")
    if line_number is not None:
        try:
            line_number = int(line_number)
            if line_number <= 0:
                logger.warning(
                    f"line_number {line_number} inválido para INSERT em '{full_path}', usando 1.")
                line_number = 1
        except ValueError:
            logger.error(
                f"line_number '{line_number}' inválido para INSERT em '{full_path}'. Pulando patch.")
            return False, lines
        idx = min(max(0, line_number - 1), len(lines))
    else:
        idx = len(lines)

    lines[idx:idx] = insert_lines
    logger.debug(
        f"Conteúdo inserido em '{full_path}' na linha {line_number if line_number else 'final'}.")
    return True, lines


def _handle_replace(full_path: Path, lines: list[str], instruction: dict,
                    logger: logging.Logger) -> tuple[bool, list[str], bool]:
    """Apply a REPLACE patch.

    Returns ``(success, updated_lines, skip_write)`` where ``skip_write``
    signals that the caller should not rewrite the file (e.g. when the file
    was deleted).
    """
    pattern = instruction.get("block_to_replace")
    content = instruction.get("content", "")
    if not isinstance(content, list):
        new_lines = content.splitlines()
    else:
        new_lines = [str(line) for line in content]

    if pattern is None:
        logger.info(
            f"REPLACE sem 'block_to_replace' para '{full_path}'. Arquivo será sobrescrito.")
        return True, new_lines, False

    file_content = "\n".join(lines)
    is_regex = instruction.get("is_regex", False) or any(c in pattern for c in r"*+?^$[]{}()|\\")

    replaced = False
    if is_regex:
        try:
            mod, num = re.subn(pattern, "\n".join(new_lines), file_content,
                                count=0, flags=re.MULTILINE | re.DOTALL)
            if num > 0:
                lines = mod.splitlines()
                logger.debug(
                    f"Bloco(s) regex '{pattern}' substituído(s) em '{full_path}' ({num} ocorrências).")
                replaced = True
            else:
                logger.warning(
                    f"Padrão regex '{pattern}' não encontrado em '{full_path}' para REPLACE.")
        except re.error as e:
            logger.error(
                f"Erro de regex em 'block_to_replace':'{pattern}' para '{full_path}'. Erro: {e}. Tentando como string literal.")
            if pattern in file_content:
                mod = file_content.replace(pattern, "\n".join(new_lines), 1)
                lines = mod.splitlines()
                logger.debug(
                    f"Bloco '{pattern}' (literal fallback) substituído em '{full_path}'.")
                replaced = True
            else:
                logger.warning(
                    f"Bloco '{pattern}' (literal fallback) não encontrado em '{full_path}' para REPLACE.")
    else:
        if pattern in file_content:
            mod = file_content.replace(pattern, "\n".join(new_lines), 1)
            lines = mod.splitlines()
            logger.debug(
                f"Bloco literal '{pattern}' substituído em '{full_path}'.")
            replaced = True
        else:
            if full_path.exists():
                logger.warning(
                    f"Bloco literal '{pattern}' não encontrado em '{full_path}' para REPLACE.")
            else:
                logger.error(
                    f"Tentativa de REPLACE de bloco específico '{pattern}' em arquivo inexistente '{full_path}'. Pulando.")
                return False, lines, True

    if not replaced and full_path.exists():
        logger.warning(
            f"Nenhuma substituição realizada para '{pattern}' em '{full_path}'.")
    elif not full_path.exists():
        logger.info(f"Arquivo '{full_path}' será criado com o novo conteúdo.")

    return True, lines, False


def _handle_delete_block(full_path: Path, lines: list[str], instruction: dict,
                         logger: logging.Logger) -> tuple[bool, list[str], bool]:
    """Apply a DELETE_BLOCK patch."""
    pattern = instruction.get("block_to_delete")
    if pattern is None:
        if full_path.exists():
            try:
                os.remove(full_path)
                logger.info(
                    f"Arquivo '{full_path}' removido com sucesso (DELETE_BLOCK com block_to_delete=None).")
            except Exception as e:
                logger.error(f"Falha ao remover arquivo '{full_path}': {e}")
                return False, lines, True
        else:
            logger.warn(
                f"Arquivo '{full_path}' não existe. Nada para deletar com DELETE_BLOCK.")
        return True, lines, True

    if not pattern:
        logger.error(
            f"Operação DELETE_BLOCK para '{full_path}' não especificou 'block_to_delete' válido. Pulando.")
        return False, lines, True

    if not full_path.exists():
        logger.warn(
            f"Arquivo '{full_path}' não existe. Nada para deletar com DELETE_BLOCK.")
        return True, lines, True

    file_content = "\n".join(lines)
    is_regex = instruction.get("is_regex", False) or any(c in pattern for c in r"*+?^$[]{}()|\\")

    deleted = False
    if is_regex:
        try:
            mod, num = re.subn(pattern, "", file_content, count=0,
                               flags=re.MULTILINE | re.DOTALL)
            if num > 0:
                temp_lines = mod.splitlines()
                lines = [line for i, line in enumerate(temp_lines)
                         if line.strip() or (i > 0 and temp_lines[i-1].strip())
                         or (i < len(temp_lines) - 1 and temp_lines[i+1].strip())]
                logger.debug(
                    f"Bloco(s) regex '{pattern}' deletado(s) em '{full_path}' ({num} ocorrências).")
                deleted = True
            else:
                logger.warning(
                    f"Padrão regex '{pattern}' não encontrado em '{full_path}' para DELETE_BLOCK.")
        except re.error as e:
            logger.error(
                f"Erro de regex em 'block_to_delete': '{pattern}'. Erro: {e}. Tentando como literal.")
            if pattern in file_content:
                mod = file_content.replace(pattern, "", 1)
                lines = mod.splitlines()
                logger.debug(
                    f"Bloco '{pattern}' (literal fallback) deletado em '{full_path}'.")
                deleted = True
            else:
                logger.warning(
                    f"Bloco '{pattern}' (literal fallback) não encontrado em '{full_path}' para DELETE_BLOCK.")
    else:
        if pattern in file_content:
            mod = file_content.replace(pattern, "", 1)
            lines = mod.splitlines()
            logger.debug(
                f"Bloco literal '{pattern}' deletado em '{full_path}'.")
            deleted = True
        else:
            logger.warning(
                f"Bloco literal '{pattern}' não encontrado em '{full_path}' para DELETE_BLOCK.")

    if deleted:
        pass
    elif full_path.exists():
        logger.warning(
            f"Nenhuma deleção realizada para '{pattern}' em '{full_path}'.")

    return True, lines, False

def apply_patches(instructions: list[dict], logger: logging.Logger, base_path: str = "."):
    """
    Aplica uma lista de instruções de patch aos arquivos.

    Args:
        instructions: Uma lista de dicionários, onde cada dicionário representa um patch.
                      Formato esperado por patch:
                      {
                          "file_path": "caminho/para/o/arquivo.py",
                          "operation": "INSERT" | "REPLACE" | "DELETE_BLOCK",
                          # Campos específicos da operação abaixo
                          "line_number": 10, # Para INSERT (opcional, 1-based)
                          "content": "novo conteúdo...", # Para INSERT, REPLACE
                          "block_to_replace": "bloco a ser substituído", # Para REPLACE
                          "block_to_delete": "bloco a ser deletado" # Para DELETE_BLOCK
                      }
        logger: Instância do logger para registrar informações e erros.
        base_path: Caminho base para resolver os file_path relativos.

    Returns:
        bool: True se todas as operações foram bem-sucedidas (ou pelo menos tentadas sem exceção crítica),
              False se ocorreu um erro que impediu a aplicação de um ou mais patches.
              Nota: Erros de arquivo não encontrado para uma instrução específica não necessariamente
              retornam False globalmente, mas são logados. A falha é mais para exceções inesperadas.
    """

    overall_success = True
    processed_files = set()

    if base_path != ".":
        logger.info(f"Aplicando patches com base_path: '{Path(base_path).resolve()}'")
    else:
        logger.info("Aplicando patches com base_path: '.' (diretório atual)")

    for i, instruction in enumerate(instructions):
        file_path_str = instruction.get("file_path")
        operation = instruction.get("operation")

        if not file_path_str or not operation:
            logger.error(
                f"Patch inválido (sem file_path ou operation) na instrução {i+1}: {instruction}")
            overall_success = False
            continue

        normalized = Path(os.path.normpath(file_path_str))
        full_path = Path(base_path).resolve() / normalized

        processed_files.add(str(full_path))
        logger.info(f"Processando patch {i+1}/{len(instructions)}: {operation} em '{full_path}'")

        lines: list[str] = []
        if full_path.exists():
            with open(full_path, "r", encoding="utf-8") as f:
                lines = f.read().splitlines()
        elif operation not in ["INSERT", "REPLACE"]:
            logger.warning(
                f"Operação '{operation}' em arquivo inexistente '{full_path}'. Pulando.")
            continue

        full_path.parent.mkdir(parents=True, exist_ok=True)

        skip_write = False
        success = True
        if operation == "INSERT":
            success, lines = _handle_insert(full_path, lines, instruction, logger)
        elif operation == "REPLACE":
            success, lines, skip_write = _handle_replace(full_path, lines, instruction, logger)
        elif operation == "DELETE_BLOCK":
            success, lines, skip_write = _handle_delete_block(full_path, lines, instruction, logger)
        else:
            logger.error(f"Operação desconhecida '{operation}' para o arquivo '{full_path}'. Pulando.")
            overall_success = False
            continue

        overall_success &= success

        if not skip_write:
            with open(full_path, "w", encoding="utf-8") as f:
                f.write("\n".join(lines))
            logger.info(f"Arquivo '{full_path}' salvo com sucesso após operação '{operation}'.")

    if overall_success:
        logger.info(
            f"Todas as {len(instructions)} instruções de patch processadas. Arquivos afetados (tentativas): {processed_files}")
    else:
        logger.warning(
            f"Algumas instruções de patch falharam ou foram puladas. Verifique os logs. Arquivos afetados (tentativas): {processed_files}")

    return overall_success
# Exemplo de uso (para teste manual, se necessário):
if __name__ == '__main__':
    test_logger = logging.getLogger("patch_applicator_test")
    test_logger.setLevel(logging.DEBUG)
    console_handler_test = logging.StreamHandler()
    console_handler_test.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    if not test_logger.handlers: # Evitar adicionar handlers duplicados em re-execuções (ex: no notebook)
        test_logger.addHandler(console_handler_test)
    test_logger.propagate = False # Evitar que logs subam para o logger raiz se ele tiver seus próprios handlers

    test_dir_name = "temp_patch_test_apply"
    test_dir = Path(test_dir_name)

    # Limpar diretório de teste anterior, se existir
    if test_dir.exists():
        import shutil
        shutil.rmtree(test_dir)
        test_logger.info(f"Diretório de teste anterior {test_dir} removido.")
    test_dir.mkdir(exist_ok=True)

    file1_orig_content = "Linha 1 do arquivo1\nLinha 2 do arquivo1\n# START_BLOCK_TO_DELETE\nEste bloco será deletado.\nCom múltiplas linhas.\n# END_BLOCK_TO_DELETE\nLinha após o bloco de deleção.\nLinha para ser substituída no arquivo1.\nÚltima linha do arquivo1."
    file1_path = test_dir / "file1.txt"
    with open(file1_path, "w", encoding="utf-8") as f:
        f.write(file1_orig_content)

    file2_orig_content = "def hello_world():\n    print(\"Hello from file2\")\n"
    file2_path = test_dir / "file2.py"
    with open(file2_path, "w", encoding="utf-8") as f:
        f.write(file2_orig_content)

    new_file_path = test_dir / "sub_dir" / "new_file.md" # Testar criação em subdiretório
    # Não criar new_file_path ainda, o patcher deve fazer isso.

    delete_non_existent_file_path = test_dir / "non_existent_for_delete.txt"

    patches_to_test = [
        { # 1. INSERT no início de file1.txt
            "file_path": str(file1_path.relative_to(Path("."))),
            "operation": "INSERT",
            "line_number": 1,
            "content": "### INÍCIO DO ARQUIVO ###"
        },
        { # 2. INSERT no meio de file1.txt
            "file_path": str(file1_path.name), # Testar com nome do arquivo apenas, base_path resolverá
            "operation": "INSERT",
            "line_number": 4, # Após "Linha 2 do arquivo1" e a linha de INSERT 1
            "content": ">>> Linha inserida no meio <<<"
        },
        { # 3. DELETE_BLOCK em file1.txt (usando regex com DOTALL)
            "file_path": str(file1_path), # Testar com path absoluto (convertido de relativo)
            "operation": "DELETE_BLOCK",
            "block_to_delete": r"# START_BLOCK_TO_DELETE.*?# END_BLOCK_TO_DELETE\n", # Regex para pegar tudo entre e o newline final
            "is_regex": True
        },
        { # 4. REPLACE em file1.txt (string literal)
            "file_path": str(file1_path),
            "operation": "REPLACE",
            "block_to_replace": "Linha para ser substituída no arquivo1.",
            "content": ">>> LINHA FOI SUBSTITUÍDA COM SUCESSO <<<"
        },
        { # 5. INSERT no final de file2.py
            "file_path": str(file2_path),
            "operation": "INSERT",
            # sem line_number, deve ir para o final
            "content": "\n# Função adicionada no final\ndef new_function():\n    pass"
        },
        { # 6. CREATE file (new_file.md) com INSERT
            "file_path": str(new_file_path),
            "operation": "INSERT",
            "content": "# Novo Arquivo Markdown\n\nEste arquivo foi criado pelo patch applicator."
        },
        { # 7. REPLACE para sobrescrever file2.py inteiro
            "file_path": str(file2_path),
            "operation": "REPLACE",
            "block_to_replace": None, # Indica sobrescrever o arquivo inteiro
            "content": "# Este arquivo Python foi totalmente sobrescrito.\nprint('Nova versão!')"
        },
        { # 8. DELETE_BLOCK em arquivo que não existe (deve ser pulado com warning)
            "file_path": str(delete_non_existent_file_path),
            "operation": "DELETE_BLOCK",
            "block_to_delete": "qualquer coisa"
        },
        { # 9. INSERT em arquivo que não existe (deve criar o arquivo)
            "file_path": "temp_patch_test_apply/another_new_file.txt", # caminho relativo do root do projeto
            "operation": "INSERT",
            "content": "Conteúdo para outro arquivo novo."
        },
        { # 10. REPLACE em arquivo que não existe (deve criar, tratando block_to_replace: None)
            "file_path": "temp_patch_test_apply/yet_another_new_file.json",
            "operation": "REPLACE",
            "block_to_replace": None,
            "content": "{\n  \"message\": \"Arquivo JSON criado com REPLACE\"\n}"
        },
        { # 11. Falha: REPLACE de bloco específico em arquivo que não existe
            "file_path": "temp_patch_test_apply/fail_replace_non_existent_block.txt",
            "operation": "REPLACE",
            "block_to_replace": "bloco_que_nao_existe_em_arquivo_novo",
            "content": "nao deveria aparecer"
        }
    ]

    test_logger.info(f"Iniciando aplicação de patches. Diretório base para arquivos de patch: '{Path.cwd()}'")
    # Para os testes, como os paths nos patches são relativos ao diretório de teste (ou root),
    # e a função constrói o path a partir de base_path,
    # se file_path for "temp_patch_test_apply/file1.txt", base_path="." está correto.
    # Se file_path for "file1.txt", base_path="temp_patch_test_apply" seria necessário.
    # A convenção mais simples é que file_path seja sempre relativo ao root do projeto.

    # Ajustar file_paths nos patches para serem relativos ao CWD se não forem já absolutos
    # A lógica no apply_patches agora usa `Path(base_path).resolve() / normalized_file_path`
    # então, se base_path=".", e file_path="temp_patch_test_apply/file1.txt", está correto.

    # Para o teste, vamos garantir que os caminhos em `patches_to_test` sejam relativos ao CWD.
    # O file1_path, file2_path, new_file_path são relativos ao test_dir.
    # str(file1_path.relative_to(Path("."))) -> 'temp_patch_test_apply/file1.txt'
    # A função apply_patches espera que file_path seja o caminho que, quando combinado com base_path,
    # resulta no caminho absoluto correto.
    # Se base_path=".", então file_path deve ser "temp_patch_test_apply/file1.txt".

    # Corrigindo os paths no exemplo de teste para serem relativos ao CWD (root do projeto)
    # A forma como foram definidos (ex: str(file1_path.relative_to(Path(".")))) já está correta se
    # o script é rodado do root do projeto.
    # O `base_path` na chamada `apply_patches` deve ser o diretório raiz do projeto.

    # Para o teste, o `file_path` no patch deve ser o caminho relativo ao `base_path`.
    # Se `base_path` é o diretório do projeto, e os arquivos estão em `temp_patch_test_apply/`,
    # então `file_path` deve ser `temp_patch_test_apply/file1.txt`.

    # A lógica de `full_path = Path(base_path).resolve() / normalized_file_path` é a chave.
    # Se `base_path = "."` (cwd), e `file_path = "temp_patch_test_apply/file1.txt"`,
    # `full_path` será `CWD/temp_patch_test_apply/file1.txt`. Isso está correto.

    # Se o patch viesse com `file_path = "file1.txt"`, e o arquivo estivesse em `CWD/temp_patch_test_apply/file1.txt`,
    # então `base_path` deveria ser `"temp_patch_test_apply"`.

    # A convenção mais robusta é:
    # 1. `base_path` é sempre o root do projeto.
    # 2. `file_path` nos patches é sempre relativo ao root do projeto.

    # As paths como `str(file1_path)` são absolutas.
    # Vamos torná-las relativas ao CWD para o teste, assumindo que o CWD é o root do projeto.

    def make_path_project_relative(p_obj: Path, project_root: Path):
        if p_obj.is_absolute():
            try:
                return str(p_obj.relative_to(project_root))
            except ValueError: # Se não for subpath, mantenha absoluto (ou trate o erro)
                return str(p_obj)
        return str(p_obj) # Já é relativo

    project_root_path = Path.cwd()

    # Ajustando os paths nas instruções de teste para serem relativos ao CWD.
    # Os paths como `str(file1_path)` já são absolutos. `apply_patches` vai juntar com `base_path`.
    # Se `base_path` é '.', e `file_path` é absoluto, Path(base_path).resolve() / abs_path pode não funcionar como esperado em todos os OS.
    # `Path(abs_path)` é suficiente se for absoluto.
    # A lógica `Path(base_path).resolve() / normalized_file_path` funciona bem se `normalized_file_path` for relativo.
    # Se `normalized_file_path` for absoluto, o `resolve()` do `base_path` é ignorado.

    # Para o teste, vamos garantir que os `file_path` sejam relativos ao `base_path`="."
    # Ex: `file1_path` (que é `test_dir / "file1.txt"`) deve ser passado como `str(file1_path)`
    # e a função `apply_patches` com `base_path = "."` irá resolver `Path(".").resolve() / file1_path_str`.
    # Isso funciona se `file1_path_str` é relativo.
    # Os paths como `str(file1_path)` são absolutos, então `Path.resolve()` no base_path é ignorado.
    # Isso é ok. `Path(absolute_path)` é o que queremos.

    # Modificando patches_to_test para usar paths que serão interpretados corretamente
    # pela lógica de `full_path` dentro de `apply_patches`.
    # A forma mais simples: `file_path` é relativo ao `base_path`.
    # Se `base_path` é o root do projeto (`.`), então `file_path` deve ser `temp_patch_test_apply/file1.txt`.

    # Ajuste nos patches de teste para usar caminhos relativos ao CWD
    test_patches_final = []
    for p_orig in patches_to_test:
        p_new = p_orig.copy()
        # file_path original é relativo ao root do projeto, ou absoluto.
        # Se é "temp_patch_test_apply/file1.txt", está bom.
        # Se é "file1.txt" e base_path="temp_patch_test_apply", estaria bom.
        # Se é Path_absoluto_para_file1.txt, está bom.
        # A lógica `Path(base_path).resolve() / normalized_file_path` lida com `normalized_file_path`
        # sendo absoluto (ignora `base_path`) ou relativo (concatena com `base_path`).

        # Para o teste, `file_path` em `patches_to_test` já está como `str(Path_obj)`
        # Onde `Path_obj` é algo como `CWD/temp_patch_test_apply/file1.txt`.
        # Então, `Path(base_path).resolve()` será ignorado, e `full_path` será o path absoluto. Isso é ok.
        test_patches_final.append(p_new)


    apply_patches(test_patches_final, test_logger, base_path=".") # base_path="." (CWD)

    test_logger.info("\n--- CONTEÚDO DOS ARQUIVOS APÓS PATCHES ---")
    for p_info in test_patches_final:
        fp_str = p_info["file_path"]
        # fp = Path(fp_str) # Se fp_str é relativo, precisa de base_path
        # Na verdade, precisamos reconstruir o full_path como apply_patches faz, ou usar o fp_str se ele for absoluto
        # Como os paths nos patches de teste são absolutos (str(Path_obj_absoluto)), podemos usá-los diretamente.
        fp = Path(fp_str)
        if fp.exists():
            test_logger.info(f"\nConteúdo de '{fp}':")
            with open(fp, "r", encoding="utf-8") as f_read:
                test_logger.info(f_read.read())
        else:
            test_logger.info(f"\nArquivo '{fp}' NÃO EXISTE após patches.")

    # Verificar o arquivo que deveria falhar ao ser criado por replace de bloco específico
    fail_path = Path("temp_patch_test_apply/fail_replace_non_existent_block.txt")
    if fail_path.exists():
        test_logger.error(f"ERRO DE TESTE: O arquivo {fail_path} EXISTE, mas não deveria.")
    else:
        test_logger.info(f"SUCESSO DE TESTE: O arquivo {fail_path} NÃO EXISTE, como esperado.")

    # Limpeza
    # import shutil
    # shutil.rmtree(test_dir)
    # test_logger.info(f"Diretório de teste {test_dir} removido.")
    test_logger.info(f"\nManter diretório de teste: {test_dir.resolve()}")
