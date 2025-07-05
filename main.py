import uvicorn
import sys
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('.'))

def main():
    """Função principal com validação de startup integrada"""
    # Import the FastAPI app instance from app.py
    from tools.app import app
    
    # Carregar configuração para validação
    from agent.config_loader import load_config
    config = load_config()
    
    # Validar startup
    from agent.utils.startup_validator import StartupValidator
    import logging
    
    logger = logging.getLogger("startup_validator")
    validator = StartupValidator(logger)
    
    if not validator.validate_all(config):
        print("❌ Validação de startup falhou. Verifique os logs para detalhes.")
        return
    
    # Run the FastAPI application using Uvicorn
    # host="0.0.0.0" makes the server accessible from any IP address
    # port=8000 is the default port for FastAPI applications
    print("🚀 Iniciando Hephaestus com Meta-Inteligência...")
    print("🧠 Sistema de evolução autônoma será ativado!")
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    main()
