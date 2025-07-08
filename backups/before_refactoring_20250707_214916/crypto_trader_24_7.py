#!/usr/bin/env python3
"""
CRYPTO TRADER 24/7 - Sistema completo de trading automático com execução de trades.
Combina detecção de arbitragem + execução automática + gerenciamento de risco.
"""

import asyncio
import sys
import os
import logging
import time
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import colorama
from colorama import Fore, Back, Style

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

# Initialize colorama
colorama.init()

from crypto_hunter_24_7 import CryptoHunter247, ArbitrageAlert

# Load trading components directly to avoid complex dependencies
try:
    import importlib.util
    
    # Load trading engine
    spec_trading = importlib.util.spec_from_file_location(
        "trading_engine", 
        "src/hephaestus/financial/trading_engine.py"
    )
    trading_module = importlib.util.module_from_spec(spec_trading)
    spec_trading.loader.exec_module(trading_module)
    TradingEngine = trading_module.TradingEngine
    MockExchangeAPI = trading_module.MockExchangeAPI
    
    # Load risk manager
    spec_risk = importlib.util.spec_from_file_location(
        "risk_manager", 
        "src/hephaestus/financial/risk_manager.py"
    )
    risk_module = importlib.util.module_from_spec(spec_risk)
    spec_risk.loader.exec_module(risk_module)
    RiskManager = risk_module.RiskManager
    RiskLimits = risk_module.RiskLimits
    
    TRADING_COMPONENTS_LOADED = True
    
except Exception as e:
    print(f"⚠️  Error loading trading components: {e}")
    TradingEngine = None
    MockExchangeAPI = None
    RiskManager = None
    RiskLimits = None
    TRADING_COMPONENTS_LOADED = False

class AutoTrader247:
    """Sistema completo de trading automático 24/7."""
    
    def __init__(self, config: Dict):
        self.config = config
        self.logger = self._setup_logger()
        
        # Componentes principais
        self.hunter = None
        self.trading_engine = None
        self.risk_manager = None
        
        # Estado do sistema
        self.running = False
        self.auto_trading_enabled = config.get('auto_trading_enabled', False)
        self.simulation_mode = config.get('simulation_mode', True)
        
        # Estatísticas
        self.stats = {
            'start_time': None,
            'opportunities_detected': 0,
            'trades_executed': 0,
            'successful_trades': 0,
            'total_profit': 0.0,
            'total_fees': 0.0,
            'uptime': timedelta()
        }
    
    def _setup_logger(self) -> logging.Logger:
        """Setup do sistema de logging."""
        logger = logging.getLogger('AutoTrader247')
        logger.setLevel(logging.INFO)
        
        # File handler
        file_handler = logging.FileHandler('crypto_trader_24_7.log')
        file_handler.setLevel(logging.INFO)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        return logger
    
    async def initialize(self):
        """Inicializar todos os componentes do sistema."""
        try:
            self.logger.info("🚀 Inicializando Auto Trader 24/7...")
            
            # 1. Inicializar CryptoHunter (detecção de oportunidades)
            self.hunter = CryptoHunter247()
            self.hunter.PROFIT_THRESHOLD = self.config.get('min_profit_threshold', 0.003)  # 0.3%
            self.hunter.HIGH_PROFIT_THRESHOLD = self.config.get('high_profit_threshold', 0.01)  # 1%
            self.hunter.SCAN_INTERVAL = self.config.get('scan_interval', 15)  # 15 segundos
            
            # 2. Inicializar Trading Engine
            trading_config = {
                'max_trade_amount': self.config.get('max_trade_amount', 500),
                'min_profit_threshold': self.config.get('min_profit_threshold', 0.003),
                'execution_timeout': self.config.get('execution_timeout', 30)
            }
            self.trading_engine = TradingEngine(trading_config)
            
            # 3. Configurar exchanges (modo simulação por padrão)
            if self.simulation_mode:
                self.logger.info("🧪 Modo simulação ativado - usando exchanges mock")
                self.trading_engine.add_exchange('binance', MockExchangeAPI('binance'))
                self.trading_engine.add_exchange('coinbase', MockExchangeAPI('coinbase'))
                self.trading_engine.add_exchange('kraken', MockExchangeAPI('kraken'))
            else:
                self.logger.warning("⚠️  Modo real ainda não implementado - usando simulação")
                self.trading_engine.add_exchange('binance', MockExchangeAPI('binance'))
                self.trading_engine.add_exchange('coinbase', MockExchangeAPI('coinbase'))
            
            # 4. Inicializar Risk Manager
            risk_limits = RiskLimits(
                max_trade_amount=self.config.get('max_trade_amount', 500),
                max_daily_trades=self.config.get('max_daily_trades', 20),
                max_daily_loss=self.config.get('max_daily_loss', 1000),
                min_profit_threshold=self.config.get('min_profit_threshold', 0.003),
                max_position_size=self.config.get('max_position_size', 0.1),
                stop_loss_percentage=self.config.get('stop_loss_percentage', 0.02)
            )
            self.risk_manager = RiskManager(risk_limits)
            
            # Configurar portfólio inicial (simulação)
            if self.simulation_mode:
                self.risk_manager.portfolio.update_balance('USD', 10000.0)  # $10k inicial
                self.risk_manager.portfolio.update_balance('BTC', 0.1)
                self.risk_manager.portfolio.update_balance('ETH', 2.0)
            
            self.logger.info("✅ Auto Trader 24/7 inicializado com sucesso!")
            
        except Exception as e:
            self.logger.error(f"❌ Erro na inicialização: {e}")
            raise
    
    async def __aenter__(self):
        await self.initialize()
        await self.hunter.__aenter__()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.hunter:
            await self.hunter.__aexit__(exc_type, exc_val, exc_tb)
    
    async def process_opportunity(self, opportunity: ArbitrageAlert) -> bool:
        """Processar uma oportunidade de arbitragem."""
        try:
            self.stats['opportunities_detected'] += 1
            
            # 1. Validação de risco
            trade_amount = min(self.config.get('max_trade_amount', 500), 100)  # Start small
            risk_validation = self.risk_manager.validate_trade(opportunity, trade_amount)
            
            if not risk_validation['approved']:
                self.logger.info(f"🚫 Trade bloqueado por risco: {opportunity.symbol}")
                for block_reason in risk_validation['blocks']:
                    self.logger.info(f"   Motivo: {block_reason}")
                return False
            
            # Ajustar valor se necessário
            if risk_validation['adjusted_amount'] != trade_amount:
                trade_amount = risk_validation['adjusted_amount']
                self.logger.info(f"💰 Valor ajustado para ${trade_amount:.2f}")
            
            # 2. Log da oportunidade
            self.logger.info(f"💰 EXECUTANDO TRADE: {opportunity.symbol}")
            self.logger.info(f"   Lucro esperado: {opportunity.profit_percentage:.3%}")
            self.logger.info(f"   {opportunity.buy_exchange} → {opportunity.sell_exchange}")
            self.logger.info(f"   Valor: ${trade_amount:.2f}")
            self.logger.info(f"   Risk Score: {risk_validation['risk_score']:.2f}")
            
            # 3. Executar arbitragem
            if self.auto_trading_enabled:
                execution_result = await self.trading_engine.execute_arbitrage(opportunity)
                
                if execution_result:
                    # 4. Registrar resultado no risk manager
                    self.risk_manager.record_trade_result(execution_result)
                    
                    # 5. Atualizar estatísticas
                    self.stats['trades_executed'] += 1
                    
                    if execution_result.status == 'completed':
                        self.stats['successful_trades'] += 1
                        self.stats['total_profit'] += execution_result.actual_profit or 0
                        
                        self.logger.info(f"✅ TRADE CONCLUÍDO: ${execution_result.actual_profit:.2f} lucro")
                    else:
                        self.logger.error(f"❌ TRADE FALHOU: {execution_result.status}")
                    
                    # 6. Salvar log de execução
                    self._save_execution_log(opportunity, execution_result, risk_validation)
                    
                    return execution_result.status == 'completed'
                else:
                    self.logger.error(f"❌ Falha na execução de {opportunity.symbol}")
                    return False
            else:
                self.logger.info("📝 MODO ANÁLISE: Trade não executado (auto_trading_enabled=False)")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Erro processando oportunidade {opportunity.symbol}: {e}")
            return False
    
    def _save_execution_log(self, opportunity: ArbitrageAlert, execution_result, risk_validation: Dict):
        """Salvar log detalhado da execução."""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'opportunity': {
                'symbol': opportunity.symbol,
                'profit_percentage': opportunity.profit_percentage,
                'buy_exchange': opportunity.buy_exchange,
                'sell_exchange': opportunity.sell_exchange,
                'buy_price': opportunity.buy_price,
                'sell_price': opportunity.sell_price,
                'confidence': opportunity.confidence
            },
            'risk_validation': risk_validation,
            'execution_result': execution_result.to_dict() if execution_result else None,
            'system_stats': self.get_statistics()
        }
        
        # Append to daily log file
        log_file = f"trades_{datetime.now().strftime('%Y%m%d')}.json"
        
        try:
            # Load existing logs
            if os.path.exists(log_file):
                with open(log_file, 'r') as f:
                    logs = json.load(f)
            else:
                logs = []
            
            # Add new entry
            logs.append(log_entry)
            
            # Save updated logs
            with open(log_file, 'w') as f:
                json.dump(logs, f, indent=2, default=str)
                
        except Exception as e:
            self.logger.error(f"Erro salvando log de execução: {e}")
    
    def print_status_dashboard(self):
        """Imprimir dashboard de status em tempo real."""
        now = datetime.now()
        uptime = now - self.stats['start_time'] if self.stats['start_time'] else timedelta()
        
        # Obter estatísticas atuais
        trading_stats = self.trading_engine.get_statistics() if self.trading_engine else {}
        risk_stats = self.risk_manager.get_daily_statistics() if self.risk_manager else {}
        
        print(f"\n{Fore.CYAN}{'='*80}{Style.RESET_ALL}")
        print(f"{Fore.WHITE}🤖 CRYPTO TRADER 24/7 - DASHBOARD EM TEMPO REAL{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}")
        
        # Status geral
        mode_color = Fore.GREEN if self.auto_trading_enabled else Fore.YELLOW
        mode_text = "TRADING ATIVO" if self.auto_trading_enabled else "ANÁLISE APENAS"
        sim_text = " (SIMULAÇÃO)" if self.simulation_mode else " (REAL)"
        
        print(f"{Fore.GREEN}⏰ Tempo:{Style.RESET_ALL} {now.strftime('%H:%M:%S')}")
        print(f"{Fore.BLUE}⏱️  Uptime:{Style.RESET_ALL} {uptime}")
        print(f"{Fore.YELLOW}🎛️  Modo:{Style.RESET_ALL} {mode_color}{mode_text}{sim_text}{Style.RESET_ALL}")
        
        # Estatísticas de detecção
        print(f"\n{Fore.CYAN}🔍 DETECÇÃO DE OPORTUNIDADES:{Style.RESET_ALL}")
        print(f"   Oportunidades detectadas: {self.stats['opportunities_detected']}")
        print(f"   Threshold mínimo: {self.hunter.PROFIT_THRESHOLD:.3%}" if self.hunter else "N/A")
        print(f"   Intervalo de scan: {self.hunter.SCAN_INTERVAL}s" if self.hunter else "N/A")
        
        # Estatísticas de trading
        print(f"\n{Fore.GREEN}💰 EXECUÇÃO DE TRADES:{Style.RESET_ALL}")
        success_rate = (self.stats['successful_trades'] / max(1, self.stats['trades_executed'])) * 100
        print(f"   Trades executados: {self.stats['trades_executed']}")
        print(f"   Trades bem-sucedidos: {self.stats['successful_trades']}")
        print(f"   Taxa de sucesso: {success_rate:.1f}%")
        print(f"   Lucro total: ${self.stats['total_profit']:.2f}")
        
        # Risk management
        if risk_stats:
            risk_color = Fore.RED if risk_stats.get('circuit_breaker_active') else Fore.GREEN
            print(f"\n{Fore.YELLOW}🛡️  GERENCIAMENTO DE RISCO:{Style.RESET_ALL}")
            print(f"   Nível de risco: {risk_color}{risk_stats.get('portfolio_summary', {}).get('current_drawdown', 0):.1%}{Style.RESET_ALL}")
            print(f"   Circuit breaker: {'ATIVO' if risk_stats.get('circuit_breaker_active') else 'INATIVO'}")
            print(f"   Trades hoje: {risk_stats.get('trades_today', 0)}")
            print(f"   P&L do dia: ${risk_stats.get('net_pnl', 0):.2f}")
        
        # Portfólio (simulação)
        if self.simulation_mode and self.risk_manager:
            portfolio = self.risk_manager.portfolio.get_summary()
            print(f"\n{Fore.MAGENTA}📊 PORTFÓLIO (SIMULAÇÃO):{Style.RESET_ALL}")
            print(f"   Valor total: ${portfolio.get('total_value', 0):.2f}")
            for currency, amount in portfolio.get('balances', {}).items():
                if amount > 0:
                    print(f"   {currency}: {amount:.6f}")
        
        print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}")
    
    async def run_trading_loop(self):
        """Loop principal de trading 24/7."""
        self.running = True
        self.stats['start_time'] = datetime.now()
        
        self.logger.info("🚀 Iniciando loop de trading 24/7...")
        
        try:
            cycle_count = 0
            
            while self.running:
                cycle_start = time.time()
                cycle_count += 1
                
                try:
                    # 1. Buscar oportunidades
                    # Use the hunter's existing method to get prices and detect opportunities
                    prices = await self.hunter.get_all_prices()
                    opportunities = self.hunter.detect_arbitrage_opportunities(prices)
                    
                    # 2. Processar cada oportunidade
                    for opportunity in opportunities:
                        if not self.running:
                            break
                            
                        # Verificar se é uma oportunidade válida para trading
                        if opportunity.profit_percentage >= self.hunter.PROFIT_THRESHOLD:
                            await self.process_opportunity(opportunity)
                            
                            # Pequeno delay entre trades
                            await asyncio.sleep(2)
                    
                    # 3. Mostrar dashboard a cada 10 ciclos
                    if cycle_count % 10 == 0:
                        self.print_status_dashboard()
                    
                    # 4. Salvar estatísticas periodicamente
                    if cycle_count % 50 == 0:
                        self._save_statistics()
                        if self.risk_manager:
                            self.risk_manager.save_risk_log()
                    
                    # 5. Aguardar próximo ciclo
                    cycle_time = time.time() - cycle_start
                    sleep_time = max(0, self.hunter.SCAN_INTERVAL - cycle_time)
                    
                    if sleep_time > 0:
                        await asyncio.sleep(sleep_time)
                    
                except Exception as e:
                    self.logger.error(f"Erro no ciclo de trading: {e}")
                    await asyncio.sleep(5)  # Delay antes de tentar novamente
                    
        except KeyboardInterrupt:
            self.logger.info("🛑 Trading interrompido pelo usuário")
        except Exception as e:
            self.logger.error(f"Erro fatal no loop de trading: {e}")
        finally:
            self.running = False
            await self._cleanup()
    
    def _save_statistics(self):
        """Salvar estatísticas em arquivo."""
        stats_data = {
            'system_stats': self.get_statistics(),
            'trading_stats': self.trading_engine.get_statistics() if self.trading_engine else {},
            'risk_stats': self.risk_manager.get_daily_statistics() if self.risk_manager else {},
            'timestamp': datetime.now().isoformat()
        }
        
        with open('trader_statistics.json', 'w') as f:
            json.dump(stats_data, f, indent=2, default=str)
    
    async def _cleanup(self):
        """Limpeza final do sistema."""
        self.logger.info("🧹 Executando limpeza final...")
        
        # Salvar estatísticas finais
        self._save_statistics()
        
        # Salvar logs de trading
        if self.trading_engine:
            self.trading_engine.save_execution_log()
        
        # Salvar log de risco
        if self.risk_manager:
            self.risk_manager.save_risk_log()
        
        self.logger.info("✅ Limpeza concluída")
    
    def get_statistics(self) -> Dict:
        """Obter estatísticas consolidadas do sistema."""
        now = datetime.now()
        uptime = now - self.stats['start_time'] if self.stats['start_time'] else timedelta()
        
        return {
            **self.stats,
            'uptime_seconds': uptime.total_seconds(),
            'current_time': now.isoformat(),
            'auto_trading_enabled': self.auto_trading_enabled,
            'simulation_mode': self.simulation_mode,
            'running': self.running
        }

async def main():
    """Função principal."""
    print(f"{Fore.GREEN}🤖 CRYPTO TRADER 24/7 - SISTEMA DE TRADING AUTOMÁTICO{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*70}{Style.RESET_ALL}")
    
    # Configuração do sistema
    config = {
        # Trading settings
        'auto_trading_enabled': True,    # True para executar trades automaticamente
        'simulation_mode': True,         # True para usar exchanges mock
        'max_trade_amount': 200,         # Máximo $200 por trade
        'min_profit_threshold': 0.003,   # Mínimo 0.3% de lucro
        'high_profit_threshold': 0.01,   # 1% considerado alto lucro
        
        # Risk management
        'max_daily_trades': 30,          # Máximo 30 trades por dia
        'max_daily_loss': 500,           # Máxima perda de $500/dia
        'max_position_size': 0.1,        # Máximo 10% do portfolio por posição
        'stop_loss_percentage': 0.02,    # Stop loss de 2%
        
        # System settings
        'scan_interval': 15,             # Scan a cada 15 segundos
        'execution_timeout': 30          # Timeout de 30s para execução
    }
    
    print(f"{Fore.WHITE}⚙️  Configuração:{Style.RESET_ALL}")
    print(f"   Auto Trading: {'ATIVADO' if config['auto_trading_enabled'] else 'DESATIVADO'}")
    print(f"   Modo: {'SIMULAÇÃO' if config['simulation_mode'] else 'REAL'}")
    print(f"   Máximo por trade: ${config['max_trade_amount']}")
    print(f"   Threshold de lucro: {config['min_profit_threshold']:.2%}")
    print(f"   Intervalo de scan: {config['scan_interval']}s")
    
    if config['simulation_mode']:
        print(f"\n{Fore.YELLOW}🧪 MODO SIMULAÇÃO ATIVO{Style.RESET_ALL}")
        print(f"   Portfólio inicial: $10,000 USD + 0.1 BTC + 2 ETH")
        print(f"   Trades serão simulados com exchanges mock")
    
    print(f"\n{Fore.GREEN}⚠️  Pressione Ctrl+C para parar o sistema{Style.RESET_ALL}")
    
    # Aguardar confirmação
    await asyncio.sleep(3)
    
    # Inicializar e executar trader
    async with AutoTrader247(config) as trader:
        await trader.run_trading_loop()
    
    print(f"\n{Fore.GREEN}👋 Sistema finalizado!{Style.RESET_ALL}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}🛑 Sistema interrompido pelo usuário{Style.RESET_ALL}")
    except Exception as e:
        print(f"\n{Fore.RED}❌ Erro fatal: {e}{Style.RESET_ALL}")
        import traceback
        traceback.print_exc()