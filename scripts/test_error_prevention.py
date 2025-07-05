#!/usr/bin/env python3
"""
Test Error Prevention System - Script para testar o sistema de prevenção de erros
"""

import sys
import os
import logging
import time
from datetime import datetime

# Adicionar o projeto ao path
sys.path.insert(0, os.path.abspath('.'))

from agent.utils.error_prevention_system import ErrorPreventionSystem, ErrorEvent, ErrorType, ErrorSeverity
from agent.utils.startup_validator import StartupValidator
from agent.utils.continuous_monitor import ContinuousMonitor
from agent.config_loader import load_config

def setup_logging():
    """Configura logging para os testes"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/error_prevention_test.log'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger("error_prevention_test")

def test_error_prevention_system():
    """Testa o sistema de prevenção de erros"""
    logger = setup_logging()
    logger.info("🧪 Iniciando testes do sistema de prevenção de erros")
    
    # Carregar configuração
    config = load_config()
    
    # Teste 1: Sistema de Prevenção de Erros
    logger.info("Teste 1: Sistema de Prevenção de Erros")
    error_prevention = ErrorPreventionSystem(logger)
    error_prevention.start()
    
    # Simular alguns erros
    test_errors = [
        ErrorEvent(
            timestamp=datetime.now(),
            error_type=ErrorType.CONSTRUCTOR_ERROR,
            severity=ErrorSeverity.CRITICAL,
            component="MaestroAgent",
            error_message="Test constructor error",
            stack_trace="Test stack trace",
            context={'test': True}
        ),
        ErrorEvent(
            timestamp=datetime.now(),
            error_type=ErrorType.RUNTIME_ERROR,
            severity=ErrorSeverity.MEDIUM,
            component="ArchitectAgent",
            error_message="Test runtime error",
            stack_trace="Test stack trace",
            context={'test': True}
        )
    ]
    
    for error in test_errors:
        error_prevention.record_error(error)
        time.sleep(0.1)
    
    # Verificar status
    status = error_prevention.get_system_status()
    logger.info(f"Status do sistema: {status}")
    
    error_prevention.stop()
    
    # Teste 2: Validador de Startup
    logger.info("Teste 2: Validador de Startup")
    startup_validator = StartupValidator(logger)
    
    validation_result = startup_validator.validate_all(config)
    logger.info(f"Validação de startup: {'PASSOU' if validation_result else 'FALHOU'}")
    
    if not validation_result:
        summary = startup_validator.get_validation_summary()
        logger.error(f"Resumo da validação: {summary}")
    
    # Teste 3: Monitoramento Contínuo
    logger.info("Teste 3: Monitoramento Contínuo")
    continuous_monitor = ContinuousMonitor(logger, check_interval=5)
    continuous_monitor.start_monitoring()
    
    # Deixar monitorar por alguns segundos
    time.sleep(10)
    
    # Verificar status
    monitor_status = continuous_monitor.get_system_status()
    logger.info(f"Status do monitoramento: {monitor_status}")
    
    # Gerar relatório
    report = continuous_monitor.generate_monitoring_report()
    logger.info(f"Relatório de monitoramento:\n{report}")
    
    continuous_monitor.stop_monitoring()
    
    # Teste 4: Validação de Construtores
    logger.info("Teste 4: Validação de Construtores")
    
    # Testar validação de construtor correto
    from agent.agents.maestro_agent import MaestroAgent
    test_logger = logging.getLogger("test")
    
    try:
        maestro = MaestroAgent(
            model_config={"model": "gpt-4"},
            logger=test_logger,
            config=config
        )
        logger.info("✅ Construtor do MaestroAgent validado com sucesso")
    except Exception as e:
        logger.error(f"❌ Falha na validação do construtor: {e}")
    
    # Teste 5: Simulação de Problemas
    logger.info("Teste 5: Simulação de Problemas")
    
    # Simular problema de CPU alto
    cpu_alert = ErrorEvent(
        timestamp=datetime.now(),
        error_type=ErrorType.RUNTIME_ERROR,
        severity=ErrorSeverity.CRITICAL,
        component="system",
        error_message="CPU usage critical: 95%",
        stack_trace="",
        context={'cpu_percent': 95.0}
    )
    
    error_prevention.record_error(cpu_alert)
    
    # Verificar se a recuperação automática foi tentada
    recovery_history = error_prevention.auto_recovery.recovery_history
    logger.info(f"Tentativas de recuperação: {len(recovery_history)}")
    
    for recovery in recovery_history:
        logger.info(f"Recuperação: {recovery.resolution_method} - {'Sucesso' if recovery.resolved else 'Falha'}")
    
    logger.info("🎉 Todos os testes do sistema de prevenção de erros concluídos!")
    
    return True

def test_integration():
    """Testa a integração dos sistemas"""
    logger = setup_logging()
    logger.info("🔗 Testando integração dos sistemas")
    
    config = load_config()
    
    # Criar instância do HephaestusAgent para testar integração
    try:
        from agent.hephaestus_agent import HephaestusAgent
        
        # Criar logger temporário
        temp_logger = logging.getLogger("integration_test")
        
        # Inicializar agente (isso deve ativar todos os sistemas de prevenção)
        agent = HephaestusAgent(
            logger_instance=temp_logger,
            config=config,
            continuous_mode=False
        )
        
        # Verificar se os sistemas foram inicializados
        has_error_prevention = hasattr(agent, 'error_prevention')
        has_continuous_monitor = hasattr(agent, 'continuous_monitor')
        
        logger.info(f"Sistema de prevenção de erros: {'✅' if has_error_prevention else '❌'}")
        logger.info(f"Monitoramento contínuo: {'✅' if has_continuous_monitor else '❌'}")
        
        if has_error_prevention and has_continuous_monitor:
            # Testar relatório de saúde
            health_report = agent.get_system_health_report()
            logger.info(f"Relatório de saúde: {health_report['overall_health']}")
            
            logger.info("✅ Integração dos sistemas funcionando corretamente!")
        else:
            logger.error("❌ Falha na integração dos sistemas")
            return False
        
        # Cleanup
        del agent
        
    except Exception as e:
        logger.error(f"❌ Erro na integração: {e}")
        return False
    
    return True

def main():
    """Função principal dos testes"""
    print("🚀 Iniciando testes do sistema de prevenção de erros...")
    
    # Criar diretório de logs se não existir
    os.makedirs("logs", exist_ok=True)
    
    # Executar testes
    tests = [
        ("Sistema de Prevenção de Erros", test_error_prevention_system),
        ("Integração dos Sistemas", test_integration)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n🧪 Executando: {test_name}")
        try:
            result = test_func()
            results.append((test_name, result))
            print(f"{'✅ PASSOU' if result else '❌ FALHOU'}: {test_name}")
        except Exception as e:
            results.append((test_name, False))
            print(f"❌ ERRO: {test_name} - {e}")
    
    # Resumo final
    print("\n" + "="*60)
    print("RESUMO DOS TESTES")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} testes passaram")
    
    if passed == total:
        print("🎉 Todos os testes passaram! Sistema de prevenção funcionando corretamente.")
        return 0
    else:
        print("⚠️ Alguns testes falharam. Verifique os logs para detalhes.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 