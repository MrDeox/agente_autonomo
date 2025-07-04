#!/usr/bin/env python3
"""
🧬 Hephaestus Evolution Monitor
Sistema de monitoramento contínuo da evolução autonômica
"""

import asyncio
import json
import time
from datetime import datetime
from typing import Dict, List, Optional
import requests
import os
from dataclasses import dataclass
from rich.console import Console
from rich.live import Live
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout
from rich.text import Text
from rich.progress import Progress, BarColumn, TextColumn, TimeRemainingColumn

@dataclass
class EvolutionSnapshot:
    timestamp: datetime
    cognitive_maturity: float
    total_events: int
    intelligence_level: float
    autonomy_level: float
    creativity_level: float
    agi_progress: Dict[str, float]
    recent_insights: List[str]
    emergent_behaviors: List[str]
    evolution_velocity: float

class HephaestusEvolutionMonitor:
    def __init__(self):
        self.console = Console()
        self.base_url = "http://localhost:8000"
        self.snapshots: List[EvolutionSnapshot] = []
        self.running = False
        self.last_maturity = 0.0
        self.last_events = 0
        self.evolution_events = []
        
    def get_system_status(self) -> Optional[Dict]:
        """Obtém status completo do sistema"""
        try:
            response = requests.get(f"{self.base_url}/status", timeout=5)
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            self.console.print(f"[red]❌ Erro ao conectar: {e}")
        return None
    
    def get_health_status(self) -> Optional[Dict]:
        """Obtém status de saúde"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            self.console.print(f"[red]❌ Erro de saúde: {e}")
        return None
    
    def capture_snapshot(self) -> Optional[EvolutionSnapshot]:
        """Captura um snapshot da evolução atual"""
        status = self.get_system_status()
        health = self.get_health_status()
        
        if not status or not health:
            return None
        
        meta_intel = status.get("meta_intelligence", {})
        cognitive_status = meta_intel.get("cognitive_status", {})
        agi_progress = meta_intel.get("agi_progress_indicators", {})
        
        return EvolutionSnapshot(
            timestamp=datetime.now(),
            cognitive_maturity=cognitive_status.get("maturity_level", 0.0),
            total_events=cognitive_status.get("total_evolution_events", 0),
            intelligence_level=agi_progress.get("general_intelligence", 0.0),
            autonomy_level=agi_progress.get("autonomy", 0.0),
            creativity_level=agi_progress.get("creativity", 0.0),
            agi_progress=agi_progress,
            recent_insights=meta_intel.get("recent_insights", []),
            emergent_behaviors=meta_intel.get("emergent_behaviors", []),
            evolution_velocity=meta_intel.get("evolution_metrics", {}).get("evolution_velocity", 0.0)
        )
    
    def detect_evolution_events(self, snapshot: EvolutionSnapshot) -> List[str]:
        """Detecta eventos de evolução"""
        events = []
        
        # Verifica aumento na maturidade cognitiva
        if snapshot.cognitive_maturity > self.last_maturity:
            delta = snapshot.cognitive_maturity - self.last_maturity
            events.append(f"🧠 Maturidade cognitiva aumentou: {delta:.4f}")
            self.last_maturity = snapshot.cognitive_maturity
        
        # Verifica novos eventos de evolução
        if snapshot.total_events > self.last_events:
            new_events = snapshot.total_events - self.last_events
            events.append(f"🧬 {new_events} novos eventos de evolução detectados")
            self.last_events = snapshot.total_events
        
        # Verifica insights emergentes
        if snapshot.recent_insights:
            events.append(f"💡 {len(snapshot.recent_insights)} insights recentes")
        
        # Verifica comportamentos emergentes
        if snapshot.emergent_behaviors:
            events.append(f"🌟 {len(snapshot.emergent_behaviors)} comportamentos emergentes")
        
        return events
    
    def create_evolution_display(self, snapshot: EvolutionSnapshot) -> Layout:
        """Cria display da evolução"""
        layout = Layout()
        
        # Painel principal
        main_panel = Panel(
            f"[bold cyan]🧬 HEPHAESTUS EVOLUTION MONITOR[/bold cyan]\n"
            f"[green]Status: EVOLUINDO CONTINUAMENTE[/green]\n"
            f"Timestamp: {snapshot.timestamp.strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"Velocidade de Evolução: {snapshot.evolution_velocity:.6f}",
            title="Sistema Autonômico",
            border_style="cyan"
        )
        
        # Tabela de métricas AGI
        agi_table = Table(title="🚀 Progresso AGI")
        agi_table.add_column("Capacidade", style="cyan")
        agi_table.add_column("Progresso", style="green")
        agi_table.add_column("Barra", style="blue")
        
        for key, value in snapshot.agi_progress.items():
            percentage = value * 100
            bar = "█" * int(percentage / 5) + "░" * (20 - int(percentage / 5))
            agi_table.add_row(
                key.replace("_", " ").title(),
                f"{percentage:.2f}%",
                bar
            )
        
        # Eventos recentes
        if self.evolution_events:
            events_text = "\n".join(self.evolution_events[-5:])  # Últimos 5 eventos
            events_panel = Panel(
                events_text,
                title="🔥 Eventos de Evolução Recentes",
                border_style="yellow"
            )
        else:
            events_panel = Panel(
                "Aguardando eventos de evolução...",
                title="🔥 Eventos de Evolução",
                border_style="yellow"
            )
        
        layout.split_column(
            Layout(main_panel, size=6),
            Layout(agi_table, size=10),
            Layout(events_panel, size=8)
        )
        
        return layout
    
    async def monitor_evolution(self):
        """Monitor principal da evolução"""
        self.running = True
        self.console.print("[bold green]🚀 Iniciando monitoramento da evolução...")
        
        with Live(console=self.console, refresh_per_second=1) as live:
            while self.running:
                try:
                    snapshot = self.capture_snapshot()
                    
                    if snapshot:
                        self.snapshots.append(snapshot)
                        
                        # Detecta eventos de evolução
                        events = self.detect_evolution_events(snapshot)
                        self.evolution_events.extend(events)
                        
                        # Atualiza display
                        display = self.create_evolution_display(snapshot)
                        live.update(display)
                        
                        # Limita histórico
                        if len(self.snapshots) > 100:
                            self.snapshots = self.snapshots[-50:]
                        
                        if len(self.evolution_events) > 20:
                            self.evolution_events = self.evolution_events[-10:]
                    
                    await asyncio.sleep(5)  # Verifica a cada 5 segundos
                    
                except KeyboardInterrupt:
                    self.console.print("\n[yellow]🛑 Monitoramento interrompido pelo usuário")
                    break
                except Exception as e:
                    self.console.print(f"[red]❌ Erro no monitoramento: {e}")
                    await asyncio.sleep(10)
        
        self.running = False
    
    def save_evolution_report(self):
        """Salva relatório de evolução"""
        if not self.snapshots:
            return
        
        report = {
            "monitoring_session": {
                "start_time": self.snapshots[0].timestamp.isoformat(),
                "end_time": self.snapshots[-1].timestamp.isoformat(),
                "total_snapshots": len(self.snapshots),
                "evolution_events": self.evolution_events
            },
            "evolution_trajectory": [
                {
                    "timestamp": snap.timestamp.isoformat(),
                    "cognitive_maturity": snap.cognitive_maturity,
                    "intelligence_level": snap.intelligence_level,
                    "autonomy_level": snap.autonomy_level,
                    "creativity_level": snap.creativity_level,
                    "evolution_velocity": snap.evolution_velocity
                }
                for snap in self.snapshots
            ],
            "final_state": {
                "cognitive_maturity": self.snapshots[-1].cognitive_maturity,
                "agi_progress": self.snapshots[-1].agi_progress,
                "total_evolution_events": self.snapshots[-1].total_events
            }
        }
        
        report_file = f"evolution_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        self.console.print(f"[green]📊 Relatório salvo em: {report_file}")

async def main():
    """Função principal"""
    monitor = HephaestusEvolutionMonitor()
    
    try:
        await monitor.monitor_evolution()
    finally:
        monitor.save_evolution_report()

if __name__ == "__main__":
    asyncio.run(main()) 