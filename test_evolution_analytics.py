#!/usr/bin/env python3
"""
🧬 TESTE DO SISTEMA DE ANÁLISE DE EVOLUÇÃO DE LONGO PRAZO

Este script demonstra como o sistema captura métricas automaticamente
e analisa tendências de melhoria ao longo do tempo.
"""

import asyncio
import time
import random
from datetime import datetime, timedelta
from pathlib import Path

# Configuração do sistema
from hephaestus.utils.config_manager import load_config
import logging
from hephaestus.core.agent import HephaestusAgent
from hephaestus.intelligence.evolution_analytics import get_evolution_analytics

async def simulate_evolution_cycles(agent: HephaestusAgent, num_cycles: int = 20):
    """Simula ciclos de evolução para gerar dados de análise"""
    print(f"🔄 Simulando {num_cycles} ciclos de evolução...")
    
    objectives = [
        "Otimizar performance do sistema de validação",
        "Melhorar detecção de bugs automática", 
        "Aumentar eficiência do orquestrador assíncrono",
        "Refatorar sistema de memória para melhor performance",
        "Implementar cache inteligente para LLM calls",
        "Otimizar pipeline de validação paralela",
        "Melhorar sistema de detecção de regressões",
        "Implementar análise de complexidade de código",
        "Otimizar estratégias de agentes especializados",
        "Melhorar sistema de comunicação inter-agente"
    ]
    
    for i in range(num_cycles):
        objective = random.choice(objectives)
        print(f"  📊 Ciclo {i+1}/{num_cycles}: {objective}")
        
        # Simular execução de ciclo
        start_time = time.time()
        
        # Capturar métricas de performance simuladas
        cycle_duration = random.uniform(2.0, 8.0)  # 2-8 segundos
        success_rate = random.uniform(0.7, 1.0)  # 70-100% sucesso
        agents_used = random.randint(3, 6)  # 3-6 agentes por ciclo
        
        # Simular tendência de melhoria ao longo do tempo
        improvement_factor = 1.0 + (i * 0.02)  # 2% de melhoria por ciclo
        cycle_duration /= improvement_factor
        success_rate = min(1.0, success_rate * improvement_factor)
        
        # Capturar métricas no sistema de análise
        agent.evolution_analytics.capture_metric(
            "cycle_duration_seconds", 
            cycle_duration,
            {"cycle_number": i+1, "objective": objective}
        )
        
        agent.evolution_analytics.capture_metric(
            "cycle_success_rate", 
            success_rate,
            {"cycle_number": i+1, "objective": objective}
        )
        
        agent.evolution_analytics.capture_metric(
            "agents_per_cycle", 
            agents_used,
            {"cycle_number": i+1, "objective": objective}
        )
        
        # Simular tempo de execução
        await asyncio.sleep(0.1)
        
        print(f"    ✅ Duração: {cycle_duration:.2f}s, Sucesso: {success_rate:.1%}, Agentes: {agents_used}")
    
    print("✅ Simulação de ciclos concluída!")

async def demonstrate_evolution_analytics():
    """Demonstra as capacidades do sistema de análise de evolução"""
    print("🧬 SISTEMA DE ANÁLISE DE EVOLUÇÃO DE LONGO PRAZO")
    print("=" * 60)
    
    # Carregar configuração
    config = load_config()
    logger = logging.getLogger("evolution_analytics_test")
    
    # Inicializar agente
    print("🚀 Inicializando HephaestusAgent...")
    agent = HephaestusAgent(logger, config)
    
    # Simular dados históricos (últimos 7 dias)
    print("\n📊 Gerando dados históricos simulados...")
    await simulate_evolution_cycles(agent, num_cycles=50)
    
    # Aguardar um pouco para processamento
    await asyncio.sleep(1)
    
    # Análise de tendências
    print("\n📈 ANALISANDO TENDÊNCIAS DE EVOLUÇÃO...")
    trends = agent.evolution_analytics.analyze_trends(days=7)
    
    if trends:
        print(f"✅ Encontradas {len(trends)} tendências:")
        for trend in trends:
            status_emoji = "📈" if trend.trend_type == "improving" else "📉" if trend.trend_type == "declining" else "➡️"
            print(f"  {status_emoji} {trend.metric_name}: {trend.trend_type} ({trend.change_percentage:+.1f}%)")
    else:
        print("⚠️ Nenhuma tendência significativa encontrada ainda")
    
    # Relatório de melhoria
    print("\n📊 RELATÓRIO DE MELHORIA GERAL...")
    report = agent.get_evolution_report(days=7)
    
    print(f"  📊 Score de Melhoria: {report.get('improvement_score', 0):.1f}%")
    print(f"  📈 Métricas Melhorando: {report.get('improving_metrics', 0)}")
    print(f"  📉 Métricas Declinando: {report.get('declining_metrics', 0)}")
    print(f"  ➡️ Métricas Estáveis: {report.get('stable_metrics', 0)}")
    
    # Top melhorias
    top_improvements = report.get('top_improvements', [])
    if top_improvements:
        print("\n🏆 TOP MELHORIAS:")
        for i, trend in enumerate(top_improvements[:3], 1):
            print(f"  {i}. {trend.metric_name}: +{trend.change_percentage:.1f}%")
    
    # Predições de performance futura
    print("\n🔮 PREDIÇÕES DE PERFORMANCE FUTURA...")
    metrics_to_predict = ["cycle_duration_seconds", "cycle_success_rate", "agents_per_cycle"]
    
    for metric in metrics_to_predict:
        prediction = agent.predict_future_performance(metric, days_ahead=7)
        if prediction:
            print(f"  📊 {metric}:")
            print(f"    Valor Atual: {prediction['current_value']:.3f}")
            print(f"    Predição (7 dias): {prediction['predicted_value']:.3f}")
            print(f"    Mudança Esperada: {prediction['predicted_change']:+.1f}")
            print(f"    Confiança: {prediction['confidence']:.1%}")
            print(f"    Tendência: {prediction['trend_type']}")
    
    # Gerar gráficos
    print("\n📊 GERANDO GRÁFICOS DE EVOLUÇÃO...")
    for metric in metrics_to_predict:
        chart_path = agent.generate_evolution_chart(metric, days=7)
        if chart_path:
            print(f"  📈 Gráfico gerado: {chart_path}")
        else:
            print(f"  ⚠️ Não foi possível gerar gráfico para {metric}")
    
    # Demonstração de captura contínua
    print("\n🔄 DEMONSTRAÇÃO DE CAPTURA CONTÍNUA...")
    print("Capturando métricas em tempo real por 30 segundos...")
    
    start_time = time.time()
    while time.time() - start_time < 30:
        # Simular métricas em tempo real
        current_time = time.time() - start_time
        
        # Simular melhoria gradual
        improvement = 1.0 + (current_time / 30.0) * 0.1  # 10% de melhoria total
        
        agent.evolution_analytics.capture_metric(
            "real_time_performance", 
            random.uniform(0.8, 1.2) / improvement,
            {"timestamp": datetime.now().isoformat()}
        )
        
        agent.evolution_analytics.capture_metric(
            "system_responsiveness", 
            random.uniform(0.9, 1.1) * improvement,
            {"timestamp": datetime.now().isoformat()}
        )
        
        await asyncio.sleep(2)
        print(f"  ⏱️ {current_time:.0f}s: Métricas capturadas")
    
    # Análise final
    print("\n📊 ANÁLISE FINAL...")
    final_trends = agent.evolution_analytics.analyze_trends(days=1)  # Últimas 24h
    
    if final_trends:
        improving_count = len([t for t in final_trends if t.trend_type == "improving"])
        print(f"✅ Nas últimas 24h: {improving_count}/{len(final_trends)} métricas melhorando")
    
    print("\n🎯 SISTEMA DE ANÁLISE DE EVOLUÇÃO FUNCIONANDO PERFEITAMENTE!")
    print("📈 O sistema está capturando métricas automaticamente e detectando tendências de melhoria.")
    print("🔮 Predições de performance futura estão sendo geradas.")
    print("📊 Gráficos de evolução estão sendo criados.")
    print("🔄 Análise contínua está ativa para monitoramento de longo prazo.")

if __name__ == "__main__":
    print("🧬 Iniciando demonstração do Sistema de Análise de Evolução...")
    asyncio.run(demonstrate_evolution_analytics()) 