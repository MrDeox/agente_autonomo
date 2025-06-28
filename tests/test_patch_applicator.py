# tests/test_patch_applicator.py
# tests/test_patch_applicator.py
import pytest
import logging
from pathlib import Path
import os # Para os.path.normpath
import aiofiles # Adicionado
import aiofiles.os as aios # Adicionado
from agent.patch_applicator import apply_patches

# Logger para os testes do patch_applicator
patch_logger = logging.getLogger("test_patch_applicator")
patch_logger.setLevel(logging.DEBUG)
# Se precisar ver os logs durante o teste:
# import sys
# handler = logging.StreamHandler(sys.stdout)
# patch_logger.addHandler(handler)


@pytest.fixture
async def test_files_dir(tmp_path: Path) -> Path: # Fixture agora pode ser async se precisar de I/O async no setup
    """Cria um diretório base para os arquivos de teste dentro de tmp_path."""
    test_dir = tmp_path / "patch_test_ws"
    # Usar aiofiles.os.makedirs que suporta exist_ok
    await aios.makedirs(test_dir, exist_ok=True)
    return test_dir

# Helper para verificar conteúdo do arquivo (agora async)
async def check_file_content(file_path: Path, expected_lines: list[str]):
    assert await aios.path.exists(file_path), f"Arquivo {file_path} deveria existir."
    async with aiofiles.open(file_path, "r", encoding="utf-8") as f:
        content = await f.read()
    actual_lines = content.splitlines()

    normalized_expected = [line.rstrip('\r\n') for line in expected_lines]
    normalized_actual = [line.rstrip('\r\n') for line in actual_lines]

    assert normalized_actual == normalized_expected, \
        f"Conteúdo de {file_path} não esperado.\nAtual:\n{normalized_actual}\nEsperado:\n{normalized_expected}"

# Helper para escrever texto em arquivo de forma assíncrona
async def write_text_async(file_path: Path, text: str):
    async with aiofiles.open(file_path, "w", encoding="utf-8") as f:
        await f.write(text)

# Helper para criar arquivo vazio de forma assíncrona
async def touch_async(file_path: Path):
    async with aiofiles.open(file_path, "w", encoding="utf-8") as f:
        pass # Arquivo vazio

# --- Testes para Operação INSERT ---

@pytest.mark.asyncio
async def test_insert_into_existing_file_start(test_files_dir: Path):
    resolved_test_files_dir = await test_files_dir # Resolver a fixture
    file_path = resolved_test_files_dir / "file_to_insert.txt"
    await write_text_async(file_path, "Linha1\nLinha2")
    patches = [{
        "file_path": str(file_path), "operation": "INSERT",
        "line_number": 1, "content": "NovaLinhaNoInicio"
    }]
    await apply_patches(patches, patch_logger, base_path=str(resolved_test_files_dir.parent))
    await check_file_content(file_path, ["NovaLinhaNoInicio", "Linha1", "Linha2"])

@pytest.mark.asyncio
async def test_insert_into_existing_file_middle(test_files_dir: Path):
    resolved_test_files_dir = await test_files_dir
    file_path = resolved_test_files_dir / "file_insert_middle.txt"
    await write_text_async(file_path, "Linha1\nLinha2\nLinha3")
    patches = [{
        "file_path": str(file_path), "operation": "INSERT",
        "line_number": 3, "content": "NovaLinhaNoMeio1\nNovaLinhaNoMeio2"
    }]
    await apply_patches(patches, patch_logger, base_path=str(resolved_test_files_dir.parent))
    await check_file_content(file_path, ["Linha1", "Linha2", "NovaLinhaNoMeio1", "NovaLinhaNoMeio2", "Linha3"])

@pytest.mark.asyncio
async def test_insert_into_existing_file_end_with_line_number(test_files_dir: Path):
    resolved_test_files_dir = await test_files_dir
    file_path = resolved_test_files_dir / "file_insert_end_ln.txt"
    await write_text_async(file_path, "Linha1\nLinha2")
    patches = [{
        "file_path": str(file_path), "operation": "INSERT",
        "line_number": 100,
        "content": "NovaLinhaNoFim"
    }]
    await apply_patches(patches, patch_logger, base_path=str(resolved_test_files_dir.parent))
    await check_file_content(file_path, ["Linha1", "Linha2", "NovaLinhaNoFim"])

@pytest.mark.asyncio
async def test_insert_into_existing_file_end_no_line_number(test_files_dir: Path):
    resolved_test_files_dir = await test_files_dir
    file_path = resolved_test_files_dir / "file_insert_end_no_ln.txt"
    await write_text_async(file_path, "Linha1\nLinha2")
    patches = [{
        "file_path": str(file_path), "operation": "INSERT",
        "content": "NovaLinhaNoFim"
    }]
    await apply_patches(patches, patch_logger, base_path=str(resolved_test_files_dir.parent))
    await check_file_content(file_path, ["Linha1", "Linha2", "NovaLinhaNoFim"])

@pytest.mark.asyncio
async def test_insert_creates_new_file(test_files_dir: Path):
    resolved_test_files_dir = await test_files_dir
    new_file_path = resolved_test_files_dir / "subdir" / "created_by_insert.txt"
    patches = [{
        "file_path": str(new_file_path), "operation": "INSERT",
        "content": "Conteúdo inicial do novo arquivo."
    }]
    await apply_patches(patches, patch_logger, base_path=str(resolved_test_files_dir.parent))
    await check_file_content(new_file_path, ["Conteúdo inicial do novo arquivo."])
    assert await aios.path.exists(new_file_path.parent)

@pytest.mark.asyncio
async def test_insert_into_empty_file(test_files_dir: Path):
    resolved_test_files_dir = await test_files_dir
    empty_file_path = resolved_test_files_dir / "empty_for_insert.txt"
    await touch_async(empty_file_path)
    patches = [{
        "file_path": str(empty_file_path), "operation": "INSERT",
        "content": "Primeira linha."
    }]
    await apply_patches(patches, patch_logger, base_path=str(resolved_test_files_dir.parent))
    await check_file_content(empty_file_path, ["Primeira linha."])

@pytest.mark.asyncio
async def test_insert_invalid_line_number_string(test_files_dir: Path, caplog):
    resolved_test_files_dir = await test_files_dir
    file_path = resolved_test_files_dir / "file_insert_invalid_ln.txt"
    await write_text_async(file_path, "Linha1")
    patches = [{
        "file_path": str(file_path), "operation": "INSERT",
        "line_number": "abc", "content": "Não deve inserir"
    }]
    await apply_patches(patches, patch_logger, base_path=str(resolved_test_files_dir.parent))
    await check_file_content(file_path, ["Linha1"])
    assert "line_number 'abc' inválido para INSERT" in caplog.text


# --- Testes para Operação REPLACE ---

@pytest.mark.asyncio
async def test_replace_block_literal_in_existing_file(test_files_dir: Path):
    resolved_test_files_dir = await test_files_dir
    file_path = resolved_test_files_dir / "file_replace_literal.txt"
    await write_text_async(file_path, "LinhaA\nBlocoParaSubstituir\nLinhaC")
    patches = [{
        "file_path": str(file_path), "operation": "REPLACE",
        "block_to_replace": "BlocoParaSubstituir",
        "content": "BlocoSubstituido"
    }]
    await apply_patches(patches, patch_logger, base_path=str(resolved_test_files_dir.parent))
    await check_file_content(file_path, ["LinhaA", "BlocoSubstituido", "LinhaC"])

@pytest.mark.asyncio
async def test_replace_block_regex_in_existing_file(test_files_dir: Path):
    resolved_test_files_dir = await test_files_dir
    file_path = resolved_test_files_dir / "file_replace_regex.txt"
    await write_text_async(file_path, "Header\nValor: 123\nFooter\nValor: 456")
    patches = [{
        "file_path": str(file_path), "operation": "REPLACE",
        "block_to_replace": r"Valor: \d+",
        "is_regex": True,
        "content": "Valor: SUBSTITUIDO_VIA_REGEX"
    }]
    await apply_patches(patches, patch_logger, base_path=str(resolved_test_files_dir.parent))
    await check_file_content(file_path, ["Header", "Valor: SUBSTITUIDO_VIA_REGEX", "Footer", "Valor: SUBSTITUIDO_VIA_REGEX"])

@pytest.mark.asyncio
async def test_replace_block_regex_implicit(test_files_dir: Path):
    resolved_test_files_dir = await test_files_dir
    file_path = resolved_test_files_dir / "file_replace_regex_implicit.txt"
    await write_text_async(file_path, "abc\noption = value1\ndef\noption = value2")
    patches = [{
        "file_path": str(file_path), "operation": "REPLACE",
        "block_to_replace": r"option = .*?1",
        "content": "option = new_value_implicit_regex"
    }]
    await apply_patches(patches, patch_logger, base_path=str(resolved_test_files_dir.parent))
    await check_file_content(file_path, ["abc", "option = new_value_implicit_regex", "def", "option = value2"])


@pytest.mark.asyncio
async def test_replace_entire_file_content(test_files_dir: Path):
    resolved_test_files_dir = await test_files_dir
    file_path = resolved_test_files_dir / "file_replace_all.txt"
    await write_text_async(file_path, "Conteúdo antigo todo.")
    patches = [{
        "file_path": str(file_path), "operation": "REPLACE",
        "block_to_replace": None,
        "content": "Novo conteúdo completo.\nCom duas linhas."
    }]
    await apply_patches(patches, patch_logger, base_path=str(resolved_test_files_dir.parent))
    await check_file_content(file_path, ["Novo conteúdo completo.", "Com duas linhas."])

@pytest.mark.asyncio
async def test_replace_creates_new_file_if_block_is_null(test_files_dir: Path):
    resolved_test_files_dir = await test_files_dir
    new_file_path = resolved_test_files_dir / "created_by_replace.txt"
    patches = [{
        "file_path": str(new_file_path), "operation": "REPLACE",
        "block_to_replace": None,
        "content": "Arquivo criado com REPLACE e conteúdo completo."
    }]
    await apply_patches(patches, patch_logger, base_path=str(resolved_test_files_dir.parent))
    await check_file_content(new_file_path, ["Arquivo criado com REPLACE e conteúdo completo."])

@pytest.mark.asyncio
async def test_replace_block_not_found_literal(test_files_dir: Path, caplog):
    resolved_test_files_dir = await test_files_dir
    file_path = resolved_test_files_dir / "file_replace_notfound_lit.txt"
    original_content = "Linha existente."
    await write_text_async(file_path, original_content)
    patches = [{
        "file_path": str(file_path), "operation": "REPLACE",
        "block_to_replace": "BlocoInexistente",
        "content": "Não deve aparecer"
    }]
    await apply_patches(patches, patch_logger, base_path=str(resolved_test_files_dir.parent))
    await check_file_content(file_path, [original_content])
    assert "Bloco literal 'BlocoInexistente' não encontrado" in caplog.text

@pytest.mark.asyncio
async def test_replace_block_not_found_regex(test_files_dir: Path, caplog):
    resolved_test_files_dir = await test_files_dir
    file_path = resolved_test_files_dir / "file_replace_notfound_reg.txt"
    original_content = "Data: 2023-01-01"
    await write_text_async(file_path, original_content)
    patches = [{
        "file_path": str(file_path), "operation": "REPLACE",
        "block_to_replace": r"Time: \d{2}:\d{2}",
        "is_regex": True,
        "content": "Não deve aparecer"
    }]
    await apply_patches(patches, patch_logger, base_path=str(resolved_test_files_dir.parent))
    await check_file_content(file_path, [original_content])
    assert "Padrão regex 'Time: \\d{2}:\\d{2}' não encontrado" in caplog.text


@pytest.mark.asyncio
async def test_replace_specific_block_in_non_existent_file_fails(test_files_dir: Path, caplog):
    resolved_test_files_dir = await test_files_dir
    non_existent_file = resolved_test_files_dir / "non_existent_for_replace.txt"
    patches = [{
        "file_path": str(non_existent_file), "operation": "REPLACE",
        "block_to_replace": "Algo específico",
        "content": "Não deve criar nem escrever"
    }]
    await apply_patches(patches, patch_logger, base_path=str(resolved_test_files_dir.parent))
    assert not await aios.path.exists(non_existent_file)
    assert f"Tentativa de REPLACE de bloco específico 'Algo específico' em arquivo inexistente '{str(non_existent_file)}'" in caplog.text

# --- Testes para Operação DELETE_BLOCK ---

@pytest.mark.asyncio
async def test_delete_block_literal_in_existing_file(test_files_dir: Path):
    resolved_test_files_dir = await test_files_dir
    file_path = resolved_test_files_dir / "file_delete_literal.txt"
    await write_text_async(file_path, "LinhaAntes\nBlocoParaDeletar\nOutraLinha\nBlocoParaDeletar\nLinhaDepois")
    patches = [{
        "file_path": str(file_path), "operation": "DELETE_BLOCK",
        "block_to_delete": "BlocoParaDeletar\n",
    }]
    await apply_patches(patches, patch_logger, base_path=str(resolved_test_files_dir.parent))
    await check_file_content(file_path, ["LinhaAntes", "OutraLinha", "BlocoParaDeletar", "LinhaDepois"])

@pytest.mark.asyncio
async def test_delete_block_regex_in_existing_file(test_files_dir: Path):
    resolved_test_files_dir = await test_files_dir
    file_path = resolved_test_files_dir / "file_delete_regex.txt"
    await write_text_async(file_path, "CodeA\n// REMOVE_START\nLinhaComentario1\nLinhaComentario2\n// REMOVE_END\nCodeB\n// REMOVE_START\nOutro Bloco\n// REMOVE_END")
    patches = [{
        "file_path": str(file_path), "operation": "DELETE_BLOCK",
        "block_to_delete": r"// REMOVE_START.*?// REMOVE_END\n?",
        "is_regex": True
    }]
    await apply_patches(patches, patch_logger, base_path=str(resolved_test_files_dir.parent))
    await check_file_content(file_path, ["CodeA", "CodeB"])


@pytest.mark.asyncio
async def test_delete_entire_file_with_block_to_delete_none(test_files_dir: Path):
    resolved_test_files_dir = await test_files_dir
    file_path = resolved_test_files_dir / "file_to_be_deleted.txt"
    await write_text_async(file_path, "Este arquivo será deletado.")
    assert await aios.path.exists(file_path)
    patches = [{
        "file_path": str(file_path), "operation": "DELETE_BLOCK",
        "block_to_delete": None
    }]
    await apply_patches(patches, patch_logger, base_path=str(resolved_test_files_dir.parent))
    assert not await aios.path.exists(file_path)

@pytest.mark.asyncio
async def test_delete_block_not_found_literal(test_files_dir: Path, caplog):
    resolved_test_files_dir = await test_files_dir
    file_path = resolved_test_files_dir / "file_delete_notfound_lit.txt"
    original_content = "Manter esta linha."
    await write_text_async(file_path, original_content)
    patches = [{
        "file_path": str(file_path), "operation": "DELETE_BLOCK",
        "block_to_delete": "BlocoDeTextoInexistente"
    }]
    await apply_patches(patches, patch_logger, base_path=str(resolved_test_files_dir.parent))
    await check_file_content(file_path, [original_content])
    assert "Bloco literal 'BlocoDeTextoInexistente' não encontrado" in caplog.text

@pytest.mark.asyncio
async def test_delete_block_in_non_existent_file(test_files_dir: Path, caplog):
    resolved_test_files_dir = await test_files_dir
    non_existent_file = resolved_test_files_dir / "ghost_file_for_delete.txt"
    patches = [{
        "file_path": str(non_existent_file), "operation": "DELETE_BLOCK",
        "block_to_delete": "QualquerCoisa"
    }]
    await apply_patches(patches, patch_logger, base_path=str(resolved_test_files_dir.parent))
    assert not await aios.path.exists(non_existent_file)
    assert f"Operação '{'DELETE_BLOCK'}' em arquivo inexistente '{str(non_existent_file)}'. Pulando." in caplog.text # Ajustado para corresponder ao log exato

# --- Testes Gerais e de Erro ---

@pytest.mark.asyncio
async def test_apply_patches_invalid_operation(test_files_dir: Path, caplog):
    resolved_test_files_dir = await test_files_dir
    file_path = resolved_test_files_dir / "file_invalid_op.txt"
    await write_text_async(file_path, "Conteúdo original.")
    patches = [{
        "file_path": str(file_path), "operation": "UNKNOWN_OPERATION",
        "content": "bla"
    }]
    await apply_patches(patches, patch_logger, base_path=str(resolved_test_files_dir.parent))
    await check_file_content(file_path, ["Conteúdo original."])
    assert "Operação desconhecida 'UNKNOWN_OPERATION'" in caplog.text

@pytest.mark.asyncio
async def test_apply_patches_missing_filepath(test_files_dir: Path, caplog): # test_files_dir é uma fixture, ok
    resolved_test_files_dir = await test_files_dir
    patches = [{"operation": "INSERT", "content": "abc"}]
    await apply_patches(patches, patch_logger, base_path=str(resolved_test_files_dir.parent)) # Passar test_files_dir.parent como base
    assert "Patch inválido (sem file_path ou operation)" in caplog.text


@pytest.mark.asyncio
async def test_apply_patches_base_path_resolution(tmp_path: Path):
    project_root = tmp_path / "my_project"
    await aios.mkdir(project_root)

    target_file_in_subdir = project_root / "src" / "module.py"
    # O diretório src será criado por apply_patches se não existir

    patches = [{
        "file_path": "src/module.py",
        "operation": "INSERT",
        "content": "print('hello from module')"
    }]

    await apply_patches(patches, patch_logger, base_path=str(project_root))

    assert await aios.path.exists(target_file_in_subdir)
    await check_file_content(target_file_in_subdir, ["print('hello from module')"])


@pytest.mark.asyncio
async def test_apply_patches_filepath_is_normalized(tmp_path: Path):
    actual_project_dir = tmp_path / "actual_dir"
    await aios.mkdir(actual_project_dir)

    non_normalized_path_str = f"{actual_project_dir.name}/../{actual_project_dir.name}/target_file.txt"
    expected_file_path = actual_project_dir / "target_file.txt"

    patches = [{
        "file_path": non_normalized_path_str,
        "operation": "INSERT",
        "content": "Normalized path content"
    }]

    await apply_patches(patches, patch_logger, base_path=str(tmp_path))

    assert await aios.path.exists(expected_file_path)
    await check_file_content(expected_file_path, ["Normalized path content"])

@pytest.mark.asyncio
async def test_replace_regex_with_special_chars_in_content(test_files_dir: Path):
    resolved_test_files_dir = await test_files_dir
    file_path = resolved_test_files_dir / "file_replace_regex_special_content.txt"
    await write_text_async(file_path, "Replace this: SOMETHING")
    patches = [{
        "file_path": str(file_path), "operation": "REPLACE",
        "block_to_replace": r"SOMETHING",
        "is_regex": True,
        "content": "With this: $1 and \\1 and \\g<0>"
    }]
    await apply_patches(patches, patch_logger, base_path=str(resolved_test_files_dir.parent))
    await check_file_content(file_path, ["Replace this: With this: $1 and \\1 and \\g<0>"])

@pytest.mark.asyncio
async def test_delete_block_literal_multiline(test_files_dir: Path):
    resolved_test_files_dir = await test_files_dir
    file_path = resolved_test_files_dir / "file_delete_multiline_literal.txt"
    content_to_delete = "Primeira linha do bloco a deletar.\nSegunda linha do bloco a deletar.\n"
    await write_text_async(file_path, f"Antes\n{content_to_delete}Depois")
    patches = [{
        "file_path": str(file_path), "operation": "DELETE_BLOCK",
        "block_to_delete": content_to_delete
    }]
    await apply_patches(patches, patch_logger, base_path=str(resolved_test_files_dir.parent))
    await check_file_content(file_path, ["Antes", "Depois"])


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
