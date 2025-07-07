"""
Arthur Interface Generator - Gerador de interfaces para Arthur
"""

import logging
from typing import Dict, Any, List
from datetime import datetime

class ArthurInterfaceGenerator:
    """Gerador de interfaces especializadas para Arthur."""
    
    def __init__(self, config: Dict, logger: logging.Logger):
        self.config = config
        self.logger = logger
        self.interfaces = {}
        self.active_sessions = []
        
        self.logger.info("🎨 ArthurInterfaceGenerator inicializado")
    
    def generate_interface(self, interface_type: str, specs: Dict) -> Dict[str, Any]:
        """Gerar interface baseada no tipo e especificações."""
        try:
            interface_id = f"{interface_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            interface = {
                'id': interface_id,
                'type': interface_type,
                'specs': specs,
                'created_at': datetime.now(),
                'status': 'active',
                'components': self._generate_components(interface_type, specs)
            }
            
            self.interfaces[interface_id] = interface
            self.logger.info(f"🎨 Interface {interface_type} gerada: {interface_id}")
            
            return interface
            
        except Exception as e:
            self.logger.error(f"❌ Erro gerando interface {interface_type}: {e}")
            return {}
    
    def _generate_components(self, interface_type: str, specs: Dict) -> List[Dict]:
        """Gerar componentes da interface."""
        components = []
        
        if interface_type == "dashboard":
            components = [
                {'type': 'header', 'title': specs.get('title', 'Hephaestus Dashboard')},
                {'type': 'metrics', 'data_source': 'system_metrics'},
                {'type': 'logs', 'max_lines': specs.get('max_logs', 100)},
                {'type': 'controls', 'actions': ['start', 'stop', 'restart']}
            ]
        elif interface_type == "trading":
            components = [
                {'type': 'market_data', 'symbols': specs.get('symbols', [])},
                {'type': 'portfolio', 'balance_display': True},
                {'type': 'trade_history', 'max_records': specs.get('max_trades', 50)},
                {'type': 'risk_controls', 'limits': specs.get('risk_limits', {})}
            ]
        elif interface_type == "agent_monitor":
            components = [
                {'type': 'agent_status', 'agents': specs.get('agents', [])},
                {'type': 'task_queue', 'max_tasks': specs.get('max_tasks', 20)},
                {'type': 'performance_chart', 'timeframe': specs.get('timeframe', '1h')}
            ]
        
        return components
    
    def get_interface(self, interface_id: str) -> Dict[str, Any]:
        """Obter interface por ID."""
        return self.interfaces.get(interface_id, {})
    
    def list_interfaces(self) -> List[Dict]:
        """Listar todas as interfaces."""
        return list(self.interfaces.values())
    
    def update_interface(self, interface_id: str, updates: Dict) -> bool:
        """Atualizar interface existente."""
        if interface_id in self.interfaces:
            self.interfaces[interface_id].update(updates)
            self.logger.info(f"🔄 Interface {interface_id} atualizada")
            return True
        return False
    
    def remove_interface(self, interface_id: str) -> bool:
        """Remover interface."""
        if interface_id in self.interfaces:
            del self.interfaces[interface_id]
            self.logger.info(f"🗑️ Interface {interface_id} removida")
            return True
        return False
    
    def start_session(self, user_id: str, interface_id: str) -> str:
        """Iniciar sessão de interface."""
        session_id = f"session_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        session = {
            'id': session_id,
            'user_id': user_id,
            'interface_id': interface_id,
            'started_at': datetime.now(),
            'last_activity': datetime.now(),
            'status': 'active'
        }
        
        self.active_sessions.append(session)
        self.logger.info(f"🔐 Sessão iniciada: {session_id}")
        
        return session_id
    
    def end_session(self, session_id: str) -> bool:
        """Encerrar sessão."""
        for session in self.active_sessions:
            if session['id'] == session_id:
                session['status'] = 'ended'
                session['ended_at'] = datetime.now()
                self.logger.info(f"🔒 Sessão encerrada: {session_id}")
                return True
        return False
    
    def get_active_sessions(self) -> List[Dict]:
        """Obter sessões ativas."""
        return [s for s in self.active_sessions if s['status'] == 'active']
    
    def generate_adaptive_interface(self, user_preferences: Dict, system_state: Dict) -> Dict[str, Any]:
        """Gerar interface adaptativa baseada nas preferências do usuário e estado do sistema."""
        interface_type = "adaptive_dashboard"
        
        specs = {
            'title': f"Hephaestus - {user_preferences.get('theme', 'Default')}",
            'layout': user_preferences.get('layout', 'grid'),
            'widgets': self._select_widgets(user_preferences, system_state),
            'theme': user_preferences.get('theme', 'dark'),
            'auto_refresh': user_preferences.get('auto_refresh', 30)
        }
        
        return self.generate_interface(interface_type, specs)
    
    def _select_widgets(self, preferences: Dict, system_state: Dict) -> List[str]:
        """Selecionar widgets baseado nas preferências e estado do sistema."""
        available_widgets = [
            'system_health', 'agent_status', 'performance_metrics',
            'trading_dashboard', 'log_viewer', 'task_monitor',
            'memory_usage', 'network_activity', 'error_alerts'
        ]
        
        # Priorizar widgets baseado no estado do sistema
        priority_widgets = []
        
        if system_state.get('trading_active'):
            priority_widgets.extend(['trading_dashboard', 'performance_metrics'])
        
        if system_state.get('errors_detected'):
            priority_widgets.extend(['error_alerts', 'log_viewer'])
        
        if system_state.get('high_cpu_usage'):
            priority_widgets.extend(['system_health', 'memory_usage'])
        
        # Combinar com preferências do usuário
        user_widgets = preferences.get('preferred_widgets', available_widgets[:6])
        
        # Mesclar e remover duplicatas
        selected = list(dict.fromkeys(priority_widgets + user_widgets))
        
        return selected[:preferences.get('max_widgets', 8)]