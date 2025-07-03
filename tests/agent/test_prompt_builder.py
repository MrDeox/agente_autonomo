import unittest
from agent.prompt_builder import (
    build_memory_context_section,
    build_initial_objective_prompt,
    build_meta_analysis_objective_prompt,
    build_standard_objective_prompt
)

class TestPromptBuilder(unittest.TestCase):

    def test_build_memory_context_section_with_summary(self):
        summary = "Recent failure: X. Recent success: Y."
        expected_section = """
[HISTÓRICO RECENTE DO PROJETO E DO AGENTE]
Recent failure: X. Recent success: Y.
Consider this history to avoid repeating failures, build on successes, and identify gaps.
"""
        self.assertEqual(build_memory_context_section(summary).strip(), expected_section.strip())

    def test_build_memory_context_section_empty_summary(self):
        self.assertEqual(build_memory_context_section(""), "")
        self.assertEqual(build_memory_context_section("   "), "")

    def test_build_memory_context_section_no_history_message(self):
        self.assertEqual(build_memory_context_section("no relevant history available."), "")
        self.assertEqual(build_memory_context_section("NO RELEVANT HISTORY AVAILABLE."), "")

    def test_build_initial_objective_prompt(self):
        memory_section = "[HISTÓRICO RECENTE DO PROJETO E DO AGENTE]\nSome history."
        prompt = build_initial_objective_prompt(memory_section)
        self.assertIn("[Context]\nYou are the 'Planejador Estratégico'", prompt)
        self.assertIn(memory_section, prompt)
        self.assertIn("Generate ONLY a single text string", prompt)

    def test_build_meta_analysis_objective_prompt(self):
        prompt = build_meta_analysis_objective_prompt(
            current_objective="[META-ANALYSIS OBJECTIVE] Analyze failure of X",
            original_failed_objective="Implement X",
            error_reason_for_meta="Syntax Error",
            performance_summary_str="Performance good.",
            memory_context_section="[HISTÓRICO RECENTE DO PROJETO E DO AGENTE]\nMemory context.",
            capabilities_content="Capabilities: Can do X.",
            roadmap_content="Roadmap: Achieve Y."
        )
        self.assertIn("You are the 'Meta-Strategic Planner'", prompt)
        self.assertIn("[META-ANALYSIS OBJECTIVE] Analyze failure of X", prompt)
        self.assertIn("[ORIGINAL FAILED OBJECTIVE]\nImplement X", prompt)
        self.assertIn("[REASON FOR FAILURE (from ErrorAnalysisAgent)]\nSyntax Error", prompt)
        self.assertIn("[PERFORMANCE ANALYSIS (Overall Agent Performance)]\nPerformance good.", prompt)
        self.assertIn("[HISTÓRICO RECENTE DO PROJETO E DO AGENTE]\nMemory context.", prompt)
        self.assertIn("[CAPABILITIES DOCUMENT (CAPABILITIES.md)]\nCapabilities: Can do X.", prompt)
        self.assertIn("[ROADMAP DOCUMENT (ROADMAP.md)]\nRoadmap: Achieve Y.", prompt)

        self.assertIn("Generate ONLY a single text string containing the NEXT STRATEGIC OBJECTIVE", prompt)

    def test_build_standard_objective_prompt(self):
        prompt = build_standard_objective_prompt(
            memory_context_section="[HISTÓRICO RECENTE DO PROJETO E DO AGENTE]\nStandard memory.",
            performance_summary_str="Standard performance.",
            code_analysis_summary_str="Standard code analysis.",
            current_manifest="Standard manifest.",
            capabilities_content="Caps: Build Z.",
            roadmap_content="Roadmap: Phase 1."
        )
        self.assertIn("You are the 'Planejador Estratégico Avançado'", prompt)
        self.assertIn("[HISTÓRICO RECENTE DO PROJETO E DO AGENTE]\nStandard memory.", prompt)
        self.assertIn("[PERFORMANCE ANALYSIS]\nStandard performance.", prompt)
        self.assertIn("[CODE METRICS AND ANALYSIS]\nStandard code analysis.", prompt)
        self.assertIn("[CAPABILITIES DOCUMENT (CAPABILITIES.md)]\nCaps: Build Z.", prompt)
        self.assertIn("[ROADMAP DOCUMENT (ROADMAP.md)]\nRoadmap: Phase 1.", prompt)

        self.assertIn("[CURRENT PROJECT MANIFEST (if existing)]\nStandard manifest.", prompt)
        self.assertIn("generate ONLY a single text string containing the NEXT STRATEGIC OBJECTIVE", prompt)

    def test_build_standard_objective_prompt_empty_manifest(self):
        prompt = build_standard_objective_prompt(
            memory_context_section="",
            performance_summary_str="Perf sum",
            code_analysis_summary_str="Code sum",
            current_manifest="  ", # Empty manifest
            capabilities_content="Caps content",
            roadmap_content="Roadmap content"
        )
        self.assertIn("[CURRENT PROJECT MANIFEST (if existing)]\nN/A (Manifesto non-existent or empty)", prompt)
        self.assertIn("[CAPABILITIES DOCUMENT (CAPABILITIES.md)]\nCaps content", prompt)
        self.assertIn("[ROADMAP DOCUMENT (ROADMAP.md)]\nRoadmap content", prompt)

if __name__ == '__main__':
    unittest.main()
