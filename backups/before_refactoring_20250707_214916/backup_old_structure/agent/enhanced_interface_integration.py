
# Enhanced Interface System Integration
import json
from typing import Dict, Any, List, Optional
from pathlib import Path

class EnhancedInterface:
    """Enhanced interface system using activated features."""
    
    def __init__(self):
        self.interface_elements = {}
        self.templates = {}
    
    def generate_dashboard(self, data: Dict[str, Any]) -> str:
        """Generate a dashboard HTML."""
        html_template = """
<!DOCTYPE html>
<html>
<head>
    <title>Hephaestus Enhanced Dashboard</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .metric {{ background: #f5f5f5; padding: 15px; margin: 10px 0; border-radius: 5px; }}
        .status-pass {{ color: green; }}
        .status-fail {{ color: red; }}
        .status-warning {{ color: orange; }}
    </style>
</head>
<body>
    <h1>🚀 Hephaestus Enhanced Dashboard</h1>
    
    <div class="metric">
        <h2>System Status</h2>
        <p>Status: <span class="status-pass">✅ Active</span></p>
        <p>Features Activated: {features_count}</p>
        <p>Workflows Created: {workflows_count}</p>
    </div>
    
    <div class="metric">
        <h2>Recent Activity</h2>
        <ul>
            {recent_activity}
        </ul>
    </div>
    
    <div class="metric">
        <h2>Performance Metrics</h2>
        <p>Cache Hit Rate: {cache_hit_rate}%</p>
        <p>Validation Success Rate: {validation_rate}%</p>
    </div>
</body>
</html>
"""
        
        # Generate recent activity list
        recent_activity = ""
        if 'recent_activity' in data:
            for activity in data['recent_activity'][:5]:
                recent_activity += f"<li>{activity}</li>"
        
        return html_template.format(
            features_count=data.get('features_count', 0),
            workflows_count=data.get('workflows_count', 0),
            recent_activity=recent_activity,
            cache_hit_rate=data.get('cache_hit_rate', 0),
            validation_rate=data.get('validation_rate', 0)
        )
    
    def generate_api_documentation(self, endpoints: List[Dict[str, Any]]) -> str:
        """Generate API documentation."""
        doc_template = """
# Enhanced API Documentation

## Available Endpoints

{endpoints}

## Usage Examples

{examples}
"""
        
        endpoints_doc = ""
        for endpoint in endpoints:
            endpoints_doc += f"""
### {endpoint['name']}
- **Method**: {endpoint['method']}
- **Path**: {endpoint['path']}
- **Description**: {endpoint['description']}
"""
        
        examples_doc = """
```bash
# Example API calls
curl -X GET http://localhost:8000/health
curl -X POST http://localhost:8000/analyze -H "Content-Type: application/json" -d '{"target": "agent/"}'
```
"""
        
        return doc_template.format(
            endpoints=endpoints_doc,
            examples=examples_doc
        )
    
    def save_interface(self, content: str, file_path: str):
        """Save interface content to file."""
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)

# Global enhanced interface instance
enhanced_interface = EnhancedInterface()
