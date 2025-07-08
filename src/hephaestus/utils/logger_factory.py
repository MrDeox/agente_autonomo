"""
Logger Factory - Standardized logger creation and configuration
"""

import logging
import sys
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime


class LoggerFactory:
    """Factory for creating standardized loggers with consistent formatting."""
    
    _loggers: Dict[str, logging.Logger] = {}
    _configured = False
    
    @classmethod
    def _ensure_configured(cls):
        """Ensure logging is configured."""
        if not cls._configured:
            cls._configure_logging()
    
    @classmethod
    def _configure_logging(cls):
        """Configure basic logging settings."""
        # Create logs directory if it doesn't exist
        logs_dir = Path("data/logs")
        logs_dir.mkdir(parents=True, exist_ok=True)
        
        # Configure root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.INFO)
        
        # Clear existing handlers
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
        
        # Create formatters
        detailed_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        simple_formatter = logging.Formatter(
            '%(levelname)s - %(name)s - %(message)s'
        )
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(simple_formatter)
        root_logger.addHandler(console_handler)
        
        # File handler for all logs
        main_file_handler = logging.FileHandler(
            logs_dir / "hephaestus_main.log",
            encoding='utf-8'
        )
        main_file_handler.setLevel(logging.DEBUG)
        main_file_handler.setFormatter(detailed_formatter)
        root_logger.addHandler(main_file_handler)
        
        cls._configured = True
    
    @classmethod
    def get_component_logger(cls, 
                           component_name: str, 
                           parent_logger: Optional[logging.Logger] = None) -> logging.Logger:
        """
        Get a logger for a specific component with standardized naming.
        
        Args:
            component_name: Name of the component
            parent_logger: Optional parent logger
            
        Returns:
            Configured logger instance
        """
        cls._ensure_configured()
        
        # Normalize component name
        component_name = component_name.replace(' ', '_').lower()
        
        # Create hierarchical name if parent provided
        if parent_logger:
            logger_name = f"{parent_logger.name}.{component_name}"
        else:
            logger_name = f"hephaestus.{component_name}"
        
        # Return cached logger if exists
        if logger_name in cls._loggers:
            return cls._loggers[logger_name]
        
        # Create new logger
        logger = logging.getLogger(logger_name)
        
        # Set level based on component type
        if 'agent' in component_name or 'service' in component_name:
            logger.setLevel(logging.INFO)
        elif 'utils' in component_name or 'core' in component_name:
            logger.setLevel(logging.DEBUG)
        else:
            logger.setLevel(logging.INFO)
        
        # Cache and return
        cls._loggers[logger_name] = logger
        return logger
    
    @classmethod
    def get_agent_logger(cls, agent_name: str) -> logging.Logger:
        """
        Get a standardized logger for an agent.
        
        Args:
            agent_name: Name of the agent (e.g., "ArchitectAgent")
            
        Returns:
            Configured logger for the agent
        """
        # Normalize agent name
        if agent_name.endswith('Agent'):
            agent_name = agent_name[:-5]  # Remove 'Agent' suffix
        
        agent_name = agent_name.lower()
        logger_name = f"agents.{agent_name}"
        
        logger = cls.get_component_logger(logger_name)
        
        # Add agent-specific file handler if not already present
        cls._add_agent_file_handler(logger, agent_name)
        
        return logger
    
    @classmethod
    def get_service_logger(cls, service_name: str) -> logging.Logger:
        """
        Get a standardized logger for a service.
        
        Args:
            service_name: Name of the service
            
        Returns:
            Configured logger for the service
        """
        service_name = service_name.lower()
        logger_name = f"services.{service_name}"
        
        logger = cls.get_component_logger(logger_name)
        
        # Add service-specific file handler if not already present
        cls._add_service_file_handler(logger, service_name)
        
        return logger
    
    @classmethod
    def _add_agent_file_handler(cls, logger: logging.Logger, agent_name: str):
        """Add agent-specific file handler."""
        # Check if agent file handler already exists
        for handler in logger.handlers:
            if isinstance(handler, logging.FileHandler) and agent_name in handler.baseFilename:
                return
        
        # Create agent-specific log file
        logs_dir = Path("data/logs/agents")
        logs_dir.mkdir(parents=True, exist_ok=True)
        
        agent_file_handler = logging.FileHandler(
            logs_dir / f"{agent_name}_agent.log",
            encoding='utf-8'
        )
        agent_file_handler.setLevel(logging.DEBUG)
        
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        agent_file_handler.setFormatter(formatter)
        
        logger.addHandler(agent_file_handler)
    
    @classmethod
    def _add_service_file_handler(cls, logger: logging.Logger, service_name: str):
        """Add service-specific file handler."""
        # Check if service file handler already exists
        for handler in logger.handlers:
            if isinstance(handler, logging.FileHandler) and service_name in handler.baseFilename:
                return
        
        # Create service-specific log file
        logs_dir = Path("data/logs/services")
        logs_dir.mkdir(parents=True, exist_ok=True)
        
        service_file_handler = logging.FileHandler(
            logs_dir / f"{service_name}_service.log",
            encoding='utf-8'
        )
        service_file_handler.setLevel(logging.DEBUG)
        
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        service_file_handler.setFormatter(formatter)
        
        logger.addHandler(service_file_handler)
    
    @classmethod
    def set_global_level(cls, level: int):
        """Set logging level for all loggers."""
        for logger in cls._loggers.values():
            logger.setLevel(level)
    
    @classmethod
    def get_logger_stats(cls) -> Dict[str, Any]:
        """Get statistics about created loggers."""
        return {
            'total_loggers': len(cls._loggers),
            'logger_names': list(cls._loggers.keys()),
            'configured': cls._configured,
        }
    
    @classmethod
    def cleanup_old_logs(cls, days_to_keep: int = 7):
        """Clean up old log files."""
        logs_dir = Path("data/logs")
        if not logs_dir.exists():
            return
        
        cutoff_date = datetime.now().timestamp() - (days_to_keep * 24 * 60 * 60)
        
        for log_file in logs_dir.rglob("*.log"):
            if log_file.stat().st_mtime < cutoff_date:
                try:
                    log_file.unlink()
                except OSError:
                    pass  # File might be in use