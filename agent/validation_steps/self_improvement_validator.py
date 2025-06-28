import ast
import radon
from radon.complexity import cc_visit
from pathlib import Path
import subprocess
import logging
from typing import Tuple
import json
from datetime import datetime

class SelfImprovementValidator:
    def __init__(self, logger: logging.Logger, base_path: Path, patches_to_apply: list, use_sandbox: bool = False):
        self.logger = logger.getChild("SelfImprovementValidator")
        self.base_path = base_path
        self.patches_to_apply = patches_to_apply
        self.use_sandbox = use_sandbox
        self.metrics = {
            'complexity': {},
            'test_coverage': {},
            'performance': {}
        }

    def execute(self) -> Tuple[bool, str, str]:
        try:
            self._collect_metrics()
            improvement_patches = self._generate_improvements()
            
            if improvement_patches:
                self._apply_improvements(improvement_patches)
                return True, "SELF_IMPROVED", f"Applied {len(improvement_patches)} self-improvements"
            return True, "NO_IMPROVEMENT_NEEDED", "Code meets quality thresholds"

        except Exception as e:
            self.logger.error(f"Self-improvement failed: {str(e)}", exc_info=True)
            return False, "SELF_IMPROVEMENT_ERROR", str(e)

    def _collect_metrics(self):
        """Collect code quality metrics from the project"""
        self.metrics = {'complexity': {}, 'test_coverage': {}}  # Reset metrics
        for file_path in self.base_path.glob('**/*.py'):
            if 'tests/' in str(file_path):
                continue
                
            with open(file_path, 'r', encoding='utf-8') as f:
                code = f.read()
                self._analyze_complexity(file_path, code)
                self._analyze_test_coverage(file_path)

    def _analyze_complexity(self, file_path: Path, code: str):
        """Calculate cyclomatic complexity using radon"""
        try:
            tree = ast.parse(code)
            complexities = cc_visit(code)
            total_complexity = sum([c.complexity for c in complexities])
            self.metrics['complexity'][str(file_path)] = {
                'average': total_complexity / len(complexities) if complexities else 0,
                'max': max([c.complexity for c in complexities], default=0)
            }
        except Exception as e:
            self.logger.warning(f"Complexity analysis failed for {file_path}: {str(e)}")

    def _analyze_test_coverage(self, file_path: Path):
        """Run coverage analysis for the target file"""
        try:
            # Run coverage on the entire project to capture dependencies
            subprocess.run(
                ['coverage', 'erase'],
                cwd=self.base_path,
                check=True
            )
            
            result = subprocess.run(
                ['coverage', 'run', '--source', str(self.base_path), '-m', 'pytest', str(file_path)],
                cwd=self.base_path,
                capture_output=True,
                text=True,
                timeout=60
            )
            if result.returncode == 0:
                report = subprocess.check_output(
                    ['coverage', 'report', '--format=json'],
                    text=True
                )
                coverage_data = json.loads(report)
                # Usar caminho relativo correto para o arquivo testado
                rel_path = str(file_path.relative_to(self.base_path)).replace('/', '.').replace('.py', '')
                file_coverage = coverage_data.get('files', {}).get(rel_path, {}).get('summary', {}).get('percent_covered', 0)
                self.metrics['test_coverage'][rel_path] = file_coverage
        except Exception as e:
            self.logger.warning(f"Coverage analysis failed for {file_path}: {str(e)}")

    def _generate_improvements(self) -> list:
        """Generate improvement patches based on collected metrics"""
        improvements = []
        threshold = {
            'complexity': 3,  # Threshold reduzido para ambiente de teste
            'coverage': 30
        }

        for file_path, metrics in self.metrics['complexity'].items():
            if metrics['max'] > threshold['complexity']:
                improvements.append({
                    'file_path': str(Path(file_path).relative_to(self.base_path)),
                    'operation': 'REFACTOR',
                    'reason': f"High cyclomatic complexity ({metrics['max']})",
                    'guidance': "Refactor complex functions using decomposition and design patterns"
                })

        for file_path, coverage in self.metrics['test_coverage'].items():
            if coverage < threshold['coverage']:
                improvements.append({
                    'file_path': file_path,
                    'operation': 'ENHANCE',
                    'reason': f"Low test coverage ({coverage}%)",
                    'guidance': "Add test cases for edge scenarios and error conditions"
                })

        return improvements

    def _apply_improvements(self, improvements: list):
        """Store improvements in memory for next cycle"""
        memory_path = self.base_path / "HEPHAESTUS_MEMORY.json"
        try:
            if memory_path.exists():
                with open(memory_path, 'r+', encoding='utf-8') as f:
                    memory = json.load(f)
                    memory.setdefault('improvements', []).extend(improvements)
                    f.seek(0)
                    json.dump(memory, f, indent=2)
            else:
                with open(memory_path, 'w', encoding='utf-8') as f:
                    json.dump({'improvements': improvements}, f, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to save improvements: {str(e)}")
