"""
Unified Dashboard - Central monitoring system for Hephaestus
"""

import json
import time
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from collections import defaultdict
import asyncio

from hephaestus.utils.metrics_collector import get_global_metrics_collector
from hephaestus.utils.config_manager import ConfigManager
from hephaestus.utils.logger_factory import LoggerFactory


@dataclass
class SystemHealth:
    """System health status."""
    overall_score: float  # 0-100
    status: str  # excellent, good, fair, poor, critical
    components: Dict[str, float]
    issues: List[str]
    recommendations: List[str]
    timestamp: datetime


@dataclass
class AgentStatus:
    """Individual agent status."""
    name: str
    status: str  # active, idle, error, offline
    last_activity: datetime
    success_rate: float
    avg_response_time: float
    total_operations: int
    current_load: float


class UnifiedDashboard:
    """
    Central monitoring dashboard for the entire Hephaestus system.
    
    Features:
    - Real-time system health monitoring
    - Agent performance tracking
    - Resource usage monitoring
    - Automated alerting
    - Historical trend analysis
    """
    
    def __init__(self):
        self.logger = LoggerFactory.get_component_logger("UnifiedDashboard")
        self.metrics = get_global_metrics_collector()
        
        # Dashboard state
        self.agents: Dict[str, AgentStatus] = {}
        self.system_health: Optional[SystemHealth] = None
        self.alerts: List[Dict[str, Any]] = []
        
        # Configuration
        self.refresh_interval = ConfigManager.get_config_value("monitoring.refresh_interval", 30)
        self.alert_thresholds = ConfigManager.get_config_value("monitoring.thresholds", {
            "error_rate": 0.1,
            "response_time": 5.0,
            "memory_usage": 0.8,
            "cpu_usage": 0.9
        })
        
        # Monitoring state
        self._running = False
        self._last_update = None
        
        self.logger.info("📊 Unified Dashboard initialized")
    
    async def start_monitoring(self):
        """Start real-time monitoring."""
        if self._running:
            return
        
        self._running = True
        self.logger.info("🚀 Starting unified monitoring")
        
        # Start monitoring loop
        asyncio.create_task(self._monitoring_loop())
    
    async def stop_monitoring(self):
        """Stop monitoring."""
        self._running = False
        self.logger.info("⏹️ Stopping unified monitoring")
    
    async def _monitoring_loop(self):
        """Main monitoring loop."""
        while self._running:
            try:
                await self._update_dashboard()
                await self._check_alerts()
                await asyncio.sleep(self.refresh_interval)
                
            except Exception as e:
                self.logger.error(f"Monitoring loop error: {e}")
                await asyncio.sleep(5)  # Brief pause on error
    
    async def _update_dashboard(self):
        """Update all dashboard data."""
        start_time = time.time()
        
        # Update agent statuses
        await self._update_agent_statuses()
        
        # Update system health
        await self._update_system_health()
        
        # Record update time
        self._last_update = datetime.now()
        update_duration = time.time() - start_time
        
        self.logger.debug(f"Dashboard updated in {update_duration:.2f}s")
    
    async def _update_agent_statuses(self):
        """Update status for all agents."""
        agent_metrics = self.metrics.get_all_agent_dashboards()
        
        for agent_name, metrics_data in agent_metrics.items():
            # Calculate agent status
            status = self._determine_agent_status(metrics_data)
            
            # Calculate success rate
            total_calls = metrics_data.get('total_calls', 0)
            successful_calls = metrics_data.get('successful_calls', 0)
            success_rate = (successful_calls / total_calls) if total_calls > 0 else 1.0
            
            # Calculate average response time
            avg_response_time = metrics_data.get('average_duration', 0.0)
            
            # Calculate current load (operations per minute)
            recent_ops = self._count_recent_operations(agent_name)
            current_load = recent_ops / 60.0  # ops per second
            
            self.agents[agent_name] = AgentStatus(
                name=agent_name,
                status=status,
                last_activity=datetime.now(),  # Would be from actual metrics
                success_rate=success_rate,
                avg_response_time=avg_response_time,
                total_operations=total_calls,
                current_load=current_load
            )
    
    async def _update_system_health(self):
        """Calculate overall system health."""
        if not self.agents:
            self.system_health = SystemHealth(
                overall_score=0.0,
                status="unknown",
                components={},
                issues=["No agents detected"],
                recommendations=["Start agent monitoring"],
                timestamp=datetime.now()
            )
            return
        
        # Calculate component scores
        components = {}
        issues = []
        recommendations = []
        
        # Agent health
        agent_scores = []
        for agent in self.agents.values():
            if agent.status == "error":
                score = 0.0
                issues.append(f"Agent {agent.name} is in error state")
            elif agent.status == "offline":
                score = 0.0
                issues.append(f"Agent {agent.name} is offline")
            elif agent.success_rate < 0.8:
                score = agent.success_rate * 100
                issues.append(f"Agent {agent.name} has low success rate: {agent.success_rate:.1%}")
            else:
                score = min(100, agent.success_rate * 100)
            
            agent_scores.append(score)
        
        components["agents"] = sum(agent_scores) / len(agent_scores) if agent_scores else 0
        
        # Memory health (simulated)
        memory_usage = self._get_memory_usage()
        if memory_usage > 0.9:
            components["memory"] = 20
            issues.append(f"High memory usage: {memory_usage:.1%}")
            recommendations.append("Consider reducing memory footprint")
        elif memory_usage > 0.7:
            components["memory"] = 60
            recommendations.append("Monitor memory usage")
        else:
            components["memory"] = 100
        
        # Performance health
        avg_response_times = [agent.avg_response_time for agent in self.agents.values()]
        if avg_response_times:
            max_response_time = max(avg_response_times)
            if max_response_time > 5.0:
                components["performance"] = 30
                issues.append(f"Slow response times detected: {max_response_time:.2f}s")
            elif max_response_time > 2.0:
                components["performance"] = 70
                recommendations.append("Monitor response times")
            else:
                components["performance"] = 100
        else:
            components["performance"] = 100
        
        # Calculate overall score
        overall_score = sum(components.values()) / len(components) if components else 0
        
        # Determine status
        if overall_score >= 90:
            status = "excellent"
        elif overall_score >= 75:
            status = "good"
        elif overall_score >= 50:
            status = "fair"
        elif overall_score >= 25:
            status = "poor"
        else:
            status = "critical"
        
        self.system_health = SystemHealth(
            overall_score=overall_score,
            status=status,
            components=components,
            issues=issues,
            recommendations=recommendations,
            timestamp=datetime.now()
        )
    
    async def _check_alerts(self):
        """Check for alert conditions."""
        new_alerts = []
        
        # Check agent alerts
        for agent in self.agents.values():
            if agent.status == "error":
                new_alerts.append({
                    "type": "agent_error",
                    "severity": "high",
                    "message": f"Agent {agent.name} is in error state",
                    "timestamp": datetime.now(),
                    "agent": agent.name
                })
            
            if agent.success_rate < self.alert_thresholds["error_rate"]:
                new_alerts.append({
                    "type": "low_success_rate",
                    "severity": "medium",
                    "message": f"Agent {agent.name} success rate: {agent.success_rate:.1%}",
                    "timestamp": datetime.now(),
                    "agent": agent.name
                })
            
            if agent.avg_response_time > self.alert_thresholds["response_time"]:
                new_alerts.append({
                    "type": "slow_response",
                    "severity": "medium",
                    "message": f"Agent {agent.name} slow response: {agent.avg_response_time:.2f}s",
                    "timestamp": datetime.now(),
                    "agent": agent.name
                })
        
        # Check system alerts
        if self.system_health and self.system_health.overall_score < 50:
            new_alerts.append({
                "type": "system_health",
                "severity": "high",
                "message": f"System health critical: {self.system_health.overall_score:.1f}%",
                "timestamp": datetime.now()
            })
        
        # Add new alerts
        for alert in new_alerts:
            # Avoid duplicate alerts
            if not any(
                existing["type"] == alert["type"] and 
                existing.get("agent") == alert.get("agent") and
                (datetime.now() - existing["timestamp"]).seconds < 300  # 5 min
                for existing in self.alerts
            ):
                self.alerts.append(alert)
                self.logger.warning(f"ALERT: {alert['message']}")
        
        # Clean old alerts (keep last 50)
        self.alerts = sorted(self.alerts, key=lambda x: x["timestamp"], reverse=True)[:50]
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get comprehensive dashboard data."""
        return {
            "system_health": asdict(self.system_health) if self.system_health else None,
            "agents": {name: asdict(agent) for name, agent in self.agents.items()},
            "alerts": self.alerts[-10:],  # Last 10 alerts
            "statistics": self._get_statistics(),
            "last_update": self._last_update.isoformat() if self._last_update else None,
            "monitoring_active": self._running
        }
    
    def get_agent_dashboard(self, agent_name: str) -> Dict[str, Any]:
        """Get detailed dashboard for specific agent."""
        if agent_name not in self.agents:
            return {"error": f"Agent {agent_name} not found"}
        
        agent = self.agents[agent_name]
        agent_metrics = self.metrics.get_agent_dashboard(agent_name)
        
        return {
            "agent_status": asdict(agent),
            "detailed_metrics": agent_metrics,
            "recent_alerts": [
                alert for alert in self.alerts
                if alert.get("agent") == agent_name
            ][-5:],  # Last 5 alerts for this agent
            "health_score": self._calculate_agent_health(agent),
            "recommendations": self._get_agent_recommendations(agent)
        }
    
    def get_system_summary(self) -> Dict[str, Any]:
        """Get concise system summary."""
        active_agents = len([a for a in self.agents.values() if a.status == "active"])
        error_agents = len([a for a in self.agents.values() if a.status == "error"])
        recent_alerts = len([a for a in self.alerts if (datetime.now() - a["timestamp"]).seconds < 3600])
        
        return {
            "overall_health": self.system_health.overall_score if self.system_health else 0,
            "status": self.system_health.status if self.system_health else "unknown",
            "total_agents": len(self.agents),
            "active_agents": active_agents,
            "error_agents": error_agents,
            "recent_alerts": recent_alerts,
            "last_update": self._last_update.isoformat() if self._last_update else None
        }
    
    def _determine_agent_status(self, metrics_data: Dict[str, Any]) -> str:
        """Determine agent status from metrics."""
        total_calls = metrics_data.get('total_calls', 0)
        successful_calls = metrics_data.get('successful_calls', 0)
        
        if total_calls == 0:
            return "idle"
        
        success_rate = successful_calls / total_calls
        if success_rate < 0.5:
            return "error"
        elif success_rate < 0.8:
            return "degraded"
        else:
            return "active"
    
    def _count_recent_operations(self, agent_name: str) -> int:
        """Count recent operations for an agent."""
        # This would query actual metrics for operations in last minute
        # For now, return a simulated value
        return len(self.agents) * 2  # Simulated
    
    def _get_memory_usage(self) -> float:
        """Get current memory usage."""
        # This would get actual memory usage
        # For now, return a simulated value
        import random
        return random.uniform(0.3, 0.8)
    
    def _get_statistics(self) -> Dict[str, Any]:
        """Get system statistics."""
        if not self.agents:
            return {}
        
        total_operations = sum(agent.total_operations for agent in self.agents.values())
        avg_success_rate = sum(agent.success_rate for agent in self.agents.values()) / len(self.agents)
        avg_response_time = sum(agent.avg_response_time for agent in self.agents.values()) / len(self.agents)
        
        return {
            "total_operations": total_operations,
            "average_success_rate": avg_success_rate,
            "average_response_time": avg_response_time,
            "uptime_hours": 24,  # Simulated
            "data_processed_mb": total_operations * 0.1,  # Estimated
        }
    
    def _calculate_agent_health(self, agent: AgentStatus) -> float:
        """Calculate health score for an agent."""
        if agent.status == "error":
            return 0.0
        elif agent.status == "offline":
            return 0.0
        
        # Base score from success rate
        health = agent.success_rate * 100
        
        # Penalize slow response times
        if agent.avg_response_time > 2.0:
            health *= 0.8
        elif agent.avg_response_time > 5.0:
            health *= 0.6
        
        # Penalize high load
        if agent.current_load > 10:
            health *= 0.9
        
        return min(100, max(0, health))
    
    def _get_agent_recommendations(self, agent: AgentStatus) -> List[str]:
        """Get recommendations for an agent."""
        recommendations = []
        
        if agent.success_rate < 0.8:
            recommendations.append("Investigate error patterns and improve error handling")
        
        if agent.avg_response_time > 2.0:
            recommendations.append("Optimize response time - check for bottlenecks")
        
        if agent.current_load > 10:
            recommendations.append("Consider load balancing or scaling")
        
        if agent.status == "idle":
            recommendations.append("Agent appears idle - check if tasks are being assigned")
        
        return recommendations


# Global dashboard instance
_dashboard = None

def get_unified_dashboard() -> UnifiedDashboard:
    """Get the global unified dashboard instance."""
    global _dashboard
    if _dashboard is None:
        _dashboard = UnifiedDashboard()
    return _dashboard