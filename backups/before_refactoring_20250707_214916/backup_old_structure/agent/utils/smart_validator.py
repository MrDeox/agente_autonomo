"""
Sistema de validação inteligente
"""
import json
from typing import Any, Dict, List, Optional, Tuple

class SmartValidator:
    """Validador inteligente para diferentes tipos de dados"""
    
    @staticmethod
    def validate_json(data: str) -> Tuple[bool, Optional[str]]:
        """Validar JSON"""
        try:
            json.loads(data)
            return True, None
        except json.JSONDecodeError as e:
            return False, f"JSON inválido: {e}"
    
    @staticmethod
    def validate_python_code(code: str) -> Tuple[bool, Optional[str]]:
        """Validar código Python"""
        try:
            compile(code, '<string>', 'exec')
            return True, None
        except SyntaxError as e:
            return False, f"Sintaxe Python inválida: {e}"
    
    @staticmethod
    def validate_config(config: Dict[str, Any], required_keys: List[str]) -> Tuple[bool, Optional[str]]:
        """Validar configuração"""
        missing_keys = [key for key in required_keys if key not in config]
        if missing_keys:
            return False, f"Chaves obrigatórias faltando: {missing_keys}"
        return True, None
