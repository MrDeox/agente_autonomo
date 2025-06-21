import re
import shutil
from pathlib import Path
from typing import Dict, List

def apply_changes(ai_response: str) -> Dict:
    """
    Aplica as mudanças sugeridas pela IA nos arquivos do projeto, com backup seguro.
    
    Args:
        ai_response: String com a resposta formatada da IA contendo as mudanças
        
    Returns:
        Dicionário com relatório detalhado da operação
    """
    pattern = re.compile(
        r'--- INÍCIO DO ARQUIVO: (.*?) ---\s*```+python\n(.*?)\n```+',
        re.DOTALL
    )
    
    report = {
        "status": "success",
        "changes": [],
        "errors": []
    }
    
    matches = pattern.findall(ai_response)
    if not matches:
        report["status"] = "failed"
        report["errors"].append("Nenhuma mudança detectada na resposta da IA.")
        return report
    
    for file_path_str, new_content in matches:
        file_path = Path(file_path_str)
        
        if not file_path.exists():
            report["errors"].append(f"Arquivo não encontrado: {file_path_str}")
            report["status"] = "partial" if report["status"] != "failed" else "failed"
            continue
            
        backup_path = file_path.with_suffix(file_path.suffix + ".bak")
        
        try:
            # Cria backup
            shutil.copyfile(file_path, backup_path)
        except Exception as e:
            report["errors"].append(f"Falha ao criar backup para {file_path_str}: {str(e)}")
            report["status"] = "failed"
            continue
            
        try:
            # Aplica mudanças
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
                
            report["changes"].append({
                "file": str(file_path),
                "status": "applied",
                "backup": str(backup_path)
            })
        except Exception as e:
            report["errors"].append(f"Falha ao escrever no arquivo {file_path_str}: {str(e)}")
            report["status"] = "partial"
            
    return report
