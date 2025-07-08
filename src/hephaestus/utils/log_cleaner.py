"""
Log Cleaner - Sistema de limpeza automática de logs e backups
"""

import os
import glob
import shutil
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any
import json


class LogCleaner:
    """Sistema de limpeza automática de logs e backups"""
    
    def __init__(self, config: Dict[str, Any], logger: logging.Logger):
        self.config = config
        self.logger = logger.getChild("LogCleaner")
        
        # Configurações de limpeza
        self.backup_retention_days = config.get("log_cleaner", {}).get("backup_retention_days", 7)
        self.log_retention_days = config.get("log_cleaner", {}).get("log_retention_days", 30)
        self.max_backup_files = config.get("log_cleaner", {}).get("max_backup_files", 50)
        self.max_log_size_mb = config.get("log_cleaner", {}).get("max_log_size_mb", 100)
        
        self.logger.info(f"🧹 LogCleaner initialized - Retention: {self.backup_retention_days}d backups, {self.log_retention_days}d logs")
    
    def clean_all(self) -> Dict[str, Any]:
        """Executa limpeza completa de logs e backups"""
        results = {
            "backups_cleaned": 0,
            "logs_cleaned": 0,
            "space_freed_mb": 0.0,
            "errors": []
        }
        
        try:
            # Limpar backups antigos
            backup_results = self._clean_backups()
            results.update(backup_results)
            
            # Limpar logs antigos
            log_results = self._clean_logs()
            results.update(log_results)
            
            # Rotacionar logs grandes
            rotation_results = self._rotate_large_logs()
            results.update(rotation_results)
            
            self.logger.info(f"🧹 Cleanup completed: {results['backups_cleaned']} backups, {results['logs_cleaned']} logs cleaned")
            
        except Exception as e:
            error_msg = f"Cleanup failed: {e}"
            self.logger.error(error_msg)
            results["errors"].append(error_msg)
        
        return results
    
    def _clean_backups(self) -> Dict[str, Any]:
        """Limpa backups antigos e excessivos"""
        results = {
            "backups_cleaned": 0,
            "space_freed_mb": 0.0
        }
        
        backup_dir = Path("data/backups")
        if not backup_dir.exists():
            return results
        
        # Data limite para retenção
        cutoff_date = datetime.now() - timedelta(days=self.backup_retention_days)
        
        # Padrões de backup para limpar
        backup_patterns = [
            "config_backup_*.yaml",
            "architect_config_backup_*.yaml", 
            "bug_hunter_config_backup_*.yaml",
            "maestro_config_backup_*.yaml",
            "architect_prompts_backup_*.txt",
            "maestro_prompts_backup_*.txt",
            "agent_coordination_workflow_backup_*.yaml"
        ]
        
        for pattern in backup_patterns:
            files = list(backup_dir.glob(pattern))
            
            # Ordenar por data de modificação (mais antigos primeiro)
            files.sort(key=lambda x: x.stat().st_mtime)
            
            # Manter apenas os mais recentes
            files_to_keep = files[-self.max_backup_files:] if len(files) > self.max_backup_files else []
            files_to_delete = [f for f in files if f not in files_to_keep]
            
            # Deletar arquivos antigos
            for file_path in files_to_delete:
                try:
                    file_size = file_path.stat().st_size / (1024 * 1024)  # MB
                    file_path.unlink()
                    results["backups_cleaned"] += 1
                    results["space_freed_mb"] += file_size
                    self.logger.debug(f"🗑️ Deleted old backup: {file_path.name}")
                except Exception as e:
                    self.logger.warning(f"Failed to delete backup {file_path}: {e}")
        
        return results
    
    def _clean_logs(self) -> Dict[str, Any]:
        """Limpa logs antigos"""
        results = {
            "logs_cleaned": 0,
            "space_freed_mb": 0.0
        }
        
        log_dir = Path("logs")
        if not log_dir.exists():
            return results
        
        # Data limite para retenção
        cutoff_date = datetime.now() - timedelta(days=self.log_retention_days)
        
        # Padrões de log para limpar
        log_patterns = [
            "*.log.*",  # Logs rotacionados
            "*.log.old",
            "*.log.backup"
        ]
        
        for pattern in log_patterns:
            files = list(log_dir.glob(pattern))
            
            for file_path in files:
                try:
                    # Verificar se o arquivo é mais antigo que o limite
                    file_mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
                    if file_mtime < cutoff_date:
                        file_size = file_path.stat().st_size / (1024 * 1024)  # MB
                        file_path.unlink()
                        results["logs_cleaned"] += 1
                        results["space_freed_mb"] += file_size
                        self.logger.debug(f"🗑️ Deleted old log: {file_path.name}")
                except Exception as e:
                    self.logger.warning(f"Failed to delete log {file_path}: {e}")
        
        return results
    
    def _rotate_large_logs(self) -> Dict[str, Any]:
        """Rotaciona logs que ficaram muito grandes"""
        results = {
            "logs_rotated": 0,
            "space_freed_mb": 0.0
        }
        
        log_dir = Path("logs")
        if not log_dir.exists():
            return results
        
        # Verificar logs principais
        main_logs = [
            "error_prevention.log",
            "evolution_log.csv",
            "app.log"
        ]
        
        for log_name in main_logs:
            log_path = log_dir / log_name
            if not log_path.exists():
                continue
            
            try:
                file_size_mb = log_path.stat().st_size / (1024 * 1024)
                
                if file_size_mb > self.max_log_size_mb:
                    # Criar backup do log atual
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    backup_path = log_path.with_suffix(f".{timestamp}")
                    
                    # Mover arquivo atual para backup
                    shutil.move(str(log_path), str(backup_path))
                    
                    # Criar novo arquivo vazio
                    log_path.touch()
                    
                    results["logs_rotated"] += 1
                    results["space_freed_mb"] += file_size_mb
                    
                    self.logger.info(f"🔄 Rotated large log: {log_name} ({file_size_mb:.1f}MB)")
                    
            except Exception as e:
                self.logger.warning(f"Failed to rotate log {log_name}: {e}")
        
        return results
    
    def get_cleanup_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas de uso de espaço"""
        stats = {
            "backup_count": 0,
            "backup_size_mb": 0.0,
            "log_count": 0,
            "log_size_mb": 0.0,
            "total_size_mb": 0.0
        }
        
        # Estatísticas de backups
        backup_dir = Path("data/backups")
        if backup_dir.exists():
            backup_files = list(backup_dir.rglob("*"))
            stats["backup_count"] = len(backup_files)
            stats["backup_size_mb"] = sum(f.stat().st_size for f in backup_files if f.is_file()) / (1024 * 1024)
        
        # Estatísticas de logs
        log_dir = Path("logs")
        if log_dir.exists():
            log_files = list(log_dir.rglob("*"))
            stats["log_count"] = len(log_files)
            stats["log_size_mb"] = sum(f.stat().st_size for f in log_files if f.is_file()) / (1024 * 1024)
        
        stats["total_size_mb"] = stats["backup_size_mb"] + stats["log_size_mb"]
        
        return stats
    
    def schedule_cleanup(self) -> None:
        """Agenda limpeza automática"""
        # Esta função pode ser chamada periodicamente pelo sistema
        self.logger.info("🧹 Scheduled cleanup started")
        results = self.clean_all()
        
        if results["errors"]:
            self.logger.error(f"Cleanup errors: {results['errors']}")
        else:
            self.logger.info(f"🧹 Scheduled cleanup completed: {results['backups_cleaned']} backups, {results['logs_cleaned']} logs cleaned")


def get_log_cleaner(config: Dict[str, Any], logger: logging.Logger) -> LogCleaner:
    """Factory function para criar LogCleaner"""
    return LogCleaner(config, logger) 