"""
Melhorador de experiência do usuário
"""
import time
from typing import Any, Dict, List

class UXEnhancer:
    """Melhorador de experiência do usuário"""
    
    def __init__(self):
        pass
    
    def show_progress(self, tasks: List[str], title: str = "Processando"):
        """Mostrar progresso visual"""
        print(f"🔄 {title}")
        for i, task in enumerate(tasks, 1):
            print(f"   {i}/{len(tasks)} - {task}")
            time.sleep(0.1)  # Simular trabalho
        print("✅ Concluído!")
    
    def show_status(self, data: Dict[str, Any]):
        """Mostrar status do sistema"""
        print("📊 Status do Sistema:")
        for component, info in data.items():
            status = "✅ OK" if info.get("ok", True) else "❌ Erro"
            print(f"   {component}: {status}")
    
    def show_success_message(self, message: str):
        """Mostrar mensagem de sucesso"""
        print(f"✅ {message}")
    
    def show_error_message(self, message: str):
        """Mostrar mensagem de erro"""
        print(f"❌ {message}")

    def format_welcome_message(self, name: str) -> str:
        """Format a personalized welcome message
        
        Args:
            name: The name to include in the welcome message
            
        Returns:
            A formatted welcome string
        """
        return f"✨ Welcome, {name}! Hephaestus is ready to assist you with your AI needs. ✨"