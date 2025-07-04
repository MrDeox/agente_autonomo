"""
Unified Configuration Manager - Sistema Unificado de Configuração

Este módulo resolve o conflito entre Hydra (YAML) e JSON criando um sistema
unificado que mantém compatibilidade com ambos mas elimina a confusão.
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List

from agent.config_loader import load_config as load_hydra_config


class UnifiedConfigManager:
    """Gerenciador unificado de configuração que resolve conflitos Hydra/JSON"""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger(__name__)
        self.project_root = Path.cwd()
        self._config_cache: Optional[Dict[str, Any]] = None
        
    def load_unified_config(self, force_reload: bool = False) -> Dict[str, Any]:
        """Carrega configuração unificada combinando Hydra e JSON"""
        if not force_reload and self._config_cache:
            return self._config_cache
        
        self.logger.info("🔧 Carregando configuração unificada...")
        
        # 1. Carregar Hydra (sistema principal)
        hydra_config = self._load_hydra_config()
        
        # 2. Carregar JSON (fallback/override)
        json_config = self._load_json_config()
        
        # 3. Combinar configurações
        unified_config = self._merge_configurations(hydra_config, json_config)
        
        # 4. Cache e log
        self._config_cache = unified_config
        self._log_config_summary(unified_config)
        
        return unified_config
    
    def _load_hydra_config(self) -> Dict[str, Any]:
        """Carrega configuração do Hydra"""
        try:
            hydra_config = load_hydra_config()
            self.logger.info(f"✅ Hydra: {len(hydra_config.keys())} seções")
            return hydra_config
        except Exception as e:
            self.logger.warning(f"⚠️ Falha ao carregar Hydra: {e}")
            return {}
    
    def _load_json_config(self) -> Dict[str, Any]:
        """Carrega configuração do JSON"""
        json_path = self.project_root / "hephaestus_config.json"
        
        if not json_path.exists():
            self.logger.info("📄 JSON config não encontrado")
            return {}
        
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                json_config = json.load(f)
            self.logger.info(f"✅ JSON: {len(json_config.keys())} seções")
            return json_config
        except Exception as e:
            self.logger.error(f"❌ Erro ao carregar JSON: {e}")
            return {}
    
    def _merge_configurations(self, hydra_config: Dict[str, Any], 
                            json_config: Dict[str, Any]) -> Dict[str, Any]:
        """Combina configurações Hydra e JSON"""
        self.logger.info("🔀 Combinando configurações...")
        
        # Começar com Hydra como base
        unified = hydra_config.copy() if hydra_config else {}
        
        if not json_config:
            return unified
        
        # Merge seção por seção
        for section, json_data in json_config.items():
            if section == "validation_strategies":
                # Merge especial para estratégias
                hydra_strategies = unified.get(section, {})
                merged_strategies = hydra_strategies.copy() if hydra_strategies else {}
                merged_strategies.update(json_data)
                unified[section] = merged_strategies
                
                self.logger.info(f"   📊 Estratégias: {len(merged_strategies)} total")
                
            elif section in unified and isinstance(unified[section], dict) and isinstance(json_data, dict):
                # Merge recursivo para dicionários
                unified[section].update(json_data)
                
            else:
                # JSON sobrescreve ou adiciona
                unified[section] = json_data
        
        return unified
    
    def _log_config_summary(self, config: Dict[str, Any]):
        """Log resumo da configuração"""
        strategies = len(config.get("validation_strategies", {}))
        models = len(config.get("models", {}))
        
        self.logger.info("📊 Configuração unificada:")
        self.logger.info(f"   • Estratégias: {strategies}")
        self.logger.info(f"   • Modelos: {models}")
        self.logger.info(f"   • Seções: {len(config.keys())}")


# Singleton global
_unified_config_manager: Optional[UnifiedConfigManager] = None


def get_unified_config_manager(logger: Optional[logging.Logger] = None) -> UnifiedConfigManager:
    """Retorna instância singleton do gerenciador"""
    global _unified_config_manager
    
    if _unified_config_manager is None:
        _unified_config_manager = UnifiedConfigManager(logger)
    
    return _unified_config_manager


def load_unified_config(logger: Optional[logging.Logger] = None, 
                       force_reload: bool = False) -> Dict[str, Any]:
    """Função principal para carregar configuração unificada"""
    manager = get_unified_config_manager(logger)
    return manager.load_unified_config(force_reload) 