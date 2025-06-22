import tempfile
import os
import py_compile
import sys
import json

def validate_python_code(code_string: str) -> tuple[bool, str | None]:
    """
    Valida se o código Python é sintaticamente correto usando py_compile.
    Retorna (True, None) se válido, ou (False, mensagem de erro) se inválido.
    """
    try:
        # Cria arquivo temporário em memória
        with tempfile.NamedTemporaryFile(suffix='.py', mode='w', encoding='utf-8', delete=False) as temp:
            temp.write(code_string)
            temp_name = temp.name
        
        # Tenta compilar o código
        py_compile.compile(temp_name, doraise=True)
        return (True, None)
    
    except py_compile.PyCompileError as e:
        # Captura o erro de compilação
        return (False, str(e))
    
    finally:
        # Limpeza: remove o arquivo temporário
        if temp_name and os.path.exists(temp_name):
            try:
                os.unlink(temp_name)
            except OSError:
                pass

def validate_json_syntax(json_string: str) -> tuple[bool, str]:
    """Valida se uma string é um JSON válido.
    
    Args:
        json_string: String contendo JSON a ser validado
        
    Returns:
        Tupla (is_valid, error_message)
    """
    try:
        json.loads(json_string)
        return True, ""
    except json.JSONDecodeError as e:
        return False, str(e)
