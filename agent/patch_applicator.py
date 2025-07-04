"""Utilities for applying textual patches to files.

The functions here are used by the agent to modify project files.  Each
instruction describes an ``INSERT``, ``REPLACE`` or ``DELETE_BLOCK``
operation and this module executes them.
"""

import os
import re
import logging
from pathlib import Path
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Tuple, Type


class PatchOperationHandler(ABC):
    """Abstract base class for a patch operation handler."""

    def __init__(self, full_path: Path, lines: List[str], instruction: Dict[str, Any], logger: logging.Logger):
        self.full_path = full_path
        self.lines = lines
        self.instruction = instruction
        self.logger = logger

    @abstractmethod
    def execute(self) -> Tuple[bool, List[str], bool]:
        """
        Apply a patch and return (success, updated_lines, skip_write).
        
        skip_write signals that the caller should not rewrite the file 
        (e.g., when the file was deleted).
        """
        pass

class InsertHandler(PatchOperationHandler):
    """Handler for INSERT operations."""
    def execute(self) -> Tuple[bool, List[str], bool]:
        content = self.instruction.get("content", "")
        if not isinstance(content, list):
            insert_lines = content.splitlines()
        else:
            insert_lines = [str(line) for line in content]

        line_number = self.instruction.get("line_number")
        if line_number is not None:
            try:
                line_number = int(line_number)
                if line_number <= 0:
                    self.logger.warning(
                        f"line_number {line_number} inválido para INSERT em '{self.full_path}', usando 1.")
                    line_number = 1
            except ValueError:
                self.logger.error(
                    f"line_number '{line_number}' inválido para INSERT em '{self.full_path}'. Pulando patch.")
                return False, self.lines, True
            idx = min(max(0, line_number - 1), len(self.lines))
        else:
            idx = len(self.lines)

        self.lines[idx:idx] = insert_lines
        self.logger.debug(
            f"Conteúdo inserido em '{self.full_path}' na linha {line_number if line_number else 'final'}.")
        return True, self.lines, False

class ReplaceHandler(PatchOperationHandler):
    """Handler for REPLACE operations."""
    def execute(self) -> Tuple[bool, List[str], bool]:
        pattern = self.instruction.get("block_to_replace")
        content = self.instruction.get("content", "")
        if not isinstance(content, list):
            new_lines = content.splitlines()
        else:
            new_lines = [str(line) for line in content]

        if pattern is None:
            self.logger.info(
                f"REPLACE sem 'block_to_replace' para '{self.full_path}'. Arquivo será sobrescrito.")
            return True, new_lines, False

        file_content = "\n".join(self.lines)
        is_regex = self.instruction.get("is_regex", False) or any(c in pattern for c in r"*+?^$[]{}()|\\")

        replaced = False
        if is_regex:
            try:
                mod, num = re.subn(pattern, "\n".join(new_lines), file_content,
                                   count=0, flags=re.MULTILINE | re.DOTALL)
                if num > 0:
                    self.lines = mod.splitlines()
                    self.logger.debug(
                        f"Bloco(s) regex '{pattern}' substituído(s) em '{self.full_path}' ({num} ocorrências).")
                    replaced = True
                else:
                    self.logger.warning(
                        f"Padrão regex '{pattern}' não encontrado em '{self.full_path}' para REPLACE.")
            except re.error as e:
                self.logger.error(
                    f"Erro de regex em 'block_to_replace':'{pattern}' para '{self.full_path}'. Erro: {e}. Tentando como string literal.")
                if pattern in file_content:
                    mod = file_content.replace(pattern, "\n".join(new_lines), 1)
                    self.lines = mod.splitlines()
                    self.logger.debug(
                        f"Bloco '{pattern}' (literal fallback) substituído em '{self.full_path}'.")
                    replaced = True
                else:
                    self.logger.warning(
                        f"Bloco '{pattern}' (literal fallback) não encontrado em '{self.full_path}' para REPLACE.")
        else:
            if pattern in file_content:
                mod = file_content.replace(pattern, "\n".join(new_lines), 1)
                self.lines = mod.splitlines()
                self.logger.debug(
                    f"Bloco literal '{pattern}' substituído em '{self.full_path}'.")
                replaced = True
            else:
                if self.full_path.exists():
                    self.logger.warning(
                        f"Bloco literal '{pattern}' não encontrado em '{self.full_path}' para REPLACE.")
                else:
                    self.logger.error(
                        f"Tentativa de REPLACE de bloco específico '{pattern}' em arquivo inexistente '{self.full_path}'. Pulando.")
                    return False, self.lines, True

        if not replaced and self.full_path.exists():
            self.logger.warning(
                f"Nenhuma substituição realizada para '{pattern}' em '{self.full_path}'.")
        elif not self.full_path.exists():
            self.logger.info(f"Arquivo '{self.full_path}' será criado com o novo conteúdo.")

        return True, self.lines, False

class DeleteBlockHandler(PatchOperationHandler):
    """Handler for DELETE_BLOCK operations."""
    def execute(self) -> Tuple[bool, List[str], bool]:
        pattern = self.instruction.get("block_to_delete")
        if pattern is None:
            if self.full_path.exists():
                try:
                    os.remove(self.full_path)
                    self.logger.info(
                        f"Arquivo '{self.full_path}' removido com sucesso (DELETE_BLOCK com block_to_delete=None).")
                except Exception as e:
                    self.logger.error(f"Falha ao remover arquivo '{self.full_path}': {e}")
                    return False, self.lines, True
            else:
                self.logger.warning(
                    f"Arquivo '{self.full_path}' não existe. Nada para deletar com DELETE_BLOCK.")
            return True, self.lines, True

        if not pattern:
            self.logger.error(
                f"Operação DELETE_BLOCK para '{self.full_path}' não especificou 'block_to_delete' válido. Pulando.")
            return False, self.lines, True

        if not self.full_path.exists():
            self.logger.warning(
                f"Arquivo '{self.full_path}' não existe. Nada para deletar com DELETE_BLOCK.")
            return True, self.lines, True

        file_content = "\n".join(self.lines)
        is_regex = self.instruction.get("is_regex", False) or any(c in pattern for c in r"*+?^$[]{}()|\\")

        deleted = False
        if is_regex:
            try:
                mod, num = re.subn(pattern, "", file_content, count=0,
                                   flags=re.MULTILINE | re.DOTALL)
                if num > 0:
                    temp_lines = mod.splitlines()
                    self.lines = [line for i, line in enumerate(temp_lines)
                             if line.strip() or (i > 0 and temp_lines[i-1].strip())
                             or (i < len(temp_lines) - 1 and temp_lines[i+1].strip())]
                    self.logger.debug(
                        f"Bloco(s) regex '{pattern}' deletado(s) em '{self.full_path}' ({num} ocorrências).")
                    deleted = True
                else:
                    self.logger.warning(
                        f"Padrão regex '{pattern}' não encontrado em '{self.full_path}' para DELETE_BLOCK.")
            except re.error as e:
                self.logger.error(
                    f"Erro de regex em 'block_to_delete': '{pattern}'. Erro: {e}. Tentando como literal.")
                if pattern in file_content:
                    mod = file_content.replace(pattern, "", 1)
                    self.lines = mod.splitlines()
                    self.logger.debug(
                        f"Bloco '{pattern}' (literal fallback) deletado em '{self.full_path}'.")
                    deleted = True
                else:
                    self.logger.warning(
                        f"Bloco '{pattern}' (literal fallback) não encontrado em '{self.full_path}' para DELETE_BLOCK.")
        else:
            if pattern in file_content:
                mod = file_content.replace(pattern, "", 1)
                self.lines = mod.splitlines()
                self.logger.debug(
                    f"Bloco literal '{pattern}' deletado em '{self.full_path}'.")
                deleted = True
            else:
                self.logger.warning(
                    f"Bloco literal '{pattern}' não encontrado em '{self.full_path}' para DELETE_BLOCK.")

        if deleted:
            self.logger.debug(
                f"Bloco removido para '{pattern}' em '{self.full_path}'.")
        elif self.full_path.exists():
            self.logger.warning(
                f"Nenhuma deleção realizada para '{pattern}' em '{self.full_path}'.")

        return True, self.lines, False

def get_handler(operation: str) -> Type[PatchOperationHandler]:
    """Factory function to get the correct handler for an operation."""
    handlers = {
        "INSERT": InsertHandler,
        "REPLACE": ReplaceHandler,
        "DELETE_BLOCK": DeleteBlockHandler,
    }
    handler = handlers.get(operation)
    if not handler:
        raise ValueError(f"Operação desconhecida: {operation}")
    return handler

def apply_patches(instructions: List[Dict[str, Any]], logger: logging.Logger, base_path: str = "."):
    """
    Aplica uma lista de instruções de patch aos arquivos.
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

        lines: List[str] = []
        if full_path.exists():
            with open(full_path, "r", encoding="utf-8") as f:
                lines = f.read().splitlines()
        elif operation not in ["INSERT", "REPLACE"]:
            logger.warning(
                f"Operação '{operation}' em arquivo inexistente '{full_path}'. Pulando.")
            continue
        
        full_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            handler_class = get_handler(operation)
            handler = handler_class(full_path, lines, instruction, logger)
            success, new_lines, skip_write = handler.execute()

            if not success:
                overall_success = False
            
            if not skip_write:
                with open(full_path, "w", encoding="utf-8") as f:
                    f.write("\n".join(new_lines))
                logger.info(
                    f"Arquivo '{full_path}' salvo após operação '{operation}'.")

        except ValueError as e:
            logger.error(f"Erro ao processar patch {i+1}: {e}")
            overall_success = False
            continue
        except Exception as e:
            logger.error(f"Erro inesperado ao processar patch {i+1}: {e}", exc_info=True)
            overall_success = False
            continue

    if overall_success:
        logger.info(
            f"Todas as {len(instructions)} instruções de patch processadas. Arquivos afetados (tentativas): {processed_files}")
    else:
        logger.warning(
            f"Algumas instruções de patch falharam ou foram puladas. Verifique os logs. Arquivos afetados (tentativas): {processed_files}")

    return overall_success
