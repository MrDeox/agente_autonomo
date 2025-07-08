"""
Metrics Collector - Centralized metrics collection and reporting
"""

import time
from collections import defaultdict, deque
from typing import Dict, Any, Optional, List, Deque
from datetime import datetime, timedelta
import threading
import json


class MetricsCollector:
    """Centralized metrics collection system for all agents and services."""
    
    def __init__(self, max_history: int = 1000):
        self.max_history = max_history
        self._lock = threading.Lock()
        
        # Metrics storage
        self.agent_metrics: Dict[str, Deque[Dict[str, Any]]] = defaultdict(lambda: deque(maxlen=max_history))
        self.llm_metrics: Deque[Dict[str, Any]] = deque(maxlen=max_history)
        self.service_metrics: Dict[str, Deque[Dict[str, Any]]] = defaultdict(lambda: deque(maxlen=max_history))
        self.system_metrics: Deque[Dict[str, Any]] = deque(maxlen=max_history)
        
        # Aggregated stats
        self._agent_stats: Dict[str, Dict[str, Any]] = defaultdict(dict)
        self._llm_stats: Dict[str, Any] = {}
        self._last_aggregation = time.time()
        self._aggregation_interval = 60  # seconds
    
    def record_agent_performance(self, 
                               agent_name: str,
                               operation: str, 
                               duration: float,
                               success: bool,
                               metadata: Optional[Dict[str, Any]] = None):
        """
        Record agent performance metrics.
        
        Args:
            agent_name: Name of the agent
            operation: Operation being performed
            duration: Duration in seconds
            success: Whether the operation succeeded
            metadata: Additional metadata
        """
        with self._lock:
            metric = {
                'timestamp': datetime.now().isoformat(),
                'operation': operation,
                'duration': duration,
                'success': success,
                'metadata': metadata or {}
            }
            
            self.agent_metrics[agent_name].append(metric)
            self._update_agent_stats(agent_name)
    
    def record_llm_call(self,
                       model: str,
                       prompt_tokens: int,
                       completion_tokens: int,
                       duration: float,
                       success: bool,
                       cached: bool = False,
                       fallback: bool = False,
                       attempt: int = 1):
        """
        Record LLM call metrics.
        
        Args:
            model: Model used for the call
            prompt_tokens: Number of prompt tokens
            completion_tokens: Number of completion tokens
            duration: Duration in seconds
            success: Whether the call succeeded
            cached: Whether result was from cache
            fallback: Whether a fallback model was used
            attempt: Attempt number (for retries)
        """
        with self._lock:
            metric = {
                'timestamp': datetime.now().isoformat(),
                'model': model,
                'prompt_tokens': prompt_tokens,
                'completion_tokens': completion_tokens,
                'total_tokens': prompt_tokens + completion_tokens,
                'duration': duration,
                'success': success,
                'cached': cached,
                'fallback': fallback,
                'attempt': attempt
            }
            
            self.llm_metrics.append(metric)
            self._update_llm_stats()
    
    def record_service_metric(self,
                            service_name: str,
                            metric_name: str,
                            value: Any,
                            tags: Optional[Dict[str, str]] = None):
        """
        Record service-specific metrics.
        
        Args:
            service_name: Name of the service
            metric_name: Name of the metric
            value: Metric value
            tags: Optional tags for categorization
        """
        with self._lock:
            metric = {
                'timestamp': datetime.now().isoformat(),
                'metric_name': metric_name,
                'value': value,
                'tags': tags or {}
            }
            
            self.service_metrics[service_name].append(metric)
    
    def record_system_metric(self,
                           metric_name: str,
                           value: Any,
                           tags: Optional[Dict[str, str]] = None):
        """
        Record system-wide metrics.
        
        Args:
            metric_name: Name of the metric
            value: Metric value
            tags: Optional tags for categorization
        """
        with self._lock:
            metric = {
                'timestamp': datetime.now().isoformat(),
                'metric_name': metric_name,
                'value': value,
                'tags': tags or {}
            }
            
            self.system_metrics.append(metric)
    
    def get_agent_dashboard(self, agent_name: str) -> Dict[str, Any]:
        """
        Get dashboard data for a specific agent.
        
        Args:
            agent_name: Name of the agent
            
        Returns:
            Dashboard data dictionary
        """
        with self._lock:
            if agent_name not in self.agent_metrics:
                return {'error': f'No metrics found for agent: {agent_name}'}
            
            metrics = list(self.agent_metrics[agent_name])
            if not metrics:
                return {'error': f'No metrics data for agent: {agent_name}'}
            
            # Calculate statistics
            total_calls = len(metrics)
            successful_calls = sum(1 for m in metrics if m['success'])
            failed_calls = total_calls - successful_calls
            
            durations = [m['duration'] for m in metrics]
            avg_duration = sum(durations) / len(durations) if durations else 0
            
            # Recent activity (last hour)
            one_hour_ago = datetime.now() - timedelta(hours=1)
            recent_metrics = [
                m for m in metrics 
                if datetime.fromisoformat(m['timestamp']) > one_hour_ago
            ]
            
            # Operation breakdown
            operations = defaultdict(int)
            for m in metrics:
                operations[m['operation']] += 1
            
            return {
                'agent_name': agent_name,
                'total_calls': total_calls,
                'successful_calls': successful_calls,
                'failed_calls': failed_calls,
                'success_rate': successful_calls / total_calls if total_calls > 0 else 0,
                'average_duration': avg_duration,
                'recent_activity_count': len(recent_metrics),
                'operations': dict(operations),
                'last_activity': metrics[-1]['timestamp'] if metrics else None
            }
    
    def get_llm_dashboard(self) -> Dict[str, Any]:
        """Get dashboard data for LLM calls."""
        with self._lock:
            metrics = list(self.llm_metrics)
            if not metrics:
                return {'error': 'No LLM metrics available'}
            
            # Calculate statistics
            total_calls = len(metrics)
            successful_calls = sum(1 for m in metrics if m['success'])
            cached_calls = sum(1 for m in metrics if m.get('cached', False))
            fallback_calls = sum(1 for m in metrics if m.get('fallback', False))
            
            total_tokens = sum(m['total_tokens'] for m in metrics)
            total_duration = sum(m['duration'] for m in metrics)
            
            # Model usage
            models = defaultdict(int)
            for m in metrics:
                models[m['model']] += 1
            
            # Recent activity
            one_hour_ago = datetime.now() - timedelta(hours=1)
            recent_metrics = [
                m for m in metrics 
                if datetime.fromisoformat(m['timestamp']) > one_hour_ago
            ]
            
            return {
                'total_calls': total_calls,
                'successful_calls': successful_calls,
                'failed_calls': total_calls - successful_calls,
                'success_rate': successful_calls / total_calls if total_calls > 0 else 0,
                'cached_calls': cached_calls,
                'cache_hit_rate': cached_calls / total_calls if total_calls > 0 else 0,
                'fallback_calls': fallback_calls,
                'total_tokens': total_tokens,
                'total_duration': total_duration,
                'average_duration': total_duration / total_calls if total_calls > 0 else 0,
                'tokens_per_second': total_tokens / total_duration if total_duration > 0 else 0,
                'models_used': dict(models),
                'recent_activity_count': len(recent_metrics),
                'last_activity': metrics[-1]['timestamp'] if metrics else None
            }
    
    def get_service_dashboard(self, service_name: str) -> Dict[str, Any]:
        """Get dashboard data for a specific service."""
        with self._lock:
            if service_name not in self.service_metrics:
                return {'error': f'No metrics found for service: {service_name}'}
            
            metrics = list(self.service_metrics[service_name])
            if not metrics:
                return {'error': f'No metrics data for service: {service_name}'}
            
            # Group by metric name
            metric_groups = defaultdict(list)
            for m in metrics:
                metric_groups[m['metric_name']].append(m)
            
            # Calculate stats for each metric
            metric_stats = {}
            for metric_name, metric_list in metric_groups.items():
                values = [m['value'] for m in metric_list if isinstance(m['value'], (int, float))]
                if values:
                    metric_stats[metric_name] = {
                        'count': len(metric_list),
                        'min': min(values),
                        'max': max(values),
                        'avg': sum(values) / len(values),
                        'last_value': metric_list[-1]['value'],
                        'last_updated': metric_list[-1]['timestamp']
                    }
                else:
                    metric_stats[metric_name] = {
                        'count': len(metric_list),
                        'last_value': metric_list[-1]['value'],
                        'last_updated': metric_list[-1]['timestamp']
                    }
            
            return {
                'service_name': service_name,
                'total_metrics': len(metrics),
                'metric_types': list(metric_groups.keys()),
                'metrics': metric_stats,
                'last_activity': metrics[-1]['timestamp'] if metrics else None
            }
    
    def get_system_dashboard(self) -> Dict[str, Any]:
        """Get system-wide dashboard data."""
        with self._lock:
            return {
                'agents': {
                    name: self.get_agent_dashboard(name) 
                    for name in self.agent_metrics.keys()
                },
                'llm': self.get_llm_dashboard(),
                'services': {
                    name: self.get_service_dashboard(name)
                    for name in self.service_metrics.keys()
                },
                'system_metrics_count': len(self.system_metrics),
                'total_metrics_tracked': (
                    sum(len(deque_) for deque_ in self.agent_metrics.values()) +
                    len(self.llm_metrics) +
                    sum(len(deque_) for deque_ in self.service_metrics.values()) +
                    len(self.system_metrics)
                )
            }
    
    def get_all_agent_dashboards(self) -> Dict[str, Dict[str, Any]]:
        """Get dashboard data for all agents."""
        with self._lock:
            return {
                name: self.get_agent_dashboard(name) 
                for name in self.agent_metrics.keys()
            }
    
    def _update_agent_stats(self, agent_name: str):
        """Update aggregated agent statistics."""
        # This could be expanded to maintain running averages, etc.
        pass
    
    def _update_llm_stats(self):
        """Update aggregated LLM statistics."""
        # This could be expanded to maintain running averages, etc.
        pass
    
    def export_metrics(self, format: str = "json") -> str:
        """
        Export all metrics in the specified format.
        
        Args:
            format: Export format ("json", "csv")
            
        Returns:
            Exported metrics as string
        """
        with self._lock:
            if format.lower() == "json":
                return json.dumps(self.get_system_dashboard(), indent=2)
            else:
                raise ValueError(f"Unsupported export format: {format}")
    
    def clear_metrics(self, older_than_hours: Optional[int] = None):
        """
        Clear metrics, optionally only those older than specified hours.
        
        Args:
            older_than_hours: If specified, only clear metrics older than this many hours
        """
        with self._lock:
            if older_than_hours is None:
                # Clear all metrics
                self.agent_metrics.clear()
                self.llm_metrics.clear()
                self.service_metrics.clear()
                self.system_metrics.clear()
            else:
                # Clear only old metrics
                cutoff_time = datetime.now() - timedelta(hours=older_than_hours)
                
                # Filter agent metrics
                for agent_name in self.agent_metrics:
                    filtered_metrics = deque([
                        m for m in self.agent_metrics[agent_name]
                        if datetime.fromisoformat(m['timestamp']) > cutoff_time
                    ], maxlen=self.max_history)
                    self.agent_metrics[agent_name] = filtered_metrics
                
                # Filter LLM metrics
                self.llm_metrics = deque([
                    m for m in self.llm_metrics
                    if datetime.fromisoformat(m['timestamp']) > cutoff_time
                ], maxlen=self.max_history)
                
                # Filter service metrics
                for service_name in self.service_metrics:
                    filtered_metrics = deque([
                        m for m in self.service_metrics[service_name]
                        if datetime.fromisoformat(m['timestamp']) > cutoff_time
                    ], maxlen=self.max_history)
                    self.service_metrics[service_name] = filtered_metrics
                
                # Filter system metrics
                self.system_metrics = deque([
                    m for m in self.system_metrics
                    if datetime.fromisoformat(m['timestamp']) > cutoff_time
                ], maxlen=self.max_history)


# Global metrics collector instance
_global_metrics_collector = None

def get_global_metrics_collector() -> MetricsCollector:
    """Get the global metrics collector instance."""
    global _global_metrics_collector
    if _global_metrics_collector is None:
        _global_metrics_collector = MetricsCollector()
    return _global_metrics_collector