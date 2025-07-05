import logging
from typing import Dict, List, Optional, Tuple
from enum import Enum, auto
from dataclasses import dataclass
from pathlib import Path
from agent.utils import advanced_logging
from agent.code_metrics import analyze_complexity, detect_code_duplication
from agent.project_scanner import analyze_code_metrics
from agent.memory import Memory

class DebtType(Enum):
    CODE_SMELL = auto()
    ARCHITECTURAL = auto()
    PERFORMANCE = auto()
    SECURITY = auto()
    TEST_COVERAGE = auto()
    DOCUMENTATION = auto()
    DEPRECATED = auto()

@dataclass
class TechnicalDebtItem:
    file_path: str
    line_number: int
    debt_type: DebtType
    description: str
    severity: int  # 1-5 scale
    estimated_resolution_time: int  # in hours

class DebtHunterAgent:
    """
    An autonomous agent that proactively hunts for technical debt and proposes
    solutions based on severity and impact analysis.
    """

    def __init__(self, logger: Optional[logging.Logger] = None, memory: Optional[Memory] = None):
        self.logger = logger or advanced_logging.setup_advanced_logging('debt_hunter')
        self.memory = memory
        self.debt_categories = self._load_debt_categories()

    def _load_debt_categories(self) -> Dict[DebtType, Dict[str, any]]:
        """Load debt categories with their detection patterns and weights."""
        return {
            DebtType.CODE_SMELL: {
                'patterns': ['code smell', 'bad practice', 'anti-pattern'],
                'weight': 1.0
            },
            DebtType.ARCHITECTURAL: {
                'patterns': ['circular dependency', 'tight coupling', 'god object'],
                'weight': 1.5
            },
            DebtType.PERFORMANCE: {
                'patterns': ['slow', 'inefficient', 'bottleneck', 'high complexity'],
                'weight': 1.3
            },
            DebtType.SECURITY: {
                'patterns': ['vulnerability', 'insecure', 'risk'],
                'weight': 2.0
            },
            DebtType.TEST_COVERAGE: {
                'patterns': ['untested', 'missing test', 'low coverage'],
                'weight': 0.8
            },
            DebtType.DOCUMENTATION: {
                'patterns': ['undocumented', 'missing doc', 'outdated doc'],
                'weight': 0.5
            },
            DebtType.DEPRECATED: {
                'patterns': ['deprecated', 'legacy', 'obsolete'],
                'weight': 1.2
            }
        }

    def scan_project(self, project_root: str) -> List[TechnicalDebtItem]:
        """
        Scan the project for technical debt items.
        Returns a list of identified technical debt items with metadata.
        """
        self.logger.info(f"Starting technical debt scan for project: {project_root}")
        
        # Get code metrics first
        metrics = analyze_code_metrics(project_root)
        debt_items = []
        
        # Add debt items based on metrics
        for file_metrics in metrics:
            if file_metrics['loc'] > 300:
                debt_items.append(TechnicalDebtItem(
                    file_path=file_metrics['file'],
                    line_number=0,
                    debt_type=DebtType.CODE_SMELL,
                    description=f"File is too large ({file_metrics['loc']} lines). Consider splitting.",
                    severity=3,
                    estimated_resolution_time=2
                ))
            
            for func_metrics in file_metrics['functions']:
                if func_metrics['cyclomatic_complexity'] > 10:
                    debt_items.append(TechnicalDebtItem(
                        file_path=file_metrics['file'],
                        line_number=func_metrics['line_number'],
                        debt_type=DebtType.PERFORMANCE,
                        description=f"High cyclomatic complexity ({func_metrics['cyclomatic_complexity']}) in function {func_metrics['name']}",
                        severity=4,
                        estimated_resolution_time=3
                    ))
                
                if func_metrics['loc'] > 50:
                    debt_items.append(TechnicalDebtItem(
                        file_path=file_metrics['file'],
                        line_number=func_metrics['line_number'],
                        debt_type=DebtType.CODE_SMELL,
                        description=f"Long function ({func_metrics['loc']} lines) {func_metrics['name']}",
                        severity=3,
                        estimated_resolution_time=2
                    ))
        
        # Check for missing tests
        for file_metrics in metrics:
            if not file_metrics['has_tests'] and not file_metrics['is_test_file']:
                debt_items.append(TechnicalDebtItem(
                    file_path=file_metrics['file'],
                    line_number=0,
                    debt_type=DebtType.TEST_COVERAGE,
                    description=f"Missing tests for file {file_metrics['file']}",
                    severity=2,
                    estimated_resolution_time=1
                ))
        
        self.logger.info(f"Found {len(debt_items)} technical debt items")
        return debt_items

    def prioritize_debt(self, debt_items: List[TechnicalDebtItem]) -> List[TechnicalDebtItem]:
        """
        Prioritize technical debt items based on severity, impact, and other factors.
        Returns a sorted list with highest priority items first.
        """
        # Simple priority calculation (can be enhanced with ML later)
        for item in debt_items:
            category_info = self.debt_categories[item.debt_type]
            item.priority_score = item.severity * category_info['weight']
        
        return sorted(debt_items, key=lambda x: x.priority_score, reverse=True)

    def generate_debt_report(self, debt_items: List[TechnicalDebtItem]) -> str:
        """Generate a formatted report of technical debt findings."""
        report = "# Technical Debt Report\n\n"
        report += f"## Summary\nTotal items found: {len(debt_items)}\n\n"
        
        by_type = {t: 0 for t in DebtType}
        for item in debt_items:
            by_type[item.debt_type] += 1
        
        report += "## By Category\n"
        for debt_type, count in by_type.items():
            report += f"- {debt_type.name}: {count}\n"
        
        report += "\n## High Priority Items (Top 10)\n"
        high_priority = sorted(debt_items, key=lambda x: x.priority_score, reverse=True)[:10]
        for item in high_priority:
            report += (
                f"### {item.debt_type.name} - Severity {item.severity}\n"
                f"**File:** {item.file_path}:{item.line_number}\n"
                f"**Description:** {item.description}\n"
                f"**Estimated Resolution Time:** {item.estimated_resolution_time} hours\n\n"
            )
        
        return report

    def save_report(self, report: str, output_path: str = "reports/technical_debt_report.md") -> None:
        """Save the technical debt report to a file."""
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            f.write(report)
        self.logger.info(f"Saved technical debt report to {output_path}")

    def run(self, project_root: str) -> None:
        """Main execution method for the debt hunter agent."""
        debt_items = self.scan_project(project_root)
        prioritized = self.prioritize_debt(debt_items)
        report = self.generate_debt_report(prioritized)
        self.save_report(report)
        
        if self.memory:
            self._store_in_memory(prioritized)

    def _store_in_memory(self, debt_items: List[TechnicalDebtItem]) -> None:
        """Store technical debt findings in the agent's memory."""
        for item in debt_items:
            self.memory.store(
                category="technical_debt",
                key=f"{item.file_path}:{item.line_number}",
                value={
                    "type": item.debt_type.name,
                    "description": item.description,
                    "severity": item.severity,
                    "timestamp": datetime.now().isoformat()
                }
            )