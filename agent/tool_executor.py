import asyncio
import sys
import time # Mantido para run_in_sandbox síncrono por enquanto
import aiohttp # Adicionado para web_search assíncrono
from typing import Tuple, Dict, Any, List

import psutil # Mantido para run_in_sandbox síncrono por enquanto
import os
from pathlib import Path
import subprocess # Mantido para run_in_sandbox síncrono por enquanto


async def _read_stream(stream, output_lines):
    while True:
        line = await stream.readline()
        if line:
            output_lines.append(line.decode())
        else:
            break

async def run_async_subprocess(command: List[str], cwd: str | Path | None = None) -> Tuple[int, str, str]:
    """Helper to run a subprocess asynchronously and capture its output."""
    if isinstance(cwd, Path):
        cwd_str = str(cwd)
    else:
        cwd_str = cwd

    process = await asyncio.create_subprocess_exec(
        *command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        cwd=cwd_str
    )

    stdout_lines = []
    stderr_lines = []

    await asyncio.gather(
        _read_stream(process.stdout, stdout_lines),
        _read_stream(process.stderr, stderr_lines)
    )

    await process.wait()
    return process.returncode, "".join(stdout_lines), "".join(stderr_lines)


async def run_pytest(test_dir: str = "tests/", cwd: str | Path | None = None) -> Tuple[bool, str]:
    """
    Executa testes pytest no diretório especificado e retorna resultados de forma assíncrona.
    
    Args:
        test_dir: Diretório contendo os testes (padrão: 'tests/'), relativo ao cwd.
        cwd: Diretório de trabalho atual para executar o pytest (padrão: None, usa o CWD atual).
    
    Returns:
        Tuple[bool, str]: (success, output) 
        - success: True se todos os testes passarem, False caso contrário
        - output: Saída combinada de stdout e stderr da execução
    """
    command = [sys.executable, "-m", "pytest", test_dir]

    if isinstance(cwd, Path):
        cwd_str = str(cwd)
    else:
        cwd_str = cwd

    try:
        returncode, stdout, stderr = await run_async_subprocess(command, cwd_str)
        success = returncode == 0
        output_message = f"Pytest Command: {' '.join(command)} (CWD: {cwd_str or '.'})\n"
        output_message += f"Exit Code: {returncode}\n\nStdout:\n{stdout}\nStderr:\n{stderr}"
        return success, output_message
    except FileNotFoundError:
        return False, f"Erro ao executar pytest: Comando '{sys.executable} -m pytest' não encontrado ou pytest não instalado."
    except Exception as e:
        return False, f"Erro inesperado ao executar pytest: {str(e)}"


async def check_file_existence(file_paths: list[str]) -> Tuple[bool, str]:
    """
    Verifica se todos os arquivos especificados existem.

    Args:
        file_paths: Uma lista de caminhos de arquivo para verificar.

    Returns:
        Tuple[bool, str]: (success, message)
        - success: True se todos os arquivos existirem, False caso contrário.
        - message: Mensagem indicando o resultado.
    """
    if not file_paths:
        return False, "Nenhum caminho de arquivo fornecido para verificação."

    # Para I/O de arquivo assíncrono, aiofiles seria o ideal,
    # mas os.path.exists é geralmente rápido o suficiente para não precisar de async.
    # Se houver muitos arquivos ou caminhos de rede, isso pode ser reconsiderado.
    # Por enquanto, mantemos síncrono dentro de uma função async.
    missing_files = []
    for file_path in file_paths:
        if not await asyncio.to_thread(os.path.exists, file_path):
            missing_files.append(file_path)

    if not missing_files:
        return True, "Todos os arquivos especificados existem."
    else:
        return False, f"Arquivo(s) não encontrado(s): {', '.join(missing_files)}"


async def run_in_sandbox(temp_dir_path: str, objective: str) -> Dict[str, Any]:
    """Executa o main.py de um diretório isolado monitorando tempo e memória, de forma assíncrona."""
    # Nota: A monitoração de memória com psutil em um processo filho assíncrono
    # pode ser complexa. Esta implementação foca na execução do subprocesso.
    # A monitoração de recursos pode precisar ser ajustada ou simplificada.

    cmd = [sys.executable, "main.py", objective, "--benchmark", "--max-cycles=1"] # Adicionado max-cycles para garantir que termine

    start_time = asyncio.get_event_loop().time() # Usar o tempo do loop de eventos

    returncode, stdout, stderr = await run_async_subprocess(cmd, temp_dir_path)

    execution_time = asyncio.get_event_loop().time() - start_time
    output = f"Stdout:\n{stdout}\nStderr:\n{stderr}"

    # A medição de pico de memória com psutil é mais difícil de forma confiável
    # para um subprocesso que já terminou. Para uma medição precisa,
    # seria necessário um monitoramento em tempo real ou uma abordagem diferente.
    # Por simplicidade, vamos omitir o pico de memória preciso nesta versão async.
    peak_memory_mb = -1 # Placeholder

    return {
        "execution_time": execution_time,
        "peak_memory_mb": peak_memory_mb, # Simplificado
        "exit_code": returncode,
        "output": output,
    }


async def run_git_command(command: list[str]) -> Tuple[bool, str]:
    """
    Executa um comando Git e retorna o status e a saída.

    Args:
        command: Uma lista de strings representando o comando Git e seus argumentos.
                 Ex: ['git', 'add', '.'] or ['git', 'commit', '-m', 'Initial commit']

    Returns:
        Tuple[bool, str]: (success, output)
        - success: True se o comando Git for executado com sucesso (returncode == 0), False caso contrário.
        - output: Saída combinada de stdout e stderr da execução do comando Git.
    """
    if not command or command[0] != 'git':
        return False, "Comando inválido. Deve começar com 'git'."
    try:
        returncode, stdout, stderr = await run_async_subprocess(command)
        success = returncode == 0
        output = f"Comando: {' '.join(command)}\nExit Code: {returncode}\n\nStdout:\n{stdout}\nStderr:\n{stderr}"
        return success, output
    except FileNotFoundError: # Isto pode não ser capturável diretamente por run_async_subprocess se o próprio comando 'git' não for encontrado pelo SO.
                              # create_subprocess_exec pode levantar FileNotFoundError se o executável não for encontrado.
        return False, "Erro: O comando 'git' não foi encontrado. Certifique-se de que o Git está instalado e no PATH."
    except Exception as e:
        return False, f"Erro inesperado ao executar comando Git: {str(e)}"


async def web_search(query: str) -> Tuple[bool, str]:
    """
    Realiza uma pesquisa na web usando a API DuckDuckGo e retorna os resultados de forma assíncrona.

    Args:
        query: A string de pesquisa a ser enviada para o DuckDuckGo.

    Returns:
        Tuple[bool, str]: (success, results)
        - success: True se a pesquisa for bem-sucedida, False caso contrário.
        - results: Resultados formatados da pesquisa ou mensagem de erro.
    """
    try:
        search_url = f"https://api.duckduckgo.com/?q={query}&format=json"
        async with aiohttp.ClientSession() as session:
            async with session.get(search_url) as response:
                response.raise_for_status() # Levanta exceção para status HTTP 4xx/5xx
                data = await response.json()

                # Processar resultados
                output_parts = []
                if data.get("AbstractText"):
                    output_parts.append(f"Resumo: {data['AbstractText']} (Fonte: {data.get('AbstractSource', 'N/A')})")

                related_topics = data.get("RelatedTopics", [])
                if related_topics:
                    output_parts.append("\nTópicos Relacionados:")
                    for i, topic in enumerate(related_topics[:3], 1): # Limitar a 3 tópicos relacionados
                        if topic.get("Text"):
                             output_parts.append(f"{i}. {topic['Text']}")
                             if topic.get("FirstURL"):
                                 output_parts.append(f"   URL: {topic['FirstURL']}")
                        elif topic.get("Topics"): # Estrutura aninhada de tópicos
                            output_parts.append(f"{i}. {topic.get('Name', 'Grupo de tópicos')}:")
                            for sub_topic in topic.get("Topics", [])[:2]: # Limitar a 2 subtópicos
                                if sub_topic.get("Text") and sub_topic.get("FirstURL"):
                                     output_parts.append(f"  - {sub_topic['Text']} (URL: {sub_topic['FirstURL']})")


                if not data.get("AbstractText") and len(related_topics) < 2 :
                    web_results = data.get("Results", [])
                    if web_results:
                        output_parts.append("\nResultados da Web:")
                        for i, result in enumerate(web_results[:3], 1): # Limitar a 3 resultados web
                            output_parts.append(f"{i}. {result.get('Text', 'Sem descrição')}")
                            if result.get("FirstURL"):
                                output_parts.append(f"   URL: {result.get('FirstURL')}")

                if not output_parts:
                    return True, "Nenhum resultado principal encontrado para a pesquisa."

                return True, "\n".join(output_parts)

    except aiohttp.ClientError as e:
        return False, f"Erro na pesquisa web (ClientError): {str(e)}"
    except Exception as e:
        return False, f"Erro inesperado na pesquisa web: {str(e)}"
