"""
🔑 API Key Manager com Redundância
Sistema inteligente de gerenciamento de múltiplas chaves API com fallover automático
"""

import os
import json
import random
import time
import logging
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from dotenv import load_dotenv

# Ensure .env is loaded
load_dotenv()

@dataclass
class APIKey:
    """Representa uma chave API com metadados de saúde"""
    key: str
    provider: str  # "openrouter", "gemini"
    name: str  # nome identificador
    is_active: bool = True
    failure_count: int = 0
    last_success: Optional[datetime] = None
    last_failure: Optional[datetime] = None
    rate_limit_reset: Optional[datetime] = None
    daily_usage: int = 0
    priority: int = 1  # 1=alta, 2=média, 3=baixa
    
    def mark_success(self):
        """Marca uso bem-sucedido da chave"""
        self.last_success = datetime.now()
        self.failure_count = 0
        self.daily_usage += 1
        self.is_active = True
    
    def mark_failure(self, reason: str = ""):
        """Marca falha na chave"""
        self.last_failure = datetime.now()
        self.failure_count += 1
        
        # Desativa temporariamente após muitas falhas
        if self.failure_count >= 3:
            self.is_active = False
            logging.warning(f"🔑 Key {self.name} temporarily disabled after {self.failure_count} failures")
    
    def mark_rate_limit(self, reset_time: Optional[datetime] = None):
        """Marca rate limit atingido"""
        self.rate_limit_reset = reset_time or (datetime.now() + timedelta(minutes=10))
        self.is_active = False
        logging.warning(f"🔑 Key {self.name} rate limited until {self.rate_limit_reset}")
    
    def is_available(self) -> bool:
        """Verifica se a chave está disponível para uso"""
        if not self.is_active:
            # Reativa chaves após cooldown
            if self.rate_limit_reset and datetime.now() > self.rate_limit_reset:
                self.is_active = True
                self.rate_limit_reset = None
                logging.info(f"🔑 Key {self.name} reactivated after rate limit cooldown")
            elif self.last_failure and datetime.now() > (self.last_failure + timedelta(minutes=30)):
                self.is_active = True
                self.failure_count = 0
                logging.info(f"🔑 Key {self.name} reactivated after failure cooldown")
        
        return self.is_active
    
    def to_dict(self) -> Dict:
        """Converte para dict (sem expor a chave real)"""
        return {
            "provider": self.provider,
            "name": self.name,
            "is_active": self.is_active,
            "failure_count": self.failure_count,
            "last_success": self.last_success.isoformat() if self.last_success else None,
            "last_failure": self.last_failure.isoformat() if self.last_failure else None,
            "rate_limit_reset": self.rate_limit_reset.isoformat() if self.rate_limit_reset else None,
            "daily_usage": self.daily_usage,
            "priority": self.priority
        }

class APIKeyManager:
    """
    🔑 Gerenciador de Chaves API com Redundância Inteligente
    
    Features:
    - Múltiplas chaves por provedor
    - Fallback automático
    - Health checking
    - Rate limit handling
    - Load balancing
    - Persistent state
    """
    
    def __init__(self, config_path: str = "data/api_keys_config.json"):
        self.config_path = Path(config_path)
        self.logger = logging.getLogger("APIKeyManager")
        self.keys: Dict[str, List[APIKey]] = {"openrouter": [], "gemini": []}
        self.stats = {
            "total_calls": 0,
            "successful_calls": 0,
            "failed_calls": 0,
            "fallback_usage": 0
        }
        
        # Load configuration
        self._load_config()
        self._load_keys_from_env()
        
        self.logger.info(f"🔑 APIKeyManager initialized with {self.get_total_active_keys()} active keys")
    
    def _load_config(self):
        """Carrega configuração salva"""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    data = json.load(f)
                    self.stats = data.get("stats", self.stats)
                    
                    # Reconstruct keys (without actual key values)
                    for provider, keys_data in data.get("keys", {}).items():
                        for key_data in keys_data:
                            # Placeholder - actual keys loaded from env
                            pass
                            
            except Exception as e:
                self.logger.warning(f"Could not load config: {e}")
    
    def _load_keys_from_env(self):
        """Carrega chaves do ambiente (.env)"""
        # OpenRouter keys
        openrouter_keys = []
        existing_keys = set()
        
        for i in range(1, 11):  # Support up to 10 keys
            key = os.getenv(f"OPENROUTER_API_KEY_{i}")
            self.logger.debug(f"Checking OPENROUTER_API_KEY_{i}: {'Found' if key else 'Not found'}")
            
            if key and key not in existing_keys:
                existing_keys.add(key)
                openrouter_keys.append(APIKey(
                    key=key,
                    provider="openrouter",
                    name=f"openrouter_{i}",
                    priority=1 if i <= 2 else (2 if i <= 5 else 3)
                ))
                self.logger.debug(f"Added key: openrouter_{i}")
            elif key:
                self.logger.debug(f"Duplicate key detected for openrouter_{i}")
        
        # Add main key as fallback if not already included
        main_key = os.getenv("OPENROUTER_API_KEY")
        if main_key and main_key not in existing_keys:
            existing_keys.add(main_key)
            openrouter_keys.append(APIKey(
                key=main_key,
                provider="openrouter",
                name="openrouter_main",
                priority=3  # Lower priority as it's fallback
            ))
        
        # Gemini keys
        gemini_keys = []
        for i in range(1, 11):  # Support up to 10 keys
            key = os.getenv(f"GEMINI_API_KEY_{i}") or (os.getenv("GEMINI_API_KEY") if i == 1 else None)
            if key and key not in [k.key for k in gemini_keys]:
                gemini_keys.append(APIKey(
                    key=key,
                    provider="gemini",
                    name=f"gemini_{i}",
                    priority=1 if i <= 2 else (2 if i <= 5 else 3)
                ))
        
        self.keys["openrouter"] = openrouter_keys
        self.keys["gemini"] = gemini_keys
        
        self.logger.info(f"🔑 Loaded {len(openrouter_keys)} OpenRouter keys, {len(gemini_keys)} Gemini keys")
        
        # Debug: Print all loaded keys
        for i, key in enumerate(openrouter_keys):
            self.logger.info(f"  OpenRouter Key {i+1}: {key.name} (priority: {key.priority})")
    
    def get_best_key(self, provider: str) -> Optional[APIKey]:
        """
        Obtém a melhor chave disponível para um provedor
        
        Estratégia:
        1. Prioriza chaves ativas
        2. Considera prioridade (1 > 2 > 3)
        3. Balanceia uso (menos usadas primeiro)
        4. Evita chaves com falhas recentes
        """
        available_keys = [k for k in self.keys.get(provider, []) if k.is_available()]
        
        if not available_keys:
            self.logger.warning(f"🔑 No available keys for provider: {provider}")
            return None
        
        # Sort by priority, then by usage (load balancing)
        available_keys.sort(key=lambda k: (k.priority, k.daily_usage, k.failure_count))
        
        best_key = available_keys[0]
        self.logger.debug(f"🔑 Selected key: {best_key.name} (usage: {best_key.daily_usage})")
        
        return best_key
    
    def get_key_with_fallback(self, preferred_provider: str = "openrouter") -> Tuple[Optional[APIKey], str]:
        """
        Obtém chave com fallback automático entre provedores
        
        Returns:
            (APIKey, provider) or (None, "")
        """
        # Try preferred provider first
        key = self.get_best_key(preferred_provider)
        if key:
            return key, preferred_provider
        
        # Fallback to other providers
        other_providers = [p for p in self.keys.keys() if p != preferred_provider]
        for provider in other_providers:
            key = self.get_best_key(provider)
            if key:
                self.stats["fallback_usage"] += 1
                self.logger.info(f"🔄 Fallback to {provider} (preferred {preferred_provider} unavailable)")
                return key, provider
        
        self.logger.error("🚨 NO AVAILABLE API KEYS FOR ANY PROVIDER!")
        return None, ""
    
    def mark_key_result(self, key: APIKey, success: bool, reason: str = ""):
        """Marca resultado de uso de uma chave"""
        self.stats["total_calls"] += 1
        
        if success:
            key.mark_success()
            self.stats["successful_calls"] += 1
        else:
            key.mark_failure(reason)
            self.stats["failed_calls"] += 1
            
            # Handle specific error types
            if "rate limit" in reason.lower() or "429" in reason:
                key.mark_rate_limit()
            elif "401" in reason or "invalid" in reason.lower():
                key.is_active = False
                self.logger.error(f"🔑 Key {key.name} deactivated due to auth error: {reason}")
        
        # Save state periodically
        if self.stats["total_calls"] % 10 == 0:
            self._save_config()
    
    def get_total_active_keys(self) -> int:
        """Retorna total de chaves ativas"""
        return sum(len([k for k in keys if k.is_available()]) for keys in self.keys.values())
    
    def get_status_report(self) -> Dict:
        """Retorna relatório de status detalhado"""
        report = {
            "total_active_keys": self.get_total_active_keys(),
            "stats": self.stats.copy(),
            "providers": {}
        }
        
        for provider, keys in self.keys.items():
            active_keys = [k for k in keys if k.is_available()]
            report["providers"][provider] = {
                "total_keys": len(keys),
                "active_keys": len(active_keys),
                "key_details": [k.to_dict() for k in keys]
            }
        
        return report
    
    def _save_config(self):
        """Salva configuração atual"""
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            
            data = {
                "stats": self.stats,
                "keys": {
                    provider: [k.to_dict() for k in keys]
                    for provider, keys in self.keys.items()
                },
                "last_updated": datetime.now().isoformat()
            }
            
            with open(self.config_path, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            self.logger.error(f"Could not save config: {e}")

# Singleton instance
_api_key_manager = None

def get_api_key_manager() -> APIKeyManager:
    """Get singleton instance of APIKeyManager"""
    global _api_key_manager
    if _api_key_manager is None:
        _api_key_manager = APIKeyManager()
    return _api_key_manager