"""
Simple Dashboard Server - Web interface for monitoring and validation
"""

import json
import asyncio
from datetime import datetime
from typing import Dict, Any

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import uvicorn

from hephaestus.monitoring import get_unified_dashboard
from hephaestus.validation import get_unified_validator
from hephaestus.utils.logger_factory import LoggerFactory


class DashboardServer:
    """Simple web dashboard for Hephaestus monitoring and validation."""
    
    def __init__(self, host: str = "localhost", port: int = 8080):
        self.host = host
        self.port = port
        self.app = FastAPI(title="Hephaestus Dashboard")
        self.logger = LoggerFactory.get_component_logger("DashboardServer")
        
        # Components
        self.dashboard = get_unified_dashboard()
        self.validator = get_unified_validator()
        
        # WebSocket connections
        self.connections: list[WebSocket] = []
        
        # Setup routes
        self._setup_routes()
        
        self.logger.info(f"📊 Dashboard server initialized on {host}:{port}")
    
    def _setup_routes(self):
        """Setup FastAPI routes."""
        
        @self.app.get("/")
        async def root():
            """Serve the main dashboard page."""
            return HTMLResponse(self._get_dashboard_html())
        
        @self.app.get("/api/system/health")
        async def system_health():
            """Get system health summary."""
            return self.dashboard.get_system_summary()
        
        @self.app.get("/api/system/dashboard")
        async def system_dashboard():
            """Get full dashboard data."""
            return self.dashboard.get_dashboard_data()
        
        @self.app.get("/api/agents/{agent_name}")
        async def agent_details(agent_name: str):
            """Get detailed agent information."""
            return self.dashboard.get_agent_dashboard(agent_name)
        
        @self.app.get("/api/validation/summary")
        async def validation_summary():
            """Get validation summary."""
            return self.validator.get_validation_summary()
        
        @self.app.get("/api/validation/history")
        async def validation_history():
            """Get validation history."""
            return self.validator.get_validation_history()
        
        @self.app.post("/api/validation/run/{scope}")
        async def run_validation(scope: str = "full"):
            """Run validation suite."""
            result = await self.validator.validate_system(scope)
            return result.to_dict()
        
        @self.app.websocket("/ws")
        async def websocket_endpoint(websocket: WebSocket):
            """WebSocket endpoint for real-time updates."""
            await websocket.accept()
            self.connections.append(websocket)
            
            try:
                while True:
                    # Send real-time updates
                    data = {
                        "type": "update",
                        "timestamp": datetime.now().isoformat(),
                        "system_health": self.dashboard.get_system_summary(),
                        "validation": self.validator.get_validation_summary()
                    }
                    
                    await websocket.send_text(json.dumps(data))
                    await asyncio.sleep(5)  # Update every 5 seconds
                    
            except WebSocketDisconnect:
                self.connections.remove(websocket)
    
    def _get_dashboard_html(self) -> str:
        """Generate simple HTML dashboard."""
        return """
<!DOCTYPE html>
<html>
<head>
    <title>Hephaestus Dashboard</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
            text-align: center;
        }
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }
        .card {
            background: white;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .status-excellent { border-left: 5px solid #4CAF50; }
        .status-good { border-left: 5px solid #8BC34A; }
        .status-fair { border-left: 5px solid #FF9800; }
        .status-poor { border-left: 5px solid #FF5722; }
        .status-critical { border-left: 5px solid #F44336; }
        .metric {
            display: flex;
            justify-content: space-between;
            margin: 10px 0;
            padding: 10px;
            background: #f8f9fa;
            border-radius: 5px;
        }
        .metric-value {
            font-weight: bold;
            font-size: 1.2em;
        }
        .btn {
            background: #667eea;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            margin: 5px;
        }
        .btn:hover {
            background: #5a6fd8;
        }
        .alerts {
            max-height: 300px;
            overflow-y: auto;
        }
        .alert {
            padding: 10px;
            margin: 5px 0;
            border-radius: 5px;
            border-left: 4px solid;
        }
        .alert-high { border-color: #F44336; background: #ffebee; }
        .alert-medium { border-color: #FF9800; background: #fff3e0; }
        .alert-low { border-color: #2196F3; background: #e3f2fd; }
        .status-indicator {
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-right: 8px;
        }
        .status-active { background: #4CAF50; }
        .status-error { background: #F44336; }
        .status-idle { background: #FFC107; }
        .status-offline { background: #9E9E9E; }
        #connection-status {
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 10px;
            border-radius: 5px;
            color: white;
            font-weight: bold;
        }
        .connected { background: #4CAF50; }
        .disconnected { background: #F44336; }
    </style>
</head>
<body>
    <div id="connection-status" class="disconnected">Disconnected</div>
    
    <div class="container">
        <div class="header">
            <h1>🔥 Hephaestus Dashboard</h1>
            <p>Real-time monitoring and validation for the autonomous agent system</p>
        </div>
        
        <div class="grid">
            <div class="card" id="system-health">
                <h3>System Health</h3>
                <div class="metric">
                    <span>Overall Score:</span>
                    <span class="metric-value" id="health-score">Loading...</span>
                </div>
                <div class="metric">
                    <span>Status:</span>
                    <span class="metric-value" id="health-status">Loading...</span>
                </div>
                <div class="metric">
                    <span>Active Agents:</span>
                    <span class="metric-value" id="active-agents">Loading...</span>
                </div>
                <div class="metric">
                    <span>Recent Alerts:</span>
                    <span class="metric-value" id="recent-alerts">Loading...</span>
                </div>
            </div>
            
            <div class="card">
                <h3>Validation Status</h3>
                <div class="metric">
                    <span>Last Validation:</span>
                    <span class="metric-value" id="last-validation">Loading...</span>
                </div>
                <div class="metric">
                    <span>Status:</span>
                    <span class="metric-value" id="validation-status">Loading...</span>
                </div>
                <div class="metric">
                    <span>Critical Issues:</span>
                    <span class="metric-value" id="critical-issues">Loading...</span>
                </div>
                <button class="btn" onclick="runValidation('full')">Run Full Validation</button>
                <button class="btn" onclick="runValidation('security')">Security Check</button>
            </div>
            
            <div class="card">
                <h3>Quick Actions</h3>
                <button class="btn" onclick="refreshDashboard()">Refresh Dashboard</button>
                <button class="btn" onclick="downloadReport()">Download Report</button>
                <button class="btn" onclick="viewLogs()">View Logs</button>
                <button class="btn" onclick="runValidation('agents')">Validate Agents</button>
            </div>
        </div>
        
        <div class="grid">
            <div class="card">
                <h3>Active Agents</h3>
                <div id="agents-list">Loading...</div>
            </div>
            
            <div class="card">
                <h3>Recent Alerts</h3>
                <div class="alerts" id="alerts-list">Loading...</div>
            </div>
        </div>
    </div>

    <script>
        let ws = null;
        let reconnectInterval = null;
        
        function connectWebSocket() {
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            const wsUrl = `${protocol}//${window.location.host}/ws`;
            
            ws = new WebSocket(wsUrl);
            
            ws.onopen = function() {
                document.getElementById('connection-status').textContent = 'Connected';
                document.getElementById('connection-status').className = 'connected';
                if (reconnectInterval) {
                    clearInterval(reconnectInterval);
                    reconnectInterval = null;
                }
            };
            
            ws.onmessage = function(event) {
                const data = JSON.parse(event.data);
                updateDashboard(data);
            };
            
            ws.onclose = function() {
                document.getElementById('connection-status').textContent = 'Disconnected';
                document.getElementById('connection-status').className = 'disconnected';
                
                if (!reconnectInterval) {
                    reconnectInterval = setInterval(connectWebSocket, 5000);
                }
            };
            
            ws.onerror = function(error) {
                console.error('WebSocket error:', error);
            };
        }
        
        function updateDashboard(data) {
            if (data.system_health) {
                const health = data.system_health;
                document.getElementById('health-score').textContent = health.overall_health.toFixed(1) + '%';
                document.getElementById('health-status').textContent = health.status;
                document.getElementById('active-agents').textContent = health.active_agents + '/' + health.total_agents;
                document.getElementById('recent-alerts').textContent = health.recent_alerts;
                
                // Update system health card class
                const healthCard = document.getElementById('system-health');
                healthCard.className = 'card status-' + health.status;
            }
            
            if (data.validation) {
                const validation = data.validation;
                document.getElementById('last-validation').textContent = validation.status === 'no_validation' ? 'Never' : 'Recently';
                document.getElementById('validation-status').textContent = validation.status;
                document.getElementById('critical-issues').textContent = validation.critical_issues || 0;
            }
        }
        
        async function refreshDashboard() {
            try {
                const response = await fetch('/api/system/dashboard');
                const data = await response.json();
                
                // Update agents list
                const agentsList = document.getElementById('agents-list');
                if (data.agents) {
                    agentsList.innerHTML = Object.entries(data.agents).map(([name, agent]) => `
                        <div class="metric">
                            <span><span class="status-indicator status-${agent.status}"></span>${name}</span>
                            <span>${(agent.success_rate * 100).toFixed(1)}%</span>
                        </div>
                    `).join('');
                }
                
                // Update alerts
                const alertsList = document.getElementById('alerts-list');
                if (data.alerts) {
                    alertsList.innerHTML = data.alerts.map(alert => `
                        <div class="alert alert-${alert.severity}">
                            <strong>${alert.type}:</strong> ${alert.message}
                        </div>
                    `).join('') || '<p>No recent alerts</p>';
                }
                
            } catch (error) {
                console.error('Error refreshing dashboard:', error);
            }
        }
        
        async function runValidation(scope) {
            try {
                document.getElementById('validation-status').textContent = 'Running...';
                const response = await fetch(`/api/validation/run/${scope}`, { method: 'POST' });
                const result = await response.json();
                
                document.getElementById('validation-status').textContent = result.overall_status;
                document.getElementById('critical-issues').textContent = result.results.filter(r => r.status === 'failed' && r.severity === 'critical').length;
                
                alert(`Validation completed: ${result.overall_status}\\n${result.passed} passed, ${result.failed} failed, ${result.warnings} warnings`);
                
            } catch (error) {
                console.error('Error running validation:', error);
                alert('Error running validation');
            }
        }
        
        function downloadReport() {
            alert('Report download feature coming soon!');
        }
        
        function viewLogs() {
            alert('Log viewer coming soon!');
        }
        
        // Initialize
        connectWebSocket();
        refreshDashboard();
        
        // Refresh every 30 seconds as fallback
        setInterval(refreshDashboard, 30000);
    </script>
</body>
</html>
        """
    
    async def start(self):
        """Start the dashboard server."""
        # Start monitoring
        await self.dashboard.start_monitoring()
        
        self.logger.info(f"🚀 Starting dashboard server on http://{self.host}:{self.port}")
        
        config = uvicorn.Config(
            app=self.app,
            host=self.host,
            port=self.port,
            log_level="info"
        )
        server = uvicorn.Server(config)
        await server.serve()
    
    async def broadcast_update(self, data: Dict[str, Any]):
        """Broadcast update to all connected clients."""
        if self.connections:
            message = json.dumps(data)
            for connection in self.connections.copy():
                try:
                    await connection.send_text(message)
                except Exception:
                    self.connections.remove(connection)


# Convenience function to start dashboard
async def start_dashboard(host: str = "localhost", port: int = 8080):
    """Start the dashboard server."""
    server = DashboardServer(host, port)
    await server.start()


if __name__ == "__main__":
    asyncio.run(start_dashboard())