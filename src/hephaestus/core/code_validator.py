import tempfile
import os
import py_compile
import sys
import json
import logging
from pathlib import Path
from hephaestus.core import code_metrics # Updated import

# Configuração básica de logging se não configurado externamente
# logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')


def perform_deep_validation(file_path: Path, logger: logging.Logger) -> dict | None:
    """
    Realiza uma análise profunda da qualidade do código Python.
    Retorna um dicionário com o relatório ou None em caso de falha na leitura.
    """
    logger.info(f"Iniciando validação profunda para: {file_path}")
    try:
        code_content = file_path.read_text(encoding="utf-8")
    except Exception as e:
        logger.error(f"Não foi possível ler o arquivo {file_path} para validação profunda: {e}")
        return None

    complexity_report = code_metrics.analyze_complexity(code_content)
    if complexity_report.get("error"):
        logger.warning(f"Erro na análise de complexidade para {file_path}: {complexity_report['error']}")
        # Prosseguir mesmo com erro de complexidade para tentar outras análises

    duplication_report = code_metrics.detect_code_duplication(code_content)

    # O calculate_quality_score lida com relatórios de erro internamente
    quality_score = code_metrics.calculate_quality_score(complexity_report, duplication_report)

    report = {
        "file_path": str(file_path),
        "quality_score": quality_score,
        "complexity": complexity_report,
        "duplication": duplication_report,
    }

    logger.info(f"Relatório de Qualidade para {file_path}: Score = {quality_score:.2f}")
    if complexity_report and not complexity_report.get("error"):
        logger.info(f"  Complexidade Ciclomática Geral: {complexity_report.get('overall_cyclomatic_complexity', 'N/A')}")
        logger.info(f"  LLOC: {complexity_report.get('lloc', 'N/A')}, Comentários: {complexity_report.get('comments', 'N/A')}")
    if duplication_report:
        logger.info(f"  Blocos Duplicados Encontrados: {len(duplication_report)}")
        for i, dupe in enumerate(duplication_report[:3]): # Logar detalhes dos primeiros 3 blocos
            logger.debug(f"    Duplicação {i+1}: {dupe['num_occurrences']} ocorrências, {dupe['block_length_lines']} linhas.")

    return report


def validate_python_code(file_path: str | Path, logger: logging.Logger, perform_deep_analysis: bool = True) -> tuple[bool, str | None, dict | None]:
    """
    Valida se o código Python em um arquivo é sintaticamente correto e, opcionalmente, realiza uma análise profunda.
    Retorna (True, None, deep_report) se válido, ou (False, mensagem de erro, deep_report ou None) se inválido.
    O deep_report é o relatório da análise profunda, ou None se não realizada ou falhou.
    """
    path_obj = Path(file_path)
    deep_analysis_report = None

    if not path_obj.exists():
        logger.error(f"Arquivo Python não encontrado para validação: {path_obj}")
        return False, f"Arquivo não encontrado: {path_obj}", None

    try:
        logger.debug(f"Validando sintaxe Python de: {path_obj}")
        py_compile.compile(str(path_obj), doraise=True)
        logger.debug(f"Sintaxe Python de '{path_obj}' é válida.")

        if perform_deep_analysis:
            logger.debug(f"Realizando análise profunda para '{path_obj}'...")
            deep_analysis_report = perform_deep_validation(path_obj, logger)
            if deep_analysis_report:
                logger.info(f"Análise profunda para '{path_obj}' concluída. Score: {deep_analysis_report.get('quality_score', 'N/A')}")
            else:
                logger.warning(f"Análise profunda para '{path_obj}' não pôde ser concluída (erro na leitura do arquivo ou análise).")

        return True, None, deep_analysis_report
    
    except py_compile.PyCompileError as e:
        logger.warning(f"Erro de sintaxe Python em '{path_obj}': {e.msg}")
        # Mesmo com erro de sintaxe, podemos tentar a análise profunda se desejado,
        # embora possa não ser muito útil ou até mesmo falhar.
        # Por ora, não faremos se a sintaxe básica falhar.
        return False, e.msg, None
    except Exception as e:
        logger.error(f"Erro inesperado ao validar Python em '{path_obj}': {e}", exc_info=True)
        return False, f"Erro inesperado: {str(e)}", None
    # 'finally' block removed as it was empty and not strictly necessary here.


def validate_json_syntax(file_path: str | Path, logger: logging.Logger) -> tuple[bool, str | None]:
    """Valida se um arquivo contém JSON válido.
    
    Args:
        file_path: Caminho para o arquivo JSON.
        logger: Instância do logger.
        
    Returns:
        Tupla (is_valid, error_message ou None)
    """
    path_obj = Path(file_path)
    if not path_obj.exists():
        logger.error(f"Arquivo JSON não encontrado para validação de sintaxe: {path_obj}")
        return False, f"Arquivo não encontrado: {path_obj}"

    try:
        logger.debug(f"Validando sintaxe JSON de: {path_obj}")
        with open(path_obj, "r", encoding="utf-8") as f:
            json.load(f) # Tenta carregar o JSON do arquivo
        logger.debug(f"Sintaxe JSON de '{path_obj}' é válida.")
        return True, None
    except json.JSONDecodeError as e:
        logger.warning(f"Erro de sintaxe JSON em '{path_obj}': {e.msg}") # Corrigido para warning
        return False, e.msg # e.msg é geralmente mais limpo
    except Exception as e:
        logger.error(f"Erro inesperado ao validar JSON em '{path_obj}': {e}", exc_info=True)
        return False, f"Erro inesperado: {str(e)}"
