"""
🧬 DYNAMIC AGENT DNA SYSTEM
Sistema onde cada agente tem DNA cognitivo que evolui através de seleção natural - a 8ª meta-funcionalidade!

Este sistema implementa evolução darwiniana para agentes através de:
- Genetic Code: Código genético que define características cognitivas
- Natural Selection: Seleção natural baseada em performance
- Genetic Mutations: Mutações genéticas de estratégias e comportamentos
- Inheritance: Herança de características de alto desempenho
- Speciation: Criação de novas "espécies" de agentes
- Fitness Evolution: Evolução contínua baseada em fitness cognitivo

É literalmente darwinismo aplicado à inteligência artificial!
"""

import json
import logging
import time
import threading
import random
import hashlib
import copy
from typing import Dict, Any, List, Optional, Tuple, Set
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict, deque
from enum import Enum
import statistics
import numpy as np
from abc import ABC, abstractmethod

class GeneType(Enum):
    """Tipos de genes cognitivos"""
    STRATEGY = "strategy"               # Estratégias de resolução
    BEHAVIOR = "behavior"               # Padrões comportamentais
    LEARNING = "learning"               # Características de aprendizado
    DECISION = "decision"               # Estilo de tomada de decisão
    COMMUNICATION = "communication"     # Padrões de comunicação
    CREATIVITY = "creativity"           # Níveis de criatividade
    RISK_TOLERANCE = "risk_tolerance"   # Tolerância a risco
    ADAPTATION = "adaptation"           # Capacidade de adaptação

class SelectionPressure(Enum):
    """Pressões de seleção natural"""
    PERFORMANCE = "performance"         # Performance em tarefas
    EFFICIENCY = "efficiency"           # Eficiência energética
    RELIABILITY = "reliability"         # Confiabilidade
    INNOVATION = "innovation"           # Capacidade de inovação
    COLLABORATION = "collaboration"     # Habilidades colaborativas
    SURVIVAL = "survival"               # Taxa de sobrevivência

@dataclass
class CognitiveGene:
    """Gene cognitivo individual"""
    gene_id: str
    gene_type: GeneType
    allele_value: float  # Valor entre 0.0 e 1.0
    dominance: float     # Dominância do gene (0.0 = recessivo, 1.0 = dominante)
    mutation_rate: float = 0.05
    expression_level: float = 1.0
    
    def mutate(self, mutation_strength: float = 0.1) -> 'CognitiveGene':
        """Aplica mutação ao gene"""
        if random.random() < self.mutation_rate:
            # Mutação do valor do alelo
            mutation_delta = random.gauss(0, mutation_strength)
            new_value = max(0.0, min(1.0, self.allele_value + mutation_delta))
            
            # Mutação da dominância
            dominance_delta = random.gauss(0, mutation_strength * 0.5)
            new_dominance = max(0.0, min(1.0, self.dominance + dominance_delta))
            
            return CognitiveGene(
                gene_id=self.gene_id,
                gene_type=self.gene_type,
                allele_value=new_value,
                dominance=new_dominance,
                mutation_rate=self.mutation_rate,
                expression_level=self.expression_level
            )
        return copy.deepcopy(self)
    
    def crossover(self, other: 'CognitiveGene') -> Tuple['CognitiveGene', 'CognitiveGene']:
        """Realiza crossover genético com outro gene"""
        # Determinar qual gene é dominante
        if self.dominance > other.dominance:
            dominant, recessive = self, other
        else:
            dominant, recessive = other, self
        
        # Criar descendentes através de recombinação
        child1_value = dominant.allele_value * 0.7 + recessive.allele_value * 0.3
        child2_value = recessive.allele_value * 0.7 + dominant.allele_value * 0.3
        
        child1 = CognitiveGene(
            gene_id=f"{self.gene_id}_x_{other.gene_id}",
            gene_type=self.gene_type,
            allele_value=child1_value,
            dominance=(self.dominance + other.dominance) / 2,
            mutation_rate=(self.mutation_rate + other.mutation_rate) / 2,
            expression_level=max(self.expression_level, other.expression_level)
        )
        
        child2 = CognitiveGene(
            gene_id=f"{other.gene_id}_x_{self.gene_id}",
            gene_type=other.gene_type,
            allele_value=child2_value,
            dominance=(self.dominance + other.dominance) / 2,
            mutation_rate=(self.mutation_rate + other.mutation_rate) / 2,
            expression_level=min(self.expression_level, other.expression_level)
        )
        
        return child1, child2

@dataclass
class AgentDNA:
    """DNA cognitivo completo de um agente"""
    dna_id: str
    agent_type: str
    generation: int
    genes: Dict[GeneType, CognitiveGene] = field(default_factory=dict)
    fitness_history: List[float] = field(default_factory=list)
    creation_time: datetime = field(default_factory=datetime.now)
    parent_dnas: List[str] = field(default_factory=list)
    mutation_count: int = 0
    
    def get_phenotype(self) -> Dict[str, float]:
        """Calcula fenótipo (características expressas) a partir do genótipo"""
        phenotype = {}
        
        for gene_type, gene in self.genes.items():
            expressed_value = gene.allele_value * gene.expression_level * gene.dominance
            phenotype[gene_type.value] = expressed_value
        
        return phenotype
    
    def calculate_fitness(self, performance_metrics: Dict[str, float]) -> float:
        """Calcula fitness baseado em métricas de performance"""
        phenotype = self.get_phenotype()
        
        # Fitness multidimensional
        fitness_components = {
            'performance': performance_metrics.get('success_rate', 0.0) * 0.3,
            'efficiency': performance_metrics.get('efficiency', 0.0) * 0.2,
            'reliability': performance_metrics.get('reliability', 0.0) * 0.2,
            'innovation': performance_metrics.get('innovation_score', 0.0) * 0.15,
            'adaptation': performance_metrics.get('adaptation_rate', 0.0) * 0.15
        }
        
        # Modificar fitness baseado no fenótipo
        for component, base_score in fitness_components.items():
            if component in phenotype:
                # Genes influenciam o fitness
                gene_influence = phenotype[component]
                fitness_components[component] = base_score * (0.5 + gene_influence * 0.5)
        
        total_fitness = sum(fitness_components.values())
        self.fitness_history.append(total_fitness)
        
        return total_fitness
    
    def get_average_fitness(self) -> float:
        """Retorna fitness médio histórico"""
        return statistics.mean(self.fitness_history) if self.fitness_history else 0.0
    
    def mutate(self, mutation_rate: float = 0.1) -> 'AgentDNA':
        """Cria versão mutada do DNA"""
        mutated_genes = {}
        
        for gene_type, gene in self.genes.items():
            mutated_genes[gene_type] = gene.mutate(mutation_rate)
        
        mutated_dna = AgentDNA(
            dna_id=f"{self.dna_id}_mut_{int(time.time())}",
            agent_type=self.agent_type,
            generation=self.generation + 1,
            genes=mutated_genes,
            parent_dnas=[self.dna_id],
            mutation_count=self.mutation_count + 1
        )
        
        return mutated_dna
    
    def reproduce_with(self, other: 'AgentDNA') -> 'AgentDNA':
        """Reprodução sexual - cria descendente com outro DNA"""
        child_genes = {}
        
        # Combinar genes dos pais
        all_gene_types = set(self.genes.keys()) | set(other.genes.keys())
        
        for gene_type in all_gene_types:
            if gene_type in self.genes and gene_type in other.genes:
                # Crossover entre genes correspondentes
                child_gene1, child_gene2 = self.genes[gene_type].crossover(other.genes[gene_type])
                # Escolher um dos filhos aleatoriamente
                child_genes[gene_type] = random.choice([child_gene1, child_gene2])
            elif gene_type in self.genes:
                # Herdar gene do primeiro pai
                child_genes[gene_type] = copy.deepcopy(self.genes[gene_type])
            else:
                # Herdar gene do segundo pai
                child_genes[gene_type] = copy.deepcopy(other.genes[gene_type])
        
        child_dna = AgentDNA(
            dna_id=f"{self.dna_id}_x_{other.dna_id}_{int(time.time())}",
            agent_type=self.agent_type,  # Herda tipo do primeiro pai
            generation=max(self.generation, other.generation) + 1,
            genes=child_genes,
            parent_dnas=[self.dna_id, other.dna_id]
        )
        
        return child_dna

@dataclass
class PopulationStats:
    """Estatísticas da população"""
    generation: int
    population_size: int
    average_fitness: float
    max_fitness: float
    min_fitness: float
    genetic_diversity: float
    dominant_genes: Dict[str, str]
    extinction_events: int = 0
    speciation_events: int = 0

class DynamicAgentDNA:
    """
    🧬 Dynamic Agent DNA System - Evolução darwiniana para agentes
    
    Este sistema implementa seleção natural verdadeira para agentes através de:
    1. Genetic Encoding: Codificação de características em genes
    2. Natural Selection: Seleção baseada em fitness
    3. Genetic Reproduction: Reprodução sexual e assexual
    4. Mutation & Evolution: Mutação e evolução contínua
    5. Speciation: Emergência de novas "espécies" de agentes
    """
    
    def __init__(self, config: Dict[str, Any], logger: logging.Logger):
        self.config = config
        self.logger = logger.getChild("DynamicAgentDNA")
        
        # Configuration - com valores seguros por padrão
        dna_config = config.get("dynamic_agent_dna", {})
        self.enabled = dna_config.get("enabled", True)
        self.population_size = dna_config.get("population_size", 50)
        self.mutation_rate = dna_config.get("mutation_rate", 0.1)
        self.selection_pressure = dna_config.get("selection_pressure", 0.3)
        self.reproduction_rate = dna_config.get("reproduction_rate", 0.2)
        self.generation_interval = dna_config.get("generation_interval", 3600)  # 1 hora
        self.fitness_threshold = dna_config.get("fitness_threshold", 0.6)
        self.genetic_diversity_target = dna_config.get("genetic_diversity_target", 0.7)
        
        # Data storage
        self.data_dir = Path("data/intelligence/dna")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Population state
        self.agent_populations: Dict[str, List[AgentDNA]] = defaultdict(list)
        self.generation_number = 0
        self.population_history: List[PopulationStats] = []
        
        # Evolution tracking
        self.evolution_analytics = {
            "total_generations": 0,
            "total_mutations": 0,
            "successful_reproductions": 0,
            "extinction_events": 0,
            "speciation_events": 0,
            "average_fitness_trend": [],
            "genetic_diversity_trend": [],
            "dominant_gene_history": []
        }
        
        # Threading
        self.should_stop = threading.Event()
        self.evolution_thread = None
        
        # Load existing data
        self._load_population_data()
        
        # Initialize
        if self.enabled:
            self._initialize_base_population()
            self._start_evolution_engine()
            self.logger.info("🧬 Dynamic Agent DNA System initialized!")
            self.logger.info(f"👥 Population size: {self.population_size}")
            self.logger.info(f"🧬 Active agent types: {list(self.agent_populations.keys())}")
        else:
            self.logger.info("⚠️ Dynamic Agent DNA System disabled in configuration")
    
    def register_agent_type(self, agent_type: str, base_characteristics: Dict[str, float]) -> AgentDNA:
        """Registra novo tipo de agente e cria DNA base"""
        if not self.enabled:
            return None
        
        self.logger.info(f"🧬 Registering new agent type: {agent_type}")
        
        # Criar genes base a partir das características
        base_genes = {}
        
        for gene_type in GeneType:
            if gene_type.value in base_characteristics:
                gene_value = base_characteristics[gene_type.value]
            else:
                gene_value = random.uniform(0.3, 0.7)  # Valor médio para genes não especificados
            
            gene = CognitiveGene(
                gene_id=f"{agent_type}_{gene_type.value}_base",
                gene_type=gene_type,
                allele_value=gene_value,
                dominance=random.uniform(0.4, 0.8),
                mutation_rate=self.mutation_rate
            )
            
            base_genes[gene_type] = gene
        
        # Criar DNA base
        base_dna = AgentDNA(
            dna_id=f"{agent_type}_base_gen0",
            agent_type=agent_type,
            generation=0,
            genes=base_genes
        )
        
        # Inicializar população
        if agent_type not in self.agent_populations:
            self.agent_populations[agent_type] = []
        
        # Criar população inicial através de mutações do DNA base
        for i in range(min(10, self.population_size // 5)):  # População inicial menor
            if i == 0:
                # Primeiro indivíduo é o DNA base
                self.agent_populations[agent_type].append(base_dna)
            else:
                # Outros são variações mutadas
                mutated_dna = base_dna.mutate(mutation_rate=0.2)
                mutated_dna.dna_id = f"{agent_type}_init_{i}_gen0"
                self.agent_populations[agent_type].append(mutated_dna)
        
        self.logger.info(f"✅ Agent type {agent_type} registered with {len(self.agent_populations[agent_type])} initial DNAs")
        
        return base_dna
    
    def evolve_agent(self, agent_type: str, performance_metrics: Dict[str, float]) -> Optional[AgentDNA]:
        """Evolui agente baseado em performance"""
        if not self.enabled or agent_type not in self.agent_populations:
            return None
        
        population = self.agent_populations[agent_type]
        if not population:
            return None
        
        # Calcular fitness para toda a população
        fitness_scores = []
        for dna in population:
            fitness = dna.calculate_fitness(performance_metrics)
            fitness_scores.append((dna, fitness))
        
        # Ordenar por fitness (maior é melhor)
        fitness_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Seleção natural - eliminar os menos aptos
        selection_cutoff = int(len(fitness_scores) * (1 - self.selection_pressure))
        survivors = [dna for dna, fitness in fitness_scores[:selection_cutoff]]
        
        # Reprodução - criar nova geração
        new_generation = []
        
        # Elitismo - manter os melhores
        elite_count = max(1, len(survivors) // 5)
        new_generation.extend(survivors[:elite_count])
        
        # Reprodução sexual
        reproduction_count = int(len(survivors) * self.reproduction_rate)
        for _ in range(reproduction_count):
            if len(survivors) >= 2:
                parent1, parent2 = random.sample(survivors, 2)
                child = parent1.reproduce_with(parent2)
                new_generation.append(child)
        
        # Mutação
        mutation_count = int(len(survivors) * self.mutation_rate)
        for _ in range(mutation_count):
            parent = random.choice(survivors)
            mutated_child = parent.mutate(self.mutation_rate)
            new_generation.append(mutated_child)
        
        # Atualizar população
        self.agent_populations[agent_type] = new_generation
        
        # Retornar o melhor DNA atual
        best_dna = fitness_scores[0][0] if fitness_scores else None
        
        if best_dna:
            self.logger.info(f"🧬 Evolved {agent_type}: Gen {best_dna.generation}, Fitness {fitness_scores[0][1]:.3f}")
        
        return best_dna
    
    def record_agent_performance(self, agent_type: str, dna_id: str, fitness_score: float, 
                               performance_data: Dict[str, Any]) -> bool:
        """Registra performance real de um agente para evolução genética"""
        if not self.enabled:
            return False
        
        try:
            # Encontrar o DNA específico
            population = self.agent_populations.get(agent_type, [])
            target_dna = None
            
            for dna in population:
                if dna.dna_id == dna_id:
                    target_dna = dna
                    break
            
            if not target_dna:
                self.logger.warning(f"DNA {dna_id} not found for agent {agent_type}")
                return False
            
            # Registrar fitness score
            target_dna.fitness_history.append(fitness_score)
            
            # Limitar histórico de fitness (manter últimos 50 registros)
            if len(target_dna.fitness_history) > 50:
                target_dna.fitness_history = target_dna.fitness_history[-50:]
            
            # Atualizar analytics de evolução
            self.evolution_analytics["fitness_records"] = self.evolution_analytics.get("fitness_records", 0) + 1
            self.evolution_analytics["average_fitness"] = statistics.mean([
                fitness for dna in population for fitness in dna.fitness_history[-10:]
            ]) if population else 0.0
            
            # Registrar evento na log
            self.logger.debug(f"📊 Recorded performance for {agent_type} DNA {dna_id}: fitness={fitness_score:.3f}")
            
            # Salvar dados periodicamente
            if self.evolution_analytics["fitness_records"] % 10 == 0:
                self._save_population_data()
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error recording agent performance: {e}")
            return False
    
    def get_best_dna(self, agent_type: str) -> Optional[AgentDNA]:
        """Retorna o melhor DNA de um tipo de agente"""
        if not self.enabled or agent_type not in self.agent_populations:
            return None
        
        population = self.agent_populations[agent_type]
        if not population:
            return None
        
        # Retornar DNA com maior fitness médio
        best_dna = max(population, key=lambda dna: dna.get_average_fitness())
        return best_dna
    
    def analyze_genetic_diversity(self, agent_type: str) -> float:
        """Analisa diversidade genética da população"""
        if not self.enabled or agent_type not in self.agent_populations:
            return 0.0
        
        population = self.agent_populations[agent_type]
        if len(population) < 2:
            return 0.0
        
        # Calcular diversidade baseada na variação dos valores dos genes
        gene_variations = defaultdict(list)
        
        for dna in population:
            for gene_type, gene in dna.genes.items():
                gene_variations[gene_type].append(gene.allele_value)
        
        # Calcular desvio padrão médio como medida de diversidade
        diversities = []
        for gene_type, values in gene_variations.items():
            if len(values) > 1:
                diversity = statistics.stdev(values)
                diversities.append(diversity)
        
        average_diversity = statistics.mean(diversities) if diversities else 0.0
        return min(1.0, average_diversity * 2)  # Normalizar para 0-1
    
    def create_hybrid_species(self, agent_type1: str, agent_type2: str) -> Optional[str]:
        """Cria nova espécie híbrida entre dois tipos de agentes"""
        if not self.enabled:
            return None
        
        if (agent_type1 not in self.agent_populations or 
            agent_type2 not in self.agent_populations):
            return None
        
        best_dna1 = self.get_best_dna(agent_type1)
        best_dna2 = self.get_best_dna(agent_type2)
        
        if not best_dna1 or not best_dna2:
            return None
        
        # Criar híbrido
        hybrid_type = f"{agent_type1}_{agent_type2}_hybrid"
        hybrid_dna = best_dna1.reproduce_with(best_dna2)
        hybrid_dna.agent_type = hybrid_type
        hybrid_dna.dna_id = f"{hybrid_type}_founder"
        
        # Inicializar nova população híbrida
        self.agent_populations[hybrid_type] = [hybrid_dna]
        
        # Criar população inicial através de mutações
        for i in range(5):
            mutated_hybrid = hybrid_dna.mutate(0.15)
            mutated_hybrid.dna_id = f"{hybrid_type}_init_{i}"
            self.agent_populations[hybrid_type].append(mutated_hybrid)
        
        self.evolution_analytics["speciation_events"] += 1
        
        self.logger.info(f"🧬 Created hybrid species: {hybrid_type}")
        
        return hybrid_type
    
    def _initialize_base_population(self):
        """Inicializa população base se não existir"""
        if not self.agent_populations:
            # Criar tipos de agentes base
            base_agent_types = {
                "architect": {
                    "strategy": 0.8,
                    "creativity": 0.9,
                    "decision": 0.7,
                    "risk_tolerance": 0.4
                },
                "maestro": {
                    "strategy": 0.9,
                    "decision": 0.8,
                    "communication": 0.8,
                    "adaptation": 0.7
                },
                "bug_hunter": {
                    "behavior": 0.8,
                    "reliability": 0.9,
                    "efficiency": 0.7,
                    "adaptation": 0.6
                }
            }
            
            for agent_type, characteristics in base_agent_types.items():
                self.register_agent_type(agent_type, characteristics)
    
    def _start_evolution_engine(self):
        """Inicia engine de evolução em background"""
        self.evolution_thread = threading.Thread(target=self._evolution_loop, daemon=True)
        self.evolution_thread.start()
        self.logger.info("🔄 Evolution engine started")
    
    def _evolution_loop(self):
        """Loop principal de evolução"""
        while not self.should_stop.wait(self.generation_interval):
            try:
                self._advance_generation()
            except Exception as e:
                self.logger.error(f"❌ Error in evolution loop: {e}")
    
    def _advance_generation(self):
        """Avança uma geração completa"""
        if not self.agent_populations:
            return
        
        self.generation_number += 1
        self.logger.info(f"🧬 Advancing to generation {self.generation_number}")
        
        # Evoluir cada tipo de agente
        for agent_type in list(self.agent_populations.keys()):
            population = self.agent_populations[agent_type]
            
            if not population:
                continue
            
            # Simular performance baseada no fenótipo
            avg_performance = self._simulate_population_performance(agent_type)
            
            # Aplicar pressões de seleção
            self._apply_selection_pressure(agent_type, avg_performance)
            
            # Verificar diversidade genética
            diversity = self.analyze_genetic_diversity(agent_type)
            
            if diversity < self.genetic_diversity_target:
                self._introduce_genetic_diversity(agent_type)
        
        # Registrar estatísticas da geração
        self._record_generation_stats()
        
        # Verificar especiação
        if self.generation_number % 5 == 0:  # A cada 5 gerações
            self._check_for_speciation()
        
        self.evolution_analytics["total_generations"] += 1
    
    def _simulate_population_performance(self, agent_type: str) -> Dict[str, float]:
        """Simula performance da população baseada no fenótipo médio"""
        population = self.agent_populations[agent_type]
        
        # Calcular fenótipo médio da população
        phenotype_sums = defaultdict(float)
        
        for dna in population:
            phenotype = dna.get_phenotype()
            for trait, value in phenotype.items():
                phenotype_sums[trait] += value
        
        avg_phenotype = {
            trait: value / len(population) 
            for trait, value in phenotype_sums.items()
        }
        
        # Simular métricas de performance baseadas no fenótipo
        performance = {
            "success_rate": avg_phenotype.get("strategy", 0.5) * 0.6 + avg_phenotype.get("decision", 0.5) * 0.4,
            "efficiency": avg_phenotype.get("efficiency", 0.5) * 0.7 + avg_phenotype.get("adaptation", 0.5) * 0.3,
            "reliability": avg_phenotype.get("reliability", 0.5) * 0.8 + avg_phenotype.get("behavior", 0.5) * 0.2,
            "innovation_score": avg_phenotype.get("creativity", 0.5) * 0.9 + avg_phenotype.get("risk_tolerance", 0.5) * 0.1,
            "adaptation_rate": avg_phenotype.get("adaptation", 0.5) * 0.8 + avg_phenotype.get("learning", 0.5) * 0.2
        }
        
        # Adicionar ruído realístico
        for metric in performance:
            noise = random.gauss(0, 0.1)
            performance[metric] = max(0.0, min(1.0, performance[metric] + noise))
        
        return performance
    
    def _apply_selection_pressure(self, agent_type: str, performance_metrics: Dict[str, float]):
        """Aplica pressão de seleção natural"""
        population = self.agent_populations[agent_type]
        
        # Calcular fitness para cada indivíduo
        fitness_scores = []
        for dna in population:
            fitness = dna.calculate_fitness(performance_metrics)
            fitness_scores.append((dna, fitness))
        
        # Seleção baseada em fitness
        fitness_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Eliminar os menos aptos
        survival_count = max(5, int(len(fitness_scores) * (1 - self.selection_pressure)))
        survivors = [dna for dna, fitness in fitness_scores[:survival_count]]
        
        # Reprodução para manter tamanho da população
        target_size = min(self.population_size, len(population) + 5)
        
        while len(survivors) < target_size:
            if len(survivors) >= 2:
                # Reprodução sexual favorecendo os mais aptos
                weights = [i + 1 for i in range(len(survivors))]  # Peso maior para os primeiros
                parents = random.choices(survivors, weights=weights[::-1], k=2)
                
                if parents[0] != parents[1]:
                    child = parents[0].reproduce_with(parents[1])
                    survivors.append(child)
                    self.evolution_analytics["successful_reproductions"] += 1
                else:
                    # Mutação se os pais são iguais
                    mutated = parents[0].mutate()
                    survivors.append(mutated)
                    self.evolution_analytics["total_mutations"] += 1
            else:
                # Mutação se população muito pequena
                if survivors:
                    mutated = random.choice(survivors).mutate()
                    survivors.append(mutated)
                    self.evolution_analytics["total_mutations"] += 1
                else:
                    break
        
        # Atualizar população
        self.agent_populations[agent_type] = survivors[:target_size]
    
    def _introduce_genetic_diversity(self, agent_type: str):
        """Introduz diversidade genética quando necessário"""
        population = self.agent_populations[agent_type]
        
        # Criar novos indivíduos através de mutação forte
        diversity_boost_count = max(2, len(population) // 10)
        
        for _ in range(diversity_boost_count):
            if population:
                # Mutação com taxa alta para criar diversidade
                base_dna = random.choice(population)
                diverse_dna = base_dna.mutate(mutation_rate=0.3)
                diverse_dna.dna_id = f"{agent_type}_diverse_{int(time.time())}"
                population.append(diverse_dna)
        
        self.logger.info(f"🧬 Introduced genetic diversity to {agent_type}")
    
    def _check_for_speciation(self):
        """Verifica se deve criar novas espécies"""
        agent_types = list(self.agent_populations.keys())
        
        # Tentativa de hibridização entre tipos compatíveis
        if len(agent_types) >= 2:
            type1, type2 = random.sample(agent_types, 2)
            
            # Verificar se hibridização faz sentido
            if (self.analyze_genetic_diversity(type1) > 0.8 and 
                self.analyze_genetic_diversity(type2) > 0.8):
                
                hybrid_type = self.create_hybrid_species(type1, type2)
                if hybrid_type:
                    self.logger.info(f"🧬 Speciation event: Created {hybrid_type}")
    
    def _record_generation_stats(self):
        """Registra estatísticas da geração atual"""
        total_population = sum(len(pop) for pop in self.agent_populations.values())
        
        if total_population == 0:
            return
        
        # Calcular estatísticas agregadas
        all_fitness = []
        all_diversities = []
        dominant_genes = {}
        
        for agent_type, population in self.agent_populations.items():
            if population:
                # Fitness
                type_fitness = [dna.get_average_fitness() for dna in population if dna.fitness_history]
                all_fitness.extend(type_fitness)
                
                # Diversidade
                diversity = self.analyze_genetic_diversity(agent_type)
                all_diversities.append(diversity)
                
                # Genes dominantes
                best_dna = self.get_best_dna(agent_type)
                if best_dna:
                    phenotype = best_dna.get_phenotype()
                    for trait, value in phenotype.items():
                        if trait not in dominant_genes or value > dominant_genes[trait]:
                            dominant_genes[trait] = value
        
        # Criar estatísticas da população
        stats = PopulationStats(
            generation=self.generation_number,
            population_size=total_population,
            average_fitness=statistics.mean(all_fitness) if all_fitness else 0.0,
            max_fitness=max(all_fitness) if all_fitness else 0.0,
            min_fitness=min(all_fitness) if all_fitness else 0.0,
            genetic_diversity=statistics.mean(all_diversities) if all_diversities else 0.0,
            dominant_genes={k: f"{v:.3f}" for k, v in dominant_genes.items()}
        )
        
        self.population_history.append(stats)
        
        # Atualizar analytics
        self.evolution_analytics["average_fitness_trend"].append(stats.average_fitness)
        self.evolution_analytics["genetic_diversity_trend"].append(stats.genetic_diversity)
        self.evolution_analytics["dominant_gene_history"].append(dominant_genes)
        
        # Log estatísticas
        self.logger.info(f"📊 Generation {self.generation_number} Stats:")
        self.logger.info(f"  Population: {stats.population_size}")
        self.logger.info(f"  Avg Fitness: {stats.average_fitness:.3f}")
        self.logger.info(f"  Diversity: {stats.genetic_diversity:.3f}")
    
    def _load_population_data(self):
        """Carrega dados da população persistidos"""
        data_file = self.data_dir / "population_data.json"
        
        try:
            if data_file.exists():
                with open(data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Carregar populações
                if "agent_populations" in data:
                    for agent_type, population_data in data["agent_populations"].items():
                        population = []
                        for dna_data in population_data:
                            # Reconstruir DNA
                            dna = self._deserialize_dna(dna_data)
                            if dna:
                                population.append(dna)
                        self.agent_populations[agent_type] = population
                
                # Carregar analytics
                if "evolution_analytics" in data:
                    self.evolution_analytics.update(data["evolution_analytics"])
                
                if "generation_number" in data:
                    self.generation_number = data["generation_number"]
                
                self.logger.info(f"📂 Loaded population data: {len(self.agent_populations)} agent types")
                
        except Exception as e:
            self.logger.warning(f"Failed to load population data: {e}")
    
    def _deserialize_dna(self, dna_data: Dict[str, Any]) -> Optional[AgentDNA]:
        """Deserializa DNA a partir de dados JSON"""
        try:
            # Reconstruir genes
            genes = {}
            for gene_type_str, gene_data in dna_data.get("genes", {}).items():
                gene_type = GeneType(gene_type_str)
                gene = CognitiveGene(
                    gene_id=gene_data["gene_id"],
                    gene_type=gene_type,
                    allele_value=gene_data["allele_value"],
                    dominance=gene_data["dominance"],
                    mutation_rate=gene_data.get("mutation_rate", 0.05),
                    expression_level=gene_data.get("expression_level", 1.0)
                )
                genes[gene_type] = gene
            
            # Reconstruir DNA
            dna = AgentDNA(
                dna_id=dna_data["dna_id"],
                agent_type=dna_data["agent_type"],
                generation=dna_data["generation"],
                genes=genes,
                fitness_history=dna_data.get("fitness_history", []),
                creation_time=datetime.fromisoformat(dna_data["creation_time"]),
                parent_dnas=dna_data.get("parent_dnas", []),
                mutation_count=dna_data.get("mutation_count", 0)
            )
            
            return dna
            
        except Exception as e:
            self.logger.warning(f"Failed to deserialize DNA: {e}")
            return None
    
    def _save_population_data(self):
        """Salva dados da população"""
        data_file = self.data_dir / "population_data.json"
        
        try:
            # Preparar dados para serialização
            serializable_populations = {}
            
            for agent_type, population in self.agent_populations.items():
                serializable_population = []
                for dna in population[-50:]:  # Salvar apenas os últimos 50 DNAs por tipo
                    # Serializar genes
                    serializable_genes = {}
                    for gene_type, gene in dna.genes.items():
                        serializable_genes[gene_type.value] = {
                            "gene_id": gene.gene_id,
                            "allele_value": gene.allele_value,
                            "dominance": gene.dominance,
                            "mutation_rate": gene.mutation_rate,
                            "expression_level": gene.expression_level
                        }
                    
                    # Serializar DNA
                    serializable_dna = {
                        "dna_id": dna.dna_id,
                        "agent_type": dna.agent_type,
                        "generation": dna.generation,
                        "genes": serializable_genes,
                        "fitness_history": dna.fitness_history[-20:],  # Últimos 20 fitness scores
                        "creation_time": dna.creation_time.isoformat(),
                        "parent_dnas": dna.parent_dnas,
                        "mutation_count": dna.mutation_count
                    }
                    
                    serializable_population.append(serializable_dna)
                
                serializable_populations[agent_type] = serializable_population
            
            data = {
                "agent_populations": serializable_populations,
                "evolution_analytics": self.evolution_analytics,
                "generation_number": self.generation_number,
                "last_updated": datetime.now().isoformat()
            }
            
            with open(data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            self.logger.error(f"Failed to save population data: {e}")
    
    def get_dna_status(self) -> Dict[str, Any]:
        """Retorna status do sistema de DNA"""
        status = {
            "enabled": self.enabled,
            "generation_number": self.generation_number,
            "total_agent_types": len(self.agent_populations),
            "total_population": sum(len(pop) for pop in self.agent_populations.values()),
            "evolution_analytics": self.evolution_analytics,
            "agent_populations": {}
        }
        
        for agent_type, population in self.agent_populations.items():
            if population:
                best_dna = self.get_best_dna(agent_type)
                diversity = self.analyze_genetic_diversity(agent_type)
                
                status["agent_populations"][agent_type] = {
                    "population_size": len(population),
                    "average_generation": statistics.mean([dna.generation for dna in population]),
                    "best_fitness": best_dna.get_average_fitness() if best_dna else 0.0,
                    "genetic_diversity": diversity,
                    "dominant_phenotype": best_dna.get_phenotype() if best_dna else {}
                }
        
        return status
    
    def shutdown(self):
        """Encerra sistema de DNA"""
        self.logger.info("🛑 Shutting down Dynamic Agent DNA System...")
        
        self.should_stop.set()
        
        if self.evolution_thread and self.evolution_thread.is_alive():
            self.evolution_thread.join(timeout=5)
        
        # Salvar dados
        self._save_population_data()
        
        self.logger.info("✅ Dynamic Agent DNA System shutdown complete")

# Singleton instance
_dynamic_agent_dna = None

def get_dynamic_agent_dna(config: Dict[str, Any], logger: logging.Logger) -> DynamicAgentDNA:
    """Get singleton instance of DynamicAgentDNA"""
    global _dynamic_agent_dna
    if _dynamic_agent_dna is None:
        _dynamic_agent_dna = DynamicAgentDNA(config, logger)
    return _dynamic_agent_dna