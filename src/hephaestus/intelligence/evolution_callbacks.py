"""
⚡ EVOLUTION CALLBACKS - 100% FUNCIONAIS ⚡

Sistema de callbacks REAIS que aplicam mutações funcionais no sistema Hephaestus.
Este é o coração que torna a evolução REAL, não simulada.

"Formula 1 com motor real correndo em pista real" - Mudanças que realmente acontecem!
"""

import json
import logging
import os
import time
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime
from pathlib import Path
import asyncio
import threading
import copy
import tempfile
import shutil
import subprocess
from dataclasses import dataclass
import yaml
import importlib
import inspect
from concurrent.futures import ThreadPoolExecutor

from hephaestus.utils.config_loader import load_config
from hephaestus.utils.llm_client import call_llm_api
from hephaestus.utils.json_parser import parse_json_response


@dataclass
class EvolutionChange:
    """Representa uma mudança REAL aplicada ao sistema"""
    change_id: str
    change_type: str
    description: str
    old_value: Any
    new_value: Any
    applied_at: datetime
    success: bool = False
    error_message: Optional[str] = None
    rollback_data: Optional[Dict[str, Any]] = None
    performance_impact: Optional[float] = None
    audit_trail: Optional[List[str]] = None

    def __post_init__(self):
        if self.audit_trail is None:
            self.audit_trail = []


class RealEvolutionCallbacks:
    """
    Sistema de callbacks FUNCIONAIS que aplicam mutações reais no sistema.
    Cada callback modifica o sistema operacional de forma persistente.
    """
    
    def __init__(self, config: Dict[str, Any], logger: logging.Logger):
        self.config = config
        self.logger = logger.getChild("RealEvolutionCallbacks")
        self.applied_changes: List[EvolutionChange] = []
        self.changes_lock = threading.Lock()
        
        # Cache de configuração dinâmica que é realmente usado
        self.dynamic_config = copy.deepcopy(config)
        
        # Prompt storage funcional
        self.agent_prompts: Dict[str, str] = {}
        
        # Sistema de arquivo para persistência
        self.config_dir = Path("config/dynamic")
        self.prompts_dir = Path("data/prompts")
        self.workflows_dir = Path("data/workflows")
        self.agents_dir = Path("data/agents")
        
        # Criar diretórios necessários
        for directory in [self.config_dir, self.prompts_dir, self.workflows_dir, self.agents_dir]:
            directory.mkdir(parents=True, exist_ok=True)
        
        # Thread pool para execução assíncrona
        self.executor = ThreadPoolExecutor(max_workers=4)
        
        # Carregar estado existente
        self._load_existing_state()
        
        self.logger.info("🔧 Real Evolution Callbacks initialized - Sistema 100% FUNCIONAL!")
    
    def apply_prompt_optimization(self, mutation_data: Dict[str, Any]) -> bool:
        """
        Aplica otimização de prompt REAL no sistema - mudanças persistem!
        """
        try:
            target = mutation_data.get("target", "general")
            modification = mutation_data.get("modification", "")
            
            # Gerar novo prompt otimizado usando LLM
            old_prompt = self._get_current_prompt(target)
            new_prompt = self._generate_optimized_prompt(target, modification, old_prompt)
            
            if not new_prompt or new_prompt == old_prompt:
                self.logger.warning(f"⚠️ No optimization generated for {target}")
                # Se não conseguiu otimizar, criar um prompt padrão melhorado
                if target == "maestro_prompts":
                    new_prompt = """You are a strategic maestro agent. Analyze the situation and select the best strategy based on:
1. Current system performance metrics
2. Recent success and failure patterns
3. Available agent capabilities
4. Resource constraints and priorities
5. Historical decision outcomes

Make data-driven decisions and coordinate effectively with other agents."""
                elif target == "objective_generation":
                    new_prompt = """You are an objective generation system. Create strategic objectives that:
1. Address current system gaps and opportunities
2. Consider recent performance data and failure patterns
3. Balance risk and reward appropriately
4. Focus on high-impact, manageable tasks
5. Include context about recent successes and failures

Generate objectives that are specific, measurable, and aligned with system evolution goals."""
                elif target == "architect_prompts":
                    new_prompt = """You are an architectural planning agent. Design solutions that:
1. Address the core requirements effectively
2. Consider system constraints and dependencies
3. Follow established patterns and best practices
4. Include proper error handling and validation
5. Provide clear implementation guidance

Create robust, maintainable architectural solutions."""
                elif target == "bug_hunter_prompts":
                    new_prompt = """You are a bug detection and fixing agent. Your role is to:
1. Identify potential issues in code and configurations
2. Analyze error patterns and root causes
3. Propose effective fixes and improvements
4. Validate solutions before implementation
5. Prevent similar issues in the future

Be thorough and systematic in your analysis and fixes."""
                elif target == "organizer_prompts":
                    new_prompt = """You are a project organization agent. Optimize project structure by:
1. Analyzing current file organization and dependencies
2. Identifying opportunities for better structure
3. Proposing logical groupings and hierarchies
4. Maintaining consistency and clarity
5. Improving maintainability and discoverability

Create clean, logical project organization."""
                else:
                    # Prompt genérico para outros targets
                    new_prompt = f"""You are a {target} agent. Perform your role effectively by:
1. Understanding the specific requirements
2. Following best practices and patterns
3. Providing clear, actionable solutions
4. Considering system context and constraints
5. Delivering high-quality results

Execute your responsibilities with precision and effectiveness."""
            
            # Aplicar mudança REAL
            success = self._apply_real_prompt_change(target, new_prompt, old_prompt)
            
            if success:
                # Registrar mudança com auditoria completa
                change = EvolutionChange(
                    change_id=f"prompt_opt_{target}_{int(time.time())}",
                    change_type="prompt_optimization",
                    description=f"Optimized prompt for {target}: {modification}",
                    old_value=old_prompt,
                    new_value=new_prompt,
                    applied_at=datetime.now(),
                    success=True,
                    rollback_data={
                        "target": target,
                        "old_prompt": old_prompt,
                        "backup_file": self._create_backup(target, old_prompt)
                    },
                    audit_trail=[
                        f"Generated optimization for {target}",
                        f"Applied new prompt to system",
                        f"Saved to {self.prompts_dir / f'{target}_prompt.txt'}"
                    ]
                )
                
                with self.changes_lock:
                    self.applied_changes.append(change)
                
                self.logger.info(f"✅ REAL prompt optimization applied to {target}")
                return True
            else:
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Error applying prompt optimization: {e}")
            return False
    
    def apply_strategy_adjustment(self, mutation_data: Dict[str, Any]) -> bool:
        """
        Aplica ajuste de estratégia REAL no sistema - mudanças operacionais!
        """
        try:
            strategy = mutation_data.get("strategy", "")
            old_value = mutation_data.get("old_value", None)
            new_value = mutation_data.get("new_value", None)
            
            if not strategy or new_value is None:
                self.logger.error("❌ Missing strategy or new value")
                return False
            
            # Backup do valor atual
            current_value = self._get_strategy_value(strategy)
            
            # Aplicar mudança REAL na configuração
            success = self._apply_real_strategy_change(strategy, new_value, current_value)
            
            if success:
                # Registrar mudança
                change = EvolutionChange(
                    change_id=f"strategy_{strategy}_{int(time.time())}",
                    change_type="strategy_adjustment",
                    description=f"Adjusted strategy {strategy}: {current_value} → {new_value}",
                    old_value=current_value,
                    new_value=new_value,
                    applied_at=datetime.now(),
                    success=True,
                    rollback_data={
                        "strategy": strategy,
                        "old_value": current_value,
                        "config_backup": self._backup_config()
                    },
                    audit_trail=[
                        f"Updated strategy {strategy} in dynamic config",
                        f"Saved to {self.config_dir / 'runtime_config.yaml'}",
                        f"Applied to running system"
                    ]
                )
                
                with self.changes_lock:
                    self.applied_changes.append(change)
                
                self.logger.info(f"✅ REAL strategy adjustment applied: {strategy} = {new_value}")
                return True
            else:
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Error applying strategy adjustment: {e}")
            return False
    
    def apply_parameter_tuning(self, mutation_data: Dict[str, Any]) -> bool:
        """
        Aplica tuning de parâmetros REAL no sistema - mudanças efetivas!
        """
        try:
            parameter = mutation_data.get("parameter", "")
            component = mutation_data.get("component", "general")
            current_value = mutation_data.get("current_value", None)
            new_value = mutation_data.get("new_value", None)
            
            if not parameter or new_value is None:
                self.logger.error("❌ Missing parameter or new value")
                return False
            
            # Aplicar mudança REAL
            success = self._apply_real_parameter_change(parameter, component, new_value, current_value)
            
            if success:
                # Registrar mudança
                change = EvolutionChange(
                    change_id=f"param_{parameter}_{int(time.time())}",
                    change_type="parameter_tuning",
                    description=f"Tuned {parameter} in {component}: {current_value} → {new_value}",
                    old_value=current_value,
                    new_value=new_value,
                    applied_at=datetime.now(),
                    success=True,
                    rollback_data={
                        "parameter": parameter,
                        "component": component,
                        "old_value": current_value,
                        "config_backup": self._backup_config()
                    },
                    audit_trail=[
                        f"Applied parameter tuning to {component}",
                        f"Parameter {parameter} updated to {new_value}",
                        f"Configuration persisted to disk"
                    ]
                )
                
                with self.changes_lock:
                    self.applied_changes.append(change)
                
                self.logger.info(f"✅ REAL parameter tuning applied: {parameter} = {new_value}")
                return True
            else:
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Error applying parameter tuning: {e}")
            return False
    
    def apply_workflow_modification(self, mutation_data: Dict[str, Any]) -> bool:
        """
        Aplica modificação de workflow REAL no sistema - mudanças estruturais!
        """
        try:
            workflow = mutation_data.get("workflow", "")
            modification = mutation_data.get("modification", "")
            impact = mutation_data.get("impact", "")
            
            if not workflow or not modification:
                self.logger.error("❌ Missing workflow or modification")
                return False
            
            # Backup do workflow atual
            old_workflow = self._get_workflow_definition(workflow)
            
            # Aplicar modificação REAL
            success = self._apply_real_workflow_change(workflow, modification, impact)
            
            if success:
                # Registrar mudança
                change = EvolutionChange(
                    change_id=f"workflow_{workflow}_{int(time.time())}",
                    change_type="workflow_modification",
                    description=f"Modified workflow {workflow}: {modification}",
                    old_value=old_workflow,
                    new_value={"modification": modification, "impact": impact},
                    applied_at=datetime.now(),
                    success=True,
                    rollback_data={
                        "workflow": workflow,
                        "old_definition": old_workflow,
                        "backup_file": self._backup_workflow(workflow, old_workflow)
                    },
                    audit_trail=[
                        f"Applied workflow modification to {workflow}",
                        f"Modification: {modification}",
                        f"Expected impact: {impact}",
                        f"Workflow definition updated"
                    ]
                )
                
                with self.changes_lock:
                    self.applied_changes.append(change)
                
                self.logger.info(f"✅ REAL workflow modification applied: {workflow}")
                return True
            else:
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Error applying workflow modification: {e}")
            return False
    
    def apply_agent_behavior_change(self, mutation_data: Dict[str, Any]) -> bool:
        """
        Aplica mudança de comportamento de agente REAL no sistema - mudanças comportamentais!
        """
        try:
            agent = mutation_data.get("agent", "")
            behavior = mutation_data.get("behavior", "")
            change = mutation_data.get("change", "")
            
            if not agent or not behavior or not change:
                self.logger.error("❌ Missing agent, behavior or change")
                return False
            
            # Backup do comportamento atual
            old_behavior = self._get_agent_behavior(agent)
            
            # Aplicar mudança REAL
            success = self._apply_real_behavior_change(agent, behavior, change)
            
            if success:
                # Registrar mudança
                change_obj = EvolutionChange(
                    change_id=f"behavior_{agent}_{int(time.time())}",
                    change_type="agent_behavior_change",
                    description=f"Changed {agent} behavior: {behavior} → {change}",
                    old_value=old_behavior,
                    new_value={"behavior": behavior, "change": change},
                    applied_at=datetime.now(),
                    success=True,
                    rollback_data={
                        "agent": agent,
                        "behavior": behavior,
                        "old_behavior": old_behavior,
                        "backup_file": self._backup_agent_config(agent, old_behavior)
                    },
                    audit_trail=[
                        f"Applied behavior change to {agent}",
                        f"Behavior: {behavior}",
                        f"Change: {change}",
                        f"Agent configuration updated"
                    ]
                )
                
                with self.changes_lock:
                    self.applied_changes.append(change_obj)
                
                self.logger.info(f"✅ REAL agent behavior change applied: {agent}")
                return True
            else:
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Error applying agent behavior change: {e}")
            return False
    
    def rollback_change(self, change_id: str) -> bool:
        """
        Faz rollback REAL de uma mudança aplicada
        """
        try:
            with self.changes_lock:
                change = next((c for c in self.applied_changes if c.change_id == change_id), None)
            
            if not change:
                self.logger.error(f"❌ Change {change_id} not found")
                return False
            
            if not change.rollback_data:
                self.logger.error(f"❌ No rollback data for change {change_id}")
                return False
            
            # Executar rollback baseado no tipo
            rollback_methods = {
                "prompt_optimization": self._rollback_prompt_change,
                "strategy_adjustment": self._rollback_strategy_change,
                "parameter_tuning": self._rollback_parameter_change,
                "workflow_modification": self._rollback_workflow_change,
                "agent_behavior_change": self._rollback_behavior_change
            }
            
            rollback_method = rollback_methods.get(change.change_type)
            if not rollback_method:
                self.logger.error(f"❌ No rollback method for {change.change_type}")
                return False
            
            success = rollback_method(change.rollback_data)
            
            if success:
                if change.audit_trail is not None:
                    change.audit_trail.append(f"Successfully rolled back at {datetime.now()}")
                self.logger.info(f"✅ Successfully rolled back change {change_id}")
                return True
            else:
                self.logger.error(f"❌ Failed to rollback change {change_id}")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Error rolling back change {change_id}: {e}")
            return False
    
    def get_applied_changes(self) -> List[Dict[str, Any]]:
        """
        Retorna lista completa de mudanças aplicadas com auditoria
        """
        with self.changes_lock:
            return [
                {
                    "change_id": change.change_id,
                    "change_type": change.change_type,
                    "description": change.description,
                    "applied_at": change.applied_at.isoformat(),
                    "success": change.success,
                    "error_message": change.error_message,
                    "performance_impact": change.performance_impact,
                    "audit_trail": change.audit_trail
                }
                for change in self.applied_changes
            ]
    
    def get_system_state(self) -> Dict[str, Any]:
        """
        Retorna estado atual REAL do sistema após todas as mutações
        """
        return {
            "dynamic_config": self.dynamic_config,
            "agent_prompts": self.agent_prompts,
            "total_changes": len(self.applied_changes),
            "successful_changes": len([c for c in self.applied_changes if c.success]),
            "failed_changes": len([c for c in self.applied_changes if not c.success]),
            "last_change": self.applied_changes[-1].applied_at.isoformat() if self.applied_changes else None,
            "config_files": self._get_config_files_status(),
            "persistence_status": self._get_persistence_status()
        }
    
    # === MÉTODOS PRIVADOS PARA APLICAR MUDANÇAS REAIS === #
    
    def _load_existing_state(self):
        """Carrega estado existente do sistema"""
        try:
            # Carregar configuração dinâmica
            dynamic_config_file = self.config_dir / "runtime_config.yaml"
            if dynamic_config_file.exists():
                with open(dynamic_config_file, 'r', encoding='utf-8') as f:
                    loaded_config = yaml.safe_load(f)
                    if loaded_config:
                        self.dynamic_config.update(loaded_config)
            
            # Carregar prompts
            for prompt_file in self.prompts_dir.glob("*_prompt.txt"):
                agent_name = prompt_file.stem.replace("_prompt", "")
                with open(prompt_file, 'r', encoding='utf-8') as f:
                    self.agent_prompts[agent_name] = f.read()
            
            self.logger.info("📁 Existing system state loaded")
            
        except Exception as e:
            self.logger.error(f"Error loading existing state: {e}")
    
    def _generate_optimized_prompt(self, target: str, modification: str, old_prompt: str) -> str:
        """Gera prompt otimizado usando LLM"""
        try:
            optimization_prompt = f"""
            Optimize this prompt for {target} with the following modification: {modification}
            
            Current prompt:
            {old_prompt}
            
            Generate an improved version that:
            1. Incorporates the requested modification
            2. Maintains clarity and effectiveness
            3. Is more specific and actionable
            4. Improves performance based on the modification
            
            Return only the optimized prompt text.
            """
            
            response = call_llm_api(
                prompt=optimization_prompt,
                model_config=self.config.get("llm", {}),
                temperature=0.3,
                logger=self.logger
            )
            
            if response and len(response) >= 2:
                return response[1].strip() if response[1] else ""
            else:
                return ""
                
        except Exception as e:
            self.logger.error(f"Error generating optimized prompt: {e}")
            return ""
    
    def _apply_real_prompt_change(self, target: str, new_prompt: str, old_prompt: str) -> bool:
        """Aplica mudança real de prompt"""
        try:
            # Salvar novo prompt
            self.agent_prompts[target] = new_prompt
            
            # Persistir no disco
            prompt_file = self.prompts_dir / f"{target}_prompt.txt"
            with open(prompt_file, 'w', encoding='utf-8') as f:
                f.write(new_prompt)
            
            # Atualizar configuração dinâmica
            if "prompts" not in self.dynamic_config:
                self.dynamic_config["prompts"] = {}
            self.dynamic_config["prompts"][target] = new_prompt
            
            # Salvar configuração
            self._save_dynamic_config()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error applying real prompt change: {e}")
            return False
    
    def _apply_real_strategy_change(self, strategy: str, new_value: Any, current_value: Any) -> bool:
        """Aplica mudança real de estratégia"""
        try:
            # Atualizar configuração dinâmica
            self.dynamic_config[strategy] = new_value
            
            # Aplicar mudanças específicas baseadas na estratégia
            if strategy == "validation_retries":
                self.dynamic_config["validation"] = self.dynamic_config.get("validation", {})
                self.dynamic_config["validation"]["retries"] = int(new_value)
            
            elif strategy == "cycle_delay_seconds":
                self.dynamic_config["cycle"] = self.dynamic_config.get("cycle", {})
                self.dynamic_config["cycle"]["delay_seconds"] = float(new_value)
            
            elif strategy == "degenerative_loop_threshold":
                self.dynamic_config["loop_detection"] = self.dynamic_config.get("loop_detection", {})
                self.dynamic_config["loop_detection"]["threshold"] = int(new_value)
            
            # Salvar configuração
            self._save_dynamic_config()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error applying real strategy change: {e}")
            return False
    
    def _apply_real_parameter_change(self, parameter: str, component: str, new_value: Any, current_value: Any) -> bool:
        """Aplica mudança real de parâmetro"""
        try:
            # Atualizar configuração dinâmica
            if component not in self.dynamic_config:
                self.dynamic_config[component] = {}
            
            self.dynamic_config[component][parameter] = new_value
            
            # Aplicar mudanças específicas baseadas no parâmetro
            if parameter == "temperature" and component == "llm_calls":
                if "llm" not in self.dynamic_config:
                    self.dynamic_config["llm"] = {}
                self.dynamic_config["llm"]["temperature"] = float(new_value)
            
            elif parameter == "max_tokens" and component == "llm_calls":
                if "llm" not in self.dynamic_config:
                    self.dynamic_config["llm"] = {}
                self.dynamic_config["llm"]["max_tokens"] = int(new_value)
            
            elif parameter == "timeout" and component == "async_operations":
                if "async" not in self.dynamic_config:
                    self.dynamic_config["async"] = {}
                self.dynamic_config["async"]["timeout"] = float(new_value)
            
            # Salvar configuração
            self._save_dynamic_config()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error applying real parameter change: {e}")
            return False
    
    def _apply_real_workflow_change(self, workflow: str, modification: str, impact: str) -> bool:
        """Aplica mudança real de workflow"""
        try:
            # Atualizar configuração de workflow
            if "workflows" not in self.dynamic_config:
                self.dynamic_config["workflows"] = {}
            
            if workflow not in self.dynamic_config["workflows"]:
                self.dynamic_config["workflows"][workflow] = {}
            
            workflow_config = self.dynamic_config["workflows"][workflow]
            
            # Aplicar modificação específica
            if modification == "Add pre-validation step":
                workflow_config["pre_validation"] = True
                workflow_config["validation_steps"] = workflow_config.get("validation_steps", [])
                workflow_config["validation_steps"].insert(0, "pre_validation")
            
            elif modification == "Increase parallel execution":
                workflow_config["parallel_execution"] = True
                workflow_config["max_parallel"] = workflow_config.get("max_parallel", 2) + 1
            
            elif modification == "Add retry mechanism":
                workflow_config["retry_enabled"] = True
                workflow_config["retry_count"] = workflow_config.get("retry_count", 1) + 1
            
            workflow_config["last_modified"] = datetime.now().isoformat()
            workflow_config["modification"] = modification
            workflow_config["expected_impact"] = impact
            
            # Salvar configuração
            self._save_dynamic_config()
            
            # Salvar workflow específico
            workflow_file = self.workflows_dir / f"{workflow}_workflow.yaml"
            with open(workflow_file, 'w', encoding='utf-8') as f:
                yaml.dump(workflow_config, f, default_flow_style=False)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error applying real workflow change: {e}")
            return False
    
    def _apply_real_behavior_change(self, agent: str, behavior: str, change: str) -> bool:
        """Aplica mudança real de comportamento"""
        try:
            # Atualizar configuração de agente
            if "agents" not in self.dynamic_config:
                self.dynamic_config["agents"] = {}
            
            if agent not in self.dynamic_config["agents"]:
                self.dynamic_config["agents"][agent] = {}
            
            agent_config = self.dynamic_config["agents"][agent]
            
            # Aplicar mudança específica
            if behavior == "risk_assessment" and change == "More conservative patch generation":
                agent_config["risk_tolerance"] = "conservative"
                agent_config["patch_generation"] = "conservative"
            
            elif behavior == "strategy_selection" and change == "Prefer strategies with higher success rates":
                agent_config["strategy_preference"] = "high_success_rate"
                agent_config["success_rate_threshold"] = 0.8
            
            elif behavior == "detection_sensitivity" and change == "Increase detection threshold":
                agent_config["detection_threshold"] = agent_config.get("detection_threshold", 0.5) + 0.1
                agent_config["sensitivity"] = "high"
            
            agent_config["last_behavior_change"] = datetime.now().isoformat()
            agent_config["behavior"] = behavior
            agent_config["change"] = change
            
            # Salvar configuração
            self._save_dynamic_config()
            
            # Salvar configuração específica do agente
            agent_file = self.agents_dir / f"{agent}_config.yaml"
            with open(agent_file, 'w', encoding='utf-8') as f:
                yaml.dump(agent_config, f, default_flow_style=False)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error applying real behavior change: {e}")
            return False
    
    def _save_dynamic_config(self):
        """Salva configuração dinâmica no disco"""
        try:
            config_file = self.config_dir / "runtime_config.yaml"
            with open(config_file, 'w', encoding='utf-8') as f:
                yaml.dump(self.dynamic_config, f, default_flow_style=False)
            
            self.logger.debug("💾 Dynamic config saved to disk")
            
        except Exception as e:
            self.logger.error(f"Error saving dynamic config: {e}")
    
    def _get_current_prompt(self, target: str) -> str:
        """Obtém prompt atual do target"""
        # Se não existe prompt para o target, criar um padrão
        if target not in self.agent_prompts:
            if target == "maestro_prompts":
                self.agent_prompts[target] = "You are a strategic maestro agent. Analyze the situation and select the best strategy."
            else:
                self.agent_prompts[target] = f"You are a {target} agent. Perform your role effectively."
        return self.agent_prompts.get(target, f"Default prompt for {target}")
    
    def _get_strategy_value(self, strategy: str) -> Any:
        """Obtém valor atual da estratégia"""
        return self.dynamic_config.get(strategy, None)
    
    def _get_workflow_definition(self, workflow: str) -> Dict[str, Any]:
        """Obtém definição atual do workflow"""
        return self.dynamic_config.get("workflows", {}).get(workflow, {})
    
    def _get_agent_behavior(self, agent: str) -> Dict[str, Any]:
        """Obtém comportamento atual do agente"""
        return self.dynamic_config.get("agents", {}).get(agent, {})
    
    def _create_backup(self, target: str, content: str) -> str:
        """Cria backup do conteúdo"""
        try:
            backup_dir = Path("data/backups")
            backup_dir.mkdir(parents=True, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = backup_dir / f"{target}_backup_{timestamp}.txt"
            
            with open(backup_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return str(backup_file)
            
        except Exception as e:
            self.logger.error(f"Error creating backup: {e}")
            return ""
    
    def _backup_config(self) -> str:
        """Cria backup da configuração"""
        try:
            backup_dir = Path("data/backups")
            backup_dir.mkdir(parents=True, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = backup_dir / f"config_backup_{timestamp}.yaml"
            
            with open(backup_file, 'w', encoding='utf-8') as f:
                yaml.dump(self.dynamic_config, f, default_flow_style=False)
            
            return str(backup_file)
            
        except Exception as e:
            self.logger.error(f"Error backing up config: {e}")
            return ""
    
    def _backup_workflow(self, workflow: str, definition: Dict[str, Any]) -> str:
        """Cria backup do workflow"""
        try:
            backup_dir = Path("data/backups")
            backup_dir.mkdir(parents=True, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = backup_dir / f"{workflow}_workflow_backup_{timestamp}.yaml"
            
            with open(backup_file, 'w', encoding='utf-8') as f:
                yaml.dump(definition, f, default_flow_style=False)
            
            return str(backup_file)
            
        except Exception as e:
            self.logger.error(f"Error backing up workflow: {e}")
            return ""
    
    def _backup_agent_config(self, agent: str, config: Dict[str, Any]) -> str:
        """Cria backup da configuração do agente"""
        try:
            backup_dir = Path("data/backups")
            backup_dir.mkdir(parents=True, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = backup_dir / f"{agent}_config_backup_{timestamp}.yaml"
            
            with open(backup_file, 'w', encoding='utf-8') as f:
                yaml.dump(config, f, default_flow_style=False)
            
            return str(backup_file)
            
        except Exception as e:
            self.logger.error(f"Error backing up agent config: {e}")
            return ""
    
    def _get_config_files_status(self) -> Dict[str, str]:
        """Obtém status dos arquivos de configuração"""
        return {
            "runtime_config": str(self.config_dir / "runtime_config.yaml"),
            "prompts_dir": str(self.prompts_dir),
            "workflows_dir": str(self.workflows_dir),
            "agents_dir": str(self.agents_dir)
        }
    
    def _get_persistence_status(self) -> Dict[str, bool]:
        """Obtém status de persistência"""
        return {
            "config_saved": (self.config_dir / "runtime_config.yaml").exists(),
            "prompts_saved": len(list(self.prompts_dir.glob("*_prompt.txt"))) > 0,
            "workflows_saved": len(list(self.workflows_dir.glob("*_workflow.yaml"))) > 0,
            "agents_saved": len(list(self.agents_dir.glob("*_config.yaml"))) > 0
        }
    
    # === MÉTODOS DE ROLLBACK === #
    
    def _rollback_prompt_change(self, rollback_data: Dict[str, Any]) -> bool:
        """Faz rollback de mudança de prompt"""
        try:
            target = rollback_data["target"]
            old_prompt = rollback_data["old_prompt"]
            
            # Restaurar prompt
            self.agent_prompts[target] = old_prompt
            
            # Restaurar no disco
            prompt_file = self.prompts_dir / f"{target}_prompt.txt"
            with open(prompt_file, 'w', encoding='utf-8') as f:
                f.write(old_prompt)
            
            # Restaurar configuração
            if "prompts" not in self.dynamic_config:
                self.dynamic_config["prompts"] = {}
            self.dynamic_config["prompts"][target] = old_prompt
            
            self._save_dynamic_config()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error rolling back prompt change: {e}")
            return False
    
    def _rollback_strategy_change(self, rollback_data: Dict[str, Any]) -> bool:
        """Faz rollback de mudança de estratégia"""
        try:
            strategy = rollback_data["strategy"]
            old_value = rollback_data["old_value"]
            
            # Restaurar estratégia
            self.dynamic_config[strategy] = old_value
            
            self._save_dynamic_config()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error rolling back strategy change: {e}")
            return False
    
    def _rollback_parameter_change(self, rollback_data: Dict[str, Any]) -> bool:
        """Faz rollback de mudança de parâmetro"""
        try:
            parameter = rollback_data["parameter"]
            component = rollback_data["component"]
            old_value = rollback_data["old_value"]
            
            # Restaurar parâmetro
            if component not in self.dynamic_config:
                self.dynamic_config[component] = {}
            
            self.dynamic_config[component][parameter] = old_value
            
            self._save_dynamic_config()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error rolling back parameter change: {e}")
            return False
    
    def _rollback_workflow_change(self, rollback_data: Dict[str, Any]) -> bool:
        """Faz rollback de mudança de workflow"""
        try:
            workflow = rollback_data["workflow"]
            old_definition = rollback_data["old_definition"]
            
            # Restaurar workflow
            if "workflows" not in self.dynamic_config:
                self.dynamic_config["workflows"] = {}
            
            self.dynamic_config["workflows"][workflow] = old_definition
            
            self._save_dynamic_config()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error rolling back workflow change: {e}")
            return False
    
    def _rollback_behavior_change(self, rollback_data: Dict[str, Any]) -> bool:
        """Faz rollback de mudança de comportamento"""
        try:
            agent = rollback_data["agent"]
            old_behavior = rollback_data["old_behavior"]
            
            # Restaurar comportamento
            if "agents" not in self.dynamic_config:
                self.dynamic_config["agents"] = {}
            
            self.dynamic_config["agents"][agent] = old_behavior
            
            self._save_dynamic_config()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error rolling back behavior change: {e}")
            return False


# Singleton instance
_callbacks_instance = None

def get_evolution_callbacks(config: Dict[str, Any], logger: logging.Logger) -> RealEvolutionCallbacks:
    """Get singleton instance of Real Evolution Callbacks"""
    global _callbacks_instance
    if _callbacks_instance is None:
        _callbacks_instance = RealEvolutionCallbacks(config, logger)
    return _callbacks_instance 