from dataclasses import dataclass, field
from typing import Optional, Dict, Any, Tuple, List

@dataclass
class AgentState:
    """
    Representa o estado interno do agente Hephaestus durante um ciclo de processamento.
    """
    current_objective: Optional[str] = None
    manifesto_content: str = ""
    action_plan_data: Optional[Dict[str, Any]] = None # JSON parseado do plano de ação

    # Informações da fase do Maestro
    strategy_key: Optional[str] = None # Chave da estratégia de validação escolhida

    # Resultados da execução da estratégia
    # (success: bool, reason_code: str, details: str)
    validation_result: Tuple[bool, str, str] = field(default_factory=lambda: (False, "PENDING", "Ciclo não iniciado"))

    # Relatório de arquivos que foram aplicados (útil para sanity checks)
    # Ex: {"path/to/file.py": {"status": "attempted_in_sandbox", "message": "..."}}
    applied_files_report: Dict[str, Dict[str, str]] = field(default_factory=dict)

    # Campos que foram removidos do dicionário de estado original por não serem mais usados:
    # in_memory_files: Dict[str, list[str]] = field(default_factory=dict) # Removido, não utilizado
    # model_architect: Optional[str] = None # Removido, usado localmente na fase
    # model_code_engineer: Optional[str] = None # Removido, não utilizado

    file_content_context: str = "" # Novo campo para contexto de arquivo

    def get_patches_to_apply(self) -> List[Dict[str, Any]]:
        """Helper para obter a lista de patches do action_plan_data de forma segura."""
        if self.action_plan_data and "patches_to_apply" in self.action_plan_data:
            return self.action_plan_data.get("patches_to_apply", [])
        return []

    def get_architect_analysis(self) -> str:
        """Helper para obter a análise do arquiteto do action_plan_data."""
        if self.action_plan_data:
            return self.action_plan_data.get("analysis", "Nenhuma análise do arquiteto fornecida.")
        return "Nenhum plano de ação disponível."

    def reset_for_new_cycle(self, current_objective: Optional[str] = None):
        """Reseta o estado para um novo ciclo, mantendo o objetivo atual se fornecido."""
        self.current_objective = current_objective
        self.manifesto_content = ""
        self.action_plan_data = None
        self.strategy_key = None
        self.validation_result = (False, "PENDING", "Novo ciclo")
        self.applied_files_report = {}
        self.file_content_context = "" # Redefine o contexto

# Exemplo de como poderia ser usado (não faz parte do arquivo final):
# if __name__ == '__main__':
#     state = AgentState()
#     state.current_objective = "Implementar feature X"
#     state.manifesto_content = "..."
#     print(state)
#     state.reset_for_new_cycle("Implementar feature Y")
#     print(state)
#     print(state.get_patches_to_apply())
