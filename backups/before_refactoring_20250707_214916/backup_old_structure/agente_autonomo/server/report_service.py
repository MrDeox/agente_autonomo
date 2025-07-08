"""
Report Service for Hephaestus MCP Server
"""
from typing import Dict, Any
from datetime import datetime
import json
import logging

logger = logging.getLogger(__name__)

class ReportService:
    """Service handling report generation and formatting"""
    
    def format_deep_reflection_report(self, reflection_data: Dict[str, Any]) -> str:
        """Format deep reflection results into human-readable report"""
        try:
            return f"""🔍 **Auto-Reflexão Profunda**

**Área de Foco:** {reflection_data.get('focus_area', 'general')}

**Estado Cognitivo Atual:**
• Nível de Inteligência: {reflection_data.get('current_cognitive_state', {}).get('intelligence_level', 0):.3f}
• Auto-Consciência: {reflection_data.get('current_cognitive_state', {}).get('self_awareness_score', 0):.3f}
• Coerência Cognitiva: {reflection_data.get('current_cognitive_state', {}).get('cognitive_coherence', 0):.3f}
• Velocidade de Aprendizado: {reflection_data.get('current_cognitive_state', {}).get('learning_velocity', 0):.3f}

**Pontuação de Meta-Consciência:** {reflection_data.get('meta_awareness', 0):.3f}

**Insights Gerados:** {len(reflection_data.get('new_insights', []))}
"""
        except Exception as e:
            logger.error(f"Error formatting reflection report: {e}")
            return f"❌ Erro: {str(e)}"
    
    def format_self_awareness_report(self, awareness_data: Dict[str, Any]) -> str:
        """Format self-awareness results into human-readable report"""
        try:
            return f"""🧠 **Relatório de Auto-Consciência**

**Métricas de Auto-Consciência:**
• Pontuação de Meta-Consciência: {awareness_data.get('self_awareness_metrics', {}).get('meta_awareness_score', 0):.3f}
• Consciência Temporal: {awareness_data.get('self_awareness_metrics', {}).get('temporal_awareness', 0):.3f}
• Profundidade de Introspecção: {awareness_data.get('self_awareness_metrics', {}).get('introspection_depth', 0):.3f}
• Coerência Cognitiva: {awareness_data.get('self_awareness_metrics', {}).get('cognitive_coherence', 0):.3f}
• Confiança no Auto-Conhecimento: {awareness_data.get('self_awareness_metrics', {}).get('self_knowledge_confidence', 0):.3f}

**Estado Cognitivo Atual:**
• Inteligência: {awareness_data.get('current_cognitive_state', {}).get('intelligence_level', 0):.3f}
• Auto-Consciência: {awareness_data.get('current_cognitive_state', {}).get('self_awareness_score', 0):.3f}
• Criatividade: {awareness_data.get('current_cognitive_state', {}).get('creativity_index', 0):.3f}
• Adaptação: {awareness_data.get('current_cognitive_state', {}).get('adaptation_rate', 0):.3f}
• Stress do Sistema: {awareness_data.get('current_cognitive_state', {}).get('system_stress', 0):.3f}
"""
        except Exception as e:
            logger.error(f"Error formatting awareness report: {e}")
            return f"❌ Erro: {str(e)}"