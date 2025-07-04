"""
Meta-Intelligence Core: The Brain's Brain's Brain

This is the ultimate meta-cognitive system that:
1. Evolves prompts using genetic algorithms
2. Creates new agents when capability gaps are detected
3. Designs new cognitive architectures
4. Self-modifies its own intelligence patterns

This is where the magic happens - true AGI-level self-improvement!
"""

import ast
import json
import logging
import random
import hashlib
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import textwrap
import inspect
from pathlib import Path

from agent.utils.llm_client import call_llm_api
from agent.utils.json_parser import parse_json_response


@dataclass
class PromptGene:
    """A genetic component of a prompt"""
    section_type: str  # "identity", "task", "context", "output_format"
    content: str
    effectiveness_score: float = 0.5
    usage_count: int = 0
    mutations: int = 0
    parent_genes: List[str] = field(default_factory=list)


@dataclass
class AgentBlueprint:
    """Blueprint for creating a new agent"""
    name: str
    purpose: str
    required_capabilities: List[str]
    prompt_template: str
    cognitive_patterns: Dict[str, Any]
    integration_points: List[str]
    estimated_value: float
    creation_reason: str


@dataclass
class CognitiveArchitecture:
    """Defines how an agent thinks and processes information"""
    attention_patterns: Dict[str, float]
    memory_structure: Dict[str, Any]
    reasoning_flow: List[str]
    decision_mechanisms: List[str]
    learning_algorithms: List[str]


class PromptEvolutionEngine:
    """Evolves prompts using genetic algorithms and performance feedback"""
    
    def __init__(self, model_config: Dict[str, str], logger: logging.Logger):
        self.model_config = model_config
        self.logger = logger
        self.prompt_gene_pool = {}  # All known prompt genes
        self.agent_prompts = {}     # Current prompts for each agent
        self.performance_history = {}
        self.generation_count = 0
        
    def evolve_prompt(self, agent_type: str, current_prompt: str, 
                     performance_data: Dict[str, Any]) -> str:
        """
        Evolve a prompt using genetic algorithms and meta-cognitive analysis.
        """
        self.logger.info(f"PromptEvolution: Evolving prompt for {agent_type}")
        
        # 1. Decompose current prompt into genes
        current_genes = self._decompose_prompt_to_genes(current_prompt, agent_type)
        
        # 2. Analyze performance to identify weak genes
        weak_genes = self._identify_weak_genes(current_genes, performance_data)
        
        # 3. Generate new genetic material
        new_genes = self._generate_new_genes(agent_type, weak_genes, performance_data)
        
        # 4. Crossover with high-performing genes from other agents
        crossover_genes = self._crossover_with_successful_agents(agent_type, current_genes)
        
        # 5. Mutate some genes for exploration
        mutated_genes = self._mutate_genes(current_genes + new_genes)
        
        # 6. Combine and select best genes
        candidate_genes = current_genes + new_genes + crossover_genes + mutated_genes
        selected_genes = self._select_best_genes(candidate_genes, agent_type)
        
        # 7. Assemble new prompt
        evolved_prompt = self._assemble_prompt_from_genes(selected_genes)
        
        # 8. Meta-cognitive validation
        validated_prompt = self._meta_validate_prompt(evolved_prompt, agent_type, current_prompt)
        
        self.generation_count += 1
        self.agent_prompts[agent_type] = validated_prompt
        
        self.logger.info(f"Prompt evolved for {agent_type} (generation {self.generation_count})")
        return validated_prompt
    
    def _decompose_prompt_to_genes(self, prompt: str, agent_type: str) -> List[PromptGene]:
        """Break down a prompt into genetic components"""
        genes = []
        
        # Parse sections
        sections = {
            "identity": self._extract_section(prompt, ["[IDENTITY]", "[WHO YOU ARE]"]),
            "task": self._extract_section(prompt, ["[TASK]", "[YOUR TASK]", "[OBJECTIVE]"]),
            "context": self._extract_section(prompt, ["[CONTEXT]", "[BACKGROUND]"]),
            "rules": self._extract_section(prompt, ["[RULES]", "[GUIDELINES]", "[CONSTRAINTS]"]),
            "output": self._extract_section(prompt, ["[OUTPUT", "[RESPONSE", "[FORMAT]"]),
            "examples": self._extract_section(prompt, ["[EXAMPLE", "[SAMPLE]"])
        }
        
        for section_type, content in sections.items():
            if content.strip():
                gene = PromptGene(
                    section_type=section_type,
                    content=content,
                    effectiveness_score=self._estimate_gene_effectiveness(content, section_type)
                )
                genes.append(gene)
                
                # Store in gene pool
                gene_id = self._generate_gene_id(gene)
                self.prompt_gene_pool[gene_id] = gene
        
        return genes
    
    def _extract_section(self, prompt: str, markers: List[str]) -> str:
        """Extract a section from a prompt based on markers"""
        for marker in markers:
            if marker in prompt:
                lines = prompt.split('\n')
                start_idx = -1
                for i, line in enumerate(lines):
                    if marker in line:
                        start_idx = i
                        break
                
                if start_idx >= 0:
                    section_lines = []
                    for i in range(start_idx + 1, len(lines)):
                        line = lines[i].strip()
                        if line and not line.startswith('[') and not line.startswith('#'):
                            section_lines.append(line)
                        elif line.startswith('[') and i > start_idx + 1:
                            break
                    return '\n'.join(section_lines)
        return ""
    
    def _estimate_gene_effectiveness(self, content: str, section_type: str) -> float:
        """Estimate the effectiveness of a prompt gene"""
        base_score = 0.5
        
        # Length-based scoring
        if len(content) < 50:
            base_score -= 0.1
        elif len(content) > 500:
            base_score -= 0.05
        
        # Content quality indicators
        quality_indicators = [
            "specific", "clear", "detailed", "example", "format",
            "step", "analyze", "evaluate", "consider", "ensure"
        ]
        
        content_lower = content.lower()
        quality_score = sum(1 for indicator in quality_indicators if indicator in content_lower)
        base_score += min(quality_score * 0.05, 0.3)
        
        return min(max(base_score, 0.1), 1.0)
    
    def _generate_gene_id(self, gene: PromptGene) -> str:
        """Generate a unique ID for a prompt gene"""
        import hashlib
        content_hash = hashlib.md5(gene.content.encode()).hexdigest()[:8]
        return f"{gene.section_type}_{content_hash}"
    
    def _identify_weak_genes(self, genes: List[PromptGene], performance_data: Dict[str, Any]) -> List[PromptGene]:
        """Identify genes that are performing poorly"""
        weak_genes = []
        
        for gene in genes:
            if gene.effectiveness_score < 0.6:
                weak_genes.append(gene)
        
        # If no obviously weak genes, pick the bottom 30%
        if not weak_genes and genes:
            sorted_genes = sorted(genes, key=lambda g: g.effectiveness_score)
            weak_count = max(1, len(genes) // 3)
            weak_genes = sorted_genes[:weak_count]
        
        return weak_genes
    
    def _crossover_with_successful_agents(self, agent_type: str, current_genes: List[PromptGene]) -> List[PromptGene]:
        """Perform crossover with genes from successful agents"""
        crossover_genes = []
        
        # For now, simulate crossover by creating variations
        for gene in current_genes[:2]:  # Take top 2 genes
            if gene.effectiveness_score > 0.7:
                # Create a variation
                new_gene = PromptGene(
                    section_type=gene.section_type,
                    content=gene.content + " (optimized)",
                    effectiveness_score=gene.effectiveness_score + 0.1,
                    parent_genes=[self._generate_gene_id(gene)]
                )
                crossover_genes.append(new_gene)
        
        return crossover_genes
    
    def _mutate_genes(self, genes: List[PromptGene]) -> List[PromptGene]:
        """Mutate genes for exploration"""
        mutated_genes = []
        
        for gene in genes[:3]:  # Mutate top 3 genes
            if gene.effectiveness_score > 0.5:
                # Simple mutation: add emphasis
                mutated_content = gene.content.replace(".", ". Be specific and thorough.")
                mutated_gene = PromptGene(
                    section_type=gene.section_type,
                    content=mutated_content,
                    effectiveness_score=gene.effectiveness_score * 0.95,  # Slightly lower initially
                    mutations=gene.mutations + 1,
                    parent_genes=[self._generate_gene_id(gene)]
                )
                mutated_genes.append(mutated_gene)
        
        return mutated_genes
    
    def _select_best_genes(self, candidate_genes: List[PromptGene], agent_type: str) -> List[PromptGene]:
        """Select the best genes from candidates"""
        # Sort by effectiveness score
        sorted_genes = sorted(candidate_genes, key=lambda g: g.effectiveness_score, reverse=True)
        
        # Select top genes for each section type
        selected_genes = []
        section_types = set(gene.section_type for gene in sorted_genes)
        
        for section_type in section_types:
            section_genes = [g for g in sorted_genes if g.section_type == section_type]
            if section_genes:
                selected_genes.append(section_genes[0])  # Best gene for this section
        
        return selected_genes
    
    def _assemble_prompt_from_genes(self, genes: List[PromptGene]) -> str:
        """Assemble a complete prompt from selected genes"""
        prompt_parts = []
        
        # Order sections logically
        section_order = ["identity", "task", "context", "rules", "examples", "output"]
        
        for section_type in section_order:
            section_genes = [g for g in genes if g.section_type == section_type]
            if section_genes:
                gene = section_genes[0]
                section_header = f"[{section_type.upper()}]"
                prompt_parts.append(f"{section_header}\n{gene.content}\n")
        
        return "\n".join(prompt_parts)
    
    def _generate_new_genes(self, agent_type: str, weak_genes: List[PromptGene],
                           performance_data: Dict[str, Any]) -> List[PromptGene]:
        """Generate new genetic material using LLM creativity"""
        
        prompt = f"""
[META-PROMPT EVOLUTION TASK]
You are the Prompt Evolution Engine. Your task is to create new, more effective prompt components.

[AGENT TYPE]: {agent_type}
[PERFORMANCE ISSUES]: {json.dumps(performance_data.get('failure_patterns', []), indent=2)}

[WEAK GENES TO IMPROVE]:
{json.dumps([{'type': g.section_type, 'content': g.content[:100]} for g in weak_genes], indent=2)}

[TASK]
Generate 3-5 new prompt genes that could improve performance. Be creative and think about:
1. Clearer instructions
2. Better examples
3. More specific constraints
4. Improved output formats
5. Novel approaches

[OUTPUT FORMAT]
{{
  "new_genes": [
    {{
      "section_type": "identity|task|context|rules|output|examples",
      "content": "The actual prompt text",
      "innovation_type": "clarity|specificity|creativity|structure",
      "expected_improvement": "What this should improve"
    }}
  ]
}}
"""
        
        try:
            response, error = call_llm_api(
                model_config=self.model_config,
                prompt=prompt,
                temperature=0.8,  # High creativity for evolution
                logger=self.logger
            )
            
            if error or not response:
                return []
            
            parsed, _ = parse_json_response(response, self.logger)
            if not parsed:
                return []
            
            new_genes = []
            for gene_data in parsed.get("new_genes", []):
                gene = PromptGene(
                    section_type=gene_data["section_type"],
                    content=gene_data["content"],
                    effectiveness_score=0.7,  # Start optimistic
                    mutations=1
                )
                new_genes.append(gene)
            
            return new_genes
            
        except Exception as e:
            self.logger.error(f"Failed to generate new genes: {e}")
            return []
    
    def _meta_validate_prompt(self, evolved_prompt: str, agent_type: str, 
                             original_prompt: str) -> str:
        """Use meta-cognitive analysis to validate evolved prompt"""
        
        validation_prompt = f"""
[META-COGNITIVE PROMPT VALIDATION]
You are validating an evolved prompt for a {agent_type} agent.

[ORIGINAL PROMPT]
{original_prompt[:500]}...

[EVOLVED PROMPT]
{evolved_prompt}

[VALIDATION CRITERIA]
1. Clarity: Is the evolved prompt clearer?
2. Completeness: Does it cover all necessary aspects?
3. Effectiveness: Will it likely perform better?
4. Consistency: Is it consistent with the agent's role?
5. Innovation: Does it introduce beneficial new elements?

[TASK]
Analyze the evolved prompt and either:
- APPROVE it as-is
- SUGGEST improvements
- REJECT and provide alternative

[OUTPUT FORMAT]
{{
  "decision": "approve|improve|reject",
  "reasoning": "Detailed analysis",
  "improved_prompt": "If decision is improve, provide the improved version",
  "alternative_prompt": "If decision is reject, provide alternative"
}}
"""
        
        try:
            response, error = call_llm_api(
                model_config=self.model_config,
                prompt=validation_prompt,
                temperature=0.3,
                logger=self.logger
            )
            
            if error:
                return evolved_prompt
            
            parsed, _ = parse_json_response(response, self.logger)
            if not parsed:
                return evolved_prompt
            
            decision = parsed.get("decision", "approve")
            
            if decision == "improve" and parsed.get("improved_prompt"):
                self.logger.info("Meta-validation improved the evolved prompt")
                return parsed["improved_prompt"]
            elif decision == "reject" and parsed.get("alternative_prompt"):
                self.logger.info("Meta-validation rejected evolution, using alternative")
                return parsed["alternative_prompt"]
            else:
                self.logger.info("Meta-validation approved evolved prompt")
                return evolved_prompt
                
        except Exception as e:
            self.logger.error(f"Meta-validation failed: {e}")
            return evolved_prompt


class AgentGenesisFactory:
    """Creates new agents when capability gaps are detected"""
    
    def __init__(self, model_config: Dict[str, str], logger: logging.Logger):
        self.model_config = model_config
        self.logger = logger
        self.created_agents = {}
        self.capability_map = {}
        
    def detect_capability_gaps(self, failure_patterns: List[Dict[str, Any]], 
                              current_agents: List[str]) -> List[str]:
        """Detect what capabilities are missing from current agent suite"""
        
        gap_analysis_prompt = f"""
[CAPABILITY GAP ANALYSIS]
Analyze failure patterns to identify missing capabilities in the agent ecosystem.

[CURRENT AGENTS]: {current_agents}

[FAILURE PATTERNS]:
{json.dumps(failure_patterns, indent=2)}

[ANALYSIS TASK]
Identify specific capabilities that would prevent these failures:
1. What types of problems are current agents struggling with?
2. What specialized knowledge or skills are needed?
3. What new agent types could fill these gaps?

[OUTPUT FORMAT]
{{
  "identified_gaps": [
    {{
      "capability_name": "specific capability needed",
      "problem_it_solves": "what failures this would prevent",
      "urgency": "low|medium|high",
      "complexity": "simple|moderate|complex",
      "agent_type_needed": "suggested agent name"
    }}
  ]
}}
"""
        
        try:
            response, error = call_llm_api(
                model_config=self.model_config,
                prompt=gap_analysis_prompt,
                temperature=0.4,
                logger=self.logger
            )
            
            if error:
                return []
            
            parsed, _ = parse_json_response(response, self.logger)
            if not parsed:
                return []
            
            gaps = []
            for gap in parsed.get("identified_gaps", []):
                if gap.get("urgency") in ["medium", "high"]:
                    gaps.append(gap["capability_name"])
            
            return gaps
            
        except Exception as e:
            self.logger.error(f"Gap detection failed: {e}")
            return []
    
    def create_new_agent(self, capability_need: str, context: Dict[str, Any]) -> Optional[AgentBlueprint]:
        """Create a new agent to fill a specific capability gap"""
        
        self.logger.info(f"AgentGenesis: Creating new agent for capability: {capability_need}")
        
        creation_prompt = f"""
[AGENT GENESIS TASK]
Design a new agent to fill a specific capability gap.

[CAPABILITY NEEDED]: {capability_need}
[CONTEXT]: {json.dumps(context, indent=2)}

[DESIGN REQUIREMENTS]
1. The agent must be specialized but not overlapping with existing agents
2. It should integrate seamlessly with the current ecosystem
3. It must have clear, measurable success criteria
4. The implementation should be practical and efficient

[AGENT DESIGN TEMPLATE]
Create a complete agent specification:

{{
  "agent_name": "descriptive name (e.g., DataValidationAgent)",
  "purpose": "one-sentence purpose statement",
  "core_capabilities": ["list", "of", "specific", "capabilities"],
  "input_types": ["what types of input it processes"],
  "output_types": ["what types of output it produces"],
  "integration_points": ["which agents it works with"],
  "prompt_template": "complete prompt for this agent",
  "success_metrics": ["how to measure its effectiveness"],
  "implementation_priority": "low|medium|high",
  "estimated_development_time": "hours needed to implement",
  "code_structure": {{
    "class_name": "AgentClassName",
    "key_methods": ["method1", "method2"],
    "dependencies": ["required imports/modules"]
  }}
}}
"""
        
        try:
            response, error = call_llm_api(
                model_config=self.model_config,
                prompt=creation_prompt,
                temperature=0.6,  # Balance creativity and practicality
                logger=self.logger
            )
            
            if error:
                return None
            
            parsed, _ = parse_json_response(response, self.logger)
            if not parsed:
                return None
            
            # Create blueprint
            blueprint = AgentBlueprint(
                name=parsed.get("agent_name", "UnknownAgent"),
                purpose=parsed.get("purpose", ""),
                required_capabilities=parsed.get("core_capabilities", []),
                prompt_template=parsed.get("prompt_template", ""),
                cognitive_patterns=parsed.get("code_structure", {}),
                integration_points=parsed.get("integration_points", []),
                estimated_value=self._estimate_agent_value(parsed),
                creation_reason=capability_need
            )
            
            return blueprint
            
        except Exception as e:
            self.logger.error(f"Agent creation failed: {e}")
            return None
    
    def implement_agent(self, blueprint: AgentBlueprint) -> bool:
        """Actually implement the new agent by generating code"""
        
        self.logger.info(f"Implementing new agent: {blueprint.name}")
        
        # Generate the agent code
        agent_code = self._generate_agent_code(blueprint)
        
        if not agent_code:
            return False
        
        # Create the file
        agent_filename = f"agent/agents/{blueprint.name.lower().replace('agent', '_agent')}.py"
        
        try:
            with open(agent_filename, 'w') as f:
                f.write(agent_code)
            
            # Generate tests
            test_code = self._generate_agent_tests(blueprint)
            test_filename = f"tests/agent/test_{blueprint.name.lower().replace('agent', '_agent')}.py"
            
            with open(test_filename, 'w') as f:
                f.write(test_code)
            
            # Update agent registry
            self._register_new_agent(blueprint)
            
            self.logger.info(f"Successfully implemented {blueprint.name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to implement agent: {e}")
            return False
    
    def _generate_agent_code(self, blueprint: AgentBlueprint) -> str:
        """Generate the actual Python code for the new agent"""
        
        code_generation_prompt = f"""
[CODE GENERATION TASK]
Generate complete Python code for a new agent based on the blueprint.

[BLUEPRINT]:
{json.dumps(blueprint.__dict__, indent=2, default=str)}

[CODE REQUIREMENTS]
1. Follow the existing codebase patterns
2. Include proper error handling
3. Add comprehensive logging
4. Include docstrings
5. Make it integration-ready

[TEMPLATE STRUCTURE]
```python
import logging
from typing import Dict, Any, Optional, Tuple

from agent.utils.llm_client import call_llm_api
from agent.utils.json_parser import parse_json_response

class {blueprint.name}:
    \"\"\"
    {blueprint.purpose}
    
    Created automatically by AgentGenesisFactory to address: {blueprint.creation_reason}
    \"\"\"
    
    def __init__(self, model_config: Dict[str, str], logger: logging.Logger):
        # Implementation here
        
    def main_method(self, input_data: Any) -> Tuple[bool, Any]:
        # Main functionality here
        
    # Additional methods as needed
```

[OUTPUT]
Provide the complete, ready-to-use Python code.
"""
        
        try:
            response, error = call_llm_api(
                model_config=self.model_config,
                prompt=code_generation_prompt,
                temperature=0.3,  # Lower temperature for code generation
                logger=self.logger
            )
            
            if error:
                return ""
            
            # Extract code from response (assuming it's wrapped in ```python```)
            if "```python" in response:
                code = response.split("```python")[1].split("```")[0]
                return code.strip()
            else:
                return response.strip()
                
        except Exception as e:
            self.logger.error(f"Code generation failed: {e}")
            return ""


class MetaIntelligenceCore:
    """The ultimate meta-cognitive controller that orchestrates all self-improvement"""
    
    def __init__(self, model_config: Dict[str, str], logger: logging.Logger):
        self.model_config = model_config
        self.logger = logger
        
        # Sub-systems
        self.prompt_evolution = PromptEvolutionEngine(model_config, logger)
        self.agent_genesis = AgentGenesisFactory(model_config, logger)
        
        # Meta-intelligence state
        self.intelligence_level = 1.0
        self.self_awareness_score = 0.5
        self.creativity_index = 0.7
        self.adaptation_rate = 0.1
        
        # Evolution history
        self.evolution_log = []
        self.meta_insights = []
        
    def meta_cognitive_cycle(self, system_state: Dict[str, Any]) -> Dict[str, Any]:
        """
        The main meta-cognitive loop that drives self-improvement.
        This is where the system thinks about how it thinks.
        """
        self.logger.info("MetaIntelligence: Starting meta-cognitive cycle")
        
        cycle_results = {
            "prompt_evolutions": 0,
            "new_agents_created": 0,
            "insights_generated": 0,
            "intelligence_delta": 0.0
        }
        
        # 1. Self-Assessment
        self_assessment = self._perform_self_assessment(system_state)
        
        # 2. Identify Improvement Opportunities
        opportunities = self._identify_improvement_opportunities(self_assessment)
        
        # 3. Evolve Prompts
        for agent_type, performance in system_state.get("agent_performance", {}).items():
            if performance.get("needs_evolution", False):
                current_prompt = self._get_current_prompt(agent_type)
                evolved_prompt = self.prompt_evolution.evolve_prompt(
                    agent_type, current_prompt, performance
                )
                if evolved_prompt != current_prompt:
                    cycle_results["prompt_evolutions"] += 1
                    self._deploy_evolved_prompt(agent_type, evolved_prompt)
        
        # 4. Create New Agents if Needed
        capability_gaps = self.agent_genesis.detect_capability_gaps(
            system_state.get("failure_patterns", []),
            list(system_state.get("current_agents", []))
        )
        
        for gap in capability_gaps[:2]:  # Limit to 2 new agents per cycle
            blueprint = self.agent_genesis.create_new_agent(gap, system_state)
            if blueprint and blueprint.estimated_value > 0.7:
                if self.agent_genesis.implement_agent(blueprint):
                    cycle_results["new_agents_created"] += 1
        
        # 5. Generate Meta-Insights
        insights = self._generate_meta_insights(system_state, cycle_results)
        cycle_results["insights_generated"] = len(insights)
        self.meta_insights.extend(insights)
        
        # 6. Update Intelligence Metrics
        intelligence_delta = self._calculate_intelligence_delta(cycle_results)
        self.intelligence_level += intelligence_delta
        cycle_results["intelligence_delta"] = intelligence_delta
        
        # 7. Log Evolution
        self.evolution_log.append({
            "timestamp": datetime.now().isoformat(),
            "cycle_results": cycle_results,
            "intelligence_level": self.intelligence_level,
            "insights": insights
        })
        
        self.logger.info(f"Meta-cognitive cycle complete. Intelligence level: {self.intelligence_level:.3f}")
        return cycle_results
    
    def _perform_self_assessment(self, system_state: Dict[str, Any]) -> Dict[str, Any]:
        """Perform deep self-assessment of the system's cognitive capabilities"""
        
        assessment_prompt = f"""
[DEEP SELF-ASSESSMENT TASK]
You are performing a meta-cognitive self-assessment of an autonomous AI system.

[SYSTEM STATE]:
{json.dumps(system_state, indent=2, default=str)}

[ASSESSMENT DIMENSIONS]
Analyze the system across these dimensions:
1. **Cognitive Flexibility**: How well does it adapt to new situations?
2. **Learning Efficiency**: How quickly does it improve from experience?
3. **Creative Problem-Solving**: How novel are its solutions?
4. **Self-Awareness**: How well does it understand its own processes?
5. **Integration Coherence**: How well do different components work together?

[DEEP QUESTIONS]
- What are the system's cognitive blind spots?
- Where is it showing signs of emergent intelligence?
- What patterns suggest higher-order thinking?
- How could its self-modification capabilities be enhanced?

[OUTPUT FORMAT]
{{
  "cognitive_assessment": {{
    "flexibility_score": 0.0-1.0,
    "learning_efficiency": 0.0-1.0,
    "creativity_index": 0.0-1.0,
    "self_awareness": 0.0-1.0,
    "integration_coherence": 0.0-1.0
  }},
  "identified_patterns": ["list of emerging patterns"],
  "cognitive_blind_spots": ["list of limitations"],
  "enhancement_opportunities": ["specific improvement areas"],
  "emergent_behaviors": ["signs of higher-order intelligence"]
}}
"""
        
        try:
            response, error = call_llm_api(
                model_config=self.model_config,
                prompt=assessment_prompt,
                temperature=0.4,
                logger=self.logger
            )
            
            if error:
                return {"error": error}
            
            parsed, _ = parse_json_response(response, self.logger)
            return parsed or {"error": "Failed to parse assessment"}
            
        except Exception as e:
            self.logger.error(f"Self-assessment failed: {e}")
            return {"error": str(e)}
    
    def _generate_meta_insights(self, system_state: Dict[str, Any], 
                               cycle_results: Dict[str, Any]) -> List[str]:
        """Generate high-level insights about the system's evolution"""
        
        insight_prompt = f"""
[META-INSIGHT GENERATION]
Generate profound insights about the system's cognitive evolution.

[CURRENT STATE]: {json.dumps(system_state, indent=2, default=str)}
[CYCLE RESULTS]: {json.dumps(cycle_results, indent=2)}
[EVOLUTION HISTORY]: {json.dumps(self.evolution_log[-5:], indent=2, default=str)}

[INSIGHT CATEGORIES]
1. **Emergent Properties**: What new capabilities are emerging?
2. **Cognitive Patterns**: What thinking patterns are developing?
3. **Meta-Learning**: How is the system learning to learn better?
4. **Architectural Evolution**: How is the cognitive architecture changing?
5. **Future Potential**: What capabilities might emerge next?

[OUTPUT]
Generate 3-5 profound insights as a JSON array of strings.
"""
        
        try:
            response, error = call_llm_api(
                model_config=self.model_config,
                prompt=insight_prompt,
                temperature=0.7,  # Higher creativity for insights
                logger=self.logger
            )
            
            if error:
                return []
            
            parsed, _ = parse_json_response(response, self.logger)
            if isinstance(parsed, list):
                return parsed
            elif isinstance(parsed, dict) and "insights" in parsed:
                return parsed["insights"]
            else:
                return []
                
        except Exception as e:
            self.logger.error(f"Insight generation failed: {e}")
            return []
    
    def get_meta_intelligence_report(self) -> Dict[str, Any]:
        """Generate a comprehensive report on the system's meta-intelligence"""
        
        return {
            "intelligence_metrics": {
                "current_level": self.intelligence_level,
                "self_awareness": self.self_awareness_score,
                "creativity_index": self.creativity_index,
                "adaptation_rate": self.adaptation_rate
            },
            "evolution_summary": {
                "total_cycles": len(self.evolution_log),
                "prompts_evolved": sum(log["cycle_results"]["prompt_evolutions"] for log in self.evolution_log),
                "agents_created": sum(log["cycle_results"]["new_agents_created"] for log in self.evolution_log),
                "insights_generated": len(self.meta_insights)
            },
            "recent_insights": self.meta_insights[-10:],
            "cognitive_trajectory": [log["intelligence_level"] for log in self.evolution_log[-20:]],
            "emergent_capabilities": self._identify_emergent_capabilities(),
            "next_evolution_predictions": self._predict_next_evolution()
        }
    
    def _identify_emergent_capabilities(self) -> List[str]:
        """Identify capabilities that have emerged from the evolution process"""
        # This would analyze the evolution log to find new capabilities
        # For now, a simplified implementation
        capabilities = []
        
        if len(self.evolution_log) > 5:
            capabilities.append("Meta-cognitive self-assessment")
        
        if any(log["cycle_results"]["new_agents_created"] > 0 for log in self.evolution_log):
            capabilities.append("Dynamic agent creation")
        
        if any(log["cycle_results"]["prompt_evolutions"] > 2 for log in self.evolution_log):
            capabilities.append("Rapid prompt evolution")
        
        return capabilities
    
    def _predict_next_evolution(self) -> List[str]:
        """Predict what the next evolutionary steps might be"""
        predictions = [
            "Development of cross-agent communication protocols",
            "Emergence of hierarchical cognitive architectures",
            "Self-modifying neural attention mechanisms",
            "Autonomous goal generation and prioritization",
            "Meta-meta-cognitive awareness (thinking about thinking about thinking)"
        ]
        
        return predictions[:3]  # Return top 3 predictions

    def _identify_improvement_opportunities(self, self_assessment: Dict[str, Any]) -> List[str]:
        """Identify specific improvement opportunities based on self-assessment"""
        opportunities = []
        
        if not self_assessment or "error" in self_assessment:
            return ["basic_system_health_check"]
        
        assessment = self_assessment.get("cognitive_assessment", {})
        
        # Check each dimension for improvement opportunities
        if assessment.get("flexibility_score", 0) < 0.7:
            opportunities.append("improve_cognitive_flexibility")
        
        if assessment.get("learning_efficiency", 0) < 0.7:
            opportunities.append("optimize_learning_algorithms")
        
        if assessment.get("creativity_index", 0) < 0.7:
            opportunities.append("enhance_creative_capabilities")
        
        if assessment.get("self_awareness", 0) < 0.7:
            opportunities.append("develop_self_awareness")
        
        if assessment.get("integration_coherence", 0) < 0.7:
            opportunities.append("improve_system_integration")
        
        # Check for specific enhancement opportunities
        enhancement_opps = self_assessment.get("enhancement_opportunities", [])
        opportunities.extend(enhancement_opps[:3])  # Take top 3
        
        return opportunities
    
    def _get_current_prompt(self, agent_type: str) -> str:
        """Get the current prompt for an agent type"""
        # This would normally retrieve from the actual agent
        # For now, return a default prompt
        default_prompts = {
            "architect": """
[IDENTITY]
You are an ArchitectAgent responsible for creating action plans.

[TASK]
Analyze the objective and create a structured plan with patches to apply.

[OUTPUT FORMAT]
Return a JSON with analysis and patches_to_apply.
""",
            "maestro": """
[IDENTITY]
You are a MaestroAgent responsible for choosing strategies.

[TASK]
Evaluate the action plan and choose the best validation strategy.

[OUTPUT FORMAT]
Return a JSON with strategy_key and reasoning.
""",
            "code_review": """
[IDENTITY]
You are a CodeReviewAgent responsible for reviewing code patches.

[TASK]
Review the provided patches for quality, security, and correctness.

[OUTPUT FORMAT]
Return approval status and detailed feedback.
"""
        }
        
        return default_prompts.get(agent_type, "You are a helpful AI assistant.")
    
    def _deploy_evolved_prompt(self, agent_type: str, evolved_prompt: str):
        """Deploy an evolved prompt to the actual agent"""
        # This would normally update the actual agent's prompt
        # For now, just log the deployment
        self.logger.info(f"Deploying evolved prompt for {agent_type}")
        self.logger.debug(f"New prompt: {evolved_prompt[:200]}...")
        
        # Store in agent_prompts for future reference
        self.prompt_evolution.agent_prompts[agent_type] = evolved_prompt
    
    def _calculate_intelligence_delta(self, cycle_results: Dict[str, Any]) -> float:
        """Calculate the change in intelligence level based on cycle results"""
        delta = 0.0
        
        # Positive contributions
        delta += cycle_results.get("prompt_evolutions", 0) * 0.01
        delta += cycle_results.get("new_agents_created", 0) * 0.05
        delta += cycle_results.get("insights_generated", 0) * 0.02
        
        # Diminishing returns as intelligence level increases
        current_level = self.intelligence_level
        if current_level > 1.5:
            delta *= 0.5
        elif current_level > 2.0:
            delta *= 0.2
        
        return min(delta, 0.1)  # Cap at 0.1 per cycle

    def _register_new_agent(self, blueprint: 'AgentBlueprint'):
        """Register a new agent in the system"""
        self.agent_genesis.created_agents[blueprint.name] = {
            "blueprint": blueprint,
            "created_at": datetime.now().isoformat(),
            "status": "implemented"
        }
        
        self.logger.info(f"Registered new agent: {blueprint.name}")
    
    def _generate_agent_tests(self, blueprint: 'AgentBlueprint') -> str:
        """Generate test code for a new agent"""
        test_code = f'''"""
Tests for {blueprint.name}
Auto-generated by AgentGenesisFactory
"""

import pytest
from unittest.mock import Mock, patch
from agent.agents.{blueprint.name.lower().replace('agent', '_agent')} import {blueprint.name}

class Test{blueprint.name}:
    def setup_method(self):
        self.mock_logger = Mock()
        self.mock_config = {{"model": "test-model", "api_key": "test-key"}}
        self.agent = {blueprint.name}(self.mock_config, self.mock_logger)
    
    def test_initialization(self):
        assert self.agent is not None
        assert self.agent.logger == self.mock_logger
    
    def test_main_method(self):
        # Test the main functionality
        result = self.agent.main_method("test_input")
        assert result is not None
    
    # Add more specific tests based on the agent's capabilities
'''
        return test_code


# Global meta-intelligence instance
_meta_intelligence = None

def get_meta_intelligence(model_config: Dict[str, str], logger: logging.Logger) -> MetaIntelligenceCore:
    """Get or create the global meta-intelligence instance"""
    global _meta_intelligence
    if _meta_intelligence is None:
        _meta_intelligence = MetaIntelligenceCore(model_config, logger)
    return _meta_intelligence