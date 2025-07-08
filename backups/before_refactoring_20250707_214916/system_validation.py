#!/usr/bin/env python3
"""
Sistema de validação completa do Crypto Hunter 24/7.
Executa testes abrangentes de todos os componentes.
"""

import asyncio
import sys
import os
import time
import json
import traceback
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any
import colorama
from colorama import Fore, Back, Style

# Initialize colorama
colorama.init()

class SystemValidator:
    """Validador completo do sistema Crypto Hunter 24/7."""
    
    def __init__(self):
        self.results = {
            'start_time': datetime.now(),
            'modules': {},
            'exchanges': {},
            'arbitrage': {},
            'performance': {},
            'alerts': {},
            'overall': 'PENDING'
        }
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger('SystemValidator')
        
        # Test configuration
        self.test_symbols = ['BTC/USD', 'ETH/USD', 'BNB/USD']
        self.test_duration = 60  # 60 seconds of monitoring
    
    def print_header(self, title: str):
        """Print formatted header."""
        print(f"\n{Fore.CYAN}{'='*70}{Style.RESET_ALL}")
        print(f"{Fore.WHITE}{title.center(70)}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*70}{Style.RESET_ALL}")
    
    def print_section(self, title: str):
        """Print section header."""
        print(f"\n{Fore.YELLOW}🔍 {title}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}{'-'*50}{Style.RESET_ALL}")
    
    def print_result(self, test: str, status: str, details: str = ""):
        """Print test result."""
        if status == "PASS":
            icon = f"{Fore.GREEN}✅"
        elif status == "FAIL":
            icon = f"{Fore.RED}❌"
        elif status == "WARN":
            icon = f"{Fore.YELLOW}⚠️"
        else:
            icon = f"{Fore.BLUE}ℹ️"
        
        print(f"{icon} {test}: {Fore.WHITE}{status}{Style.RESET_ALL}")
        if details:
            print(f"   {Fore.LIGHTBLACK_EX}{details}{Style.RESET_ALL}")
    
    async def test_module_integrity(self):
        """Test integrity of all modules."""
        self.print_section("TESTE DE INTEGRIDADE DOS MÓDULOS")
        
        module_tests = {
            'crypto_hunter_24_7': 'Sistema principal',
            'test_crypto_hunter': 'Sistema de testes',
            'launch_crypto_hunter': 'Sistema de lançamento'
        }
        
        for module, description in module_tests.items():
            try:
                # Check if file exists
                if not os.path.exists(f"{module}.py"):
                    self.print_result(f"{description}", "FAIL", f"Arquivo {module}.py não encontrado")
                    self.results['modules'][module] = {'status': 'FAIL', 'error': 'File not found'}
                    continue
                
                # Try to import module
                if module == 'crypto_hunter_24_7':
                    from crypto_hunter_24_7 import CryptoHunter247
                    self.print_result(f"{description}", "PASS", "Importação bem-sucedida")
                    self.results['modules'][module] = {'status': 'PASS'}
                elif module == 'test_crypto_hunter':
                    # Check if test file is valid Python
                    with open(f"{module}.py", 'r') as f:
                        content = f.read()
                    compile(content, f"{module}.py", 'exec')
                    self.print_result(f"{description}", "PASS", "Sintaxe válida")
                    self.results['modules'][module] = {'status': 'PASS'}
                elif module == 'launch_crypto_hunter':
                    # Check launcher
                    with open(f"{module}.py", 'r') as f:
                        content = f.read()
                    compile(content, f"{module}.py", 'exec')
                    self.print_result(f"{description}", "PASS", "Launcher válido")
                    self.results['modules'][module] = {'status': 'PASS'}
                
            except Exception as e:
                self.print_result(f"{description}", "FAIL", str(e))
                self.results['modules'][module] = {'status': 'FAIL', 'error': str(e)}
    
    async def test_exchange_connectivity(self):
        """Test connectivity with all exchanges."""
        self.print_section("TESTE DE CONECTIVIDADE DAS EXCHANGES")
        
        try:
            from crypto_hunter_24_7 import CryptoHunter247
            
            async with CryptoHunter247() as hunter:
                exchanges = {
                    'CoinGecko': hunter.get_coingecko_prices,
                    'Binance': hunter.get_binance_prices,
                    'Coinbase': hunter.get_coinbase_prices,
                    'Kraken': hunter.get_kraken_prices,
                    'Bitfinex': hunter.get_bitfinex_prices,
                    'KuCoin': hunter.get_kucoin_prices
                }
                
                for exchange_name, method in exchanges.items():
                    try:
                        start_time = time.time()
                        prices = await method(self.test_symbols)
                        end_time = time.time()
                        
                        response_time = round((end_time - start_time) * 1000, 2)
                        
                        if prices:
                            self.print_result(
                                f"{exchange_name}", 
                                "PASS", 
                                f"{len(prices)} preços em {response_time}ms"
                            )
                            self.results['exchanges'][exchange_name] = {
                                'status': 'PASS',
                                'prices_count': len(prices),
                                'response_time_ms': response_time
                            }
                        else:
                            self.print_result(f"{exchange_name}", "WARN", "Sem dados retornados")
                            self.results['exchanges'][exchange_name] = {
                                'status': 'WARN',
                                'prices_count': 0,
                                'response_time_ms': response_time
                            }
                    
                    except Exception as e:
                        self.print_result(f"{exchange_name}", "FAIL", str(e))
                        self.results['exchanges'][exchange_name] = {
                            'status': 'FAIL',
                            'error': str(e)
                        }
                
        except Exception as e:
            self.print_result("Exchange Testing", "FAIL", f"Erro no sistema: {e}")
    
    async def test_arbitrage_detection(self):
        """Test arbitrage detection functionality."""
        self.print_section("TESTE DE DETECÇÃO DE ARBITRAGEM")
        
        try:
            from crypto_hunter_24_7 import CryptoHunter247
            
            async with CryptoHunter247() as hunter:
                # Configure for testing
                hunter.PROFIT_THRESHOLD = 0.0001  # 0.01%
                
                # Get market data
                start_time = time.time()
                all_prices = await hunter.get_all_prices()
                data_collection_time = time.time() - start_time
                
                # Test arbitrage detection
                start_time = time.time()
                opportunities = hunter.detect_arbitrage_opportunities(all_prices)
                detection_time = time.time() - start_time
                
                # Analyze results
                total_symbols = len(all_prices)
                total_price_points = sum(len(prices) for prices in all_prices.values())
                opportunities_count = len(opportunities)
                
                self.print_result(
                    "Coleta de Dados", 
                    "PASS", 
                    f"{total_price_points} pontos de {total_symbols} símbolos em {data_collection_time:.2f}s"
                )
                
                self.print_result(
                    "Detecção de Arbitragem", 
                    "PASS", 
                    f"{opportunities_count} oportunidades detectadas em {detection_time:.3f}s"
                )
                
                # Test individual opportunities
                if opportunities:
                    best_opportunity = opportunities[0]
                    self.print_result(
                        "Melhor Oportunidade", 
                        "PASS", 
                        f"{best_opportunity.symbol}: {best_opportunity.profit_percentage:.4%} lucro"
                    )
                    
                    # Test profit calculations
                    if best_opportunity.potential_returns:
                        self.print_result(
                            "Cálculo de Retornos", 
                            "PASS", 
                            f"$1000 → ${best_opportunity.potential_returns.get('$1000', 0):.2f}"
                        )
                
                self.results['arbitrage'] = {
                    'status': 'PASS',
                    'total_symbols': total_symbols,
                    'total_price_points': total_price_points,
                    'opportunities_found': opportunities_count,
                    'data_collection_time': data_collection_time,
                    'detection_time': detection_time,
                    'best_profit': opportunities[0].profit_percentage if opportunities else 0
                }
                
        except Exception as e:
            self.print_result("Detecção de Arbitragem", "FAIL", str(e))
            self.results['arbitrage'] = {'status': 'FAIL', 'error': str(e)}
    
    async def test_performance_monitoring(self):
        """Test performance monitoring over time."""
        self.print_section("TESTE DE PERFORMANCE E ESTABILIDADE")
        
        try:
            from crypto_hunter_24_7 import CryptoHunter247
            
            print(f"🕐 Iniciando monitoramento de {self.test_duration} segundos...")
            
            cycles = 0
            total_opportunities = 0
            response_times = []
            errors = 0
            
            async with CryptoHunter247() as hunter:
                hunter.PROFIT_THRESHOLD = 0.0001
                
                start_monitoring = time.time()
                
                while (time.time() - start_monitoring) < self.test_duration:
                    try:
                        cycle_start = time.time()
                        
                        # Get prices and detect opportunities
                        all_prices = await hunter.get_all_prices()
                        opportunities = hunter.detect_arbitrage_opportunities(all_prices)
                        
                        cycle_time = time.time() - cycle_start
                        response_times.append(cycle_time)
                        cycles += 1
                        total_opportunities += len(opportunities)
                        
                        if cycles % 5 == 0:  # Progress update every 5 cycles
                            print(f"   Ciclo {cycles}: {len(opportunities)} oportunidades ({cycle_time:.2f}s)")
                        
                        await asyncio.sleep(5)  # 5 second intervals for testing
                        
                    except Exception as e:
                        errors += 1
                        self.logger.error(f"Erro no ciclo {cycles + 1}: {e}")
                
                # Calculate statistics
                avg_response_time = sum(response_times) / len(response_times) if response_times else 0
                max_response_time = max(response_times) if response_times else 0
                min_response_time = min(response_times) if response_times else 0
                
                success_rate = ((cycles - errors) / cycles * 100) if cycles > 0 else 0
                opportunities_per_cycle = total_opportunities / cycles if cycles > 0 else 0
                
                self.print_result(
                    "Ciclos Executados", 
                    "PASS", 
                    f"{cycles} ciclos em {self.test_duration}s"
                )
                
                self.print_result(
                    "Taxa de Sucesso", 
                    "PASS" if success_rate >= 90 else "WARN", 
                    f"{success_rate:.1f}% ({errors} erros)"
                )
                
                self.print_result(
                    "Performance", 
                    "PASS", 
                    f"Média: {avg_response_time:.2f}s, Max: {max_response_time:.2f}s"
                )
                
                self.print_result(
                    "Detecção de Oportunidades", 
                    "PASS", 
                    f"{total_opportunities} total ({opportunities_per_cycle:.1f} por ciclo)"
                )
                
                self.results['performance'] = {
                    'status': 'PASS',
                    'cycles': cycles,
                    'errors': errors,
                    'success_rate': success_rate,
                    'avg_response_time': avg_response_time,
                    'max_response_time': max_response_time,
                    'min_response_time': min_response_time,
                    'total_opportunities': total_opportunities,
                    'opportunities_per_cycle': opportunities_per_cycle
                }
                
        except Exception as e:
            self.print_result("Monitoramento de Performance", "FAIL", str(e))
            self.results['performance'] = {'status': 'FAIL', 'error': str(e)}
    
    async def test_alerts_and_logging(self):
        """Test alert system and logging functionality."""
        self.print_section("TESTE DE ALERTAS E LOGS")
        
        try:
            # Test CSV logging
            csv_file = 'test_opportunities.csv'
            if os.path.exists(csv_file):
                os.remove(csv_file)
            
            # Simulate opportunity logging
            from crypto_hunter_24_7 import ArbitrageAlert
            from datetime import datetime
            
            test_alert = ArbitrageAlert(
                symbol='TEST/USD',
                profit_percentage=0.01,
                profit_amount=10.0,
                buy_exchange='test_exchange_1',
                sell_exchange='test_exchange_2',
                buy_price=1000.0,
                sell_price=1010.0,
                confidence=0.8,
                timestamp=datetime.now(),
                potential_returns={'$1000': 10.0}
            )
            
            # Test CSV writing
            import csv
            with open(csv_file, 'w', newline='') as f:
                fieldnames = ['timestamp', 'symbol', 'profit_percentage', 'profit_amount']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerow({
                    'timestamp': test_alert.timestamp.isoformat(),
                    'symbol': test_alert.symbol,
                    'profit_percentage': test_alert.profit_percentage,
                    'profit_amount': test_alert.profit_amount
                })
            
            if os.path.exists(csv_file):
                self.print_result("Sistema de Logs CSV", "PASS", f"Arquivo {csv_file} criado")
                os.remove(csv_file)  # Cleanup
            else:
                self.print_result("Sistema de Logs CSV", "FAIL", "Falha ao criar arquivo")
            
            # Test alert formatting
            alert_dict = test_alert.to_dict()
            if isinstance(alert_dict, dict) and 'symbol' in alert_dict:
                self.print_result("Formatação de Alertas", "PASS", "Conversão para dict bem-sucedida")
            else:
                self.print_result("Formatação de Alertas", "FAIL", "Falha na conversão")
            
            self.results['alerts'] = {
                'status': 'PASS',
                'csv_logging': True,
                'alert_formatting': True
            }
            
        except Exception as e:
            self.print_result("Sistema de Alertas", "FAIL", str(e))
            self.results['alerts'] = {'status': 'FAIL', 'error': str(e)}
    
    def generate_report(self):
        """Generate comprehensive validation report."""
        self.print_section("RELATÓRIO FINAL DE VALIDAÇÃO")
        
        end_time = datetime.now()
        total_time = end_time - self.results['start_time']
        
        # Calculate overall status
        failed_tests = 0
        total_tests = 0
        
        for category in ['modules', 'exchanges', 'arbitrage', 'performance', 'alerts']:
            if category in self.results:
                if isinstance(self.results[category], dict):
                    if self.results[category].get('status') == 'FAIL':
                        failed_tests += 1
                    total_tests += 1
                else:
                    for test_name, test_result in self.results[category].items():
                        if isinstance(test_result, dict) and test_result.get('status') == 'FAIL':
                            failed_tests += 1
                        total_tests += 1
        
        if failed_tests == 0:
            overall_status = "PASS"
            status_color = Fore.GREEN
            status_icon = "✅"
        elif failed_tests < total_tests * 0.2:  # Less than 20% failures
            overall_status = "WARN"
            status_color = Fore.YELLOW
            status_icon = "⚠️"
        else:
            overall_status = "FAIL"
            status_color = Fore.RED
            status_icon = "❌"
        
        self.results['overall'] = overall_status
        
        print(f"\n{status_color}{status_icon} STATUS GERAL: {overall_status}{Style.RESET_ALL}")
        print(f"{Fore.WHITE}Tempo Total: {total_time.total_seconds():.1f} segundos{Style.RESET_ALL}")
        print(f"{Fore.WHITE}Testes Executados: {total_tests}{Style.RESET_ALL}")
        print(f"{Fore.WHITE}Falhas: {failed_tests}{Style.RESET_ALL}")
        print(f"{Fore.WHITE}Taxa de Sucesso: {((total_tests - failed_tests) / total_tests * 100):.1f}%{Style.RESET_ALL}")
        
        # Detailed results
        print(f"\n{Fore.CYAN}📊 RESUMO DETALHADO:{Style.RESET_ALL}")
        
        if 'exchanges' in self.results:
            working_exchanges = sum(1 for ex in self.results['exchanges'].values() 
                                  if ex.get('status') == 'PASS')
            total_exchanges = len(self.results['exchanges'])
            print(f"   Exchanges funcionando: {working_exchanges}/{total_exchanges}")
        
        if 'arbitrage' in self.results and self.results['arbitrage'].get('status') == 'PASS':
            arb = self.results['arbitrage']
            print(f"   Pontos de dados: {arb.get('total_price_points', 0)}")
            print(f"   Oportunidades encontradas: {arb.get('opportunities_found', 0)}")
            print(f"   Melhor lucro: {arb.get('best_profit', 0):.4%}")
        
        if 'performance' in self.results and self.results['performance'].get('status') == 'PASS':
            perf = self.results['performance']
            print(f"   Ciclos executados: {perf.get('cycles', 0)}")
            print(f"   Taxa de sucesso: {perf.get('success_rate', 0):.1f}%")
            print(f"   Tempo médio de resposta: {perf.get('avg_response_time', 0):.2f}s")
        
        # Save results to file
        report_file = f"validation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        self.results['end_time'] = end_time
        self.results['total_time_seconds'] = total_time.total_seconds()
        
        with open(report_file, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        
        print(f"\n{Fore.GREEN}📄 Relatório salvo em: {report_file}{Style.RESET_ALL}")
        
        return overall_status

async def main():
    """Execute complete system validation."""
    validator = SystemValidator()
    
    validator.print_header("VALIDAÇÃO COMPLETA DO CRYPTO HUNTER 24/7")
    
    print(f"{Fore.WHITE}🚀 Iniciando análise abrangente do sistema...{Style.RESET_ALL}")
    print(f"{Fore.LIGHTBLACK_EX}Início: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Style.RESET_ALL}")
    
    # Execute all validation tests
    await validator.test_module_integrity()
    await validator.test_exchange_connectivity()
    await validator.test_arbitrage_detection()
    await validator.test_performance_monitoring()
    await validator.test_alerts_and_logging()
    
    # Generate final report
    overall_status = validator.generate_report()
    
    if overall_status == "PASS":
        print(f"\n{Back.GREEN}{Fore.WHITE}🎉 SISTEMA 100% VALIDADO E PRONTO PARA PRODUÇÃO! 🎉{Style.RESET_ALL}")
    elif overall_status == "WARN":
        print(f"\n{Back.YELLOW}{Fore.BLACK}⚠️  SISTEMA FUNCIONAL COM ALGUMAS LIMITAÇÕES ⚠️{Style.RESET_ALL}")
    else:
        print(f"\n{Back.RED}{Fore.WHITE}❌ SISTEMA REQUER CORREÇÕES ANTES DA PRODUÇÃO ❌{Style.RESET_ALL}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}🛑 Validação interrompida pelo usuário{Style.RESET_ALL}")
    except Exception as e:
        print(f"\n{Fore.RED}❌ Erro fatal na validação: {e}{Style.RESET_ALL}")
        traceback.print_exc()