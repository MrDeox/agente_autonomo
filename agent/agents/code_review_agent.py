import logging
from typing import Optional, Dict, Any, Tuple
import re

from agent.utils.llm_client import call_llm_api
from agent.utils.json_parser import parse_json_response

class CodeReviewAgent:
    def __init__(self, model_config: Dict[str, str], logger: logging.Logger):
        self.model_config = model_config
        self.logger = logger

    def needs_review(self, patches: list[dict]) -> bool:
        """
        Determina se os patches precisam de revisão LLM baseado em regras.
        
        Args:
            patches: Lista de patches para avaliar
            
        Returns:
            True se precisa de revisão LLM, False se pode pular
        """
        if not patches:
            return False
            
        # Padrões que indicam mudanças triviais
        trivial_patterns = [
            r'^import\s+',           # Apenas imports
            r'^from\s+.*\s+import',  # Apenas imports
            r'^#.*$',                # Apenas comentários
            r'^\s*$',                # Linhas vazias
            r'^""".*"""$',           # Docstrings simples
            r"^'''.*'''$",           # Docstrings simples
            r'^\s*pass\s*$',         # Apenas pass
        ]
        
        # Padrões que sempre precisam de revisão
        critical_patterns = [
            r'exec\s*\(',            # Código dinâmico perigoso
            r'eval\s*\(',            # Código dinâmico perigoso
            r'__import__',           # Import dinâmico
            r'subprocess',           # Execução de processos
            r'os\.system',           # Comandos do sistema
            r'open\s*\(',            # Operações de arquivo
            r'\.write\s*\(',         # Escrita em arquivos
            r'\.delete\s*\(',        # Deleção
        ]
        
        total_patches = len(patches)
        trivial_count = 0
        
        for patch in patches:
            content = patch.get('content', '')
            operation = patch.get('operation', '')
            
            # DELETE sempre precisa de revisão
            if operation == 'DELETE_BLOCK':
                self.logger.debug("Patch contains DELETE operation - needs review")
                return True
            
            # Verifica padrões críticos
            for pattern in critical_patterns:
                if re.search(pattern, content, re.MULTILINE):
                    self.logger.debug(f"Patch contains critical pattern '{pattern}' - needs review")
                    return True
            
            # Conta patches triviais
            is_trivial = False
            for pattern in trivial_patterns:
                if re.match(pattern, content.strip()):
                    is_trivial = True
                    break
            
            if is_trivial:
                trivial_count += 1
        
        # Se todos os patches são triviais, não precisa de revisão
        if trivial_count == total_patches:
            self.logger.info(f"All {total_patches} patches are trivial - skipping LLM review")
            return False
        
        # Se a maioria é trivial e não há padrões críticos, pode pular
        trivial_ratio = trivial_count / total_patches
        if trivial_ratio > 0.8:
            self.logger.info(f"{trivial_ratio:.0%} of patches are trivial - skipping LLM review")
            return False
            
        return True

    def review_patches(self, patches_to_apply: list[dict]) -> Tuple[bool, str]:
        """
        Reviews a list of patches for code quality, style, and potential bugs.

        Args:
            patches_to_apply: The list of patch instructions from the Architect.

        Returns:
            A tuple containing:
            - bool: True if the review passed, False otherwise.
            - str: A string with feedback and suggestions if the review failed, or "OK" if it passed.
        """
        if not patches_to_apply:
            return True, "No patches to review."

        # Verifica se precisa de revisão LLM
        if not self.needs_review(patches_to_apply):
            return True, "Patches are trivial - auto-approved without LLM review."

        patches_str = "\n".join([f"--- PATCH FOR {p.get('file_path')} ---\n{p.get('content', '')}\n" for p in patches_to_apply])

        prompt = f"""
[IDENTITY]
You are an expert Senior Software Engineer performing a code review. Your standards are high, but your goal is to be helpful and constructive.

[TASK]
Review the following code patches. Your review should focus on:
1. **Code Quality:** Is the code clean, readable, and maintainable?
2. **Correctness:** Are there any obvious logic errors, bugs, or anti-patterns?
3. **Best Practices:** Does the code follow standard Python conventions (PEP 8)?
4. **Security:** Are there any potential security vulnerabilities?

[CODE PATCHES TO REVIEW]
{patches_str}

[YOUR DECISION AND OUTPUT FORMAT]
Your response MUST be a valid JSON object. There are only two valid formats for your response:

1.  If the review PASSES, respond with:
    `{{"review_passed": true, "feedback": "OK"}}`

2.  If the review FAILS, you MUST provide a detailed, actionable, and numbered list of required changes in the `feedback` field. The `review_passed` field MUST be `false`.
    Example for a FAILED review:
    `{{"review_passed": false, "feedback": "1. The function `my_func` should be split into smaller functions to reduce complexity.\\n2. Add docstrings explaining the purpose of the `process_data` function.\\n3. The variable `x` is too generic; rename it to `user_id` for clarity."}}`

**Critically important: If `review_passed` is `false`, the `feedback` field CANNOT be empty or "OK". It MUST contain specific instructions.**
"""
        self.logger.info(f"CodeReviewAgent: Reviewing {len(patches_to_apply)} patches...")
        
        # Use optimized LLM call for better performance
        from agent.llm_performance_booster import optimized_llm_call
        raw_response, metadata = optimized_llm_call(
            agent_type="CodeReviewAgent",
            prompt=prompt,
            model_config=self.model_config,
            temperature=0.2,
            context={"patches": patches_to_apply},
            logger=self.logger
        )
        
        # Check if it was an error response
        error = metadata.get('error')

        if error:
            self.logger.error(f"CodeReviewAgent: API call failed: {error}")
            return False, f"API call failed: {error}"

        if not raw_response:
            self.logger.error("CodeReviewAgent: Received empty response from LLM.")
            return False, "Received empty response from LLM."

        parsed, error = parse_json_response(raw_response, self.logger)
        if error or not isinstance(parsed, dict):
            self.logger.error(f"CodeReviewAgent: Failed to parse review response: {error or 'Invalid format'}")
            return False, f"Failed to parse review response: {raw_response}"

        review_passed = parsed.get("review_passed", False)
        feedback = parsed.get("feedback", "").strip()

        # Add validation logic
        if not review_passed and (not feedback or feedback.upper() == "OK"):
            error_message = f"CodeReviewAgent: LLM failed review but provided no actionable feedback. Response: {raw_response}"
            self.logger.error(error_message)
            return False, error_message

        if review_passed:
            self.logger.info("CodeReviewAgent: Review PASSED.")
        else:
            self.logger.warning(f"CodeReviewAgent: Review FAILED. Feedback: {feedback}")

        return review_passed, feedback 