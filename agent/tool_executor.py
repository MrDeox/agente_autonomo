import subprocess
from typing import Tuple

def run_pytest(test_dir: str = "tests/") -> Tuple[bool, str]:
    """
    Executa testes pytest no diretório especificado e retorna resultados.
    
    Args:
        test_dir: Diretório contendo os testes (padrão: 'tests/')
    
    Returns:
        Tuple[bool, str]: (success, output) 
        - success: True se todos os testes passarem, False caso contrário
        - output: Saída combinada de stdout e stderr da execução
    """
    try:
        result = subprocess.run(
            ["pytest", test_dir],
            capture_output=True,
            text=True,
            check=False
        )
        success = result.returncode == 0
        output = f"Exit Code: {result.returncode}\n\nStdout:\n{result.stdout}\nStderr:\n{result.stderr}"
        return success, output
    except Exception as e:
        return False, f"Erro ao executar pytest: {str(e)}"
