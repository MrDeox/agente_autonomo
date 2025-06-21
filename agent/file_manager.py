import shutil
from pathlib import Path
from typing import Dict, List

def apply_changes(files_to_update: List[Dict[str, str]]) -> Dict:
    """
    Aplica as mudanças sugeridas pela IA nos arquivos do projeto, com backup seguro.
    
    Args:
        files_to_update: Lista de dicionários contendo caminho do arquivo e novo conteúdo
        
    Returns:
        Dicionário com relatório detalhado da operação
    """
    report = {
        "status": "success",
        "changes": [],
        "errors": []
    }
    if not files_to_update:
        report["status"] = "failed"
        report["errors"].append("Lista de arquivos vazia.")
        return report

    for item in files_to_update:
        file_path_str = item.get("file_path")
        new_content = item.get("new_content")

        if not file_path_str or new_content is None:
            report["errors"].append("Dados inválidos para atualização de arquivo.")
            report["status"] = "partial" if report["status"] != "failed" else "failed"
            continue

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
            with open(file_path, "w", encoding="utf-8") as f:
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
