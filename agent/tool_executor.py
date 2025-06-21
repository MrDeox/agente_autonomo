import subprocess
import sys
import time
from typing import Tuple, Dict, Any

import psutil

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

        line = process.stdout.readline()
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
