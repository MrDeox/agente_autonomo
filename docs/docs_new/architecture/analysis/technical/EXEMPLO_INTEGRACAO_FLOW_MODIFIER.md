# Exemplo de Integração do Flow Self-Modifier

## 1. Integração Básica no ArchitectAgent

```python
# agent/agents/architect_agent.py
from agent.flow_self_modifier import get_flow_modifier, CallContext, optimize_llm_call

class ArchitectAgent:
    def __init__(self, model_config: Dict[str, str], logger: logging.Logger):
        self.model_config = model_config
        self.logger = logger
        self.flow_modifier = get_flow_modifier(model_config, logger)
    
    @optimize_llm_call("architect")  # Decorador automático
    def plan_action(self, objective: str, manifest: str) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        # Criar contexto para decisão
        context = CallContext(
            agent_type="architect",
            objective=objective,
            complexity_score=self._calculate_complexity(objective, manifest),
            urgency=0.8,  # Architect é geralmente urgente
            previous_failures=self._get_failure_count(objective)
        )
        
        # Obter decisão do flow modifier
        decision = self.flow_modifier.should_make_call(context)
        
        if not decision.should_call:
            self.logger.info(f"Skipping architect call: {decision.skip_reason}")
            return None, decision.skip_reason
        
        # Construir prompt (possivelmente otimizado)
        prompt = self._build_prompt(objective, manifest)
        if decision.use_simplified_prompt:
            prompt = self.flow_modifier.optimize_prompt(prompt, context)
        
        # Selecionar modelo (possivelmente menor)
        model = self.model_config.get("primary", "gpt-3.5-turbo")
        if decision.use_smaller_model:
            model = self.flow_modifier.select_model(model, context)
        
        # Fazer a chamada LLM
        self.logger.info(f"ArchitectAgent: Calling {model} (optimized: {decision.use_simplified_prompt})")
        
        # ... resto da implementação
```

## 2. Integração com Batching no HephaestusAgent

```python
# agent/hephaestus_agent.py
class HephaestusAgent:
    def __init__(self, ...):
        # ... existing init
        self.flow_modifier = get_flow_modifier(
            self.config.get("models", {}).get("flow_optimizer"),
            self.logger
        )
        self.pending_calls = []
    
    def _run_cycle_with_optimization(self):
        """Versão otimizada do ciclo principal"""
        
        # 1. Coletar todas as chamadas potenciais
        potential_calls = []
        
        # Architect call
        potential_calls.append({
            "type": "architect",
            "context": CallContext(
                agent_type="architect",
                objective=self.state.current_objective,
                complexity_score=0.7,
                urgency=0.9
            ),
            "function": self._run_architect_phase
        })
        
        # Code review call (se houver patches)
        if self.state.get_patches_to_apply():
            potential_calls.append({
                "type": "code_review",
                "context": CallContext(
                    agent_type="code_review",
                    objective="Review patches",
                    complexity_score=0.5,
                    urgency=0.7
                ),
                "function": self._run_code_review_phase
            })
        
        # 2. Deixar o flow modifier decidir
        optimized_calls = []
        for call in potential_calls:
            decision = self.flow_modifier.should_make_call(call["context"])
            
            if decision.should_call:
                call["decision"] = decision
                optimized_calls.append(call)
            else:
                self.logger.info(f"Skipping {call['type']}: {decision.skip_reason}")
        
        # 3. Identificar oportunidades de paralelização
        parallel_groups = self._group_parallel_calls(optimized_calls)
        
        # 4. Executar calls (em paralelo quando possível)
        for group in parallel_groups:
            if len(group) > 1:
                self._execute_parallel_calls(group)
            else:
                self._execute_single_call(group[0])
    
    def _execute_parallel_calls(self, calls: List[Dict]):
        """Executar múltiplas chamadas em paralelo"""
        from concurrent.futures import ThreadPoolExecutor
        
        self.logger.info(f"Executing {len(calls)} calls in parallel")
        
        with ThreadPoolExecutor(max_workers=len(calls)) as executor:
            futures = []
            for call in calls:
                future = executor.submit(call["function"])
                futures.append((future, call))
            
            for future, call in futures:
                try:
                    result = future.result(timeout=30)
                    self.logger.info(f"Parallel call {call['type']} completed")
                except Exception as e:
                    self.logger.error(f"Parallel call {call['type']} failed: {e}")
```

## 3. Meta-Análise Automática

```python
# agent/meta_analyzer.py
class MetaAnalyzer:
    """Analisa o desempenho do sistema e sugere modificações no fluxo"""
    
    def __init__(self, flow_modifier: FlowSelfModifier):
        self.flow_modifier = flow_modifier
        self.analysis_interval = 300  # 5 minutos
        self.last_analysis = 0
    
    def analyze_and_adapt(self):
        """Análise periódica e adaptação do fluxo"""
        current_time = time.time()
        
        if current_time - self.last_analysis < self.analysis_interval:
            return
        
        # Obter relatório de otimização
        report = self.flow_modifier.get_optimization_report()
        
        # Analisar padrões
        patterns = self._analyze_patterns(report)
        
        # Ajustar thresholds baseado em performance
        if patterns["high_failure_rate"]:
            # Ser mais conservador
            self.flow_modifier.thresholds["simplification_threshold"] = 0.8
            self.flow_modifier.thresholds["max_calls_per_minute"] = 8
        
        if patterns["low_complexity_average"]:
            # Ser mais agressivo com simplificação
            self.flow_modifier.thresholds["simplification_threshold"] = 0.6
        
        if patterns["many_sequential_calls"]:
            # Encorajar mais paralelização
            self.flow_modifier.thresholds["parallel_opportunity_window"] = 10.0
        
        self.last_analysis = current_time
        
        # Log adaptações
        self.logger.info(f"Flow adapted based on patterns: {patterns}")
```

## 4. Exemplo de Uso Real

```python
# Em um ciclo real do Hephaestus
def run_optimized_cycle():
    agent = HephaestusAgent(config, logger)
    
    # O flow modifier monitora e otimiza automaticamente
    while agent.continuous_mode:
        # Análise meta-cognitiva periódica
        if agent.cycle_count % 10 == 0:
            meta_analyzer = MetaAnalyzer(agent.flow_modifier)
            meta_analyzer.analyze_and_adapt()
        
        # Executar ciclo otimizado
        agent._run_cycle_with_optimization()
        
        # Verificar se devemos mudar estratégia
        report = agent.flow_modifier.get_optimization_report()
        if report["optimization_stats"]["skipped"] > 5:
            agent.logger.warning("Many calls being skipped - adjusting strategy")
            agent.flow_modifier.thresholds["max_calls_per_minute"] = 15
        
        agent.cycle_count += 1
```

## 5. Benefícios da Abordagem

### 5.1 Adaptação em Tempo Real
- O sistema ajusta dinamicamente sem precisar modificar código
- Decisões baseadas em contexto atual e histórico
- Aprendizado contínuo dos padrões

### 5.2 Redução de Custos Inteligente
- Skip automático de calls desnecessárias
- Downgrade para modelos menores quando apropriado
- Batching e paralelização automáticos

### 5.3 Resiliência
- Sistema continua funcionando mesmo com limitações
- Adaptação automática a falhas repetidas
- Priorização inteligente de calls

### 5.4 Transparência
- Todas as decisões são logadas
- Relatórios detalhados de otimização
- Fácil debugging e ajuste

## 6. Próximos Passos

1. **Implementar o decorador @optimize_llm_call** em todos os agentes
2. **Adicionar métricas de performance** em cada call
3. **Treinar o meta-decisor** com dados reais
4. **Implementar persistência** das decisões de otimização
5. **Criar dashboard** para visualizar otimizações em tempo real

Este sistema permite que o Hephaestus se torne verdadeiramente autônomo e adaptativo, otimizando seu próprio funcionamento baseado em condições reais! 