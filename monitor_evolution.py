#!/usr/bin/env python3
"""
Monitor de Evolução do Hephaestus em Tempo Real
"""
import os
import sqlite3
import json
import time
import requests
from datetime import datetime
from pathlib import Path

class HephaestusEvolutionMonitor:
    def __init__(self):
        self.base_path = Path("/home/arthur/projects/agente_autonomo")
        self.db_path = self.base_path / "reports" / "model_performance.db"
        self.memory_path = self.base_path / "data" / "memory" / "HEPHAESTUS_MEMORY.json"
        self.logs_path = self.base_path / "logs"
        self.api_base = "http://localhost:8000"
        
        self.last_performance_count = 0
        self.last_memory_update = None
        self.evolution_detected = []
    
    def check_api_health(self):
        """Verificar se a API está ativa"""
        try:
            response = requests.get(f"{self.api_base}/health", timeout=2)
            return response.status_code == 200
        except:
            return False
    
    def check_performance_db(self):
        """Verificar novos dados de performance"""
        try:
            if not self.db_path.exists():
                return {"status": "DB não existe", "count": 0}
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Contar registros de performance
            cursor.execute("SELECT COUNT(*) FROM performance_data;")
            current_count = cursor.fetchone()[0]
            
            # Ver registros recentes
            cursor.execute("""
                SELECT agent_type, success, quality_score, timestamp 
                FROM performance_data 
                ORDER BY id DESC LIMIT 5
            """)
            recent = cursor.fetchall()
            
            conn.close()
            
            new_records = current_count - self.last_performance_count
            self.last_performance_count = current_count
            
            return {
                "status": "ativo" if current_count > 0 else "inativo",
                "total_records": current_count,
                "new_records": new_records,
                "recent_calls": recent
            }
        except Exception as e:
            return {"status": f"erro: {e}", "count": 0}
    
    def check_memory_updates(self):
        """Verificar atualizações na memória"""
        try:
            if not self.memory_path.exists():
                return {"status": "Memory não existe"}
            
            stat = self.memory_path.stat()
            current_mtime = stat.st_mtime
            
            if self.last_memory_update is None:
                self.last_memory_update = current_mtime
                return {"status": "inicializado"}
            
            if current_mtime > self.last_memory_update:
                self.last_memory_update = current_mtime
                
                # Ler últimas entradas
                with open(self.memory_path) as f:
                    data = json.load(f)
                
                recent_objectives = data.get("completed_objectives", [])[-3:]
                recent_failures = data.get("failed_objectives", [])[-3:]
                
                return {
                    "status": "atualizado",
                    "last_modified": datetime.fromtimestamp(current_mtime).strftime("%H:%M:%S"),
                    "recent_completed": len(recent_objectives),
                    "recent_failed": len(recent_failures),
                    "details": {
                        "completed": recent_objectives,
                        "failed": recent_failures
                    }
                }
            
            return {"status": "sem mudanças"}
        except Exception as e:
            return {"status": f"erro: {e}"}
    
    def check_log_activity(self):
        """Verificar atividade nos logs"""
        try:
            if not self.logs_path.exists():
                return {"status": "Logs não existem"}
            
            # Encontrar log mais recente
            log_files = list(self.logs_path.glob("hephaestus_combined_*.log"))
            if not log_files:
                return {"status": "Nenhum log encontrado"}
            
            latest_log = max(log_files, key=lambda x: x.stat().st_mtime)
            
            # Verificar se está sendo escrito
            stat = latest_log.stat()
            size = stat.st_size
            mtime = stat.st_mtime
            
            # Ler últimas linhas
            try:
                with open(latest_log, 'r') as f:
                    lines = f.readlines()
                    recent_lines = lines[-5:] if lines else []
                
                return {
                    "status": "ativo",
                    "latest_file": latest_log.name,
                    "size_kb": round(size / 1024, 2),
                    "last_modified": datetime.fromtimestamp(mtime).strftime("%H:%M:%S"),
                    "recent_lines": [line.strip() for line in recent_lines]
                }
            except:
                return {
                    "status": "arquivo existe mas não consegue ler",
                    "size_kb": round(size / 1024, 2)
                }
                
        except Exception as e:
            return {"status": f"erro: {e}"}
    
    def check_best_practices(self):
        """Verificar se está capturando melhores práticas"""
        practices_path = self.base_path / "data" / "best_practices"
        
        if not practices_path.exists():
            return {"status": "Pasta não existe"}
        
        # Listar arquivos de templates
        templates = list(practices_path.glob("*_templates.json"))
        
        if not templates:
            return {"status": "Nenhum template encontrado"}
        
        template_info = []
        for template in templates:
            try:
                with open(template) as f:
                    data = json.load(f)
                    template_info.append({
                        "agent": template.stem.replace("_templates", ""),
                        "practices_count": len(data),
                        "avg_score": round(sum(p.get("score", 0) for p in data) / len(data), 3) if data else 0
                    })
            except:
                continue
        
        return {
            "status": "ativo" if template_info else "vazio",
            "templates": template_info
        }
    
    def detect_evolution_activity(self):
        """Detectar sinais de evolução ativa"""
        signals = []
        
        # 1. Performance data sendo coletada
        perf = self.check_performance_db()
        if perf.get("new_records", 0) > 0:
            signals.append(f"📊 {perf['new_records']} novos registros de performance")
        
        # 2. Memória sendo atualizada
        memory = self.check_memory_updates()
        if memory["status"] == "atualizado":
            signals.append(f"🧠 Memória atualizada às {memory['last_modified']}")
        
        # 3. Melhores práticas sendo capturadas
        practices = self.check_best_practices()
        if practices["status"] == "ativo":
            total_practices = sum(t["practices_count"] for t in practices["templates"])
            signals.append(f"✨ {total_practices} melhores práticas capturadas")
        
        return signals
    
    def print_status(self):
        """Imprimir status completo"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"\n{'='*60}")
        print(f"🤖 HEPHAESTUS EVOLUTION MONITOR - {timestamp}")
        print(f"{'='*60}")
        
        # Status da API
        api_healthy = self.check_api_health()
        print(f"🌐 API Status: {'✅ ONLINE' if api_healthy else '❌ OFFLINE'}")
        
        # Performance Database
        perf = self.check_performance_db()
        print(f"📊 Performance DB: {perf['status'].upper()}")
        if perf.get("total_records", 0) > 0:
            print(f"   Total registros: {perf['total_records']}")
            if perf.get("new_records", 0) > 0:
                print(f"   🆕 Novos: {perf['new_records']}")
        
        # Memory Status
        memory = self.check_memory_updates()
        print(f"🧠 Memory: {memory['status'].upper()}")
        if "last_modified" in memory:
            print(f"   Última atualização: {memory['last_modified']}")
        
        # Log Activity
        logs = self.check_log_activity()
        print(f"📄 Logs: {logs['status'].upper()}")
        if "latest_file" in logs:
            print(f"   Arquivo: {logs['latest_file']} ({logs['size_kb']} KB)")
            print(f"   Última modificação: {logs['last_modified']}")
        
        # Best Practices
        practices = self.check_best_practices()
        print(f"✨ Best Practices: {practices['status'].upper()}")
        if practices.get("templates"):
            for template in practices["templates"]:
                print(f"   {template['agent']}: {template['practices_count']} práticas (score: {template['avg_score']})")
        
        # Evolution Detection
        evolution_signals = self.detect_evolution_activity()
        if evolution_signals:
            print(f"\n🧬 EVOLUÇÃO DETECTADA:")
            for signal in evolution_signals:
                print(f"   {signal}")
        else:
            print(f"\n😴 Sistema em estado de espera (sem evolução ativa)")
    
    def monitor(self, interval=30):
        """Monitorar continuamente"""
        print("🚀 Iniciando monitor de evolução do Hephaestus...")
        print(f"⏱️ Intervalo: {interval} segundos")
        print("🛑 Pressione Ctrl+C para parar")
        
        try:
            while True:
                self.print_status()
                time.sleep(interval)
        except KeyboardInterrupt:
            print("\n\n🛑 Monitor parado pelo usuário.")

if __name__ == "__main__":
    monitor = HephaestusEvolutionMonitor()
    monitor.monitor()