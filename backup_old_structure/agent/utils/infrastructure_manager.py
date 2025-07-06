"""
Infrastructure Manager - Garantia de Infraestrutura Básica

Este módulo garante que toda a infraestrutura básica necessária esteja presente
e funcionando corretamente antes do sistema iniciar.
"""

import os
import sys
import logging
import shutil
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
import subprocess
import json

class InfrastructureManager:
    """Gerenciador de infraestrutura básica do sistema"""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger(__name__)
        self.project_root = Path.cwd()
        
        # Diretórios essenciais
        self.essential_dirs = [
            "logs",
            "reports",
            "reports/memory",
            "tests",
            "config"
        ]
        
        # Arquivos essenciais
        self.essential_files = {
            "logs/.gitkeep": "",
            "reports/.gitkeep": "",
            "reports/memory/.gitkeep": "",
            ".gitignore": self._get_default_gitignore()
        }
    
    def ensure_infrastructure(self) -> bool:
        """Garante que toda a infraestrutura necessária esteja presente"""
        self.logger.info("🏗️ Verificando infraestrutura básica...")
        
        success = True
        
        # 1. Criar diretórios essenciais
        success &= self._ensure_directories()
        
        # 2. Criar arquivos essenciais
        success &= self._ensure_files()
        
        # 3. Verificar dependências
        success &= self._check_dependencies()
        
        # 4. Verificar configurações
        success &= self._validate_configurations()
        
        if success:
            self.logger.info("✅ Infraestrutura verificada com sucesso")
        else:
            self.logger.error("❌ Problemas encontrados na infraestrutura")
        
        return success
    
    def _ensure_directories(self) -> bool:
        """Garante que todos os diretórios essenciais existam"""
        self.logger.info("📁 Criando diretórios essenciais...")
        
        try:
            for dir_path in self.essential_dirs:
                full_path = self.project_root / dir_path
                if not full_path.exists():
                    full_path.mkdir(parents=True, exist_ok=True)
                    self.logger.info(f"   ✅ Criado: {dir_path}")
                else:
                    self.logger.debug(f"   ✓ Existente: {dir_path}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao criar diretórios: {e}")
            return False
    
    def _ensure_files(self) -> bool:
        """Garante que todos os arquivos essenciais existam"""
        self.logger.info("📄 Criando arquivos essenciais...")
        
        try:
            for file_path, content in self.essential_files.items():
                full_path = self.project_root / file_path
                if not full_path.exists():
                    full_path.parent.mkdir(parents=True, exist_ok=True)
                    with open(full_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    self.logger.info(f"   ✅ Criado: {file_path}")
                else:
                    self.logger.debug(f"   ✓ Existente: {file_path}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao criar arquivos: {e}")
            return False
    
    def _check_dependencies(self) -> bool:
        """Verifica e corrige problemas de dependências"""
        self.logger.info("📦 Verificando dependências...")
        
        try:
            # Verificar se temos pyproject.toml E requirements.txt
            has_pyproject = (self.project_root / "pyproject.toml").exists()
            has_requirements = (self.project_root / "requirements.txt").exists()
            
            if has_pyproject and has_requirements:
                self.logger.warning("⚠️ Dependências duplicadas detectadas:")
                self.logger.warning("   • pyproject.toml (Poetry)")
                self.logger.warning("   • requirements.txt (pip)")
                
                # Sugerir ação
                self.logger.info("💡 Recomendação: Use apenas Poetry (pyproject.toml)")
                self.logger.info("   Para gerar requirements.txt do Poetry:")
                self.logger.info("   poetry export -f requirements.txt --output requirements.txt")
                
                return True  # Não é erro fatal, apenas aviso
            
            elif has_pyproject:
                self.logger.info("✅ Usando Poetry (pyproject.toml)")
                return True
            
            elif has_requirements:
                self.logger.info("✅ Usando pip (requirements.txt)")
                return True
            
            else:
                self.logger.error("❌ Nenhum arquivo de dependências encontrado!")
                return False
            
        except Exception as e:
            self.logger.error(f"Erro ao verificar dependências: {e}")
            return False
    
    def _validate_configurations(self) -> bool:
        """Valida configurações críticas"""
        self.logger.info("⚙️ Validando configurações...")
        
        try:
            # Verificar hephaestus_config.json
            config_path = self.project_root / "hephaestus_config.json"
            if config_path.exists():
                try:
                    with open(config_path, 'r', encoding='utf-8') as f:
                        config = json.load(f)
                    self.logger.info("   ✅ hephaestus_config.json válido")
                    
                    # Verificar se tem estratégias
                    strategies = config.get("validation_strategies", {})
                    if strategies:
                        self.logger.info(f"   ✅ {len(strategies)} estratégias carregadas")
                    else:
                        self.logger.warning("   ⚠️ Nenhuma estratégia encontrada")
                    
                except json.JSONDecodeError as e:
                    self.logger.error(f"   ❌ JSON inválido: {e}")
                    return False
            else:
                self.logger.warning("   ⚠️ hephaestus_config.json não encontrado")
            
            # Verificar configurações Hydra
            hydra_config = self.project_root / "config" / "default.yaml"
            if hydra_config.exists():
                self.logger.info("   ✅ Configuração Hydra encontrada")
            else:
                self.logger.warning("   ⚠️ Configuração Hydra não encontrada")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao validar configurações: {e}")
            return False
    
    def _get_default_gitignore(self) -> str:
        """Retorna conteúdo padrão do .gitignore"""
        return """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# PyInstaller
*.manifest
*.spec

# Installer logs
pip-log.txt
pip-delete-this-directory.txt

# Unit test / coverage reports
htmlcov/
.tox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
.hypothesis/
.pytest_cache/

# Virtual environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Project specific
logs/*.log
logs/*.csv
reports/
*.tmp
.hydra/
outputs/

# API Keys (security)
.env.local
.env.*.local
config/local/
secrets/
"""
    
    def diagnose_system(self) -> Dict[str, Any]:
        """Faz diagnóstico completo do sistema"""
        self.logger.info("🔍 Executando diagnóstico completo...")
        
        diagnosis = {
            "directories": {},
            "files": {},
            "dependencies": {},
            "configurations": {},
            "issues": [],
            "recommendations": []
        }
        
        # Verificar diretórios
        for dir_path in self.essential_dirs:
            full_path = self.project_root / dir_path
            diagnosis["directories"][dir_path] = {
                "exists": full_path.exists(),
                "writable": full_path.exists() and os.access(full_path, os.W_OK)
            }
            
            if not full_path.exists():
                diagnosis["issues"].append(f"Diretório ausente: {dir_path}")
                diagnosis["recommendations"].append(f"Criar diretório: {dir_path}")
        
        # Verificar arquivos
        for file_path in self.essential_files:
            full_path = self.project_root / file_path
            diagnosis["files"][file_path] = {
                "exists": full_path.exists(),
                "readable": full_path.exists() and os.access(full_path, os.R_OK)
            }
        
        # Verificar dependências
        has_pyproject = (self.project_root / "pyproject.toml").exists()
        has_requirements = (self.project_root / "requirements.txt").exists()
        
        diagnosis["dependencies"] = {
            "pyproject_toml": has_pyproject,
            "requirements_txt": has_requirements,
            "duplicated": has_pyproject and has_requirements
        }
        
        if has_pyproject and has_requirements:
            diagnosis["issues"].append("Dependências duplicadas (pyproject.toml + requirements.txt)")
            diagnosis["recommendations"].append("Usar apenas Poetry ou sincronizar arquivos")
        
        # Verificar configurações
        config_files = [
            "hephaestus_config.json",
            "config/default.yaml",
            "config/base_config.yaml"
        ]
        
        for config_file in config_files:
            full_path = self.project_root / config_file
            is_valid = True
            
            if full_path.exists():
                try:
                    if config_file.endswith('.json'):
                        with open(full_path, 'r') as f:
                            json.load(f)
                    # YAML validation would require PyYAML
                except:
                    is_valid = False
            
            diagnosis["configurations"][config_file] = {
                "exists": full_path.exists(),
                "valid": is_valid
            }
        
        return diagnosis
    
    def fix_infrastructure_issues(self, diagnosis: Optional[Dict] = None) -> bool:
        """Corrige problemas de infraestrutura identificados"""
        if not diagnosis:
            diagnosis = self.diagnose_system()
        
        self.logger.info("🔧 Corrigindo problemas de infraestrutura...")
        
        fixed_issues = 0
        total_issues = len(diagnosis.get("issues", []))
        
        try:
            # Corrigir diretórios ausentes
            for dir_path, info in diagnosis["directories"].items():
                if not info["exists"]:
                    full_path = self.project_root / dir_path
                    full_path.mkdir(parents=True, exist_ok=True)
                    self.logger.info(f"   ✅ Corrigido: Criado diretório {dir_path}")
                    fixed_issues += 1
            
            # Corrigir arquivos ausentes
            for file_path, info in diagnosis["files"].items():
                if not info["exists"]:
                    full_path = self.project_root / file_path
                    full_path.parent.mkdir(parents=True, exist_ok=True)
                    content = self.essential_files.get(file_path, "")
                    with open(full_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    self.logger.info(f"   ✅ Corrigido: Criado arquivo {file_path}")
                    fixed_issues += 1
            
            self.logger.info(f"🎯 Corrigidos {fixed_issues}/{total_issues} problemas")
            return fixed_issues == total_issues
            
        except Exception as e:
            self.logger.error(f"Erro ao corrigir infraestrutura: {e}")
            return False
    
    def get_system_status(self) -> Dict[str, Any]:
        """Retorna status detalhado do sistema"""
        diagnosis = self.diagnose_system()
        
        total_dirs = len(diagnosis["directories"])
        healthy_dirs = sum(1 for info in diagnosis["directories"].values() if info["exists"])
        
        total_files = len(diagnosis["files"])
        healthy_files = sum(1 for info in diagnosis["files"].values() if info["exists"])
        
        total_configs = len(diagnosis["configurations"])
        healthy_configs = sum(1 for info in diagnosis["configurations"].values() if info["exists"] and info["valid"])
        
        return {
            "overall_health": "healthy" if len(diagnosis["issues"]) == 0 else "issues_detected",
            "directories": f"{healthy_dirs}/{total_dirs}",
            "files": f"{healthy_files}/{total_files}",
            "configurations": f"{healthy_configs}/{total_configs}",
            "total_issues": len(diagnosis["issues"]),
            "diagnosis": diagnosis
        }


def ensure_basic_infrastructure(logger: Optional[logging.Logger] = None) -> bool:
    """Função utilitária para garantir infraestrutura básica"""
    manager = InfrastructureManager(logger)
    return manager.ensure_infrastructure()


def diagnose_and_fix_infrastructure(logger: Optional[logging.Logger] = None) -> bool:
    """Função utilitária para diagnosticar e corrigir infraestrutura"""
    manager = InfrastructureManager(logger)
    diagnosis = manager.diagnose_system()
    
    if diagnosis["issues"]:
        return manager.fix_infrastructure_issues(diagnosis)
    else:
        if logger:
            logger.info("✅ Nenhum problema de infraestrutura encontrado")
        return True


# Função para integração com outros módulos
def get_infrastructure_manager(logger: Optional[logging.Logger] = None) -> InfrastructureManager:
    """Retorna instância do gerenciador de infraestrutura"""
    return InfrastructureManager(logger) 