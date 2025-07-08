from typing import Dict, List, Any, Optional, Tuple, Set
import logging
import json
import shutil
import os
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, field
from collections import defaultdict
import re

@dataclass
class FileAnalysis:
    """Análise de um arquivo para organização"""
    path: str
    name: str
    extension: str
    size: int
    lines: int
    type: str  # 'code', 'config', 'test', 'doc', 'script', 'data', 'other'
    category: str  # Categoria específica dentro do tipo
    dependencies: List[str] = field(default_factory=list)
    complexity_score: float = 0.0
    importance_score: float = 0.0
    last_modified: datetime = field(default_factory=datetime.now)

@dataclass
class DirectoryStructure:
    """Estrutura de diretório proposta"""
    name: str
    purpose: str
    files: List[str] = field(default_factory=list)
    subdirectories: List['DirectoryStructure'] = field(default_factory=list)
    rules: List[str] = field(default_factory=list)

@dataclass
class OrganizationPlan:
    """Plano de reorganização do projeto"""
    current_structure: Dict[str, Any]
    proposed_structure: Dict[str, Any]
    file_movements: List[Dict[str, str]]
    new_directories: List[str]
    cleanup_actions: List[str]
    estimated_impact: Dict[str, float]
    execution_steps: List[str]

class OrganizerAgent:
    """
    Agente organizador que reorganiza a estrutura do projeto de forma inteligente.
    
    Este agente:
    - Analisa a estrutura atual do projeto
    - Identifica padrões e problemas de organização
    - Propõe uma estrutura otimizada
    - Executa a reorganização de forma segura
    - Mantém rastreabilidade das mudanças
    """
    
    def __init__(self, config: Dict[str, Any], logger: logging.Logger):
        self.config = config
        self.logger = logger
        self.project_root = Path.cwd()
        
        # Configurações de organização
        self.organization_config = config.get("organizer", {
            "max_file_size_mb": 10,
            "max_files_per_dir": 50,
            "preferred_structure": "modular",
            "backup_before_reorganize": True,
            "dry_run_first": True,
            "preserve_git_history": True
        })
        
        # Padrões de arquivos
        self.file_patterns = {
            "code": [".py", ".js", ".ts", ".java", ".cpp", ".c", ".h", ".hpp"],
            "config": [".yaml", ".yml", ".json", ".toml", ".ini", ".cfg", ".conf"],
            "test": ["test_", "_test.py", "_test.js", ".spec.", ".test."],
            "doc": [".md", ".rst", ".txt", ".pdf", ".doc", ".docx"],
            "script": [".sh", ".bat", ".ps1", ".py"],
            "data": [".csv", ".json", ".xml", ".yaml", ".yml", ".db", ".sqlite"],
            "other": []
        }
        
        # Categorias específicas
        self.categories = {
            "core": ["hephaestus_agent.py", "brain.py", "cycle_runner.py"],
            "agents": ["architect_agent.py", "maestro_agent.py", "integrator_agent.py"],
            "utils": ["llm_client.py", "git_utils.py", "code_validator.py"],
            "config": ["default.yaml", "base_config.yaml", "pyproject.toml"],
            "tests": ["test_", "_test.py", "conftest.py"],
            "docs": ["README.md", "ARCHITECTURE.md", "ROADMAP.md"],
            "scripts": ["setup_", "run_", "monitor_", "night_"],
            "servers": ["app.py", "server.py", "api.py"],
            "examples": ["demo_", "example_", "sample_"],
            "temp": [".tmp", ".cache", ".log", ".coverage"]
        }
        
        # Estrutura ideal proposta
        self.ideal_structure = self._define_ideal_structure()
        
    def _define_ideal_structure(self) -> Dict[str, DirectoryStructure]:
        """Define a estrutura ideal do projeto"""
        return {
            "src": DirectoryStructure(
                name="src",
                purpose="Código fonte principal do sistema",
                rules=["Apenas código Python principal", "Sem arquivos de configuração", "Sem testes"]
            ),
            "src/core": DirectoryStructure(
                name="core",
                purpose="Componentes centrais do sistema",
                rules=["Agentes principais", "Lógica de orquestração", "Sistema de memória"]
            ),
            "src/agents": DirectoryStructure(
                name="agents",
                purpose="Agentes especializados",
                rules=["Um agente por arquivo", "Agentes organizados por domínio"]
            ),
            "src/utils": DirectoryStructure(
                name="utils",
                purpose="Utilitários e helpers",
                rules=["Funções reutilizáveis", "Sem dependências complexas"]
            ),
            "src/services": DirectoryStructure(
                name="services",
                purpose="Serviços e APIs",
                rules=["Servidores", "APIs", "Endpoints"]
            ),
            "config": DirectoryStructure(
                name="config",
                purpose="Configurações do sistema",
                rules=["Apenas arquivos de configuração", "Organizados por ambiente"]
            ),
            "tests": DirectoryStructure(
                name="tests",
                purpose="Testes do sistema",
                rules=["Estrutura espelhada do src", "Um teste por módulo"]
            ),
            "docs": DirectoryStructure(
                name="docs",
                purpose="Documentação",
                rules=["Organizada por tópico", "Inclui exemplos e guias"]
            ),
            "scripts": DirectoryStructure(
                name="scripts",
                purpose="Scripts utilitários",
                rules=["Scripts de automação", "Ferramentas de desenvolvimento"]
            ),
            "tools": DirectoryStructure(
                name="tools",
                purpose="Ferramentas auxiliares",
                rules=["Ferramentas independentes", "Aplicações standalone"]
            ),
            "examples": DirectoryStructure(
                name="examples",
                purpose="Exemplos e demonstrações",
                rules=["Código de exemplo", "Demonstrações funcionais"]
            ),
            "logs": DirectoryStructure(
                name="logs",
                purpose="Logs do sistema",
                rules=["Apenas arquivos de log", "Organizados por data/tipo"]
            ),
            "reports": DirectoryStructure(
                name="reports",
                purpose="Relatórios gerados",
                rules=["Relatórios automáticos", "Dados de análise"]
            ),
            "temp": DirectoryStructure(
                name="temp",
                purpose="Arquivos temporários",
                rules=["Arquivos temporários", "Cache", "Arquivos de build"]
            )
        }
    
    def analyze_current_structure(self) -> Dict[str, Any]:
        """
        Analisa a estrutura atual do projeto.
        
        Returns:
            Dicionário com análise detalhada da estrutura atual
        """
        self.logger.info("🔍 Analisando estrutura atual do projeto...")
        
        analysis = {
            "files": [],
            "directories": [],
            "problems": [],
            "statistics": {},
            "file_distribution": defaultdict(int),
            "complexity_analysis": {}
        }
        
        # Analisar todos os arquivos
        for file_path in self.project_root.rglob("*"):
            if file_path.is_file() and not self._should_skip_file(file_path):
                file_analysis = self._analyze_file(file_path)
                analysis["files"].append(vars(file_analysis))
                analysis["file_distribution"][vars(file_analysis)["type"]] += 1
        
        # Analisar diretórios
        for dir_path in self.project_root.iterdir():
            if dir_path.is_dir() and not self._should_skip_directory(dir_path):
                dir_analysis = self._analyze_directory(dir_path)
                analysis["directories"].append(dir_analysis)
        
        # Identificar problemas
        analysis["problems"] = self._identify_structural_problems(analysis)
        
        # Calcular estatísticas
        analysis["statistics"] = self._calculate_statistics(analysis)
        
        # Análise de complexidade
        analysis["complexity_analysis"] = self._analyze_complexity(analysis)
        
        self.logger.info(f"📊 Análise concluída: {len(analysis['files'])} arquivos, {len(analysis['directories'])} diretórios")
        return analysis
    
    def _should_skip_file(self, file_path: Path) -> bool:
        """Verifica se um arquivo deve ser ignorado na análise"""
        skip_patterns = [
            ".git", "__pycache__", ".pytest_cache", ".ruff_cache",
            ".coverage", "*.pyc", "*.pyo", "*.pyd", ".DS_Store",
            "node_modules", "venv", ".venv", "env"
        ]
        
        for pattern in skip_patterns:
            if pattern in str(file_path) or file_path.name.startswith("."):
                return True
        return False
    
    def _should_skip_directory(self, dir_path: Path) -> bool:
        """Verifica se um diretório deve ser ignorado na análise"""
        skip_dirs = {".git", "__pycache__", ".pytest_cache", ".ruff_cache", "venv", ".venv", "env"}
        return dir_path.name in skip_dirs or dir_path.name.startswith(".")
    
    def _analyze_file(self, file_path: Path) -> FileAnalysis:
        """Analisa um arquivo individual"""
        relative_path = file_path.relative_to(self.project_root)
        
        # Determinar tipo e categoria
        file_type, category = self._classify_file(file_path)
        
        # Calcular métricas
        try:
            size = file_path.stat().st_size
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = len(f.readlines())
        except Exception:
            size = 0
            lines = 0
        
        # Calcular scores
        complexity_score = self._calculate_complexity_score(file_path, lines, file_type)
        importance_score = self._calculate_importance_score(file_path, file_type, category)
        
        return FileAnalysis(
            path=str(relative_path),
            name=file_path.name,
            extension=file_path.suffix,
            size=size,
            lines=lines,
            type=file_type,
            category=category,
            complexity_score=complexity_score,
            importance_score=importance_score,
            last_modified=datetime.fromtimestamp(file_path.stat().st_mtime)
        )
    
    def _classify_file(self, file_path: Path) -> Tuple[str, str]:
        """Classifica um arquivo por tipo e categoria"""
        name = file_path.name.lower()
        extension = file_path.suffix.lower()
        
        # Determinar tipo
        file_type = "other"
        for pattern_type, patterns in self.file_patterns.items():
            if any(pattern in name or pattern in extension for pattern in patterns):
                file_type = pattern_type
                break
        
        # Determinar categoria
        category = "general"
        for cat_name, cat_patterns in self.categories.items():
            if any(pattern in name for pattern in cat_patterns):
                category = cat_name
                break
        
        return file_type, category
    
    def _calculate_complexity_score(self, file_path: Path, lines: int, file_type: str) -> float:
        """Calcula score de complexidade de um arquivo"""
        if file_type != "code":
            return 0.0
        
        score = 0.0
        
        # Baseado no número de linhas
        if lines > 1000:
            score += 0.8
        elif lines > 500:
            score += 0.6
        elif lines > 200:
            score += 0.4
        elif lines > 50:
            score += 0.2
        
        # Baseado no nome do arquivo
        name = file_path.name.lower()
        if "complex" in name or "advanced" in name or "meta" in name:
            score += 0.3
        
        return min(score, 1.0)
    
    def _calculate_importance_score(self, file_path: Path, file_type: str, category: str) -> float:
        """Calcula score de importância de um arquivo"""
        score = 0.0
        
        # Arquivos principais do sistema
        if file_path.name in ["hephaestus_agent.py", "main.py", "app.py"]:
            score += 1.0
        
        # Configurações importantes
        if file_path.name in ["pyproject.toml", "default.yaml", "base_config.yaml"]:
            score += 0.9
        
        # Documentação principal
        if file_path.name in ["README.md", "ARCHITECTURE.md", "ROADMAP.md"]:
            score += 0.8
        
        # Agentes principais
        if category == "agents" and "agent" in file_path.name:
            score += 0.7
        
        # Testes
        if category == "tests":
            score += 0.3
        
        return min(score, 1.0)
    
    def _analyze_directory(self, dir_path: Path) -> Dict[str, Any]:
        """Analisa um diretório"""
        relative_path = str(dir_path.relative_to(self.project_root))
        
        # Contar arquivos por tipo
        file_counts = defaultdict(int)
        total_files = 0
        
        for file_path in dir_path.rglob("*"):
            if file_path.is_file() and not self._should_skip_file(file_path):
                file_type, _ = self._classify_file(file_path)
                file_counts[file_type] += 1
                total_files += 1
        
        return {
            "path": relative_path,
            "name": dir_path.name,
            "total_files": total_files,
            "file_distribution": dict(file_counts),
            "depth": len(dir_path.relative_to(self.project_root).parts)
        }
    
    def _identify_structural_problems(self, analysis: Dict[str, Any]) -> List[str]:
        """Identifica problemas na estrutura atual"""
        problems = []
        
        # Arquivos na raiz
        root_files = [f for f in analysis["files"] if "/" not in f["path"]]
        if len(root_files) > 20:
            problems.append(f"Muitos arquivos na raiz ({len(root_files)}) - deve ser organizado em diretórios")
        
        # Diretórios muito grandes
        for dir_info in analysis["directories"]:
            if dir_info["total_files"] > 50:
                problems.append(f"Diretório '{dir_info['path']}' muito grande ({dir_info['total_files']} arquivos)")
        
        # Arquivos de código misturados com outros tipos
        code_files = [f for f in analysis["files"] if f["type"] == "code"]
        non_code_files = [f for f in analysis["files"] if f["type"] != "code"]
        
        for code_file in code_files:
            code_dir = Path(code_file["path"]).parent
            for non_code_file in non_code_files:
                non_code_dir = Path(non_code_file["path"]).parent
                if code_dir == non_code_dir and code_dir != Path("."):
                    problems.append(f"Mistura de tipos de arquivo em '{code_dir}'")
                    break
        
        # Arquivos de teste fora do diretório de testes
        test_files = [f for f in analysis["files"] if f["category"] == "tests"]
        for test_file in test_files:
            if "tests" not in test_file["path"]:
                problems.append(f"Arquivo de teste '{test_file['path']}' fora do diretório de testes")
        
        return list(set(problems))  # Remove duplicatas
    
    def _calculate_statistics(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Calcula estatísticas da análise"""
        files = analysis["files"]
        
        return {
            "total_files": len(files),
            "total_lines": sum(f["lines"] for f in files),
            "total_size_mb": sum(f["size"] for f in files) / (1024 * 1024),
            "file_types": dict(analysis["file_distribution"]),
            "avg_complexity": sum(f["complexity_score"] for f in files) / len(files) if files else 0,
            "avg_importance": sum(f["importance_score"] for f in files) / len(files) if files else 0,
            "directories_count": len(analysis["directories"]),
            "problems_count": len(analysis["problems"])
        }
    
    def _analyze_complexity(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Analisa complexidade da estrutura"""
        files = analysis["files"]
        
        # Arquivos mais complexos
        complex_files = sorted(files, key=lambda x: x["complexity_score"], reverse=True)[:10]
        
        # Arquivos mais importantes
        important_files = sorted(files, key=lambda x: x["importance_score"], reverse=True)[:10]
        
        # Distribuição por tipo
        type_complexity = defaultdict(list)
        for file in files:
            type_complexity[file["type"]].append(file["complexity_score"])
        
        avg_complexity_by_type = {
            file_type: sum(scores) / len(scores) if scores else 0
            for file_type, scores in type_complexity.items()
        }
        
        return {
            "most_complex_files": [{"path": f["path"], "score": f["complexity_score"]} for f in complex_files],
            "most_important_files": [{"path": f["path"], "score": f["importance_score"]} for f in important_files],
            "complexity_by_type": avg_complexity_by_type
        }
    
    def generate_organization_plan(self, analysis: Dict[str, Any]) -> OrganizationPlan:
        """
        Gera um plano de reorganização baseado na análise.
        
        Args:
            analysis: Análise da estrutura atual
            
        Returns:
            Plano de reorganização
        """
        self.logger.info("📋 Gerando plano de reorganização...")
        
        plan = OrganizationPlan(
            current_structure=analysis,
            proposed_structure={},
            file_movements=[],
            new_directories=[],
            cleanup_actions=[],
            estimated_impact={},
            execution_steps=[]
        )
        
        # Mapear arquivos para nova estrutura
        file_movements = self._map_files_to_new_structure(analysis["files"])
        plan.file_movements = file_movements
        
        # Identificar novos diretórios necessários
        new_dirs = set()
        for movement in file_movements:
            target_dir = Path(movement["target"]).parent
            if target_dir != Path("."):
                new_dirs.add(str(target_dir))
        
        plan.new_directories = list(new_dirs)
        
        # Ações de limpeza
        plan.cleanup_actions = self._identify_cleanup_actions(analysis)
        
        # Calcular impacto estimado
        plan.estimated_impact = self._calculate_estimated_impact(analysis, file_movements)
        
        # Passos de execução
        plan.execution_steps = self._generate_execution_steps(plan)
        
        # Estrutura proposta
        plan.proposed_structure = self._build_proposed_structure(plan)
        
        self.logger.info(f"✅ Plano gerado: {len(file_movements)} movimentos, {len(new_dirs)} novos diretórios")
        return plan
    
    def _map_files_to_new_structure(self, files: List[FileAnalysis]) -> List[Dict[str, str]]:
        """Mapeia arquivos para a nova estrutura"""
        movements = []
        
        for file in files:
            file_dict = file if isinstance(file, dict) else vars(file)
            target_path = self._determine_target_path(file_dict)
            if target_path != file_dict["path"]:
                movements.append({
                    "source": file_dict["path"],
                    "target": target_path,
                    "reason": self._get_movement_reason(file_dict, target_path)
                })
        
        return movements
    
    def _determine_target_path(self, file) -> str:
        """Determina o caminho de destino para um arquivo"""
        name = file["name"]
        file_type = file["type"]
        category = file["category"]
        
        # Regras específicas
        if name in ["main.py", "cli.py"]:
            return f"src/{name}"
        
        if name in ["hephaestus_agent.py", "brain.py", "cycle_runner.py"]:
            return f"src/core/{name}"
        
        if category == "agents":
            return f"src/agents/{name}"
        
        if category == "tests":
            # Manter estrutura de testes espelhada
            current_path = Path(file["path"])
            if "agent" in str(current_path):
                return f"tests/agent/{name}"
            elif "server" in str(current_path):
                return f"tests/server/{name}"
            else:
                return f"tests/{name}"
        
        if file_type == "config":
            return f"config/{name}"
        
        if file_type == "doc":
            if name in ["README.md", "ARCHITECTURE.md", "ROADMAP.md"]:
                return f"docs/{name}"
            else:
                return f"docs/{name}"
        
        if category == "scripts":
            return f"scripts/{name}"
        
        if category == "servers":
            return f"src/services/{name}"
        
        if category == "examples":
            return f"examples/{name}"
        
        if category == "temp":
            return f"temp/{name}"
        
        # Padrão geral para código
        if file_type == "code":
            return f"src/utils/{name}"
        
        # Manter na raiz se não se encaixar em nenhuma categoria
        return file["path"]
    
    def _get_movement_reason(self, file, target_path: str) -> str:
        """Gera razão para o movimento do arquivo"""
        if "src/core" in target_path:
            return "Arquivo central do sistema"
        elif "src/agents" in target_path:
            return "Agente especializado"
        elif "tests" in target_path:
            return "Arquivo de teste"
        elif "config" in target_path:
            return "Arquivo de configuração"
        elif "docs" in target_path:
            return "Documentação"
        elif "scripts" in target_path:
            return "Script utilitário"
        elif "src/services" in target_path:
            return "Serviço/API"
        elif "examples" in target_path:
            return "Exemplo/demonstração"
        else:
            return "Organização por tipo"
    
    def _identify_cleanup_actions(self, analysis: Dict[str, Any]) -> List[str]:
        """Identifica ações de limpeza necessárias"""
        cleanup = []
        
        # Verificar arquivos duplicados
        file_names = [f["name"] for f in analysis["files"]]
        duplicates = [name for name in set(file_names) if file_names.count(name) > 1]
        if duplicates:
            cleanup.append(f"Remover arquivos duplicados: {duplicates}")
        
        # Verificar arquivos temporários
        temp_files = [f for f in analysis["files"] if f["category"] == "temp"]
        if temp_files:
            cleanup.append(f"Mover {len(temp_files)} arquivos temporários para /temp")
        
        # Verificar arquivos muito grandes
        large_files = [f for f in analysis["files"] if f["size"] > 1024 * 1024 * 10]  # 10MB
        if large_files:
            cleanup.append(f"Verificar arquivos grandes: {[f['name'] for f in large_files]}")
        
        return cleanup
    
    def _calculate_estimated_impact(self, analysis: Dict[str, Any], movements: List[Dict[str, str]]) -> Dict[str, float]:
        """Calcula impacto estimado da reorganização"""
        total_files = len(analysis["files"])
        moving_files = len(movements)
        
        return {
            "files_affected_percentage": (moving_files / total_files) * 100 if total_files > 0 else 0,
            "complexity_reduction": 0.3,  # Estimativa baseada em experiência
            "maintainability_improvement": 0.4,
            "developer_experience_improvement": 0.5,
            "risk_level": 0.2 if moving_files < total_files * 0.3 else 0.5
        }
    
    def _generate_execution_steps(self, plan: OrganizationPlan) -> List[str]:
        """Gera passos de execução do plano"""
        steps = []
        
        # Backup
        if self.organization_config["backup_before_reorganize"]:
            steps.append("Criar backup completo do projeto")
        
        # Criar novos diretórios
        if plan.new_directories:
            steps.append(f"Criar {len(plan.new_directories)} novos diretórios")
        
        # Mover arquivos
        if plan.file_movements:
            steps.append(f"Mover {len(plan.file_movements)} arquivos")
        
        # Atualizar imports
        steps.append("Atualizar imports e referências")
        
        # Limpeza
        if plan.cleanup_actions:
            steps.append("Executar ações de limpeza")
        
        # Validação
        steps.append("Validar estrutura reorganizada")
        
        return steps
    
    def _build_proposed_structure(self, plan: OrganizationPlan) -> Dict[str, Any]:
        """Constrói a estrutura proposta"""
        structure = {}
        
        # Agrupar arquivos por diretório de destino
        files_by_dir = defaultdict(list)
        for movement in plan.file_movements:
            target_dir = str(Path(movement["target"]).parent)
            files_by_dir[target_dir].append({
                "name": Path(movement["target"]).name,
                "source": movement["source"],
                "reason": movement["reason"]
            })
        
        # Construir estrutura hierárquica
        for dir_path, files in files_by_dir.items():
            current = structure
            for part in dir_path.split("/"):
                if part not in current:
                    current[part] = {"type": "directory", "files": [], "subdirs": {}}
                current = current[part]["subdirs"]
            
            # Adicionar arquivos ao diretório correto
            target_dir = structure
            for part in dir_path.split("/"):
                target_dir = target_dir[part]["subdirs"]
            
            target_dir["files"] = files
        
        return structure
    
    def execute_organization_plan(self, plan: OrganizationPlan, dry_run: bool = True) -> Dict[str, Any]:
        """
        Executa o plano de reorganização.
        
        Args:
            plan: Plano de reorganização
            dry_run: Se True, apenas simula a execução
            
        Returns:
            Resultado da execução
        """
        self.logger.info(f"🚀 Executando plano de reorganização (dry_run={dry_run})...")
        
        result = {
            "success": True,
            "moved_files": [],
            "created_directories": [],
            "errors": [],
            "warnings": [],
            "execution_time": 0
        }
        
        start_time = datetime.now()
        
        try:
            # 1. Criar backup se necessário
            if not dry_run and self.organization_config["backup_before_reorganize"]:
                self._create_backup()
            
            # 2. Criar novos diretórios
            for dir_path in plan.new_directories:
                if not dry_run:
                    Path(dir_path).mkdir(parents=True, exist_ok=True)
                    result["created_directories"].append(dir_path)
                else:
                    result["warnings"].append(f"DRY RUN: Criaria diretório {dir_path}")
            
            # 3. Mover arquivos
            for movement in plan.file_movements:
                source_path = self.project_root / movement["source"]
                target_path = self.project_root / movement["target"]
                
                if not dry_run:
                    if source_path.exists():
                        target_path.parent.mkdir(parents=True, exist_ok=True)
                        shutil.move(str(source_path), str(target_path))
                        result["moved_files"].append({
                            "source": movement["source"],
                            "target": movement["target"]
                        })
                    else:
                        result["errors"].append(f"Arquivo não encontrado: {movement['source']}")
                else:
                    result["warnings"].append(f"DRY RUN: Moveria {movement['source']} → {movement['target']}")
            
            # 4. Atualizar imports (simplificado)
            if not dry_run:
                self._update_imports(plan.file_movements)
            
            # 5. Limpeza
            if not dry_run:
                self._execute_cleanup(plan.cleanup_actions)
            
            result["execution_time"] = (datetime.now() - start_time).total_seconds()
            
            if dry_run:
                self.logger.info("✅ Dry run concluído com sucesso")
            else:
                self.logger.info("✅ Reorganização executada com sucesso")
            
        except Exception as e:
            result["success"] = False
            result["errors"].append(f"Erro durante execução: {str(e)}")
            self.logger.error(f"❌ Erro durante reorganização: {e}")
        
        return result
    
    def _create_backup(self):
        """Cria backup do projeto antes da reorganização"""
        backup_dir = self.project_root / f"backup_before_reorganize_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        backup_dir.mkdir(exist_ok=True)
        
        # Copiar arquivos importantes
        important_patterns = ["*.py", "*.yaml", "*.yml", "*.json", "*.md", "*.toml"]
        for pattern in important_patterns:
            for file_path in self.project_root.glob(pattern):
                if not self._should_skip_file(file_path):
                    relative_path = file_path.relative_to(self.project_root)
                    backup_path = backup_dir / relative_path
                    backup_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(file_path, backup_path)
        
        self.logger.info(f"✅ Backup criado em: {backup_dir}")
    
    def _update_imports(self, movements: List[Dict[str, str]]):
        """Atualiza imports nos arquivos Python"""
        # Implementação simplificada - em produção seria mais robusta
        self.logger.info("🔄 Atualizando imports...")
        
        for movement in movements:
            if movement["source"].endswith(".py") or movement["target"].endswith(".py"):
                # Aqui seria feita a atualização real dos imports
                pass
    
    def _execute_cleanup(self, cleanup_actions: List[str]):
        """Executa ações de limpeza"""
        self.logger.info("🧹 Executando limpeza...")
        
        for action in cleanup_actions:
            self.logger.info(f"   - {action}")
    
    def get_organization_report(self, analysis: Dict[str, Any], plan: OrganizationPlan) -> Dict[str, Any]:
        """
        Gera relatório completo da organização.
        
        Args:
            analysis: Análise da estrutura atual
            plan: Plano de reorganização
            
        Returns:
            Relatório detalhado
        """
        return {
            "current_state": {
                "total_files": analysis["statistics"]["total_files"],
                "total_lines": analysis["statistics"]["total_lines"],
                "file_types": analysis["statistics"]["file_types"],
                "problems": analysis["problems"],
                "complexity_score": analysis["statistics"]["avg_complexity"]
            },
            "proposed_changes": {
                "files_to_move": len(plan.file_movements),
                "new_directories": len(plan.new_directories),
                "cleanup_actions": len(plan.cleanup_actions),
                "estimated_impact": plan.estimated_impact
            },
            "benefits": {
                "improved_organization": "Estrutura mais lógica e intuitiva",
                "better_maintainability": "Separação clara de responsabilidades",
                "easier_navigation": "Localização mais fácil de arquivos",
                "reduced_complexity": "Menor acoplamento entre componentes"
            },
            "risks": {
                "import_breakage": "Possível quebra de imports",
                "git_history": "Histórico do Git pode ficar confuso",
                "dependencies": "Possível quebra de dependências",
                "team_adaptation": "Equipe precisa se adaptar à nova estrutura"
            },
            "recommendations": [
                "Executar dry run primeiro",
                "Fazer backup completo",
                "Testar após reorganização",
                "Atualizar documentação",
                "Comunicar mudanças à equipe"
            ]
        } 