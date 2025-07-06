
# Enhanced Monitoring System Integration
import logging
import time
from typing import Dict, Any, Optional
from datetime import datetime

class EnhancedMonitor:
    """Enhanced monitoring system using activated features."""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger(__name__)
        self.metrics = {}
        self.alerts = []
    
    def track_metric(self, name: str, value: Any, category: str = "general"):
        """Track a metric."""
        if category not in self.metrics:
            self.metrics[category] = {}
        
        if name not in self.metrics[category]:
            self.metrics[category][name] = []
        
        self.metrics[category][name].append({
            'value': value,
            'timestamp': datetime.now().isoformat()
        })
        
        # Keep only last 100 values
        if len(self.metrics[category][name]) > 100:
            self.metrics[category][name] = self.metrics[category][name][-100:]
    
    def add_alert(self, level: str, message: str, context: Dict[str, Any] = None):
        """Add an alert."""
        alert = {
            'level': level,
            'message': message,
            'context': context or {},
            'timestamp': datetime.now().isoformat()
        }
        self.alerts.append(alert)
        
        # Log alert
        if level == 'error':
            self.logger.error(f"🚨 {message}")
        elif level == 'warning':
            self.logger.warning(f"⚠️ {message}")
        else:
            self.logger.info(f"ℹ️ {message}")
    
    def get_metrics(self, category: str = None) -> Dict[str, Any]:
        """Get metrics."""
        if category:
            return self.metrics.get(category, {})
        return self.metrics
    
    def get_alerts(self, level: str = None) -> list:
        """Get alerts."""
        if level:
            return [alert for alert in self.alerts if alert['level'] == level]
        return self.alerts
    
    def clear_alerts(self):
        """Clear all alerts."""
        self.alerts = []

# Global enhanced monitor instance
enhanced_monitor = EnhancedMonitor()
