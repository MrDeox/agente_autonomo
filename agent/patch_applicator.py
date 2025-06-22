import os
import shutil
import logging
from typing import List, Dict, Any

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def apply_patches(patch_instructions: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Aplica uma lista de instruções de patch aos arquivos especificados.

    Cada instrução de patch aplica uma série de operações (INSERT_AFTER, REPLACE_BLOCK, DELETE_BLOCK)
    a um arquivo. Um backup do arquivo original é criado antes de qualquer modificação.

    Args:
        patch_instructions: Uma lista de dicionários, onde cada dicionário representa
                            as instruções de patch para um único arquivo.
                            Formato esperado por instrução:
                            {
                                "file_path": "caminho/do/arquivo.py",
                                "reasoning": "Justificativa para a mudança.",
                                "operations": [
                                    {
                                        "operation": "REPLACE_BLOCK",
                                        "start_line": <int>,  # Baseado em 1
                                        "end_line": <int>,    # Baseado em 1
                                        "content": "<string com novo bloco de código>"
                                    },
                                    {
                                        "operation": "INSERT_AFTER",
                                        "line_number": <int>, # Baseado em 1
                                        "content": "<string com código a ser inserido>"
                                    },
                                    {
                                        "operation": "DELETE_BLOCK",
                                        "start_line": <int>,  # Baseado em 1
                                        "end_line": <int>     # Baseado em 1
                                    }
                                ]
                            }

    Returns:
        Um dicionário com os resultados da aplicação dos patches.
        Exemplo:
        {
            "success": True,
            "results": {
                "caminho/do/arquivo1.py": {"status": "success", "message": "Patches aplicados com sucesso."},
                "caminho/do/arquivo2.py": {"status": "error", "message": "Erro ao aplicar patch: <detalhes>"}
            }
        }
    """
    report = {"success": True, "results": {}}

    for instruction in patch_instructions:
        file_path = instruction["file_path"]
        operations = instruction.get("operations", [])

        logger.info(f"Processando patches para o arquivo: {file_path}")

        if not os.path.exists(file_path):
            logger.error(f"Arquivo {file_path} não encontrado.")
            report["results"][file_path] = {"status": "error", "message": f"Arquivo não encontrado."}
            report["success"] = False
            continue

        # Criar backup
        backup_path = f"{file_path}.bak_patch"
        try:
            shutil.copy2(file_path, backup_path)
            logger.info(f"Backup de {file_path} criado em {backup_path}")
        except Exception as e:
            logger.error(f"Erro ao criar backup de {file_path}: {e}")
            report["results"][file_path] = {"status": "error", "message": f"Erro ao criar backup: {e}"}
            report["success"] = False
            continue

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except Exception as e:
            logger.error(f"Erro ao ler o arquivo {file_path}: {e}")
            report["results"][file_path] = {"status": "error", "message": f"Erro ao ler arquivo: {e}"}
            report["success"] = False
            # Restaurar do backup em caso de falha na leitura, embora improvável aqui
            # shutil.move(backup_path, file_path)
            continue

        # Aplicar operações em memória
        # É crucial que as operações sejam aplicadas de forma que os números de linha
        # permaneçam consistentes. Uma abordagem é processar deleções primeiro,
        # ou ajustar os números de linha dinamicamente.
        # Para simplificar inicialmente, vamos assumir que as operações são fornecidas
        # em uma ordem que não cause conflitos de índice, ou processá-las com cuidado.
        # Uma estratégia mais robusta seria ajustar os índices após cada operação.

        # Para INSERT_AFTER e REPLACE_BLOCK, o conteúdo pode ter múltiplas linhas.
        # Os números de linha são baseados em 1. Ajustar para índice 0.

        # Processar operações de forma que os índices não sejam invalidados
        # Por exemplo, se houver múltiplas operações, pode ser mais seguro
        # construir uma nova lista de linhas.

        # Vamos implementar uma abordagem que modifica a lista 'lines' diretamente,
        # mas com cuidado. REPLACE e DELETE devem ser tratados com atenção aos índices.
        # INSERT_AFTER é mais simples se feito na ordem correta ou em uma cópia.

        # Ordenar operações pode ser uma boa estratégia: DELETEs primeiro (de baixo para cima),
        # depois REPLACEs (de baixo para cima), depois INSERTs (de baixo para cima).
        # Por ora, vamos processar na ordem dada e destacar a necessidade de cautela.

        # Convert line endings in content to match the current file's majority
        # This is a simplified approach. A more robust solution would detect line endings.
        has_crlf = any('\r\n' in line for line in lines)

        def normalize_line_endings(content_str):
            if has_crlf:
                return content_str.replace('\n', '\r\n').replace('\r\r\n', '\r\n')
            else:
                return content_str.replace('\r\n', '\n')

        # Para evitar problemas com modificações que alteram o tamanho da lista e desalinham os índices
        # subsequentes, vamos aplicar as operações de forma a construir uma nova lista de linhas.
        new_lines = list(lines) # Começa como uma cópia
        offset = 0 # Mantém o controle do deslocamento de linhas devido a inserções/deleções

        # É mais seguro aplicar operações que alteram o número de linhas
        # de forma ordenada ou recalcular os índices.
        # Uma abordagem mais simples para esta primeira versão:
        # Processar operações em uma cópia e reconstruir.
        # No entanto, a instrução pede para modificar a lista em memória.

        # Vamos tentar uma abordagem que modifica 'lines' mas requer que as operações
        # sejam fornecidas de uma forma que não cause problemas de índice,
        # ou que sejam processadas de trás para frente para inserções/deleções.

        # Para REPLACE_BLOCK e DELETE_BLOCK, é mais seguro iterar de trás para frente
        # ou ajustar os índices cuidadosamente.
        # Para INSERT_AFTER, se feito de trás para frente, os índices não mudam para operações anteriores.

        # Vamos refatorar para uma abordagem mais segura que constrói o resultado linha por linha.
        # Esta é mais complexa de implementar diretamente com as operações dadas.

        # Tentativa de modificação direta com ordenação de operações (simplificado):
        # Ordenar por tipo pode ajudar: DELETEs, depois REPLACEs, depois INSERTs.
        # E dentro de cada tipo, por número de linha (decrescente para evitar problemas de índice).

        temp_lines = list(lines) # Trabalhar sobre uma cópia para as operações

        # As operações devem ser aplicadas com cuidado para os índices.
        # Ex: Se você deleta linhas, os índices das linhas subsequentes mudam.
        # Se você insere linhas, o mesmo acontece.
        # Uma forma robusta é aplicar as mudanças de baixo para cima (maior número de linha primeiro).

        sorted_operations = sorted(enumerate(operations), key=lambda x: (
            x[1].get('start_line', x[1].get('line_number', 0)), # Chave primária: linha
            {'DELETE_BLOCK': 0, 'REPLACE_BLOCK': 1, 'INSERT_AFTER': 2}.get(x[1]['operation'], 3) # Chave secundária: tipo
        ), reverse=True)


        current_lines = list(lines) # A lista que será modificada

        for op_idx, op in sorted_operations: # O op_idx original não é usado aqui, mas mantido por sorted
            op_type = op["operation"]

            try:
                if op_type == "REPLACE_BLOCK":
                    start_line = int(op["start_line"]) - 1  # Ajuste para índice 0
                    end_line = int(op["end_line"]) -1     # Ajuste para índice 0
                    content = normalize_line_endings(op["content"])
                    content_lines = content.splitlines(True) # Manter line endings
                    if not content.endswith('\n') and content_lines: # Adicionar newline se não houver no final do bloco
                         content_lines[-1] += '\n' if not has_crlf else '\r\n'


                    if start_line < 0 or end_line >= len(current_lines) or start_line > end_line:
                        raise ValueError(f"Índices inválidos para REPLACE_BLOCK: start={start_line+1}, end={end_line+1}")

                    del current_lines[start_line : end_line + 1]
                    for i, line_content in enumerate(content_lines):
                        current_lines.insert(start_line + i, line_content)
                    logger.debug(f"REPLACE_BLOCK de {start_line+1} a {end_line+1} aplicado.")

                elif op_type == "INSERT_AFTER":
                    line_number = int(op["line_number"]) - 1 # Ajuste para índice 0
                    content = normalize_line_endings(op["content"])
                    content_lines = content.splitlines(True)
                    if not content.endswith('\n') and content_lines: # Adicionar newline se não houver no final do bloco
                         content_lines[-1] += '\n' if not has_crlf else '\r\n'

                    if line_number < -1 or line_number >= len(current_lines): # -1 permite inserir no início se line_number for 0
                        raise ValueError(f"Índice inválido para INSERT_AFTER: line_number={line_number+1}")

                    # Inserir cada linha do conteúdo individualmente
                    for i, line_content in enumerate(content_lines):
                        current_lines.insert(line_number + 1 + i, line_content)
                    logger.debug(f"INSERT_AFTER linha {line_number+1} aplicado.")

                elif op_type == "DELETE_BLOCK":
                    start_line = int(op["start_line"]) - 1  # Ajuste para índice 0
                    end_line = int(op["end_line"]) - 1    # Ajuste para índice 0

                    if start_line < 0 or end_line >= len(current_lines) or start_line > end_line:
                        raise ValueError(f"Índices inválidos para DELETE_BLOCK: start={start_line+1}, end={end_line+1}")

                    del current_lines[start_line : end_line + 1]
                    logger.debug(f"DELETE_BLOCK de {start_line+1} a {end_line+1} aplicado.")
                else:
                    logger.warning(f"Operação desconhecida: {op_type}")
                    # Não marcar como erro fatal, apenas registrar

            except ValueError as ve:
                logger.error(f"Erro de valor ao processar operação para {file_path}: {op} - {ve}")
                report["results"][file_path] = {"status": "error", "message": f"Erro de valor na operação {op_type}: {ve}"}
                report["success"] = False
                # Restaurar e sair para este arquivo
                shutil.move(backup_path, file_path)
                logger.info(f"Arquivo {file_path} restaurado do backup devido a erro.")
                break # Pula para o próximo arquivo na patch_instructions
            except Exception as e:
                logger.error(f"Erro inesperado ao processar operação para {file_path}: {op} - {e}")
                report["results"][file_path] = {"status": "error", "message": f"Erro inesperado na operação {op_type}: {e}"}
                report["success"] = False
                shutil.move(backup_path, file_path)
                logger.info(f"Arquivo {file_path} restaurado do backup devido a erro.")
                break # Pula para o próximo arquivo

        if report["results"].get(file_path, {}).get("status") == "error":
            continue # Já foi tratado e logado, ir para a próxima instrução de arquivo

        # Escrever as linhas modificadas de volta ao arquivo
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(current_lines)
            logger.info(f"Patches aplicados com sucesso em {file_path}")
            report["results"][file_path] = {"status": "success", "message": "Patches aplicados com sucesso."}
            # Remover backup se tudo correu bem
            if os.path.exists(backup_path):
                os.remove(backup_path)
                logger.debug(f"Backup {backup_path} removido.")
        except Exception as e:
            logger.error(f"Erro ao escrever modificações em {file_path}: {e}")
            report["results"][file_path] = {"status": "error", "message": f"Erro ao escrever modificações: {e}"}
            report["success"] = False
            # Restaurar do backup
            shutil.move(backup_path, file_path)
            logger.info(f"Arquivo {file_path} restaurado do backup devido a erro na escrita.")

    return report

if __name__ == '__main__':
    # Exemplo de uso e teste rápido (pode ser movido para um arquivo de teste dedicado)

    # Criar arquivos de teste
    test_dir = "patch_test_files"
    os.makedirs(test_dir, exist_ok=True)

    original_content_py = """\
def hello_world():
    print("Hello, Original World!")

def another_function():
    # Este é um comentário
    pass

def function_to_delete():
    print("This will be deleted.")
"""
    original_content_txt = """\
Linha 1
Linha 2 - a ser substituída
Linha 3 - a ser substituída
Linha 4
Linha 5 - algo será inserido após esta linha
Linha 6
"""
    with open(os.path.join(test_dir, "test_file.py"), "w") as f:
        f.write(original_content_py)
    with open(os.path.join(test_dir, "test_file.txt"), "w") as f:
        f.write(original_content_txt)

    sample_patch_instructions = [
        {
            "file_path": os.path.join(test_dir, "test_file.py"),
            "reasoning": "Refatorar e adicionar funcionalidade.",
            "operations": [
                {
                    "operation": "REPLACE_BLOCK",
                    "start_line": 1,
                    "end_line": 2,
                    "content": 'def hello_new_world():\n    print("Hello, Patched World!")\n    print("Uma linha adicional")'
                },
                {
                    "operation": "INSERT_AFTER",
                    "line_number": 5, # Após 'pass' (que se tornou linha 6 após o replace acima, mas a IA deve fornecer o número original)
                                      # A lógica de ordenação deve lidar com isso se os números de linha forem do original.
                                      # Se a IA calcular os números de linha dinamicamente, então a ordenação é ainda mais crítica.
                                      # Para este teste, vamos assumir que os números de linha são relativos ao estado *antes* de qualquer operação nesta instrução.
                                      # A implementação atual reordena e aplica de baixo para cima, o que deve ser robusto.
                    "content": '    print("Nova funcionalidade inserida!")'
                },
                {
                    "operation": "DELETE_BLOCK",
                    "start_line": 7, # function_to_delete()
                    "end_line": 8   # print("This will be deleted.")
                }
            ]
        },
        {
            "file_path": os.path.join(test_dir, "test_file.txt"),
            "reasoning": "Atualizar texto.",
            "operations": [
                {
                    "operation": "REPLACE_BLOCK",
                    "start_line": 2,
                    "end_line": 3,
                    "content": "Linha 2 - substituída\nLinha 3 - também substituída"
                },
                {
                    "operation": "INSERT_AFTER",
                    "line_number": 5, # Após "Linha 5 - algo será inserido após esta linha"
                    "content": "CONTEÚDO INSERIDO AQUI"
                },
                 {
                    "operation": "INSERT_AFTER", # Testar inserção no início
                    "line_number": 0,
                    "content": "NOVA PRIMEIRA LINHA"
                }
            ]
        },
        {
            "file_path": os.path.join(test_dir,"non_existent_file.py"),
            "reasoning": "Testar arquivo inexistente.",
            "operations": [
                {"operation": "INSERT_AFTER", "line_number": 1, "content": "test"}
            ]
        }
    ]

    # Teste com a ordenação de operações (REPLACE, INSERT, DELETE para test_file.py)
    # A ordenação por linha (decrescente) e tipo de operação deve garantir que as modificações
    # não interfiram umas com as outras em termos de numeração de linha.

    # Re-verificar os números de linha para test_file.py com a ordenação:
    # Original:
    # 1: def hello_world():
    # 2:     print("Hello, Original World!")
    # 3:
    # 4: def another_function():
    # 5:     # Este é um comentário
    # 6:     pass
    # 7:
    # 8: def function_to_delete():
    # 9:     print("This will be deleted.")

    # Operações (números de linha originais):
    # 1. DELETE_BLOCK (8-9) -> function_to_delete
    # 2. INSERT_AFTER (6) -> após 'pass'
    # 3. REPLACE_BLOCK (1-2) -> hello_world

    # Se aplicadas de baixo para cima (maior linha primeiro):
    # DELETE (8-9):
    # 1: def hello_world():
    # 2:     print("Hello, Original World!")
    # 3:
    # 4: def another_function():
    # 5:     # Este é um comentário
    # 6:     pass
    # 7:
    #
    # INSERT_AFTER (6, '    print("Nova funcionalidade inserida!")'):
    # 1: def hello_world():
    # 2:     print("Hello, Original World!")
    # 3:
    # 4: def another_function():
    # 5:     # Este é um comentário
    # 6:     pass
    # 7:     print("Nova funcionalidade inserida!") <--- Nova linha
    # 8:
    #
    # REPLACE_BLOCK (1-2, 'def hello_new_world():\n    print("Hello, Patched World!")\n    print("Uma linha adicional")'):
    # 1: def hello_new_world():
    # 2:     print("Hello, Patched World!")
    # 3:     print("Uma linha adicional")
    # 4:
    # 5: def another_function():
    # 6:     # Este é um comentário
    # 7:     pass
    # 8:     print("Nova funcionalidade inserida!")
    # 9:

    # Corrigir os números de linha no teste para refletir a intenção original
    # após a ordenação. A IA deve fornecer os números de linha corretos
    # relativos ao arquivo original não modificado. A lógica de ordenação
    # no `apply_patches` é que cuida da aplicação correta.

    sample_patch_instructions[0]["operations"] = [
         { # Operação 1: REPLACE Bloco (linhas 1-2 do original)
            "operation": "REPLACE_BLOCK",
            "start_line": 1,
            "end_line": 2,
            "content": 'def hello_new_world():\n    print("Hello, Patched World!")\n    print("Uma linha adicional")'
        },
        { # Operação 2: INSERT APÓS linha 6 do original ('pass')
            "operation": "INSERT_AFTER",
            "line_number": 6,
            "content": '    print("Nova funcionalidade inserida!")'
        },
        { # Operação 3: DELETE Bloco (linhas 8-9 do original)
            "operation": "DELETE_BLOCK",
            "start_line": 8,
            "end_line": 9
        }
    ]


    results = apply_patches(sample_patch_instructions)
    logger.info(f"Resultado da aplicação dos patches de teste: {results}")

    logger.info("\nConteúdo esperado de test_file.py após patches:")
    expected_py_content = """\
def hello_new_world():
    print("Hello, Patched World!")
    print("Uma linha adicional")

def another_function():
    # Este é um comentário
    pass
    print("Nova funcionalidade inserida!")
"""
    logger.info(expected_py_content)

    logger.info("\nConteúdo real de test_file.py após patches:")
    if os.path.exists(os.path.join(test_dir, "test_file.py")):
        with open(os.path.join(test_dir, "test_file.py"), "r") as f:
            logger.info(f.read())

    logger.info("\nConteúdo esperado de test_file.txt após patches:")
    expected_txt_content = """\
NOVA PRIMEIRA LINHA
Linha 1
Linha 2 - substituída
Linha 3 - também substituída
Linha 4
Linha 5 - algo será inserido após esta linha
CONTEÚDO INSERIDO AQUI
Linha 6
"""
    # Nota: A inserção no início (linha 0) e a normalização de nova linha podem precisar de ajuste fino.
    # O `content` não deve ter newlines no início/fim se for uma única linha inserida,
    # a menos que a intenção seja adicionar uma linha em branco.
    # A função `splitlines(True)` e a adição de `\n` se necessário tentam lidar com isso.
    logger.info(expected_txt_content)

    logger.info("\nConteúdo real de test_file.txt após patches:")
    if os.path.exists(os.path.join(test_dir, "test_file.txt")):
        with open(os.path.join(test_dir, "test_file.txt"), "r") as f:
            logger.info(f.read())

    # Limpeza (opcional, pode ser útil manter para inspeção)
    # shutil.rmtree(test_dir)
    # logger.info(f"Diretório de teste {test_dir} removido.")
    pass
