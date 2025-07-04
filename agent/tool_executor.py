import subprocess
import sys
import time
import requests  # Adicionado para suportar web_search
from typing import Tuple, Dict, Any, Optional

import psutil
import os
from pathlib import Path # ADICIONADO

def run_pytest(test_dir: str = "tests/", cwd: str | Path | None = None) -> Tuple[bool, str]:
    """
    Executa testes pytest no diretório especificado e retorna resultados.
    
    Args:
        test_dir: Diretório contendo os testes (padrão: 'tests/'), relativo ao cwd.
        cwd: Diretório de trabalho atual para executar o pytest (padrão: None, usa o CWD atual).
    
    Returns:
        Tuple[bool, str]: (success, output) 
        - success: True se todos os testes passarem, False caso contrário
        - output: Saída combinada de stdout e stderr da execução
    """
    command = ["pytest", test_dir]

    # Normalizar cwd para string, se for Path
    if isinstance(cwd, Path):
        cwd_str = str(cwd)
    else:
        cwd_str = cwd

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=False,
            cwd=cwd_str # Definir o diretório de trabalho se fornecido
        )
        success = result.returncode == 0
        output_message = f"Pytest Command: {' '.join(command)} (CWD: {cwd_str or '.'})\n"
        output_message += f"Exit Code: {result.returncode}\n\nStdout:\n{result.stdout}\nStderr:\n{result.stderr}"
        return success, output_message
    except FileNotFoundError: # Se o executável pytest não for encontrado
        return False, f"Erro ao executar pytest: Comando 'pytest' não encontrado. Certifique-se de que pytest está instalado e no PATH."
    except Exception as e:
        return False, f"Erro inesperado ao executar pytest: {str(e)}"


def check_file_existence(file_paths: list[str]) -> Tuple[bool, str]:
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

    missing_files = []
    for file_path in file_paths:
        if not os.path.exists(file_path):
            missing_files.append(file_path)

    if not missing_files:
        return True, "Todos os arquivos especificados existem."
    else:
        return False, f"Arquivo(s) não encontrado(s): {', '.join(missing_files)}"


def read_file(file_path: str) -> Optional[str]:
    """
    Lê o conteúdo de um arquivo e o retorna como uma string.

    Args:
        file_path: O caminho para o arquivo.

    Returns:
        O conteúdo do arquivo como uma string, ou None se o arquivo não for encontrado.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return None
    except Exception as e:
        # Log a more general error if something else goes wrong
        # (logging would need to be passed in or handled differently)
        print(f"Error reading file {file_path}: {e}")
        return None


def run_in_sandbox(temp_dir_path: str, objective: str) -> Dict[str, Any]:
    """Executa o main.py de um diretório isolado monitorando tempo e memória."""
    cmd = [sys.executable, "main.py", objective, "--benchmark"]

    start_time = time.time()
    process = subprocess.Popen(
        cmd,
        cwd=temp_dir_path,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )

    ps_proc = psutil.Process(process.pid)
    peak_memory = 0.0
    output_lines = []

    while True:
        if process.poll() is not None:
            if process.stdout:
                remaining = process.stdout.read()
                if remaining:
                    output_lines.append(remaining)
            break

        try:
            mem = ps_proc.memory_info().rss / (1024 ** 2)
            if mem > peak_memory:
                peak_memory = mem
        except psutil.NoSuchProcess:
            pass

        line = process.stdout.readline() if process.stdout else ""
        if line:
            output_lines.append(line)
        time.sleep(0.1)

    exit_code = process.wait()
    execution_time = time.time() - start_time

    return {
        "execution_time": execution_time,
        "peak_memory_mb": peak_memory,
        "exit_code": exit_code,
        "output": "".join(output_lines),
    }


def run_git_command(command: list[str]) -> Tuple[bool, str]:
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
        process = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=False  # Não levanta exceção para returncodes diferentes de 0
        )
        success = process.returncode == 0
        output = f"Comando: {' '.join(command)}\nExit Code: {process.returncode}\n\nStdout:\n{process.stdout}\nStderr:\n{process.stderr}"
        return success, output
    except FileNotFoundError:
        return False, "Erro: O comando 'git' não foi encontrado. Certifique-se de que o Git está instalado e no PATH."
    except Exception as e:
        return False, f"Erro inesperado ao executar comando Git: {str(e)}"


def web_search(query: str, max_results: int = 5, context: str = "") -> Tuple[bool, str]:
    """
    Realiza uma pesquisa na web inteligente usando múltiplas estratégias.

    Args:
        query: A string de pesquisa.
        max_results: Número máximo de resultados a retornar.
        context: Contexto adicional para melhorar a pesquisa.

    Returns:
        Tuple[bool, str]: (success, results)
        - success: True se a pesquisa for bem-sucedida, False caso contrário.
        - results: Resultados formatados da pesquisa ou mensagem de erro.
    """
    try:
        # Otimizar query baseado no contexto
        optimized_query = _optimize_search_query(query, context)
        
        # Tentar múltiplas fontes de pesquisa
        results = []
        
        # 1. DuckDuckGo API (principal)
        ddg_results = _search_duckduckgo(optimized_query, max_results)
        if ddg_results:
            results.extend(ddg_results)
        
        # 2. Se poucos resultados, tentar busca mais específica
        if len(results) < max_results // 2:
            # Busca mais específica baseada no contexto
            fallback_query = _create_fallback_query(query, context)
            fallback_results = _search_duckduckgo(fallback_query, max_results - len(results))
            results.extend(fallback_results)
        
        # Processar e ranquear resultados
        processed_results = _process_and_rank_results(results, query, context)
        
        if not processed_results:
            return True, f"Nenhum resultado relevante encontrado para: '{query}'"
        
        # Formatear resultados
        formatted_results = _format_search_results(processed_results[:max_results])
        
        return True, formatted_results
        
    except Exception as e:
        print(f"Erro na busca DuckDuckGo: {e}")
        return False, f"Erro na pesquisa web: {str(e)}"


def _optimize_search_query(query: str, context: str) -> str:
    """Otimiza a query de busca baseada no contexto."""
    # Remove palavras muito comuns
    stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
    words = [w for w in query.lower().split() if w not in stop_words]
    
    # Adiciona termos específicos baseados no contexto
    if "python" in context.lower() or "import" in context.lower():
        if "python" not in query.lower():
            words.append("python")
    
    if "error" in context.lower() or "exception" in context.lower():
        if not any(err in query.lower() for err in ["error", "exception", "fix"]):
            words.append("fix")
    
    if "install" in context.lower() or "package" in context.lower():
        if "pip" not in query.lower():
            words.append("pip")
    
    # Adiciona site específicos para diferentes tipos de consultas
    if any(term in query.lower() for term in ["documentation", "docs", "api"]):
        return f"{' '.join(words)} site:docs.python.org OR site:readthedocs.io"
    
    if any(term in query.lower() for term in ["tutorial", "example", "how to"]):
        return f"{' '.join(words)} tutorial example"
    
    if any(term in query.lower() for term in ["error", "exception", "bug"]):
        return f"{' '.join(words)} site:stackoverflow.com OR site:github.com"
    
    return ' '.join(words)


def _create_fallback_query(query: str, context: str) -> str:
    """Cria uma query de fallback mais específica."""
    base_words = query.lower().split()
    
    # Estratégias de fallback baseadas no contexto
    if "python" in context.lower():
        return f"python {query} programming"
    elif "error" in context.lower():
        return f"{query} solution fix troubleshoot"
    elif "install" in context.lower():
        return f"how to install {query} setup"
    else:
        return f"{query} guide tutorial"


def _search_duckduckgo(query: str, max_results: int) -> list:
    """Realiza busca no DuckDuckGo."""
    try:
        # Usar tanto a API quanto busca HTML para mais resultados
        results = []
        
        # API do DuckDuckGo (limitada)
        api_url = f"https://api.duckduckgo.com/?q={query}&format=json&no_html=1"
        response = requests.get(api_url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            # Resultados instantâneos
            for result in data.get('Results', []):
                if len(results) >= max_results:
                    break
                results.append({
                    'title': result.get('Text', ''),
                    'url': result.get('FirstURL', ''),
                    'snippet': result.get('Text', ''),
                    'source': 'duckduckgo_instant'
                })
            
            # Tópicos relacionados
            for topic in data.get('RelatedTopics', []):
                if len(results) >= max_results:
                    break
                if isinstance(topic, dict) and 'Text' in topic:
                    results.append({
                        'title': topic.get('Text', '').split(' - ')[0],
                        'url': topic.get('FirstURL', ''),
                        'snippet': topic.get('Text', ''),
                        'source': 'duckduckgo_related'
                    })
        
        return results
        
    except Exception as e:
        print(f"Erro na busca DuckDuckGo: {e}")
        # Levanta exceção para que seja capturada pela função principal
        raise e


def _process_and_rank_results(results: list, original_query: str, context: str) -> list:
    """Processa e ranqueia resultados por relevância."""
    if not results:
        return []
    
    query_words = set(original_query.lower().split())
    context_words = set(context.lower().split()) if context else set()
    
    scored_results = []
    for result in results:
        score = _calculate_relevance_score(result, query_words, context_words)
        if score > 0:  # Filtrar resultados irrelevantes
            result['relevance_score'] = score
            scored_results.append(result)
    
    # Ordenar por score de relevância
    scored_results.sort(key=lambda x: x['relevance_score'], reverse=True)
    
    return scored_results


def _calculate_relevance_score(result: dict, query_words: set, context_words: set) -> float:
    """Calcula score de relevância para um resultado."""
    title = result.get('title', '').lower()
    snippet = result.get('snippet', '').lower()
    url = result.get('url', '').lower()
    
    score = 0.0
    
    # Score baseado em palavras da query no título (peso alto)
    title_matches = len(query_words.intersection(set(title.split())))
    score += title_matches * 3.0
    
    # Score baseado em palavras da query no snippet
    snippet_matches = len(query_words.intersection(set(snippet.split())))
    score += snippet_matches * 1.5
    
    # Score baseado em palavras do contexto
    context_title_matches = len(context_words.intersection(set(title.split())))
    context_snippet_matches = len(context_words.intersection(set(snippet.split())))
    score += (context_title_matches * 1.0) + (context_snippet_matches * 0.5)
    
    # Bonus para sites confiáveis
    trusted_domains = ['stackoverflow.com', 'docs.python.org', 'github.com', 'readthedocs.io', 'python.org']
    if any(domain in url for domain in trusted_domains):
        score += 2.0
    
    # Bonus para documentação oficial
    if any(term in url for term in ['docs', 'documentation', 'manual']):
        score += 1.5
    
    # Penalidade para resultados muito curtos
    if len(snippet) < 50:
        score -= 0.5
    
    return score


def _format_search_results(results: list) -> str:
    """Formata os resultados de busca para exibição."""
    if not results:
        return "Nenhum resultado encontrado."
    
    formatted = ["🔍 RESULTADOS DA PESQUISA WEB:", ""]
    
    for i, result in enumerate(results, 1):
        title = result.get('title', 'Sem título')[:100]
        url = result.get('url', '')
        snippet = result.get('snippet', 'Sem descrição')[:200]
        score = result.get('relevance_score', 0)
        
        formatted.append(f"{i}. **{title}**")
        formatted.append(f"   🔗 {url}")
        formatted.append(f"   📝 {snippet}")
        formatted.append(f"   ⭐ Relevância: {score:.1f}")
        formatted.append("")
    
    return "\n".join(formatted)


def advanced_web_search(query: str, search_type: str = "general", context: dict | None = None) -> Tuple[bool, dict]:
    """
    Busca web avançada com diferentes tipos de pesquisa otimizados.
    
    Args:
        query: Consulta de busca
        search_type: Tipo de busca ("error_solution", "documentation", "tutorial", "library_info")
        context: Contexto adicional sobre o problema/necessidade
        
    Returns:
        Tuple[bool, dict]: (success, results_dict)
    """
    if context is None:
        context = {}
    
    try:
        # Otimizar query baseada no tipo de busca
        optimized_query = _optimize_query_by_type(query, search_type, context)
        
        # Realizar busca
        success, raw_results = web_search(optimized_query, max_results=8, context=str(context))
        
        if not success:
            return False, {"error": raw_results}
        
        # Processar resultados baseado no tipo
        processed_results = _process_results_by_type(raw_results, search_type, context)
        
        return True, processed_results
        
    except Exception as e:
        return False, {"error": f"Erro na busca avançada: {str(e)}"}


def _optimize_query_by_type(query: str, search_type: str, context: dict) -> str:
    """Otimiza query baseada no tipo de busca."""
    base_query = query
    
    if search_type == "error_solution":
        error_context = context.get("error_type", "")
        language = context.get("language", "python")
        return f"{base_query} {error_context} fix solution {language} site:stackoverflow.com"
    
    elif search_type == "documentation":
        library = context.get("library", "")
        return f"{base_query} {library} documentation official docs api reference"
    
    elif search_type == "tutorial":
        skill_level = context.get("skill_level", "beginner")
        return f"{base_query} tutorial {skill_level} example step-by-step guide"
    
    elif search_type == "library_info":
        return f"{base_query} python library package pip install usage example"
    
    else:  # general
        return base_query


def _process_results_by_type(raw_results: str, search_type: str, context: dict) -> dict:
    """Processa resultados baseado no tipo de busca."""
    # Parse dos resultados brutos
    results = []
    current_result = {}
    
    for line in raw_results.split('\n'):
        if line.startswith(('1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.')):
            if current_result:
                results.append(current_result)
            current_result = {'title': line[3:].strip()}
        elif line.strip().startswith('🔗'):
            current_result['url'] = line.replace('🔗', '').strip()
        elif line.strip().startswith('📝'):
            current_result['snippet'] = line.replace('📝', '').strip()
        elif line.strip().startswith('⭐'):
            relevance = line.replace('⭐ Relevância:', '').strip()
            current_result['relevance'] = relevance
    
    if current_result:
        results.append(current_result)
    
    # Processar baseado no tipo
    processed = {
        "search_type": search_type,
        "query": context.get("original_query", ""),
        "total_results": len(results),
        "results": results,
        "summary": _create_results_summary(results, search_type),
        "recommendations": _create_recommendations(results, search_type, context)
    }
    
    return processed


def _create_results_summary(results: list, search_type: str) -> str:
    """Cria um resumo dos resultados encontrados."""
    if not results:
        return "Nenhum resultado relevante encontrado."
    
    top_result = results[0] if results else {}
    
    if search_type == "error_solution":
        return f"Encontradas {len(results)} possíveis soluções. A mais relevante sugere: {top_result.get('snippet', 'Ver detalhes')[:150]}..."
    
    elif search_type == "documentation":
        return f"Encontrada documentação em {len(results)} fontes. Recomenda-se começar por: {top_result.get('title', 'Primeiro resultado')}"
    
    elif search_type == "tutorial":
        return f"Encontrados {len(results)} tutoriais. Sugestão principal: {top_result.get('title', 'Primeiro resultado')}"
    
    elif search_type == "library_info":
        return f"Informações encontradas sobre a biblioteca em {len(results)} fontes."
    
    else:
        return f"Encontrados {len(results)} resultados relevantes."


def _create_recommendations(results: list, search_type: str, context: dict) -> list:
    """Cria recomendações baseadas nos resultados."""
    if not results:
        return ["Refinar a consulta de busca com termos mais específicos."]
    
    recommendations = []
    
    if search_type == "error_solution":
        recommendations.extend([
            f"Verificar a solução mais relevante: {results[0].get('url', '')}",
            "Confirmar se a versão da biblioteca/linguagem corresponde ao problema.",
            "Testar a solução em um ambiente isolado primeiro."
        ])
    
    elif search_type == "documentation":
        recommendations.extend([
            f"Consultar a documentação oficial: {results[0].get('url', '')}",
            "Verificar exemplos de código na documentação.",
            "Procurar por seções de 'Getting Started' ou 'Quick Start'."
        ])
    
    elif search_type == "tutorial":
        recommendations.extend([
            f"Seguir o tutorial passo-a-passo: {results[0].get('url', '')}",
            "Praticar os exemplos fornecidos.",
            "Adaptar os conceitos ao contexto específico do projeto."
        ])
    
    recommendations.append("Comparar múltiplas fontes antes de implementar soluções.")
    
    return recommendations
