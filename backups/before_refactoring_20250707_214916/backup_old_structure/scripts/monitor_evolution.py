#!/usr/bin/env python3
"""
🔍 Monitor de Evolução em Tempo Real
Acompanha ativamente a evolução do sistema Hephaestus
"""

import subprocess
import time
import json
import signal
import sys
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List
import threading
import queue

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("EvolutionMonitor")

class EvolutionMonitor:
    """Monitor inteligente para acompanhar a evolução do sistema"""
    
    def __init__(self):
        self.start_time = datetime.now()
        self.cycles_completed = 0
        self.objectives_completed = 0
        self.objectives_failed = 0
        self.evolution_events = []
        self.performance_metrics = []
        self.process = None
        self.monitoring = False
        self.output_queue = queue.Queue()
        
    def start_monitoring(self, target_cycles: int = 10):
        """Inicia o monitoramento por um número específico de ciclos"""
        
        logger.info(f"🚀 INICIANDO MONITORAMENTO DE EVOLUÇÃO")
        logger.info(f"🎯 Meta: {target_cycles} ciclos de evolução")
        logger.info("=" * 60)
        
        self.monitoring = True
        
        # Iniciar processo do Hephaestus
        try:
            self.process = subprocess.Popen(
                ["python", "run_agent.py", "--continuous"],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            # Thread para capturar output
            output_thread = threading.Thread(
                target=self._capture_output,
                daemon=True
            )
            output_thread.start()
            
            # Monitorar por tempo/ciclos específicos
            self._monitor_cycles(target_cycles)
            
        except Exception as e:
            logger.error(f"❌ Erro ao iniciar monitoramento: {e}")
        finally:
            self._stop_monitoring()
    
    def _capture_output(self):
        """Captura output do processo em tempo real"""
        try:
            while self.monitoring and self.process:
                line = self.process.stdout.readline()
                if line:
                    self.output_queue.put(line.strip())
                elif self.process.poll() is not None:
                    break
        except Exception as e:
            logger.error(f"Erro capturando output: {e}")
    
    def _monitor_cycles(self, target_cycles: int):
        """Monitora os ciclos de evolução"""
        
        cycle_timeout = 300  # 5 minutos por ciclo máximo
        last_activity = time.time()
        
        while self.monitoring and self.cycles_completed < target_cycles:
            try:
                # Processar output em tempo real
                try:
                    line = self.output_queue.get(timeout=1)
                    last_activity = time.time()
                    self._process_log_line(line)
                except queue.Empty:
                    pass
                
                # Verificar timeout
                if time.time() - last_activity > cycle_timeout:
                    logger.warning(f"⚠️ Timeout detectado - sem atividade por {cycle_timeout}s")
                    break
                
                # Status periódico
                if int(time.time()) % 30 == 0:  # A cada 30 segundos
                    self._show_status()
                
                time.sleep(0.1)
                
            except KeyboardInterrupt:
                logger.info("🛑 Interrupção manual detectada")
                break
        
        logger.info(f"🏁 Monitoramento concluído após {self.cycles_completed} ciclos")
    
    def _process_log_line(self, line: str):
        """Processa uma linha de log para extrair métricas"""
        
        # Detectar início de ciclo
        if "INÍCIO DO CICLO DE EVOLUÇÃO" in line:
            self.cycles_completed += 1
            cycle_num = self._extract_cycle_number(line)
            logger.info(f"🔄 CICLO #{cycle_num} INICIADO")
            
            self.evolution_events.append({
                "timestamp": datetime.now().isoformat(),
                "type": "cycle_start",
                "cycle": cycle_num
            })
        
        # Detectar objetivos
        elif "OBJETIVO ATUAL:" in line:
            objective = line.split("OBJETIVO ATUAL:")[1].strip()
            logger.info(f"🎯 Novo objetivo: {objective[:100]}...")
        
        # Detectar evolução de prompts
        elif "Prompt evolved for" in line:
            agent_type = line.split("for")[1].strip()
            logger.info(f"🧬 Prompt evoluído para: {agent_type}")
            
            self.evolution_events.append({
                "timestamp": datetime.now().isoformat(),
                "type": "prompt_evolution",
                "agent": agent_type
            })
        
        # Detectar criação de agentes
        elif "new agents created" in line:
            count = self._extract_number(line, "created")
            if count > 0:
                logger.info(f"🏭 {count} novos agentes criados!")
                
                self.evolution_events.append({
                    "timestamp": datetime.now().isoformat(),
                    "type": "agent_creation",
                    "count": count
                })
        
        # Detectar sucesso/falha
        elif "completed" in line.lower() and "failed" in line.lower():
            completed = self._extract_memory_stats(line, "completed")
            failed = self._extract_memory_stats(line, "failed")
            
            if completed is not None:
                self.objectives_completed = completed
            if failed is not None:
                self.objectives_failed = failed
        
        # Detectar métricas de inteligência
        elif "Intelligence level:" in line:
            level = self._extract_float(line, "level:")
            if level:
                logger.info(f"🧠 Nível de inteligência: {level:.3f}")
                
                self.performance_metrics.append({
                    "timestamp": datetime.now().isoformat(),
                    "intelligence_level": level,
                    "cycle": self.cycles_completed
                })
        
        # Detectar comportamentos emergentes
        elif "emergent_behaviors" in line:
            logger.info("🌟 Comportamentos emergentes detectados!")
        
        # Detectar erros críticos
        elif "ERROR" in line or "CRITICAL" in line:
            logger.warning(f"⚠️ Erro detectado: {line}")
    
    def _extract_cycle_number(self, line: str) -> int:
        """Extrai número do ciclo da linha"""
        try:
            if "Ciclo #" in line:
                return int(line.split("Ciclo #")[1].split(")")[0])
        except:
            pass
        return self.cycles_completed
    
    def _extract_number(self, line: str, keyword: str) -> int:
        """Extrai número após uma palavra-chave"""
        try:
            parts = line.split(keyword)
            if len(parts) > 1:
                # Procurar número antes da palavra-chave
                before = parts[0].split()[-1]
                return int(before)
        except:
            pass
        return 0
    
    def _extract_memory_stats(self, line: str, stat_type: str) -> int:
        """Extrai estatísticas de memória"""
        try:
            if stat_type in line:
                # Procurar padrão "X completed" ou "Y failed"
                parts = line.split(stat_type)
                if len(parts) > 0:
                    before = parts[0].split()[-1]
                    return int(before)
        except:
            pass
        return None
    
    def _extract_float(self, line: str, keyword: str) -> float:
        """Extrai valor float após palavra-chave"""
        try:
            parts = line.split(keyword)
            if len(parts) > 1:
                value_str = parts[1].strip().split()[0]
                return float(value_str)
        except:
            pass
        return None
    
    def _show_status(self):
        """Mostra status atual do monitoramento"""
        elapsed = (datetime.now() - self.start_time).total_seconds()
        
        logger.info("📊 STATUS ATUAL:")
        logger.info(f"   ⏰ Tempo decorrido: {elapsed:.1f}s")
        logger.info(f"   🔄 Ciclos completados: {self.cycles_completed}")
        logger.info(f"   ✅ Objetivos concluídos: {self.objectives_completed}")
        logger.info(f"   ❌ Objetivos falhados: {self.objectives_failed}")
        logger.info(f"   🧬 Eventos de evolução: {len(self.evolution_events)}")
        logger.info(f"   📈 Métricas coletadas: {len(self.performance_metrics)}")
    
    def _stop_monitoring(self):
        """Para o monitoramento e gera relatório final"""
        self.monitoring = False
        
        if self.process:
            try:
                self.process.terminate()
                self.process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                self.process.kill()
            except Exception as e:
                logger.error(f"Erro parando processo: {e}")
        
        self._generate_final_report()
    
    def _generate_final_report(self):
        """Gera relatório final da evolução"""
        
        elapsed = (datetime.now() - self.start_time).total_seconds()
        
        logger.info("\n" + "🎯" * 20)
        logger.info("📋 RELATÓRIO FINAL DE EVOLUÇÃO")
        logger.info("🎯" * 20)
        
        logger.info(f"⏰ Duração total: {elapsed:.1f} segundos ({elapsed/60:.1f} minutos)")
        logger.info(f"🔄 Ciclos completados: {self.cycles_completed}")
        logger.info(f"✅ Objetivos concluídos: {self.objectives_completed}")
        logger.info(f"❌ Objetivos falhados: {self.objectives_failed}")
        
        # Taxa de sucesso
        total_objectives = self.objectives_completed + self.objectives_failed
        success_rate = 0
        if total_objectives > 0:
            success_rate = (self.objectives_completed / total_objectives) * 100
            logger.info(f"📊 Taxa de sucesso: {success_rate:.1f}%")
        
        # Eventos de evolução
        evolution_types = {}
        for event in self.evolution_events:
            event_type = event["type"]
            evolution_types[event_type] = evolution_types.get(event_type, 0) + 1
        
        logger.info("🧬 Eventos de evolução:")
        for event_type, count in evolution_types.items():
            logger.info(f"   • {event_type}: {count}")
        
        # Progresso de inteligência
        if self.performance_metrics:
            initial_intelligence = self.performance_metrics[0]["intelligence_level"]
            final_intelligence = self.performance_metrics[-1]["intelligence_level"]
            intelligence_growth = final_intelligence - initial_intelligence
            
            logger.info(f"🧠 Evolução de inteligência:")
            logger.info(f"   • Inicial: {initial_intelligence:.3f}")
            logger.info(f"   • Final: {final_intelligence:.3f}")
            logger.info(f"   • Crescimento: +{intelligence_growth:.3f}")
        
        # Velocidade de evolução
        if elapsed > 0:
            cycles_per_minute = (self.cycles_completed / elapsed) * 60
            logger.info(f"⚡ Velocidade: {cycles_per_minute:.2f} ciclos/minuto")
        
        # Salvar relatório detalhado
        report_data = {
            "summary": {
                "duration_seconds": elapsed,
                "cycles_completed": self.cycles_completed,
                "objectives_completed": self.objectives_completed,
                "objectives_failed": self.objectives_failed,
                "success_rate": success_rate
            },
            "evolution_events": self.evolution_events,
            "performance_metrics": self.performance_metrics,
            "timestamp": datetime.now().isoformat()
        }
        
        report_file = f"evolution_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        logger.info(f"💾 Relatório detalhado salvo em: {report_file}")
        logger.info("🎉 Monitoramento concluído com sucesso!")

def main():
    """Função principal"""
    
    if len(sys.argv) > 1:
        try:
            target_cycles = int(sys.argv[1])
        except ValueError:
            target_cycles = 10
    else:
        target_cycles = 10
    
    monitor = EvolutionMonitor()
    
    # Handler para interrupção
    def signal_handler(sig, frame):
        logger.info("🛑 Interrupção recebida - parando monitoramento...")
        monitor._stop_monitoring()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        monitor.start_monitoring(target_cycles)
    except Exception as e:
        logger.error(f"❌ Erro durante monitoramento: {e}")
    finally:
        logger.info("🎯 Monitor finalizado")

if __name__ == "__main__":
    main() 