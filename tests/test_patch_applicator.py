# tests/test_patch_applicator.py
import pytest
import logging
from pathlib import Path
import os # Para os.path.normpath
from agent.patch_applicator import apply_patches

# Logger para os testes do patch_applicator
# Pode ser útil ter um logger dedicado ou usar o caplog do pytest
patch_logger = logging.getLogger("test_patch_applicator")
patch_logger.setLevel(logging.DEBUG)
# Se precisar ver os logs durante o teste:
# import sys
# handler = logging.StreamHandler(sys.stdout)
# patch_logger.addHandler(handler)


@pytest.fixture
def test_files_dir(tmp_path: Path) -> Path:
    """Cria um diretório base para os arquivos de teste dentro de tmp_path."""
    test_dir = tmp_path / "patch_test_ws"
    test_dir.mkdir()
    return test_dir

# Helper para verificar conteúdo do arquivo
def check_file_content(file_path: Path, expected_lines: list[str]):
    assert file_path.exists(), f"Arquivo {file_path} deveria existir."
    content = file_path.read_text(encoding="utf-8")
    actual_lines = content.splitlines() # splitlines() remove newlines finais vazias

    # Normalizar newlines esperados e atuais para comparação
    # Se expected_lines vem de uma string multiline, pode ter newlines diferentes
    normalized_expected = [line.rstrip('\r\n') for line in expected_lines]
    normalized_actual = [line.rstrip('\r\n') for line in actual_lines]

    assert normalized_actual == normalized_expected, \
        f"Conteúdo de {file_path} não esperado.\nAtual:\n{normalized_actual}\nEsperado:\n{normalized_expected}"

# --- Testes para Operação INSERT ---

def test_insert_into_existing_file_start(test_files_dir: Path):
    file_path = test_files_dir / "file_to_insert.txt"
    file_path.write_text("Linha1\nLinha2")
    patches = [{
        "file_path": str(file_path), "operation": "INSERT",
        "line_number": 1, "content": "NovaLinhaNoInicio"
    }]
    apply_patches(patches, patch_logger, base_path=str(test_files_dir.parent)) # base_path é o pai de test_files_dir
    check_file_content(file_path, ["NovaLinhaNoInicio", "Linha1", "Linha2"])

def test_insert_into_existing_file_middle(test_files_dir: Path):
    file_path = test_files_dir / "file_insert_middle.txt"
    file_path.write_text("Linha1\nLinha2\nLinha3")
    patches = [{
        "file_path": str(file_path), "operation": "INSERT",
        "line_number": 3, "content": "NovaLinhaNoMeio1\nNovaLinhaNoMeio2"
    }]
    apply_patches(patches, patch_logger, base_path=str(test_files_dir.parent))
    check_file_content(file_path, ["Linha1", "Linha2", "NovaLinhaNoMeio1", "NovaLinhaNoMeio2", "Linha3"])

def test_insert_into_existing_file_end_with_line_number(test_files_dir: Path):
    file_path = test_files_dir / "file_insert_end_ln.txt"
    file_path.write_text("Linha1\nLinha2")
    patches = [{
        "file_path": str(file_path), "operation": "INSERT",
        "line_number": 100, # Número de linha maior que o total de linhas
        "content": "NovaLinhaNoFim"
    }]
    apply_patches(patches, patch_logger, base_path=str(test_files_dir.parent))
    check_file_content(file_path, ["Linha1", "Linha2", "NovaLinhaNoFim"])

def test_insert_into_existing_file_end_no_line_number(test_files_dir: Path):
    file_path = test_files_dir / "file_insert_end_no_ln.txt"
    file_path.write_text("Linha1\nLinha2")
    patches = [{
        "file_path": str(file_path), "operation": "INSERT",
        "content": "NovaLinhaNoFim" # line_number omitido
    }]
    apply_patches(patches, patch_logger, base_path=str(test_files_dir.parent))
    check_file_content(file_path, ["Linha1", "Linha2", "NovaLinhaNoFim"])

def test_insert_creates_new_file(test_files_dir: Path):
    new_file_path = test_files_dir / "subdir" / "created_by_insert.txt"
    patches = [{
        "file_path": str(new_file_path), "operation": "INSERT",
        "content": "Conteúdo inicial do novo arquivo."
    }]
    apply_patches(patches, patch_logger, base_path=str(test_files_dir.parent))
    check_file_content(new_file_path, ["Conteúdo inicial do novo arquivo."])
    assert new_file_path.parent.exists() # Garante que o subdiretório foi criado

def test_insert_into_empty_file(test_files_dir: Path):
    empty_file_path = test_files_dir / "empty_for_insert.txt"
    empty_file_path.touch() # Cria arquivo vazio
    patches = [{
        "file_path": str(empty_file_path), "operation": "INSERT",
        "content": "Primeira linha."
    }]
    apply_patches(patches, patch_logger, base_path=str(test_files_dir.parent))
    check_file_content(empty_file_path, ["Primeira linha."])

def test_insert_invalid_line_number_string(test_files_dir: Path, caplog):
    file_path = test_files_dir / "file_insert_invalid_ln.txt"
    file_path.write_text("Linha1")
    patches = [{
        "file_path": str(file_path), "operation": "INSERT",
        "line_number": "abc", "content": "Não deve inserir"
    }]
    apply_patches(patches, patch_logger, base_path=str(test_files_dir.parent))
    check_file_content(file_path, ["Linha1"]) # Conteúdo não deve mudar
    assert "line_number 'abc' inválido para INSERT" in caplog.text


# --- Testes para Operação REPLACE ---

def test_replace_block_literal_in_existing_file(test_files_dir: Path):
    file_path = test_files_dir / "file_replace_literal.txt"
    file_path.write_text("LinhaA\nBlocoParaSubstituir\nLinhaC")
    patches = [{
        "file_path": str(file_path), "operation": "REPLACE",
        "block_to_replace": "BlocoParaSubstituir",
        "content": "BlocoSubstituido"
    }]
    apply_patches(patches, patch_logger, base_path=str(test_files_dir.parent))
    check_file_content(file_path, ["LinhaA", "BlocoSubstituido", "LinhaC"])

def test_replace_block_regex_in_existing_file(test_files_dir: Path):
    file_path = test_files_dir / "file_replace_regex.txt"
    file_path.write_text("Header\nValor: 123\nFooter\nValor: 456")
    patches = [{
        "file_path": str(file_path), "operation": "REPLACE",
        "block_to_replace": r"Valor: \d+", # Regex
        "is_regex": True, # Explicitamente regex
        "content": "Valor: SUBSTITUIDO_VIA_REGEX"
    }]
    # re.subn substitui todas as ocorrências se count=0
    # A lógica atual do patch_applicator com re.subn(..., count=0) substitui todas.
    apply_patches(patches, patch_logger, base_path=str(test_files_dir.parent))
    check_file_content(file_path, ["Header", "Valor: SUBSTITUIDO_VIA_REGEX", "Footer", "Valor: SUBSTITUIDO_VIA_REGEX"])

def test_replace_block_regex_implicit(test_files_dir: Path):
    file_path = test_files_dir / "file_replace_regex_implicit.txt"
    file_path.write_text("abc\noption = value1\ndef\noption = value2")
    patches = [{
        "file_path": str(file_path), "operation": "REPLACE",
        "block_to_replace": r"option = .*?1", # Regex com caractere especial `*`
        "content": "option = new_value_implicit_regex"
        # is_regex não fornecido, mas deve ser detectado
    }]
    apply_patches(patches, patch_logger, base_path=str(test_files_dir.parent))
    # Deve substituir apenas a primeira ocorrência se não for regex, ou se o regex for específico
    # A heurística atual de regex no patch_applicator pode ser sensível.
    # Se `is_regex: True` não é passado, ele tenta literal primeiro. Se falhar, e tiver chars de regex, tenta regex.
    # Se "option = .*?1" for tratado como literal, não acha. Se como regex, acha "option = value1".
    # O comportamento de fallback para regex precisa ser bem definido.
    # A implementação atual faz `re.subn` com `count=0` se `is_regex` é True ou detectado.
    # Se não for regex, faz `file_content_str.replace(..., 1)`
    # Dado `any(c in block_to_replace_pattern for c in r"*+?^$[]{}()|\\")`, ele detectará como regex.
    check_file_content(file_path, ["abc", "option = new_value_implicit_regex", "def", "option = value2"])


def test_replace_entire_file_content(test_files_dir: Path):
    file_path = test_files_dir / "file_replace_all.txt"
    file_path.write_text("Conteúdo antigo todo.")
    patches = [{
        "file_path": str(file_path), "operation": "REPLACE",
        "block_to_replace": None, # Indica substituir arquivo inteiro
        "content": "Novo conteúdo completo.\nCom duas linhas."
    }]
    apply_patches(patches, patch_logger, base_path=str(test_files_dir.parent))
    check_file_content(file_path, ["Novo conteúdo completo.", "Com duas linhas."])

def test_replace_creates_new_file_if_block_is_null(test_files_dir: Path):
    new_file_path = test_files_dir / "created_by_replace.txt"
    patches = [{
        "file_path": str(new_file_path), "operation": "REPLACE",
        "block_to_replace": None,
        "content": "Arquivo criado com REPLACE e conteúdo completo."
    }]
    apply_patches(patches, patch_logger, base_path=str(test_files_dir.parent))
    check_file_content(new_file_path, ["Arquivo criado com REPLACE e conteúdo completo."])

def test_replace_block_not_found_literal(test_files_dir: Path, caplog):
    file_path = test_files_dir / "file_replace_notfound_lit.txt"
    original_content = "Linha existente."
    file_path.write_text(original_content)
    patches = [{
        "file_path": str(file_path), "operation": "REPLACE",
        "block_to_replace": "BlocoInexistente",
        "content": "Não deve aparecer"
    }]
    apply_patches(patches, patch_logger, base_path=str(test_files_dir.parent))
    check_file_content(file_path, [original_content]) # Conteúdo não muda
    assert "Bloco literal 'BlocoInexistente' não encontrado" in caplog.text

def test_replace_block_not_found_regex(test_files_dir: Path, caplog):
    file_path = test_files_dir / "file_replace_notfound_reg.txt"
    original_content = "Data: 2023-01-01"
    file_path.write_text(original_content)
    patches = [{
        "file_path": str(file_path), "operation": "REPLACE",
        "block_to_replace": r"Time: \d{2}:\d{2}", # Regex que não vai casar
        "is_regex": True,
        "content": "Não deve aparecer"
    }]
    apply_patches(patches, patch_logger, base_path=str(test_files_dir.parent))
    check_file_content(file_path, [original_content]) # Conteúdo não muda
    assert "Padrão regex 'Time: \\d{2}:\\d{2}' não encontrado" in caplog.text


def test_replace_specific_block_in_non_existent_file_fails(test_files_dir: Path, caplog):
    non_existent_file = test_files_dir / "non_existent_for_replace.txt"
    patches = [{
        "file_path": str(non_existent_file), "operation": "REPLACE",
        "block_to_replace": "Algo específico", # Não é None
        "content": "Não deve criar nem escrever"
    }]
    apply_patches(patches, patch_logger, base_path=str(test_files_dir.parent))
    assert not non_existent_file.exists()
    assert f"Tentativa de REPLACE de bloco específico 'Algo específico' em arquivo inexistente '{str(non_existent_file)}'" in caplog.text

# --- Testes para Operação DELETE_BLOCK ---

def test_delete_block_literal_in_existing_file(test_files_dir: Path):
    file_path = test_files_dir / "file_delete_literal.txt"
    file_path.write_text("LinhaAntes\nBlocoParaDeletar\nOutraLinha\nBlocoParaDeletar\nLinhaDepois")
    patches = [{
        "file_path": str(file_path), "operation": "DELETE_BLOCK",
        "block_to_delete": "BlocoParaDeletar\n", # Incluindo newline para remover a linha
    }]
    # A deleção literal atual remove apenas a primeira ocorrência.
    apply_patches(patches, patch_logger, base_path=str(test_files_dir.parent))
    check_file_content(file_path, ["LinhaAntes", "OutraLinha", "BlocoParaDeletar", "LinhaDepois"])

def test_delete_block_regex_in_existing_file(test_files_dir: Path):
    file_path = test_files_dir / "file_delete_regex.txt"
    file_path.write_text("CodeA\n// REMOVE_START\nLinhaComentario1\nLinhaComentario2\n// REMOVE_END\nCodeB\n// REMOVE_START\nOutro Bloco\n// REMOVE_END")
    patches = [{
        "file_path": str(file_path), "operation": "DELETE_BLOCK",
        "block_to_delete": r"// REMOVE_START.*?// REMOVE_END\n?", # Regex para pegar o bloco e opcionalmente um newline
        "is_regex": True
    }]
    # re.subn com count=0 (padrão) deleta todas as ocorrências.
    # A limpeza de linhas vazias no patch_applicator é conservadora.
    # Se o regex pegar o \n final, a linha some. Se não, pode sobrar linha vazia.
    # O regex `\n?` no final tenta pegar o newline.
    apply_patches(patches, patch_logger, base_path=str(test_files_dir.parent))
    # Esperado: "CodeA\nCodeB" se os blocos e newlines forem removidos corretamente.
    # A lógica de limpeza de linhas vazias é complexa. `splitlines()` já ajuda.
    # Se o regex `.*?// REMOVE_END\n?` remove o newline, então as linhas vazias não deveriam sobrar.
    check_file_content(file_path, ["CodeA", "CodeB"])


def test_delete_entire_file_with_block_to_delete_none(test_files_dir: Path):
    file_path = test_files_dir / "file_to_be_deleted.txt"
    file_path.write_text("Este arquivo será deletado.")
    assert file_path.exists()
    patches = [{
        "file_path": str(file_path), "operation": "DELETE_BLOCK",
        "block_to_delete": None # Indica deletar o arquivo inteiro
    }]
    apply_patches(patches, patch_logger, base_path=str(test_files_dir.parent))
    assert not file_path.exists()

def test_delete_block_not_found_literal(test_files_dir: Path, caplog):
    file_path = test_files_dir / "file_delete_notfound_lit.txt"
    original_content = "Manter esta linha."
    file_path.write_text(original_content)
    patches = [{
        "file_path": str(file_path), "operation": "DELETE_BLOCK",
        "block_to_delete": "BlocoDeTextoInexistente"
    }]
    apply_patches(patches, patch_logger, base_path=str(test_files_dir.parent))
    check_file_content(file_path, [original_content])
    assert "Bloco literal 'BlocoDeTextoInexistente' não encontrado" in caplog.text

def test_delete_block_in_non_existent_file(test_files_dir: Path, caplog):
    non_existent_file = test_files_dir / "ghost_file_for_delete.txt"
    patches = [{
        "file_path": str(non_existent_file), "operation": "DELETE_BLOCK",
        "block_to_delete": "QualquerCoisa"
    }]
    apply_patches(patches, patch_logger, base_path=str(test_files_dir.parent))
    assert not non_existent_file.exists()
    assert f"Operação 'DELETE_BLOCK' em arquivo inexistente '{str(non_existent_file)}'. Pulando." in caplog.text

# --- Testes Gerais e de Erro ---

def test_apply_patches_invalid_operation(test_files_dir: Path, caplog):
    file_path = test_files_dir / "file_invalid_op.txt"
    file_path.write_text("Conteúdo original.")
    patches = [{
        "file_path": str(file_path), "operation": "UNKNOWN_OPERATION",
        "content": "bla"
    }]
    apply_patches(patches, patch_logger, base_path=str(test_files_dir.parent))
    check_file_content(file_path, ["Conteúdo original."])
    assert "Operação desconhecida 'UNKNOWN_OPERATION'" in caplog.text

def test_apply_patches_missing_filepath(test_files_dir: Path, caplog):
    patches = [{"operation": "INSERT", "content": "abc"}] # Sem file_path
    apply_patches(patches, patch_logger, base_path=str(test_files_dir.parent))
    assert "Patch inválido (sem file_path ou operation)" in caplog.text


def test_apply_patches_base_path_resolution(tmp_path: Path):
    # Testar se base_path funciona corretamente para file_path relativos
    project_root = tmp_path / "my_project"
    project_root.mkdir()

    sub_dir = project_root / "src"
    # Não criar sub_dir ainda, o patcher deve fazer se necessário

    target_file_in_subdir = sub_dir / "module.py"

    patches = [{
        "file_path": "src/module.py", # Relativo ao base_path (project_root)
        "operation": "INSERT",
        "content": "print('hello from module')"
    }]

    # base_path é project_root. O patch_applicator fará Path(project_root) / "src/module.py"
    apply_patches(patches, patch_logger, base_path=str(project_root))

    assert target_file_in_subdir.exists()
    check_file_content(target_file_in_subdir, ["print('hello from module')"])


def test_apply_patches_filepath_is_normalized(tmp_path: Path):
    # Garante que caminhos como "dir/./file.txt" ou "dir/../dir/file.txt" são normalizados.
    # A normalização ocorre com Path(os.path.normpath(file_path_str))
    # E depois Path(base_path).resolve() / normalized_file_path

    actual_project_dir = tmp_path / "actual_dir"
    actual_project_dir.mkdir()

    # Caminho não normalizado que aponta para o arquivo dentro de actual_project_dir
    non_normalized_path_str = f"{actual_project_dir.name}/../{actual_project_dir.name}/target_file.txt"
    # Isso resolveria para tmp_path / actual_dir_name / target_file.txt

    expected_file_path = actual_project_dir / "target_file.txt"

    patches = [{
        "file_path": non_normalized_path_str,
        "operation": "INSERT",
        "content": "Normalized path content"
    }]

    # base_path é tmp_path.
    # full_path se tornará tmp_path / non_normalized_path_str, que Path depois resolve.
    apply_patches(patches, patch_logger, base_path=str(tmp_path))

    assert expected_file_path.exists()
    check_file_content(expected_file_path, ["Normalized path content"])

def test_replace_regex_with_special_chars_in_content(test_files_dir: Path):
    file_path = test_files_dir / "file_replace_regex_special_content.txt"
    file_path.write_text("Replace this: SOMETHING")
    patches = [{
        "file_path": str(file_path), "operation": "REPLACE",
        "block_to_replace": r"SOMETHING",
        "is_regex": True,
        "content": "With this: $1 and \\1 and \\g<0>" # Caracteres especiais de substituição regex
    }]
    # re.subn trata $1, \1 etc. no 'content' se o 'block_to_replace' tiver grupos de captura.
    # Se 'block_to_replace' não tiver grupos, eles são tratados literalmente.
    # No nosso caso, "SOMETHING" não tem grupos.
    apply_patches(patches, patch_logger, base_path=str(test_files_dir.parent))
    check_file_content(file_path, ["Replace this: With this: $1 and \\1 and \\g<0>"])

def test_delete_block_literal_multiline(test_files_dir: Path):
    file_path = test_files_dir / "file_delete_multiline_literal.txt"
    content_to_delete = "Primeira linha do bloco a deletar.\nSegunda linha do bloco a deletar.\n" # Adicionado \n no final
    file_path.write_text(f"Antes\n{content_to_delete}Depois") # Removido \n antes de Depois pois já está em content_to_delete
    patches = [{
        "file_path": str(file_path), "operation": "DELETE_BLOCK",
        "block_to_delete": content_to_delete
    }]
    # Para que a deleção literal funcione bem com múltiplas linhas,
    # o `block_to_delete` deve ser uma correspondência exata do que está no arquivo.
    # A remoção pode deixar uma linha em branco se o `\n` final não fizer parte do bloco.
    # Se `content_to_delete` não tiver `\n` no final, e o bloco no arquivo tiver,
    # a linha "Depois" subirá, mas pode haver um `\n` extra.
    # `splitlines()` na verificação ajuda a normalizar isso.
    # O `replace(block, "")` removerá o bloco. Se o bloco era seguido por \n, esse \n permanece.
    apply_patches(patches, patch_logger, base_path=str(test_files_dir.parent))
    check_file_content(file_path, ["Antes", "Depois"]) # Espera-se que as linhas do bloco sejam removidas.
                                                     # Se o bloco não incluir o \n final, pode sobrar uma linha.
                                                     # A implementação atual de DELETE_BLOCK com string literal
                                                     # e depois `splitlines()` deve lidar bem com isso.
                                                     # `file_content_str.replace(block_to_delete_pattern, "", 1)`
                                                     # Se block_to_delete_pattern é "L1\nL2", e o arquivo é "Antes\nL1\nL2\nDepois",
                                                     # o resultado é "Antes\n\nDepois". `splitlines()` disso é ["Antes", "", "Depois"].
                                                     # A lógica de limpeza no patch_applicator tenta remover linhas que se tornaram *completamente* vazias.
                                                     # Esta lógica de limpeza é complexa.
                                                     # Se `block_to_delete` for `content_to_delete + '\n'`, o resultado seria melhor.
                                                     # Por ora, vamos testar o comportamento atual.
                                                     # A fixture check_file_content normaliza newlines, então "" deve ser ok.
                                                     # A atual limpeza de DELETE_BLOCK é:
                                                     # lines = [line for line in temp_lines if line.strip() or line in lines]
                                                     # E depois outra mais complexa.
                                                     # Se `temp_lines` for `["Antes", "", "Depois"]` e `lines` original era `["Antes", "L1", "L2", "Depois"]`
                                                     # A primeira limpeza: `line.strip()` para "" é `False`. `"" in lines` é `False`. Então "" é removido.
                                                     # Resultado: `["Antes", "Depois"]`. Isso parece correto.

"""
Observações sobre os testes de `patch_applicator`:
- Cobertura extensiva para INSERT, REPLACE, DELETE_BLOCK.
- Uso de `test_files_dir` (baseado em `tmp_path`) para isolamento.
- `check_file_content` para verificar o resultado das operações.
- `caplog` para verificar mensagens de log em casos de aviso/erro.
- Testes para criação de arquivos/diretórios.
- Testes para blocos/arquivos não encontrados.
- Testes para resolução e normalização de caminhos.
- Testes para comportamento de regex (explícito e implícito).
"""
