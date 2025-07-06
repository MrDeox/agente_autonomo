#!/usr/bin/env python3
"""
🧠 Monitor de Fiscalização Hephaestus
Sistema de monitoramento contínuo para o agente autônomo
"""

import time
import json
import requests
import subprocess
import psutil
from datetime import datetime, timedelta
from pathlib import Path
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/monitor_hephaestus.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class HephaestusMonitor:
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.check_interval = 30  # segundos
        self.alert_threshold = 3  # falhas consecutivas antes do alerta
        self.failure_count = 0
        self.last_check = None
        
    def check_server_status(self):
        """Verifica se o servidor está respondendo"""
        try:
            response = requests.get(f"{self.base_url}/status", timeout=5)
            if response.status_code == 200:
                data = response.json()
                return {
                    'status': 'running',
                    'data': data,
                    'timestamp': datetime.now().isoformat()
                }
            else:
                return {
                    'status': 'error',
                    'error': f"HTTP {response.status_code}",
                    'timestamp': datetime.now().isoformat()
                }
        except requests.exceptions.RequestException as e:
            return {
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def check_process_status(self):
        """Verifica se o processo uvicorn está rodando"""
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                cmdline = proc.info['cmdline'] or []
                if (proc.info['name'] == 'python3.11' and 
                    any('uvicorn' in str(cmd) for cmd in cmdline)):
                    return {
                        'status': 'running',
                        'pid': proc.info['pid'],
                        'memory_mb': proc.memory_info().rss / 1024 / 1024,
                        'cpu_percent': proc.cpu_percent()
                    }
            return {'status': 'not_found'}
        except Exception as e:
            return {'status': 'error', 'error': str(e)}
    
    def check_evolution_log(self):
        """Analisa o log de evolução para métricas"""
        try:
            log_file = Path('logs/evolution_log.csv')
            if not log_file.exists():
                return {'status': 'no_file'}
            
            with open(log_file, 'r') as f:
                lines = f.readlines()
            
            if len(lines) <= 1:  # apenas header
                return {'status': 'no_data'}
            
            # Analisar últimas 10 entradas
            recent_entries = lines[-10:]
            success_count = sum(1 for line in recent_entries if 'success' in line.lower())
            failure_count = sum(1 for line in recent_entries if 'failure' in line.lower())
            
            # Calcular taxa de sucesso
            total_recent = success_count + failure_count
            success_rate = (success_count / total_recent * 100) if total_recent > 0 else 0
            
            return {
                'status': 'ok',
                'success_rate': success_rate,
                'recent_successes': success_count,
                'recent_failures': failure_count,
                'total_recent': total_recent
            }
        except Exception as e:
            return {'status': 'error', 'error': str(e)}
    
    def check_error_logs(self):
        """Verifica logs de erro recentes"""
        try:
            log_file = Path('logs/uvicorn.log')
            if not log_file.exists():
                return {'status': 'no_file'}
            
            # Buscar erros nas últimas 50 linhas
            result = subprocess.run(
                ['tail', '-n', '50', str(log_file)],
                capture_output=True, text=True, timeout=10
            )
            
            if result.returncode != 0:
                return {'status': 'error', 'error': 'Failed to read log file'}
            
            lines = result.stdout.split('\n')
            errors = [line for line in lines if 'ERROR' in line or 'CRITICAL' in line]
            warnings = [line for line in lines if 'WARNING' in line]
            
            return {
                'status': 'ok',
                'error_count': len(errors),
                'warning_count': len(warnings),
                'recent_errors': errors[-3:] if errors else [],
                'recent_warnings': warnings[-3:] if warnings else []
            }
        except Exception as e:
            return {'status': 'error', 'error': str(e)}
    
    def generate_alert(self, alert_type, message, data=None):
        """Gera alerta com timestamp"""
        alert = {
            'type': alert_type,
            'message': message,
            'timestamp': datetime.now().isoformat(),
            'data': data
        }
        
        logger.warning(f"🚨 ALERTA: {alert_type} - {message}")
        
        # Salvar alerta em arquivo
        alerts_file = Path('logs/hephaestus_alerts.json')
        alerts = []
        
        if alerts_file.exists():
            try:
                with open(alerts_file, 'r') as f:
                    alerts = json.load(f)
            except:
                alerts = []
        
        alerts.append(alert)
        
        # Manter apenas últimos 100 alertas
        if len(alerts) > 100:
            alerts = alerts[-100:]
        
        with open(alerts_file, 'w') as f:
            json.dump(alerts, f, indent=2)
        
        return alert
    
    def check_system_health(self):
        """Executa verificação completa do sistema"""
        logger.info("🔍 Iniciando verificação de saúde do sistema...")
        
        checks = {
            'server_status': self.check_server_status(),
            'process_status': self.check_process_status(),
            'evolution_log': self.check_evolution_log(),
            'error_logs': self.check_error_logs()
        }
        
        # Análise de alertas
        alerts = []
        
        # Verificar servidor
        if checks['server_status']['status'] != 'running':
            alerts.append(self.generate_alert(
                'CRITICAL',
                f"Servidor não está respondendo: {checks['server_status'].get('error', 'Unknown error')}",
                checks['server_status']
            ))
        
        # Verificar processo
        if checks['process_status']['status'] != 'running':
            alerts.append(self.generate_alert(
                'CRITICAL',
                "Processo uvicorn não encontrado",
                checks['process_status']
            ))
        
        # Verificar taxa de sucesso
        if checks['evolution_log']['status'] == 'ok':
            success_rate = checks['evolution_log'].get('success_rate', 0)
            if isinstance(success_rate, (int, float)) and success_rate < 30:
                alerts.append(self.generate_alert(
                    'WARNING',
                    f"Taxa de sucesso muito baixa: {success_rate:.1f}%",
                    checks['evolution_log']
                ))
        
        # Verificar erros recentes
        if checks['error_logs']['status'] == 'ok':
            error_count = checks['error_logs'].get('error_count', 0)
            if isinstance(error_count, (int, float)) and error_count > 5:
                alerts.append(self.generate_alert(
                    'WARNING',
                    f"Muitos erros recentes: {error_count}",
                    checks['error_logs']
                ))
        
        # Status geral
        if not alerts:
            status = "🟢 SAUDÁVEL"
        elif any(a['type'] == 'CRITICAL' for a in alerts):
            status = "🔴 CRÍTICO"
        else:
            status = "🟡 ATENÇÃO"
        
        # Gerar relatório
        report = {
            'timestamp': datetime.now().isoformat(),
            'status': status,
            'checks': checks,
            'alerts': alerts,
            'alert_count': len(alerts)
        }
        
        logger.info(f"✅ Verificação completa: {status} ({len(alerts)} alertas)")
        
        return report
    
    def run_continuous_monitoring(self):
        """Executa monitoramento contínuo"""
        logger.info("🚀 Iniciando monitoramento contínuo do Hephaestus...")
        logger.info(f"📊 Intervalo de verificação: {self.check_interval} segundos")
        
        try:
            while True:
                report = self.check_system_health()
                
                # Salvar relatório
                reports_file = Path('logs/hephaestus_monitoring.json')
                with open(reports_file, 'w') as f:
                    json.dump(report, f, indent=2)
                
                # Aguardar próximo ciclo
                time.sleep(self.check_interval)
                
        except KeyboardInterrupt:
            logger.info("🛑 Monitoramento interrompido pelo usuário")
        except Exception as e:
            logger.error(f"❌ Erro no monitoramento: {e}")
            raise

def main():
    """Função principal"""
    monitor = HephaestusMonitor()
    
    # Verificação única ou contínua
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == '--once':
        report = monitor.check_system_health()
        print(json.dumps(report, indent=2))
    else:
        monitor.run_continuous_monitoring()

if __name__ == "__main__":
    main() 