# Análise de Otimização das Chamadas ao LLM no Sistema Hephaestus

## 1. Mapeamento Atual das Chamadas ao LLM

### 1.1 Fluxo Principal de Execução

O sistema atualmente faz as seguintes chamadas ao LLM em cada ciclo:

1. **Generate Next Objective** (`brain.py`)
   - **Quando**: Início de cada ciclo ou quando a fila está vazia
   - **Propósito**: Gerar novo objetivo baseado no contexto
   - **Temperatura**: 0.3
   - **Crítico**: Sim - define a direção do ciclo

2. **Architect Plan Action** (`architect_agent.py`)
   - **Quando**: Sempre após ter um objetivo
   - **Propósito**: Criar plano de patches
   - **Temperatura**: 0.4
   - **Crítico**: Sim - gera as modificações

3. **Code Review** (`code_review_agent.py`)
   - **Quando**: Sempre após o Architect (se houver patches)
   - **Propósito**: Revisar qualidade do código
   - **Temperatura**: 0.2
   - **Crítico**: Parcial - pode ser otimizado

4. **Maestro Choose Strategy** (`maestro_agent.py`)
   - **Quando**: Sempre após aprovação do código
   - **Propósito**: Escolher estratégia de validação
   - **Temperatura**: 0.2
   - **Crítico**: Sim - define como validar

### 1.2 Chamadas Condicionais

5. **Error Analysis** (`error_analyzer.py`)
   - **Quando**: Após falhas
   - **Propósito**: Analisar e sugerir correções
   - **Temperatura**: 0.3
   - **Crítico**: Sim quando ocorre

6. **Prompt Optimizer** (`prompt_optimizer.py`)
   - **Quando**: Após múltiplas falhas similares
   - **Propósito**: Otimizar prompts que falharam
   - **Temperatura**: 0.3-0.4
   - **Crítico**: Para evolução RSI

7. **Performance Analysis** (`performance_analyzer.py`)
   - **Quando**: Periodicamente
   - **Propósito**: Analisar métricas de desempenho
   - **Temperatura**: 0.3
   - **Crítico**: Para evolução

8. **Self Reflection** (`self_reflection_agent.py`)
   - **Quando**: Sob demanda
   - **Propósito**: Auto-análise do código
   - **Temperatura**: 0.4
   - **Crítico**: Para RSI

## 2. Problemas Identificados

### 2.1 Excesso de Chamadas Sequenciais
- **Problema**: Muitas chamadas são feitas em sequência desnecessariamente
- **Impacto**: Latência alta, custo elevado
- **Exemplo**: Code Review sempre após Architect

### 2.2 Falta de Cache Inteligente
- **Problema**: Objetivos similares geram novas chamadas
- **Impacto**: Desperdício de recursos
- **Solução**: Cache baseado em similaridade

### 2.3 Prompts Não Otimizados
- **Problema**: Prompts muito longos com informação redundante
- **Impacto**: Tokens desperdiçados, respostas menos focadas
- **Solução**: Compressão contextual

### 2.4 Falta de Paralelização
- **Problema**: Algumas análises poderiam ser paralelas
- **Impacto**: Tempo de ciclo maior
- **Exemplo**: Performance Analysis poderia rodar em paralelo

## 3. Oportunidades de Otimização

### 3.1 Otimizações Imediatas

#### A. Implementar Rule-Based Pre-Filtering
```python
# Adicionar em code_review_agent.py
def needs_review(self, patches: List[Dict]) -> bool:
    """Determina se os patches precisam de revisão LLM"""
    # Skip review para mudanças triviais
    trivial_patterns = [
        r'^import\s+',  # Apenas imports
        r'^#.*$',       # Apenas comentários
        r'^\s*$',       # Linhas vazias
    ]
    
    for patch in patches:
        content = patch.get('content', '')
        if not any(re.match(pattern, content) for pattern in trivial_patterns):
            return True
    return False
```

#### B. Cache de Decisões do Maestro
```python
# Adicionar em maestro_agent.py
class StrategyCache:
    def __init__(self, ttl_seconds=3600):
        self.cache = {}
        self.ttl = ttl_seconds
    
    def get_cached_strategy(self, action_plan_hash: str) -> Optional[str]:
        if action_plan_hash in self.cache:
            timestamp, strategy = self.cache[action_plan_hash]
            if time.time() - timestamp < self.ttl:
                return strategy
        return None
```

#### C. Batch de Análises Não-Críticas
```python
# Adicionar em hephaestus_agent.py
def batch_analysis_calls(self):
    """Agrupa análises não-críticas para executar em paralelo"""
    analysis_tasks = []
    
    if self.should_run_performance_analysis():
        analysis_tasks.append(('performance', self.run_performance_analysis))
    
    if self.should_run_self_reflection():
        analysis_tasks.append(('reflection', self.run_self_reflection))
    
    # Executar em threads paralelas
    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = {executor.submit(task): name for name, task in analysis_tasks}
        results = {}
        for future in as_completed(futures):
            name = futures[future]
            results[name] = future.result()
    
    return results
```

### 3.2 Otimizações Avançadas

#### A. Prompt Compression Pipeline
```python
class PromptCompressor:
    """Comprime prompts mantendo informação essencial"""
    
    def compress_context(self, context: str, max_tokens: int = 1000) -> str:
        # 1. Remove duplicatas
        # 2. Sumariza seções longas
        # 3. Prioriza informação recente
        # 4. Mantém apenas failures relevantes
        pass
```

#### B. Adaptive Temperature Control
```python
def get_adaptive_temperature(self, agent_type: str, failure_count: int) -> float:
    """Ajusta temperatura baseado no histórico"""
    base_temps = {
        'architect': 0.4,
        'maestro': 0.2,
        'error_analyzer': 0.3
    }
    
    # Aumenta temperatura após falhas para mais criatividade
    temp = base_temps.get(agent_type, 0.3)
    if failure_count > 2:
        temp = min(temp + 0.1 * (failure_count - 2), 0.8)
    
    return temp
```

#### C. Multi-Model Strategy
```python
class ModelSelector:
    """Seleciona modelo baseado na complexidade da tarefa"""
    
    def select_model(self, task_type: str, complexity: str) -> str:
        model_matrix = {
            'simple': {
                'review': 'gpt-3.5-turbo',
                'strategy': 'gpt-3.5-turbo',
            },
            'complex': {
                'architect': 'gpt-4',
                'error_analysis': 'gpt-4',
            }
        }
        
        return model_matrix.get(complexity, {}).get(task_type, 'gpt-3.5-turbo')
```

### 3.3 Implementação de Plasticidade Evolutiva

#### A. Dynamic Agent Creation
```python
class DynamicAgentFactory:
    """Cria novos agentes baseado em necessidades emergentes"""
    
    def analyze_need_for_new_agent(self, failure_patterns: Dict) -> Optional[Dict]:
        # Analisa padrões de falha
        # Identifica gaps funcionais
        # Propõe novo agente especializado
        pass
    
    def create_specialized_agent(self, spec: Dict) -> 'BaseAgent':
        # Gera código do novo agente
        # Integra no pipeline
        # Adiciona testes
        pass
```

#### B. Prompt Evolution System
```python
class PromptEvolution:
    """Sistema de evolução genética de prompts"""
    
    def __init__(self):
        self.population = []  # População de prompts
        self.fitness_scores = {}
    
    def mutate_prompt(self, prompt: str) -> str:
        # Aplica mutações pequenas
        mutations = [
            self.add_clarification,
            self.remove_redundancy,
            self.restructure_sections,
            self.adjust_tone
        ]
        
        mutation = random.choice(mutations)
        return mutation(prompt)
    
    def crossover(self, prompt1: str, prompt2: str) -> str:
        # Combina elementos de sucesso de dois prompts
        pass
    
    def evolve_generation(self):
        # Seleciona melhores
        # Aplica mutações
        # Testa nova geração
        pass
```

## 4. Plano de Implementação

### Fase 1: Otimizações Imediatas (1-2 dias)
1. Implementar rule-based filtering no Code Review
2. Adicionar cache básico no Maestro
3. Criar batch processing para análises não-críticas

### Fase 2: Otimizações Intermediárias (3-5 dias)
1. Implementar prompt compression
2. Adicionar adaptive temperature
3. Criar multi-model strategy

### Fase 3: Plasticidade Evolutiva (1-2 semanas)
1. Desenvolver dynamic agent creation
2. Implementar prompt evolution system
3. Criar self-modification capabilities

## 5. Métricas de Sucesso

### 5.1 Redução de Custos
- **Meta**: Reduzir chamadas ao LLM em 40%
- **Como**: Cache + filtering + batching

### 5.2 Melhoria de Performance
- **Meta**: Reduzir tempo de ciclo em 30%
- **Como**: Paralelização + modelos apropriados

### 5.3 Aumento de Taxa de Sucesso
- **Meta**: Aumentar taxa de sucesso em 25%
- **Como**: Prompts otimizados + temperatura adaptativa

### 5.4 Evolução Autônoma
- **Meta**: Sistema capaz de criar novos agentes
- **Como**: Dynamic agent factory + prompt evolution

## 6. Código de Exemplo: Otimizador de Chamadas

```python
# agent/llm_optimizer.py
class LLMCallOptimizer:
    """Otimiza chamadas ao LLM do sistema"""
    
    def __init__(self, config: Dict, logger: logging.Logger):
        self.config = config
        self.logger = logger
        self.call_history = []
        self.cache = TTLCache(maxsize=100, ttl=3600)
        
    def should_make_call(self, agent_type: str, context: Dict) -> bool:
        """Decide se deve fazer chamada ao LLM"""
        # 1. Verifica cache
        cache_key = self._generate_cache_key(agent_type, context)
        if cache_key in self.cache:
            self.logger.info(f"Cache hit for {agent_type}")
            return False
        
        # 2. Verifica regras
        if agent_type == 'code_review':
            patches = context.get('patches', [])
            if self._are_patches_trivial(patches):
                self.logger.info("Skipping code review for trivial patches")
                return False
        
        # 3. Verifica rate limiting
        if self._exceeds_rate_limit(agent_type):
            self.logger.warning(f"Rate limit exceeded for {agent_type}")
            return False
        
        return True
    
    def optimize_prompt(self, prompt: str, agent_type: str) -> str:
        """Otimiza prompt antes de enviar"""
        # 1. Remove redundâncias
        prompt = self._remove_redundancies(prompt)
        
        # 2. Comprime contexto histórico
        prompt = self._compress_history(prompt)
        
        # 3. Prioriza informação relevante
        prompt = self._prioritize_content(prompt, agent_type)
        
        return prompt
    
    def record_call(self, agent_type: str, context: Dict, 
                   response: str, success: bool):
        """Registra chamada para análise futura"""
        self.call_history.append({
            'timestamp': datetime.now(),
            'agent_type': agent_type,
            'context_hash': self._hash_context(context),
            'response_length': len(response),
            'success': success,
            'tokens_used': self._estimate_tokens(context, response)
        })
        
        # Adiciona ao cache se sucesso
        if success:
            cache_key = self._generate_cache_key(agent_type, context)
            self.cache[cache_key] = response
    
    def get_optimization_report(self) -> Dict:
        """Gera relatório de otimização"""
        total_calls = len(self.call_history)
        cache_hits = sum(1 for call in self.call_history if call.get('cache_hit'))
        
        return {
            'total_calls': total_calls,
            'cache_hit_rate': cache_hits / total_calls if total_calls > 0 else 0,
            'calls_by_agent': self._group_by_agent(),
            'token_usage': self._calculate_token_usage(),
            'optimization_suggestions': self._generate_suggestions()
        }
```

## 7. Conclusão

A otimização das chamadas ao LLM é crucial para a evolução e eficiência do sistema Hephaestus. As sugestões apresentadas visam:

1. **Reduzir custos** através de cache e filtering inteligente
2. **Melhorar performance** com paralelização e batching
3. **Aumentar inteligência** com prompts evolutivos e temperatura adaptativa
4. **Habilitar plasticidade** com criação dinâmica de agentes

A implementação deve ser gradual, começando pelas otimizações mais simples e evoluindo para as mais complexas, sempre medindo o impacto em cada fase. 