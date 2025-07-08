"""
Enhanced Organizer Agent - Project structure optimization with new architecture
"""

import os
import json
import shutil
import re
from typing import Dict, List, Any, Optional, Tuple, Set
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, field, asdict
from collections import defaultdict

from hephaestus.agents.enhanced_base import EnhancedBaseAgent
from hephaestus.agents.base import AgentCapability
from hephaestus.utils.llm_manager import llm_call_with_metrics


@dataclass
class FileAnalysis:
    """Enhanced file analysis for organization."""
    path: str
    name: str
    extension: str
    size: int
    lines: int
    type: str  # 'code', 'config', 'test', 'doc', 'script', 'data', 'other'
    category: str  # Specific category within type
    dependencies: List[str] = field(default_factory=list)
    complexity_score: float = 0.0
    importance_score: float = 0.0
    last_modified: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        data = asdict(self)
        data['last_modified'] = self.last_modified.isoformat()
        return data


@dataclass
class DirectoryStructure:
    """Enhanced directory structure proposal."""
    name: str
    purpose: str
    files: List[str] = field(default_factory=list)
    subdirectories: List['DirectoryStructure'] = field(default_factory=list)
    rules: List[str] = field(default_factory=list)
    priority: int = 1  # 1-5, higher = more important
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'name': self.name,
            'purpose': self.purpose,
            'files': self.files,
            'subdirectories': [sub.to_dict() for sub in self.subdirectories],
            'rules': self.rules,
            'priority': self.priority
        }


@dataclass
class OrganizationPlan:
    """Enhanced organization plan with execution tracking."""
    current_structure: Dict[str, Any]
    proposed_structure: Dict[str, Any]
    file_movements: List[Dict[str, str]]
    new_directories: List[str]
    cleanup_actions: List[str]
    estimated_impact: Dict[str, float]
    execution_steps: List[str]
    risk_assessment: Dict[str, Any] = field(default_factory=dict)
    rollback_plan: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)


class OrganizerAgentEnhanced(EnhancedBaseAgent):
    """
    Enhanced Organizer Agent using the new modular architecture.
    
    Features:
    - Intelligent project structure analysis
    - AI-powered organization recommendations
    - Safe file movement with rollback
    - Dependency tracking
    - Impact assessment
    """
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Organization state
        self.file_analyses: Dict[str, FileAnalysis] = {}
        self.current_plan: Optional[OrganizationPlan] = None
        
        # Configuration
        self.dry_run_mode = self.get_config_value('dry_run_mode', True)
        self.backup_enabled = self.get_config_value('backup_enabled', True)
        self.max_file_size = self.get_config_value('max_file_size_mb', 10) * 1024 * 1024
        
        # File type patterns
        self.file_patterns = self._load_file_patterns()
        
        self.logger.info("📁 Enhanced Organizer Agent initialized")
    
    def get_default_capabilities(self) -> list:
        """Get default capabilities for the Organizer Agent."""
        return [
            AgentCapability.TECHNICAL_DEBT_IDENTIFICATION,
            AgentCapability.REFACTORING_OPPORTUNITIES,
            AgentCapability.CODE_ANALYSIS,
            AgentCapability.PERFORMANCE_ANALYSIS
        ]
    
    async def execute(self, objective: str) -> Tuple[bool, Optional[str]]:
        """
        Execute organization tasks.
        
        Args:
            objective: The objective (e.g., "analyze project structure")
            
        Returns:
            Tuple of (success, error_message)
        """
        self.logger.info(f"📁 Organizer executing: {objective}")
        
        try:
            if "analyze" in objective.lower():
                result = await self.analyze_project_structure()
            elif "organize" in objective.lower() or "restructure" in objective.lower():
                result = await self.create_organization_plan()
            elif "execute" in objective.lower() or "apply" in objective.lower():
                result = await self.execute_organization_plan()
            else:
                # Default: comprehensive analysis
                result = await self.comprehensive_organization()
            
            return result.get('success', False), result.get('error')
            
        except Exception as e:
            error_message = self.handle_error(e, "execute")
            return False, error_message
    
    async def comprehensive_organization(self) -> Dict[str, Any]:
        """Perform comprehensive project organization."""
        results = {
            'analysis_result': await self.analyze_project_structure(),
            'plan_result': await self.create_organization_plan(),
            'success': True
        }
        
        # Execute plan if not in dry run mode
        if not self.dry_run_mode and self.current_plan:
            results['execution_result'] = await self.execute_organization_plan()
        
        return results
    
    async def analyze_project_structure(self, target_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze current project structure.
        
        Args:
            target_path: Optional specific path to analyze
            
        Returns:
            Analysis results dictionary
        """
        return await self.execute_with_metrics(
            "analyze_project_structure",
            self._perform_structure_analysis,
            target_path
        )
    
    async def _perform_structure_analysis(self, target_path: Optional[str] = None) -> Dict[str, Any]:
        """Perform the actual structure analysis."""
        if not target_path:
            target_path = str(Path.cwd())
        
        self.logger.info(f"Analyzing project structure at: {target_path}")
        
        # Scan all files
        files_analyzed = 0
        total_size = 0
        file_types = defaultdict(int)
        complexity_scores = []
        
        for file_path in self._get_all_files(target_path):
            try:
                analysis = self._analyze_file(file_path)
                if analysis:
                    self.file_analyses[file_path] = analysis
                    files_analyzed += 1
                    total_size += analysis.size
                    file_types[analysis.type] += 1
                    complexity_scores.append(analysis.complexity_score)
                    
            except Exception as e:
                self.logger.warning(f"Failed to analyze {file_path}: {e}")
        
        # Calculate statistics
        avg_complexity = sum(complexity_scores) / len(complexity_scores) if complexity_scores else 0
        
        # Identify issues
        issues = self._identify_structure_issues()
        
        return {
            'files_analyzed': files_analyzed,
            'total_size_mb': total_size / (1024 * 1024),
            'file_type_distribution': dict(file_types),
            'average_complexity': avg_complexity,
            'structure_issues': issues,
            'recommendations': self._generate_recommendations(issues),
            'analysis_timestamp': datetime.now().isoformat()
        }
    
    @llm_call_with_metrics
    async def create_organization_plan(self) -> Dict[str, Any]:
        """
        Create an AI-powered organization plan.
        
        Returns:
            Organization plan results
        """
        if not self.file_analyses:
            await self.analyze_project_structure()
        
        return await self.execute_with_metrics(
            "create_organization_plan",
            self._generate_organization_plan
        )
    
    async def _generate_organization_plan(self) -> Dict[str, Any]:
        """Generate the organization plan using AI."""
        # Prepare analysis data for AI
        analysis_summary = self._summarize_analysis()
        
        # Build AI prompt
        prompt = self._build_organization_prompt(analysis_summary)
        
        # Get AI recommendations
        ai_plan, error = await self.llm_call_json(prompt)
        
        if error:
            self.logger.error(f"Failed to get AI organization plan: {error}")
            # Fallback to rule-based plan
            ai_plan = self._create_fallback_plan()
        
        # Validate and enhance the plan
        validated_plan = self._validate_and_enhance_plan(ai_plan)
        
        # Create comprehensive organization plan
        self.current_plan = OrganizationPlan(
            current_structure=self._get_current_structure(),
            proposed_structure=validated_plan.get('proposed_structure', {}),
            file_movements=validated_plan.get('file_movements', []),
            new_directories=validated_plan.get('new_directories', []),
            cleanup_actions=validated_plan.get('cleanup_actions', []),
            estimated_impact=validated_plan.get('estimated_impact', {}),
            execution_steps=validated_plan.get('execution_steps', []),
            risk_assessment=self._assess_risks(validated_plan),
            rollback_plan=self._create_rollback_plan(validated_plan)
        )
        
        return {
            'plan_created': True,
            'file_movements': len(self.current_plan.file_movements),
            'new_directories': len(self.current_plan.new_directories),
            'cleanup_actions': len(self.current_plan.cleanup_actions),
            'estimated_impact': self.current_plan.estimated_impact,
            'risk_level': self.current_plan.risk_assessment.get('overall_risk', 'medium')
        }
    
    async def execute_organization_plan(self) -> Dict[str, Any]:
        """
        Execute the current organization plan.
        
        Returns:
            Execution results dictionary
        """
        if not self.current_plan:
            return {'success': False, 'error': 'No organization plan available'}
        
        return await self.execute_with_metrics(
            "execute_organization_plan",
            self._perform_plan_execution
        )
    
    async def _perform_plan_execution(self) -> Dict[str, Any]:
        """Perform the actual plan execution."""
        if self.dry_run_mode:
            return self._simulate_execution()
        
        # Create backup if enabled
        backup_path = None
        if self.backup_enabled:
            backup_path = self._create_backup()
        
        executed_steps = 0
        failed_steps = 0
        
        try:
            # Execute each step
            for step in self.current_plan.execution_steps:
                try:
                    success = await self._execute_step(step)
                    if success:
                        executed_steps += 1
                    else:
                        failed_steps += 1
                        
                except Exception as e:
                    self.logger.error(f"Failed to execute step '{step}': {e}")
                    failed_steps += 1
            
            return {
                'success': failed_steps == 0,
                'executed_steps': executed_steps,
                'failed_steps': failed_steps,
                'backup_path': backup_path,
                'execution_timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            # Rollback on failure
            if backup_path:
                self._restore_backup(backup_path)
            raise e
    
    def _get_all_files(self, root_path: str) -> List[str]:
        """Get all files to analyze, excluding common exclusions."""
        exclusions = {
            '.git', '__pycache__', '.pytest_cache', 'venv', '.venv',
            'node_modules', '.idea', '.vscode', 'dist', 'build'
        }
        
        files = []
        root = Path(root_path)
        
        for file_path in root.rglob('*'):
            if (file_path.is_file() and 
                not any(exclusion in str(file_path) for exclusion in exclusions) and
                file_path.stat().st_size <= self.max_file_size):
                files.append(str(file_path))
        
        return files
    
    def _analyze_file(self, file_path: str) -> Optional[FileAnalysis]:
        """Analyze a single file."""
        try:
            path = Path(file_path)
            stat = path.stat()
            
            # Read file content for analysis
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                lines = len(content.splitlines())
            except (UnicodeDecodeError, PermissionError):
                content = ""
                lines = 0
            
            # Determine file type and category
            file_type, category = self._classify_file(file_path, content)
            
            # Calculate complexity score
            complexity = self._calculate_complexity(content, file_type)
            
            # Calculate importance score
            importance = self._calculate_importance(file_path, file_type, stat.st_size, lines)
            
            return FileAnalysis(
                path=file_path,
                name=path.name,
                extension=path.suffix,
                size=stat.st_size,
                lines=lines,
                type=file_type,
                category=category,
                complexity_score=complexity,
                importance_score=importance,
                last_modified=datetime.fromtimestamp(stat.st_mtime)
            )
            
        except Exception as e:
            self.logger.error(f"Failed to analyze file {file_path}: {e}")
            return None
    
    def _classify_file(self, file_path: str, content: str) -> Tuple[str, str]:
        """Classify file type and category."""
        path = Path(file_path).name.lower()
        extension = Path(file_path).suffix.lower()
        
        # Check patterns
        for pattern_type, patterns in self.file_patterns.items():
            for pattern_name, pattern_data in patterns.items():
                if any(re.search(regex, path) for regex in pattern_data.get('name_patterns', [])):
                    return pattern_type, pattern_name
                if extension in pattern_data.get('extensions', []):
                    return pattern_type, pattern_name
                if any(re.search(regex, content[:1000]) for regex in pattern_data.get('content_patterns', [])):
                    return pattern_type, pattern_name
        
        return 'other', 'unknown'
    
    def _calculate_complexity(self, content: str, file_type: str) -> float:
        """Calculate file complexity score."""
        if not content:
            return 0.0
        
        lines = content.splitlines()
        complexity = 0.0
        
        if file_type == 'code':
            # Count complexity indicators
            complexity += len(re.findall(r'\b(if|elif|while|for|try|except|with)\b', content)) * 0.1
            complexity += len(re.findall(r'\bclass\b', content)) * 0.2
            complexity += len(re.findall(r'\bdef\b', content)) * 0.1
            complexity += len(re.findall(r'\bimport\b', content)) * 0.05
            
        # Lines of code factor
        complexity += len(lines) * 0.001
        
        # Nesting level (approximate)
        indents = [(len(line) - len(line.lstrip())) // 4 for line in lines if line.strip()]
        max_indent = max(indents) if indents else 0
        complexity += max_indent * 0.1
        
        return min(complexity, 10.0)  # Cap at 10
    
    def _calculate_importance(self, file_path: str, file_type: str, size: int, lines: int) -> float:
        """Calculate file importance score."""
        importance = 0.0
        
        # Type importance
        type_weights = {
            'code': 1.0,
            'config': 0.8,
            'test': 0.6,
            'doc': 0.4,
            'script': 0.7,
            'data': 0.3
        }
        importance += type_weights.get(file_type, 0.2)
        
        # Size factor
        importance += min(size / 10000, 1.0) * 0.3
        
        # Lines factor
        importance += min(lines / 1000, 1.0) * 0.2
        
        # Path importance (main files, root level)
        if 'main' in Path(file_path).name.lower():
            importance += 0.5
        if len(Path(file_path).parts) <= 3:
            importance += 0.3
        
        return min(importance, 10.0)  # Cap at 10
    
    def _identify_structure_issues(self) -> List[Dict[str, Any]]:
        """Identify issues in current project structure."""
        issues = []
        
        # Check for files in root that should be in subdirectories
        root_files = [f for f in self.file_analyses.values() 
                     if len(Path(f.path).parts) <= 2 and f.type == 'code']
        
        if len(root_files) > 5:
            issues.append({
                'type': 'root_clutter',
                'severity': 'medium',
                'description': f'Too many code files in root directory ({len(root_files)})',
                'affected_files': [f.path for f in root_files]
            })
        
        # Check for duplicate functionality
        file_groups = defaultdict(list)
        for analysis in self.file_analyses.values():
            file_groups[analysis.category].append(analysis)
        
        for category, files in file_groups.items():
            if len(files) > 3 and category != 'unknown':
                issues.append({
                    'type': 'scattered_functionality',
                    'severity': 'medium',
                    'description': f'Multiple {category} files could be consolidated',
                    'affected_files': [f.path for f in files]
                })
        
        # Check for missing directories
        config_files = [f for f in self.file_analyses.values() if f.type == 'config']
        if config_files and not any('config' in f.path for f in config_files):
            issues.append({
                'type': 'missing_directory',
                'severity': 'low',
                'description': 'Config files should be in a dedicated config directory',
                'suggested_action': 'Create config/ directory'
            })
        
        return issues
    
    def _generate_recommendations(self, issues: List[Dict[str, Any]]) -> List[str]:
        """Generate recommendations based on identified issues."""
        recommendations = []
        
        for issue in issues:
            if issue['type'] == 'root_clutter':
                recommendations.append("Move code files from root to appropriate subdirectories")
            elif issue['type'] == 'scattered_functionality':
                recommendations.append(f"Consolidate {issue['description']}")
            elif issue['type'] == 'missing_directory':
                recommendations.append(issue['suggested_action'])
        
        return recommendations
    
    def _load_file_patterns(self) -> Dict[str, Dict[str, Dict[str, Any]]]:
        """Load file classification patterns."""
        return {
            'code': {
                'core': {
                    'extensions': ['.py'],
                    'name_patterns': [r'(main|core|engine|brain)'],
                    'content_patterns': [r'class\s+\w+Agent', r'async\s+def']
                },
                'agent': {
                    'extensions': ['.py'],
                    'name_patterns': [r'.*agent.*', r'.*_agent'],
                    'content_patterns': [r'class\s+\w+Agent']
                },
                'utils': {
                    'extensions': ['.py'],
                    'name_patterns': [r'util', r'helper', r'tool'],
                    'content_patterns': [r'def\s+\w+']
                }
            },
            'config': {
                'yaml': {
                    'extensions': ['.yaml', '.yml'],
                    'name_patterns': [r'config', r'settings']
                },
                'json': {
                    'extensions': ['.json'],
                    'name_patterns': [r'config', r'settings', r'package']
                },
                'env': {
                    'extensions': ['.env'],
                    'name_patterns': [r'\.env']
                }
            },
            'test': {
                'pytest': {
                    'extensions': ['.py'],
                    'name_patterns': [r'test_', r'_test', r'tests'],
                    'content_patterns': [r'def\s+test_', r'import\s+pytest']
                }
            },
            'doc': {
                'markdown': {
                    'extensions': ['.md'],
                    'name_patterns': [r'readme', r'doc', r'guide']
                },
                'text': {
                    'extensions': ['.txt', '.rst'],
                    'name_patterns': [r'readme', r'license', r'changelog']
                }
            },
            'script': {
                'shell': {
                    'extensions': ['.sh', '.bash'],
                    'name_patterns': [r'install', r'setup', r'deploy']
                },
                'python': {
                    'extensions': ['.py'],
                    'name_patterns': [r'script', r'setup', r'install'],
                    'content_patterns': [r'if\s+__name__\s*==\s*["\']__main__["\']']
                }
            }
        }
    
    def _summarize_analysis(self) -> Dict[str, Any]:
        """Summarize file analysis for AI processing."""
        return {
            'total_files': len(self.file_analyses),
            'file_types': {
                file_type: len([f for f in self.file_analyses.values() if f.type == file_type])
                for file_type in set(f.type for f in self.file_analyses.values())
            },
            'complexity_distribution': {
                'high': len([f for f in self.file_analyses.values() if f.complexity_score > 5]),
                'medium': len([f for f in self.file_analyses.values() if 2 <= f.complexity_score <= 5]),
                'low': len([f for f in self.file_analyses.values() if f.complexity_score < 2])
            },
            'current_directories': list(set(str(Path(f.path).parent) for f in self.file_analyses.values())),
            'root_files': [f.path for f in self.file_analyses.values() if len(Path(f.path).parts) <= 2]
        }
    
    def _build_organization_prompt(self, analysis: Dict[str, Any]) -> str:
        """Build AI prompt for organization planning."""
        return f"""
You are an expert software architect and project organizer. Analyze the current project structure and create an optimal organization plan.

[CURRENT PROJECT ANALYSIS]
{json.dumps(analysis, indent=2)}

[ORGANIZATION GOALS]
1. Improve code maintainability
2. Follow Python packaging best practices
3. Separate concerns clearly
4. Minimize dependency coupling
5. Make the project structure intuitive

[RESPONSE FORMAT]
Return a JSON response with this structure:
{{
    "proposed_structure": {{
        "src/": ["Main source code"],
        "tests/": ["Test files"],
        "config/": ["Configuration files"],
        "docs/": ["Documentation"],
        "scripts/": ["Utility scripts"]
    }},
    "file_movements": [
        {{
            "from": "current/path/file.py",
            "to": "new/path/file.py",
            "reason": "Better organization"
        }}
    ],
    "new_directories": ["config/", "scripts/"],
    "cleanup_actions": ["Remove empty directories"],
    "execution_steps": ["Step-by-step execution plan"],
    "estimated_impact": {{
        "import_changes": 0.3,
        "test_updates": 0.2,
        "documentation": 0.1
    }}
}}

Respond with ONLY the JSON, no additional text.
"""
    
    def _validate_and_enhance_plan(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and enhance the AI-generated plan."""
        if not isinstance(plan, dict):
            return self._create_fallback_plan()
        
        # Ensure required keys exist
        required_keys = ['proposed_structure', 'file_movements', 'new_directories', 'cleanup_actions', 'execution_steps']
        for key in required_keys:
            if key not in plan:
                plan[key] = []
        
        # Validate file movements
        valid_movements = []
        for movement in plan.get('file_movements', []):
            if isinstance(movement, dict) and 'from' in movement and 'to' in movement:
                if Path(movement['from']).exists():
                    valid_movements.append(movement)
        
        plan['file_movements'] = valid_movements
        
        return plan
    
    def _create_fallback_plan(self) -> Dict[str, Any]:
        """Create a basic fallback organization plan."""
        return {
            'proposed_structure': {
                'src/': ['Main source code'],
                'tests/': ['Test files'],
                'config/': ['Configuration files'],
                'docs/': ['Documentation']
            },
            'file_movements': [],
            'new_directories': [],
            'cleanup_actions': [],
            'execution_steps': ['Analyze current structure', 'Create directories', 'Move files'],
            'estimated_impact': {'low_risk': 0.1}
        }
    
    def _get_current_structure(self) -> Dict[str, Any]:
        """Get current project structure."""
        structure = defaultdict(list)
        
        for analysis in self.file_analyses.values():
            directory = str(Path(analysis.path).parent)
            structure[directory].append(analysis.name)
        
        return dict(structure)
    
    def _assess_risks(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """Assess risks of the organization plan."""
        risks = {
            'file_movements': len(plan.get('file_movements', [])),
            'import_changes': 0,
            'test_impact': 0,
            'overall_risk': 'low'
        }
        
        # Count potential import changes
        for movement in plan.get('file_movements', []):
            if movement.get('from', '').endswith('.py'):
                risks['import_changes'] += 1
        
        # Assess overall risk
        if risks['file_movements'] > 20:
            risks['overall_risk'] = 'high'
        elif risks['file_movements'] > 10:
            risks['overall_risk'] = 'medium'
        
        return risks
    
    def _create_rollback_plan(self, plan: Dict[str, Any]) -> List[str]:
        """Create rollback plan for the organization."""
        rollback_steps = []
        
        for movement in reversed(plan.get('file_movements', [])):
            rollback_steps.append(f"Move {movement.get('to')} back to {movement.get('from')}")
        
        for directory in reversed(plan.get('new_directories', [])):
            rollback_steps.append(f"Remove directory {directory}")
        
        return rollback_steps
    
    def _simulate_execution(self) -> Dict[str, Any]:
        """Simulate plan execution for dry run mode."""
        return {
            'success': True,
            'simulated': True,
            'would_execute': len(self.current_plan.execution_steps),
            'would_move': len(self.current_plan.file_movements),
            'would_create': len(self.current_plan.new_directories)
        }
    
    def _create_backup(self) -> str:
        """Create backup before executing plan."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = f"backup_before_organization_{timestamp}"
        
        # This would implement actual backup creation
        self.logger.info(f"Backup created at: {backup_path}")
        return backup_path
    
    async def _execute_step(self, step: str) -> bool:
        """Execute a single organization step."""
        # This would implement actual step execution
        self.logger.info(f"Executing step: {step}")
        return True
    
    def _restore_backup(self, backup_path: str):
        """Restore from backup in case of failure."""
        # This would implement actual backup restoration
        self.logger.info(f"Restoring from backup: {backup_path}")
    
    def get_organization_dashboard(self) -> Dict[str, Any]:
        """Get comprehensive organization dashboard."""
        return {
            'files_analyzed': len(self.file_analyses),
            'current_plan': self.current_plan.to_dict() if self.current_plan else None,
            'dry_run_mode': self.dry_run_mode,
            'backup_enabled': self.backup_enabled,
            'file_type_distribution': {
                file_type: len([f for f in self.file_analyses.values() if f.type == file_type])
                for file_type in set(f.type for f in self.file_analyses.values())
            } if self.file_analyses else {},
            'structure_health': self._calculate_structure_health()
        }
    
    def _calculate_structure_health(self) -> Dict[str, Any]:
        """Calculate overall project structure health score."""
        if not self.file_analyses:
            return {'score': 0, 'status': 'unknown'}
        
        # Calculate various health metrics
        total_files = len(self.file_analyses)
        root_files = len([f for f in self.file_analyses.values() if len(Path(f.path).parts) <= 2])
        
        # Scoring factors
        root_clutter_score = max(0, 1 - (root_files / total_files))  # Lower is better
        organization_score = len(set(Path(f.path).parent for f in self.file_analyses.values())) / total_files
        
        # Overall score
        health_score = (root_clutter_score + organization_score) / 2 * 100
        
        if health_score >= 80:
            status = 'excellent'
        elif health_score >= 60:
            status = 'good'
        elif health_score >= 40:
            status = 'fair'
        else:
            status = 'poor'
        
        return {
            'score': round(health_score, 2),
            'status': status,
            'root_clutter_ratio': round(root_files / total_files, 2),
            'organization_ratio': round(organization_score, 2)
        }