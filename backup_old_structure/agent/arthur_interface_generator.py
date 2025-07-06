"""
Arthur Interface Generator - Cria interfaces personalizadas autogeradas
"""

import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass
from pathlib import Path

from agent.utils.llm_client import call_llm_api
from agent.utils.json_parser import parse_json_response


@dataclass
class InterfaceElement:
    """Elemento da interface gerada"""
    element_type: str
    title: str
    content: str
    action: Optional[str] = None
    priority: int = 5
    color_theme: str = "blue"
    icon: str = "🔧"


class ArthurInterfaceGenerator:
    """Gerador de interfaces personalizadas para o Arthur"""
    
    def __init__(self, config: Dict[str, Any], logger: logging.Logger):
        self.config = config
        self.logger = logger
        
        # Configurações da interface
        self.interface_themes = {
            "dark": {"bg": "#1a1a1a", "text": "#ffffff", "accent": "#00ff88"},
            "light": {"bg": "#ffffff", "text": "#000000", "accent": "#0066cc"},
            "matrix": {"bg": "#000000", "text": "#00ff00", "accent": "#ffff00"},
            "hacker": {"bg": "#000011", "text": "#33ff33", "accent": "#ff3333"}
        }
        
        # Preferências do Arthur
        self.arthur_preferences = {
            "preferred_theme": "dark",
            "interface_complexity": "advanced",
            "update_frequency": "realtime"
        }
        
        self.logger.info("🎨 ArthurInterfaceGenerator initialized!")
    
    def generate_personalized_interface(self, system_state: Dict[str, Any]) -> Dict[str, Any]:
        """Gera interface personalizada para o Arthur"""
        self.logger.info("🎨 Generating personalized interface for Arthur...")
        
        # Gerar elementos da interface
        elements = self._generate_interface_elements()
        
        # Criar layout personalizado
        layout = self._create_personalized_layout(elements)
        
        # Gerar código da interface
        interface_code = self._generate_interface_code(layout)
        
        interface_data = {
            "interface_id": f"arthur_interface_{int(datetime.now().timestamp())}",
            "generated_at": datetime.now().isoformat(),
            "elements": elements,
            "layout": layout,
            "interface_code": interface_code,
            "system_state_snapshot": system_state
        }
        
        self.logger.info(f"✨ Interface generated with {len(elements)} elements")
        return interface_data
    
    def _generate_interface_elements(self) -> List[InterfaceElement]:
        """Gera elementos da interface"""
        elements = []
        
        # Dashboard principal
        elements.append(InterfaceElement(
            element_type="display",
            title="🚀 Hephaestus Command Center",
            content="Master control interface for your autonomous AI system",
            priority=10,
            color_theme="matrix",
            icon="🧠"
        ))
        
        # Turbo Evolution
        elements.append(InterfaceElement(
            element_type="button",
            title="🔥 Turbo Evolution",
            content="Activate maximum parallel evolution mode",
            action="enable_turbo_mode",
            priority=8,
            color_theme="red",
            icon="⚡"
        ))
        
        # Async Orchestration
        elements.append(InterfaceElement(
            element_type="button",
            title="🚀 Async Orchestration",
            content="Launch parallel multi-agent operations",
            action="start_async_evolution",
            priority=8,
            color_theme="blue",
            icon="🎯"
        ))
        
        # Deep Reflection
        elements.append(InterfaceElement(
            element_type="button",
            title="�� Deep Self-Reflection",
            content="Trigger advanced introspection",
            action="perform_deep_reflection",
            priority=6,
            color_theme="yellow",
            icon="🧠"
        ))
        
        # System Chat
        elements.append(InterfaceElement(
            element_type="input",
            title="💬 Direct System Chat",
            content="Chat directly with your AI system",
            action="chat_with_system",
            priority=7,
            color_theme="cyan",
            icon="💭"
        ))
        
        return elements
    
    def _create_personalized_layout(self, elements: List[InterfaceElement]) -> Dict[str, Any]:
        """Cria layout personalizado"""
        sorted_elements = sorted(elements, key=lambda e: e.priority, reverse=True)
        
        layout = {
            "layout_type": "advanced_dashboard",
            "theme": self.arthur_preferences["preferred_theme"],
            "sections": {
                "header": [e for e in sorted_elements if e.element_type == "display"],
                "controls": [e for e in sorted_elements if e.element_type == "button"],
                "chat": [e for e in sorted_elements if e.element_type == "input"]
            },
            "responsive_design": True
        }
        
        return layout
    
    def _generate_interface_code(self, layout: Dict[str, Any]) -> str:
        """Gera código HTML da interface"""
        
        return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Arthur's Hephaestus Command Center</title>
    <style>
        body {{
            font-family: 'Courier New', monospace;
            background: #1a1a1a;
            color: #ffffff;
            margin: 0;
            padding: 20px;
        }}
        
        .header {{
            text-align: center;
            padding: 20px;
            background: linear-gradient(45deg, #00ff88, #1a1a1a);
            border-radius: 10px;
            margin-bottom: 20px;
        }}
        
        .controls {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }}
        
        .btn {{
            padding: 15px 20px;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            cursor: pointer;
            transition: all 0.3s;
            color: #1a1a1a;
            font-weight: bold;
        }}
        
        .btn:hover {{
            transform: translateY(-2px);
            box-shadow: 0 6px 12px rgba(0,0,0,0.4);
        }}
        
        .turbo-btn {{ background: #ff3333; }}
        .async-btn {{ background: #3366ff; }}
        .reflect-btn {{ background: #ffff33; }}
        
        .chat-section {{
            background: rgba(255,255,255,0.05);
            border: 1px solid #00ff88;
            border-radius: 10px;
            padding: 20px;
        }}
        
        .chat-input {{
            width: 100%;
            padding: 15px;
            background: rgba(255,255,255,0.1);
            border: 1px solid #00ff88;
            border-radius: 8px;
            color: #ffffff;
            font-size: 16px;
        }}
        
        .status {{
            position: fixed;
            top: 20px;
            right: 20px;
            background: #00ff00;
            color: #000;
            padding: 10px 20px;
            border-radius: 20px;
            font-weight: bold;
        }}
    </style>
</head>
<body>
    <div class="status" id="system-status">ACTIVE</div>
    
    <div class="header">
        <h1>🚀 Arthur's Hephaestus Command Center</h1>
        <p>Master control interface for your autonomous AI system</p>
    </div>
    
    <div class="controls">
        <button class="btn turbo-btn" onclick="enableTurboMode()">
            🔥 Turbo Evolution<br>
            <small>Activate maximum parallel evolution mode</small>
        </button>
        
        <button class="btn async-btn" onclick="startAsyncEvolution()">
            🚀 Async Orchestration<br>
            <small>Launch parallel multi-agent operations</small>
        </button>
        
        <button class="btn reflect-btn" onclick="performDeepReflection()">
            🔍 Deep Self-Reflection<br>
            <small>Trigger advanced introspection</small>
        </button>
    </div>
    
    <div class="chat-section">
        <h2>💬 Direct System Chat</h2>
        <div id="chat-messages" style="height: 200px; overflow-y: auto; margin-bottom: 15px; padding: 10px; background: rgba(0,0,0,0.3); border-radius: 5px;"></div>
        <input type="text" class="chat-input" id="chat-input" placeholder="Chat with your AI system...">
    </div>
    
    <script>
        function enableTurboMode() {{
            fetch('/api/enable_turbo_mode', {{method: 'POST'}})
                .then(response => response.json())
                .then(data => {{
                    showNotification('🔥 Turbo Mode Activated!');
                    document.getElementById('system-status').textContent = 'TURBO';
                }})
                .catch(error => showNotification('Error: ' + error));
        }}
        
        function startAsyncEvolution() {{
            const objective = prompt('Enter evolution objective:');
            if (objective) {{
                fetch('/api/start_async_evolution', {{
                    method: 'POST',
                    headers: {{'Content-Type': 'application/json'}},
                    body: JSON.stringify({{objective: objective}})
                }})
                .then(response => response.json())
                .then(data => {{
                    showNotification('🚀 Async Evolution Started!');
                    addChatMessage('System', 'Async evolution initiated for: ' + objective);
                }})
                .catch(error => showNotification('Error: ' + error));
            }}
        }}
        
        function performDeepReflection() {{
            fetch('/api/deep_reflection', {{method: 'POST'}})
                .then(response => response.json())
                .then(data => {{
                    showNotification('🔍 Deep Reflection Complete!');
                    addChatMessage('System', 'Deep self-reflection performed. New insights generated.');
                }})
                .catch(error => showNotification('Error: ' + error));
        }}
        
        function showNotification(message) {{
            const notification = document.createElement('div');
            notification.textContent = message;
            notification.style.cssText = `
                position: fixed;
                top: 80px;
                right: 20px;
                background: #00ff88;
                color: #000;
                padding: 15px 25px;
                border-radius: 8px;
                font-weight: bold;
                z-index: 1000;
            `;
            document.body.appendChild(notification);
            
            setTimeout(() => {{
                notification.remove();
            }}, 3000);
        }}
        
        function addChatMessage(sender, message) {{
            const chatMessages = document.getElementById('chat-messages');
            const messageElement = document.createElement('div');
            messageElement.innerHTML = `
                <div style="margin-bottom: 10px;">
                    <strong>${{sender}}:</strong> ${{message}}
                    <small style="color: #666; margin-left: 10px;">${{new Date().toLocaleTimeString()}}</small>
                </div>
            `;
            chatMessages.appendChild(messageElement);
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }}
        
        // Chat input handling
        document.getElementById('chat-input').addEventListener('keypress', function(e) {{
            if (e.key === 'Enter') {{
                const message = e.target.value;
                if (message.trim()) {{
                    addChatMessage('Arthur', message);
                    e.target.value = '';
                    
                    // Simular resposta do sistema
                    setTimeout(() => {{
                        addChatMessage('Hephaestus', 'Processing your request...');
                    }}, 1000);
                }}
            }}
        }});
        
        // Inicialização
        window.onload = function() {{
            addChatMessage('Hephaestus', 'Welcome back, Arthur! Your AI system is ready for command.');
            showNotification('🚀 Interface Generated Successfully!');
        }};
    </script>
</body>
</html>
"""
    
    def save_interface_to_file(self, interface_data: Dict[str, Any], filename: str = None):
        """Salva interface gerada em arquivo"""
        if not filename:
            filename = f"arthur_interface_{int(datetime.now().timestamp())}.html"
        
        filepath = Path("generated_interfaces") / filename
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(interface_data["interface_code"])
        
        self.logger.info(f"✅ Interface saved to {filepath}")
        return str(filepath)
