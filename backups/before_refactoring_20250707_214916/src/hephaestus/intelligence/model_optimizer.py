"""
Model Optimizer: Advanced Self-Optimization System

This system captures high-performance prompts and responses to create
fine-tuning datasets, enabling the AI to literally train better versions
of itself. This is where we achieve true model-level self-improvement!
"""

import json
import logging
import hashlib
import sqlite3
import pickle
import time
import threading
import queue
import statistics
from typing import Dict, Any, List, Optional, Tuple, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict, deque

from hephaestus.utils.llm_client import call_llm_api
from hephaestus.utils.json_parser import parse_json_response


@dataclass
class ModelPerformanceData:
    """Performance data for a specific model call"""
    timestamp: datetime
    agent_type: str
    prompt: str
    response: str
    success: bool
    execution_time: float
    quality_score: float
    context_metadata: Dict[str, Any]
    prompt_hash: str = field(default="")
    response_hash: str = field(default="")
    
    def __post_init__(self):
        self.prompt_hash = hashlib.md5(self.prompt.encode()).hexdigest()
        self.response_hash = hashlib.md5(self.response.encode()).hexdigest()


@dataclass
class FineTuningDataset:
    """A dataset prepared for fine-tuning"""
    name: str
    agent_type: str
    samples: List[Dict[str, str]]
    quality_threshold: float
    created_at: datetime
    performance_improvement: float
    metadata: Dict[str, Any]


class ModelOptimizer:
    """
    Advanced system for model self-optimization through performance data collection
    and fine-tuning dataset generation.
    """
    
    def __init__(self, model_config: Dict[str, str], logger: logging.Logger):
        self.model_config = model_config
        self.logger = logger
        
        # Initialize database for performance tracking
        self.db_path = Path("reports/model_performance.db")
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()
        
        # Performance tracking
        self.performance_data = []
        self.quality_thresholds = {
            "architect": 0.8,
            "maestro": 0.75,
            "code_review": 0.9,
            "error_analysis": 0.7,
            "performance_analysis": 0.8
        }
        
        # Fine-tuning management
        self.datasets = {}
        self.optimization_history = []
        
        # Advanced analytics
        self.performance_trends = defaultdict(list)
        self.prompt_effectiveness = {}
        
        self.logger.info("🚀 ModelOptimizer initialized - Ready for self-optimization!")
    
    def _init_database(self):
        """Initialize SQLite database for performance tracking"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS performance_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    agent_type TEXT NOT NULL,
                    prompt_hash TEXT NOT NULL,
                    response_hash TEXT NOT NULL,
                    success BOOLEAN NOT NULL,
                    execution_time REAL NOT NULL,
                    quality_score REAL NOT NULL,
                    context_metadata TEXT,
                    prompt_text TEXT,
                    response_text TEXT
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS fine_tuning_datasets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    agent_type TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    quality_threshold REAL NOT NULL,
                    performance_improvement REAL,
                    sample_count INTEGER,
                    dataset_path TEXT,
                    metadata TEXT
                )
            """)
    
    def capture_performance_data(self, agent_type: str, prompt: str, response: str,
                               success: bool, execution_time: float, 
                               context_metadata: Optional[Dict[str, Any]] = None) -> float:
        """
        Capture performance data for a model call and return quality score.
        """
        # Calculate quality score
        quality_score = self._calculate_quality_score(
            agent_type, prompt, response, success, execution_time, context_metadata
        )
        
        # Create performance record
        perf_data = ModelPerformanceData(
            timestamp=datetime.now(),
            agent_type=agent_type,
            prompt=prompt,
            response=response,
            success=success,
            execution_time=execution_time,
            quality_score=quality_score,
            context_metadata=context_metadata or {}
        )
        
        # Store in memory and database
        self.performance_data.append(perf_data)
        self._store_performance_data(perf_data)
        
        # Update trends
        self.performance_trends[agent_type].append({
            "timestamp": perf_data.timestamp,
            "quality_score": quality_score,
            "success": success
        })
        
        # Check if this is high-quality data for fine-tuning
        if quality_score >= self.quality_thresholds.get(agent_type, 0.8):
            self._mark_for_fine_tuning(perf_data)
        
        # Trigger optimization if we have enough data
        if len(self.performance_data) % 100 == 0:
            self._auto_optimize()
        
        # Real-time pattern analysis
        self._analyze_real_time_patterns(agent_type, perf_data)
        
        self.logger.debug(f"Captured performance data for {agent_type}: quality={quality_score:.3f}")
        return quality_score
    
    def _calculate_quality_score(self, agent_type: str, prompt: str, response: str,
                               success: bool, execution_time: float,
                               context_metadata: Optional[Dict[str, Any]]) -> float:
        """
        Calculate a comprehensive quality score for the model interaction.
        """
        base_score = 0.5
        
        # Success factor (40% weight)
        if success:
            base_score += 0.4
        else:
            base_score -= 0.2
        
        # Response quality factors (30% weight)
        response_factors = self._analyze_response_quality(response, agent_type)
        base_score += response_factors * 0.3
        
        # Efficiency factor (20% weight)
        efficiency_score = self._calculate_efficiency_score(execution_time, len(prompt))
        base_score += efficiency_score * 0.2
        
        # Context appropriateness (10% weight)
        context_score = self._evaluate_context_appropriateness(
            prompt, response, context_metadata
        )
        base_score += context_score * 0.1
        
        return max(0.0, min(1.0, base_score))
    
    def _analyze_response_quality(self, response: str, agent_type: str) -> float:
        """Analyze the quality of the response content."""
        if not response:
            return 0.0
        
        quality_score = 0.5
        
        # Length appropriateness
        length = len(response)
        if agent_type == "architect":
            # Architect needs detailed responses
            if 500 <= length <= 3000:
                quality_score += 0.2
            elif length < 200:
                quality_score -= 0.3
        elif agent_type == "maestro":
            # Maestro needs concise decisions
            if 100 <= length <= 800:
                quality_score += 0.2
            elif length > 1500:
                quality_score -= 0.2
        
        # JSON validity for structured responses
        if agent_type in ["architect", "maestro"]:
            try:
                json.loads(response)
                quality_score += 0.2
            except json.JSONDecodeError:
                # Try to find JSON in the response
                if "{" in response and "}" in response:
                    quality_score += 0.1
                else:
                    quality_score -= 0.2
        
        # Specific quality indicators
        quality_indicators = {
            "architect": ["file_path", "operation", "content", "analysis"],
            "maestro": ["strategy", "reason", "confidence"],
            "code_review": ["issues", "suggestions", "quality"],
            "error_analysis": ["error_type", "cause", "solution"]
        }
        
        indicators = quality_indicators.get(agent_type, [])
        found_indicators = sum(1 for indicator in indicators if indicator in response.lower())
        quality_score += (found_indicators / len(indicators) * 0.3) if indicators else 0
        
        return max(0.0, min(1.0, quality_score))
    
    def _calculate_efficiency_score(self, execution_time: float, prompt_length: int) -> float:
        """Calculate efficiency score based on execution time and prompt complexity."""
        # Normalize execution time (assume 1-10 seconds is normal)
        time_score = max(0, 1 - (execution_time - 1) / 9)
        
        # Normalize prompt complexity (assume 500-2000 chars is normal)
        complexity_factor = min(1.0, prompt_length / 1000)
        
        # Efficiency is time performance adjusted for complexity
        efficiency = time_score * (1 + complexity_factor * 0.5)
        
        return max(0.0, min(1.0, efficiency))
    
    def _evaluate_context_appropriateness(self, prompt: str, response: str,
                                        context_metadata: Optional[Dict[str, Any]]) -> float:
        """Evaluate how well the response fits the context."""
        if not context_metadata:
            return 0.5
        
        # Simple heuristics for context appropriateness
        context_score = 0.5
        
        # Check if response addresses the objective
        objective = context_metadata.get("objective", "")
        if objective and any(word in response.lower() for word in objective.lower().split()[:3]):
            context_score += 0.3
        
        # Check for consistency with previous successful approaches
        if context_metadata.get("similar_success_pattern"):
            context_score += 0.2
        
        return max(0.0, min(1.0, context_score))
    
    def _store_performance_data(self, perf_data: ModelPerformanceData):
        """Store performance data in database."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO performance_data (
                    timestamp, agent_type, prompt_hash, response_hash,
                    success, execution_time, quality_score, context_metadata,
                    prompt_text, response_text
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                perf_data.timestamp.isoformat(),
                perf_data.agent_type,
                perf_data.prompt_hash,
                perf_data.response_hash,
                perf_data.success,
                perf_data.execution_time,
                perf_data.quality_score,
                json.dumps(perf_data.context_metadata),
                perf_data.prompt,
                perf_data.response
            ))
    
    def _mark_for_fine_tuning(self, perf_data: ModelPerformanceData):
        """Mark high-quality data for fine-tuning dataset."""
        agent_type = perf_data.agent_type
        
        if agent_type not in self.datasets:
            self.datasets[agent_type] = []
        
        # Add to fine-tuning dataset
        self.datasets[agent_type].append({
            "prompt": perf_data.prompt,
            "response": perf_data.response,
            "quality_score": perf_data.quality_score,
            "timestamp": perf_data.timestamp.isoformat()
        })
        
        self.logger.info(f"✨ High-quality data marked for fine-tuning: {agent_type} (score: {perf_data.quality_score:.3f})")
    
    def _auto_optimize(self):
        """Automatically trigger optimization when conditions are met."""
        self.logger.info("🔧 Auto-optimization triggered - Analyzing performance patterns...")
        
        # Analyze performance trends
        improvement_opportunities = self._identify_improvement_opportunities()
        
        # Generate fine-tuning datasets if we have enough data
        for agent_type in improvement_opportunities:
            if len(self.datasets.get(agent_type, [])) >= 50:  # Minimum samples
                self._generate_fine_tuning_dataset(agent_type)
    
    def _identify_improvement_opportunities(self) -> List[str]:
        """Identify which agents could benefit from optimization."""
        opportunities = []
        
        for agent_type, trends in self.performance_trends.items():
            if len(trends) < 20:  # Need enough data
                continue
            
            # Calculate recent performance
            recent_trends = trends[-20:]
            avg_quality = sum(t["quality_score"] for t in recent_trends) / len(recent_trends)
            success_rate = sum(1 for t in recent_trends if t["success"]) / len(recent_trends)
            
            # Identify improvement opportunities
            if avg_quality < 0.7 or success_rate < 0.8:
                opportunities.append(agent_type)
                self.logger.info(f"📊 Improvement opportunity identified: {agent_type} (quality: {avg_quality:.3f}, success: {success_rate:.3f})")
        
        return opportunities
    
    def generate_fine_tuning_dataset(self, agent_type: str, min_samples: int = 100) -> Optional[FineTuningDataset]:
        """
        Generate a fine-tuning dataset for a specific agent type.
        """
        if agent_type not in self.datasets:
            self.logger.warning(f"No data available for {agent_type}")
            return None
        
        samples = self.datasets[agent_type]
        if len(samples) < min_samples:
            self.logger.warning(f"Insufficient samples for {agent_type}: {len(samples)} < {min_samples}")
            return None
        
        # Sort by quality score and take top samples
        sorted_samples = sorted(samples, key=lambda x: x["quality_score"], reverse=True)
        top_samples = sorted_samples[:min_samples * 2]  # Take more than minimum for selection
        
        # Create fine-tuning format
        fine_tuning_data = []
        for sample in top_samples:
            fine_tuning_data.append({
                "messages": [
                    {"role": "user", "content": sample["prompt"]},
                    {"role": "assistant", "content": sample["response"]}
                ],
                "metadata": {
                    "quality_score": sample["quality_score"],
                    "agent_type": agent_type,
                    "timestamp": sample["timestamp"]
                }
            })
        
        # Create dataset
        dataset = FineTuningDataset(
            name=f"{agent_type}_optimization_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            agent_type=agent_type,
            samples=fine_tuning_data,
            quality_threshold=self.quality_thresholds.get(agent_type, 0.8),
            created_at=datetime.now(),
            performance_improvement=self._estimate_performance_improvement(agent_type),
            metadata={
                "sample_count": len(fine_tuning_data),
                "avg_quality": sum(s["metadata"]["quality_score"] for s in fine_tuning_data) / len(fine_tuning_data),
                "date_range": {
                    "start": min(s["metadata"]["timestamp"] for s in fine_tuning_data),
                    "end": max(s["metadata"]["timestamp"] for s in fine_tuning_data)
                }
            }
        )
        
        # Save dataset
        self._save_fine_tuning_dataset(dataset)
        
        self.logger.info(f"🎯 Fine-tuning dataset generated for {agent_type}: {len(fine_tuning_data)} samples")
        return dataset
    
    def _generate_fine_tuning_dataset(self, agent_type: str):
        """Internal method to generate fine-tuning dataset."""
        return self.generate_fine_tuning_dataset(agent_type)
    
    def _save_fine_tuning_dataset(self, dataset: FineTuningDataset):
        """Save fine-tuning dataset to disk and database."""
        # Save to JSONL format (standard for fine-tuning)
        dataset_path = Path(f"reports/fine_tuning/{dataset.name}.jsonl")
        dataset_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(dataset_path, 'w') as f:
            for sample in dataset.samples:
                f.write(json.dumps(sample) + '\n')
        
        # Save metadata to database
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO fine_tuning_datasets (
                    name, agent_type, created_at, quality_threshold,
                    performance_improvement, sample_count, dataset_path, metadata
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                dataset.name,
                dataset.agent_type,
                dataset.created_at.isoformat(),
                dataset.quality_threshold,
                dataset.performance_improvement,
                len(dataset.samples),
                str(dataset_path),
                json.dumps(dataset.metadata)
            ))
        
        self.logger.info(f"💾 Fine-tuning dataset saved: {dataset_path}")
    
    def _estimate_performance_improvement(self, agent_type: str) -> float:
        """Estimate potential performance improvement from fine-tuning."""
        trends = self.performance_trends.get(agent_type, [])
        if len(trends) < 10:
            return 0.0
        
        # Calculate current performance
        recent_performance = sum(t["quality_score"] for t in trends[-10:]) / 10
        
        # Estimate improvement based on data quality
        high_quality_samples = len([s for s in self.datasets.get(agent_type, []) 
                                  if s["quality_score"] >= 0.9])
        
        # Conservative estimate: 5-15% improvement based on data quality
        improvement_estimate = min(0.15, (high_quality_samples / 100) * 0.1 + 0.05)
        
        return improvement_estimate
    
    def get_optimization_report(self) -> Dict[str, Any]:
        """Get comprehensive optimization report."""
        report = {
            "timestamp": datetime.now().isoformat(),
            "performance_summary": {},
            "fine_tuning_datasets": {},
            "improvement_opportunities": [],
            "optimization_history": self.optimization_history[-10:],
            "recommendations": []
        }
        
        # Performance summary by agent type
        for agent_type, trends in self.performance_trends.items():
            if not trends:
                continue
                
            recent_trends = trends[-20:] if len(trends) >= 20 else trends
            
            report["performance_summary"][agent_type] = {
                "total_calls": len(trends),
                "recent_avg_quality": sum(t["quality_score"] for t in recent_trends) / len(recent_trends),
                "recent_success_rate": sum(1 for t in recent_trends if t["success"]) / len(recent_trends),
                "trend_direction": self._calculate_trend_direction(trends),
                "high_quality_samples": len([s for s in self.datasets.get(agent_type, []) 
                                           if s["quality_score"] >= 0.9])
            }
        
        # Fine-tuning dataset status
        for agent_type, samples in self.datasets.items():
            report["fine_tuning_datasets"][agent_type] = {
                "sample_count": len(samples),
                "avg_quality": sum(s["quality_score"] for s in samples) / len(samples) if samples else 0,
                "ready_for_training": len(samples) >= 100
            }
        
        # Generate recommendations
        report["recommendations"] = self._generate_optimization_recommendations()
        
        return report
    
    def _calculate_trend_direction(self, trends: List[Dict[str, Any]]) -> str:
        """Calculate if performance is trending up, down, or stable."""
        if len(trends) < 10:
            return "insufficient_data"
        
        # Compare first half vs second half
        mid_point = len(trends) // 2
        first_half_avg = sum(t["quality_score"] for t in trends[:mid_point]) / mid_point
        second_half_avg = sum(t["quality_score"] for t in trends[mid_point:]) / (len(trends) - mid_point)
        
        diff = second_half_avg - first_half_avg
        
        if diff > 0.05:
            return "improving"
        elif diff < -0.05:
            return "declining"
        else:
            return "stable"
    
    def _generate_optimization_recommendations(self) -> List[str]:
        """Generate recommendations based on performance data."""
        recommendations = []
        
        # Check each agent type
        for agent_type, trends in self.performance_trends.items():
            if len(trends) < 10:
                continue
            
            recent_avg = sum(t["quality_score"] for t in trends[-10:]) / 10
            samples_available = len(self.datasets.get(agent_type, []))
            
            if recent_avg < 0.7:
                recommendations.append(f"⚠️ {agent_type} performance below threshold ({recent_avg:.3f})")
            
            if samples_available >= 100:
                recommendations.append(f"🎯 {agent_type} ready for fine-tuning ({samples_available} samples)")
            
            if self._calculate_trend_direction(trends) == "declining":
                recommendations.append(f"📉 {agent_type} performance declining - investigate causes")
        
        # General recommendations
        total_high_quality = sum(len([s for s in samples if s["quality_score"] >= 0.9]) 
                               for samples in self.datasets.values())
        
        if total_high_quality >= 500:
            recommendations.append("🚀 Sufficient high-quality data for comprehensive model optimization")
        
        recommendations.append(" regularly to improve system performance.")
        
        return recommendations

    def evolutionary_prompt_optimization(self, agent_type: str, current_prompt: str) -> str:
        """
        Use evolutionary algorithms to optimize prompts based on performance data.
        """
        self.logger.info(f"🧬 Starting evolutionary prompt optimization for {agent_type}")
        
        # Get performance data for this agent type
        agent_data = [d for d in self.performance_data 
                     if d.agent_type == agent_type and d.quality_score >= 0.8]
        
        if len(agent_data) < 10:
            self.logger.warning(f"Insufficient data for prompt optimization: {len(agent_data)} samples")
            return current_prompt
        
        # Analyze high-performing prompts
        high_performers = sorted(agent_data, key=lambda x: x.quality_score, reverse=True)[:5]
        
        optimization_prompt = f"""
[EVOLUTIONARY PROMPT OPTIMIZATION]
You are optimizing a prompt for {agent_type} based on performance data.

[CURRENT PROMPT]
{current_prompt}

[HIGH-PERFORMING EXAMPLES]
{json.dumps([{"quality": hp.quality_score, "prompt_excerpt": hp.prompt[:200]} for hp in high_performers], indent=2)}

[OPTIMIZATION TASK]
Analyze the patterns in high-performing prompts and create an optimized version.
Focus on:
1. Structural improvements from successful examples
2. Clarity and specificity enhancements
3. Better instruction formatting
4. Elimination of ambiguous language

[OUTPUT FORMAT]
{{
  "optimized_prompt": "The improved prompt",
  "improvements_made": ["list of specific improvements"],
  "expected_performance_gain": "estimated percentage improvement"
}}
"""
        
        try:
            response, error = call_llm_api(
                model_config=self.model_config,
                prompt=optimization_prompt,
                temperature=0.4,
                logger=self.logger
            )
            
            if error or not response:
                return current_prompt
            
            parsed, _ = parse_json_response(response, self.logger)
            if not parsed:
                return current_prompt
            
            optimized_prompt = parsed.get("optimized_prompt", current_prompt)
            improvements = parsed.get("improvements_made", [])
            
            self.logger.info(f"🔧 Prompt optimized for {agent_type}:")
            for improvement in improvements:
                self.logger.info(f"  • {improvement}")
            
            return optimized_prompt
            
        except Exception as e:
            self.logger.error(f"Prompt optimization failed: {e}")
            return current_prompt

    def get_agent_performance_summary(self) -> Dict[str, Dict[str, Any]]:
        """
        Retrieves and summarizes performance data for each agent from the database.
        """
        summary = {}
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT
                        agent_type,
                        COUNT(*),
                        SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END),
                        AVG(quality_score)
                    FROM performance_data
                    GROUP BY agent_type
                """)
                rows = cursor.fetchall()
                
                for row in rows:
                    agent_type, total_calls, success_calls, avg_quality = row
                    success_rate = (success_calls / total_calls) if total_calls > 0 else 0
                    summary[agent_type] = {
                        "total_calls": total_calls,
                        "success_calls": success_calls,
                        "success_rate": round(success_rate, 3),
                        "average_quality_score": round(avg_quality, 3),
                        "needs_evolution": success_rate < 0.8 or avg_quality < 0.75
                    }
            return summary
        except Exception as e:
            self.logger.error(f"Failed to get agent performance summary from DB: {e}")
            return {}
    
    def _analyze_real_time_patterns(self, agent_type: str, perf_data: 'ModelPerformanceData'):
        """Análise REAL de padrões em tempo real."""
        try:
            # Análise de tendência
            recent_data = [
                d for d in self.performance_data[-50:] 
                if d.agent_type == agent_type
            ]
            
            if len(recent_data) >= 10:
                recent_scores = [d.quality_score for d in recent_data[-10:]]
                avg_recent = statistics.mean(recent_scores)
                
                # Detectar degradação de performance
                if avg_recent < 0.6:
                    self.logger.warning(f"🔻 Degradação detectada em {agent_type}: {avg_recent:.3f}")
                    self._trigger_emergency_optimization(agent_type)
                
                # Detectar melhoria
                elif avg_recent > 0.9:
                    self.logger.info(f"📈 Performance excelente em {agent_type}: {avg_recent:.3f}")
                    self._capture_best_practices(agent_type, recent_data[-5:])
            
        except Exception as e:
            self.logger.error(f"Erro na análise de padrões: {e}")
    
    def _trigger_emergency_optimization(self, agent_type: str):
        """Otimização emergencial REAL."""
        try:
            self.logger.info(f"🚨 Iniciando otimização emergencial para {agent_type}")
            
            # Análise de causa raiz
            recent_failures = [
                d for d in self.performance_data[-100:]
                if d.agent_type == agent_type and not d.success
            ]
            
            if recent_failures:
                # Identificar padrões de falha
                failure_patterns = {}
                for failure in recent_failures:
                    prompt_hash = hashlib.md5(failure.prompt.encode()).hexdigest()[:8]
                    if prompt_hash not in failure_patterns:
                        failure_patterns[prompt_hash] = []
                    failure_patterns[prompt_hash].append(failure)
                
                # Reportar padrões encontrados
                for pattern, failures in failure_patterns.items():
                    if len(failures) > 3:
                        self.logger.warning(f"🔍 Padrão de falha detectado [{pattern}]: {len(failures)} ocorrências")
                        
                        # Auto-correção: Ajustar threshold temporariamente
                        if agent_type in self.quality_thresholds:
                            self.quality_thresholds[agent_type] *= 0.9  # Reduzir em 10%
                            self.logger.info(f"🔧 Threshold ajustado para {agent_type}: {self.quality_thresholds[agent_type]:.3f}")
            
        except Exception as e:
            self.logger.error(f"Erro na otimização emergencial: {e}")
    
    def _capture_best_practices(self, agent_type: str, high_quality_data: List['ModelPerformanceData']):
        """Capturar REALMENTE as melhores práticas."""
        try:
            # Análise de prompts de alta qualidade
            successful_prompts = []
            for data in high_quality_data:
                if data.success and data.quality_score > 0.9:
                    successful_prompts.append({
                        'prompt': data.prompt,
                        'response': data.response,
                        'score': data.quality_score,
                        'execution_time': data.execution_time
                    })
            
            if successful_prompts:
                # Salvar como template para reutilização
                template_path = Path(f"data/best_practices/{agent_type}_templates.json")
                template_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Carregar templates existentes
                existing_templates = []
                if template_path.exists():
                    with open(template_path, 'r') as f:
                        existing_templates = json.load(f)
                
                # Adicionar novos templates
                existing_templates.extend(successful_prompts)
                
                # Manter apenas os melhores (top 50)
                existing_templates = sorted(existing_templates, key=lambda x: x['score'], reverse=True)[:50]
                
                # Salvar
                with open(template_path, 'w') as f:
                    json.dump(existing_templates, f, indent=2, default=str)
                
                self.logger.info(f"💾 {len(successful_prompts)} melhores práticas salvas para {agent_type}")
                
        except Exception as e:
            self.logger.error(f"Erro capturando melhores práticas: {e}")
    
    def get_best_practices_for_agent(self, agent_type: str) -> List[Dict]:
        """Obter melhores práticas REAIS para um agente."""
        try:
            template_path = Path(f"data/best_practices/{agent_type}_templates.json")
            if template_path.exists():
                with open(template_path, 'r') as f:
                    return json.load(f)
            return []
        except Exception as e:
            self.logger.error(f"Erro carregando melhores práticas: {e}")
            return []
    
    def auto_improve_prompt(self, agent_type: str, original_prompt: str) -> str:
        """Melhorar AUTOMATICAMENTE um prompt baseado nas melhores práticas."""
        try:
            best_practices = self.get_best_practices_for_agent(agent_type)
            
            if not best_practices:
                return original_prompt
            
            # Análise de similaridade com prompts de sucesso
            similarities = []
            for practice in best_practices[:10]:  # Top 10
                # Análise simples de palavras-chave em comum
                original_words = set(original_prompt.lower().split())
                practice_words = set(practice['prompt'].lower().split())
                
                common_words = original_words.intersection(practice_words)
                similarity = len(common_words) / max(len(original_words), len(practice_words))
                
                if similarity > 0.3:  # 30% de similaridade
                    similarities.append((practice, similarity))
            
            if similarities:
                # Usar o prompt mais similar como base para melhoria
                best_match = max(similarities, key=lambda x: x[1])[0]
                
                # Melhorar prompt (implementação simples)
                improved_prompt = self._enhance_prompt_with_best_practice(original_prompt, best_match)
                
                self.logger.info(f"🔧 Prompt melhorado para {agent_type} (similaridade: {similarities[0][1]:.3f})")
                return improved_prompt
            
            return original_prompt
            
        except Exception as e:
            self.logger.error(f"Erro melhorando prompt: {e}")
            return original_prompt
    
    def _enhance_prompt_with_best_practice(self, original: str, best_practice: Dict) -> str:
        """Implementação REAL de melhoria de prompt."""
        try:
            # Estratégias de melhoria baseadas em análise real
            enhanced = original
            
            # 1. Adicionar contexto se o prompt de sucesso tem mais contexto
            if len(best_practice['prompt']) > len(original) * 1.5:
                # Extrair elementos estruturais do prompt de sucesso
                if "Context:" in best_practice['prompt'] and "Context:" not in original:
                    enhanced = f"Context: Please provide detailed analysis.\n\n{enhanced}"
            
            # 2. Melhorar especificidade
            if best_practice['score'] > 0.95:
                # Adicionar palavras-chave de alta performance
                high_perf_words = ['specific', 'detailed', 'analyze', 'evaluate', 'comprehensive']
                for word in high_perf_words:
                    if word in best_practice['prompt'].lower() and word not in enhanced.lower():
                        if 'analyze' in word:
                            enhanced = enhanced.replace('look at', 'analyze')
                        elif 'detailed' in word and 'brief' not in enhanced.lower():
                            enhanced = enhanced.replace('explain', 'provide detailed explanation of')
            
            # 3. Estruturação
            if '1.' in best_practice['prompt'] and '1.' not in enhanced:
                enhanced += "\n\nPlease structure your response with numbered points."
            
            return enhanced
            
        except Exception as e:
            self.logger.error(f"Erro no enhancement: {e}")
            return original


# Global instance
_model_optimizer = None

def get_model_optimizer(model_config: Dict[str, str], logger: logging.Logger) -> ModelOptimizer:
    """Factory function to get a singleton instance of the ModelOptimizer."""
    global _model_optimizer
    if _model_optimizer is None:
        _model_optimizer = ModelOptimizer(model_config, logger)
    return _model_optimizer