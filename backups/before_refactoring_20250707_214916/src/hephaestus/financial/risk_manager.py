"""
Risk Manager - Sistema avançado de gerenciamento de risco para trading automático.
"""

import logging
import time
import json
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from decimal import Decimal

@dataclass
class RiskLimits:
    """Definição de limites de risco."""
    max_trade_amount: float = 1000.0  # Máximo por trade em USD
    max_daily_trades: int = 50        # Máximo de trades por dia
    max_daily_loss: float = 500.0     # Máxima perda diária em USD
    max_position_size: float = 0.05   # Máximo 5% do portfolio por posição
    min_profit_threshold: float = 0.005  # Mínimo 0.5% de lucro
    max_slippage: float = 0.002       # Máximo 0.2% de slippage
    stop_loss_percentage: float = 0.01  # Stop loss de 1%
    max_drawdown: float = 0.10        # Máximo drawdown de 10%
    cooldown_after_loss: int = 300    # 5 minutos de cooldown após perda

@dataclass
class RiskEvent:
    """Evento de risco detectado."""
    timestamp: datetime
    risk_type: str
    severity: str  # 'low', 'medium', 'high', 'critical'
    description: str
    action_taken: str
    metadata: Dict[str, Any]

class PortfolioManager:
    """Gerenciador de portfólio e posições."""
    
    def __init__(self):
        self.positions = {}  # {symbol: {amount, avg_price, unrealized_pnl}}
        self.balances = {}   # {currency: amount}
        self.total_value = 0.0
        self.daily_pnl = 0.0
        self.max_value = 0.0
        self.logger = logging.getLogger('PortfolioManager')
    
    def update_balance(self, currency: str, amount: float):
        """Atualizar saldo de uma moeda."""
        self.balances[currency] = amount
        self._recalculate_total_value()
    
    def update_position(self, symbol: str, amount: float, price: float):
        """Atualizar posição de um ativo."""
        if symbol not in self.positions:
            self.positions[symbol] = {'amount': 0.0, 'avg_price': 0.0, 'unrealized_pnl': 0.0}
        
        pos = self.positions[symbol]
        
        # Calcular novo preço médio
        if pos['amount'] > 0:
            total_cost = pos['amount'] * pos['avg_price'] + amount * price
            total_amount = pos['amount'] + amount
            pos['avg_price'] = total_cost / total_amount if total_amount > 0 else 0
        else:
            pos['avg_price'] = price
        
        pos['amount'] += amount
        
        # Remover posição se zerada
        if abs(pos['amount']) < 1e-8:
            del self.positions[symbol]
        
        self._recalculate_total_value()
    
    def _recalculate_total_value(self):
        """Recalcular valor total do portfólio."""
        # Valor em USD das moedas fiat
        usd_value = self.balances.get('USD', 0) + self.balances.get('USDT', 0)
        
        # TODO: Adicionar valor das posições crypto (precisa de preços atuais)
        self.total_value = usd_value
        
        if self.total_value > self.max_value:
            self.max_value = self.total_value
    
    def get_position_size_percentage(self, symbol: str, trade_amount_usd: float) -> float:
        """Calcular percentual da posição em relação ao portfólio."""
        if self.total_value <= 0:
            return 0.0
        return trade_amount_usd / self.total_value
    
    def get_current_drawdown(self) -> float:
        """Calcular drawdown atual."""
        if self.max_value <= 0:
            return 0.0
        return (self.max_value - self.total_value) / self.max_value
    
    def get_summary(self) -> Dict:
        """Obter resumo do portfólio."""
        return {
            'total_value': self.total_value,
            'positions': self.positions,
            'balances': self.balances,
            'daily_pnl': self.daily_pnl,
            'current_drawdown': self.get_current_drawdown(),
            'max_value': self.max_value
        }

class RiskManager:
    """Sistema avançado de gerenciamento de risco."""
    
    def __init__(self, limits: RiskLimits = None):
        self.limits = limits or RiskLimits()
        self.portfolio = PortfolioManager()
        self.logger = logging.getLogger('RiskManager')
        
        # Tracking de trades e eventos
        self.daily_trades = []
        self.daily_losses = []
        self.risk_events = []
        self.last_loss_time = None
        self.circuit_breaker_active = False
        
        # Performance tracking
        self.trade_history = []
        self.daily_stats = {
            'trades_count': 0,
            'total_profit': 0.0,
            'total_loss': 0.0,
            'largest_win': 0.0,
            'largest_loss': 0.0,
            'win_rate': 0.0
        }
    
    def validate_trade(self, opportunity, trade_amount_usd: float) -> Dict[str, Any]:
        """Validar se um trade pode ser executado baseado nas regras de risco."""
        validation_result = {
            'approved': True,
            'risk_score': 0.0,
            'warnings': [],
            'blocks': [],
            'adjusted_amount': trade_amount_usd
        }
        
        try:
            # 1. Circuit breaker check
            if self.circuit_breaker_active:
                validation_result['approved'] = False
                validation_result['blocks'].append("Circuit breaker ativo")
                return validation_result
            
            # 2. Verificar cooldown após perda
            if self._is_in_cooldown():
                validation_result['approved'] = False
                validation_result['blocks'].append("Em cooldown após perda recente")
                return validation_result
            
            # 3. Verificar limite de trades diários
            today_trades = self._get_today_trades_count()
            if today_trades >= self.limits.max_daily_trades:
                validation_result['approved'] = False
                validation_result['blocks'].append(f"Limite diário de trades atingido ({today_trades}/{self.limits.max_daily_trades})")
                return validation_result
            
            # 4. Verificar perdas diárias
            daily_loss = self._get_today_loss()
            if daily_loss >= self.limits.max_daily_loss:
                validation_result['approved'] = False
                validation_result['blocks'].append(f"Limite de perda diária atingido (${daily_loss:.2f})")
                return validation_result
            
            # 5. Verificar threshold de lucro mínimo
            if opportunity.profit_percentage < self.limits.min_profit_threshold:
                validation_result['approved'] = False
                validation_result['blocks'].append(f"Lucro abaixo do mínimo ({opportunity.profit_percentage:.3%} < {self.limits.min_profit_threshold:.3%})")
                return validation_result
            
            # 6. Verificar tamanho máximo do trade
            if trade_amount_usd > self.limits.max_trade_amount:
                validation_result['adjusted_amount'] = self.limits.max_trade_amount
                validation_result['warnings'].append(f"Valor reduzido para ${self.limits.max_trade_amount}")
                trade_amount_usd = self.limits.max_trade_amount
            
            # 7. Verificar tamanho da posição
            position_percentage = self.portfolio.get_position_size_percentage(opportunity.symbol, trade_amount_usd)
            if position_percentage > self.limits.max_position_size:
                max_allowed = self.portfolio.total_value * self.limits.max_position_size
                validation_result['adjusted_amount'] = max_allowed
                validation_result['warnings'].append(f"Posição reduzida para {self.limits.max_position_size:.1%} do portfólio")
            
            # 8. Verificar drawdown atual
            current_drawdown = self.portfolio.get_current_drawdown()
            if current_drawdown >= self.limits.max_drawdown:
                validation_result['approved'] = False
                validation_result['blocks'].append(f"Drawdown máximo atingido ({current_drawdown:.1%})")
                return validation_result
            
            # 9. Calcular risk score
            risk_score = self._calculate_risk_score(opportunity, trade_amount_usd, today_trades, daily_loss)
            validation_result['risk_score'] = risk_score
            
            # 10. Verificar risk score crítico
            if risk_score > 0.8:
                validation_result['approved'] = False
                validation_result['blocks'].append(f"Risk score muito alto ({risk_score:.2f})")
            elif risk_score > 0.6:
                validation_result['warnings'].append(f"Risk score elevado ({risk_score:.2f})")
            
            self.logger.info(f"Trade validation for {opportunity.symbol}: {'APPROVED' if validation_result['approved'] else 'BLOCKED'}")
            
            return validation_result
            
        except Exception as e:
            self.logger.error(f"Error in trade validation: {e}")
            validation_result['approved'] = False
            validation_result['blocks'].append("Erro na validação de risco")
            return validation_result
    
    def _calculate_risk_score(self, opportunity, trade_amount_usd: float, today_trades: int, daily_loss: float) -> float:
        """Calcular score de risco de 0.0 (baixo) a 1.0 (alto)."""
        risk_factors = []
        
        # Fator 1: Profit margin (menor margem = maior risco)
        profit_factor = max(0, 1 - (opportunity.profit_percentage / 0.02))  # Risk decreases as profit increases
        risk_factors.append(profit_factor * 0.3)
        
        # Fator 2: Trade size relative to limits
        size_factor = trade_amount_usd / self.limits.max_trade_amount
        risk_factors.append(size_factor * 0.2)
        
        # Fator 3: Daily trade count
        trade_count_factor = today_trades / self.limits.max_daily_trades
        risk_factors.append(trade_count_factor * 0.2)
        
        # Fator 4: Daily losses
        loss_factor = daily_loss / self.limits.max_daily_loss
        risk_factors.append(loss_factor * 0.2)
        
        # Fator 5: Portfolio drawdown
        drawdown_factor = self.portfolio.get_current_drawdown() / self.limits.max_drawdown
        risk_factors.append(drawdown_factor * 0.1)
        
        return sum(risk_factors)
    
    def record_trade_result(self, execution_result) -> None:
        """Registrar resultado de um trade para análise de risco."""
        try:
            trade_record = {
                'timestamp': datetime.now(),
                'symbol': execution_result.symbol,
                'profit': execution_result.actual_profit or 0.0,
                'expected_profit': execution_result.expected_profit,
                'execution_time': execution_result.execution_time,
                'status': execution_result.status
            }
            
            self.trade_history.append(trade_record)
            self.daily_trades.append(trade_record)
            
            # Atualizar estatísticas diárias
            profit = trade_record['profit']
            self.daily_stats['trades_count'] += 1
            
            if profit > 0:
                self.daily_stats['total_profit'] += profit
                if profit > self.daily_stats['largest_win']:
                    self.daily_stats['largest_win'] = profit
            else:
                self.daily_stats['total_loss'] += abs(profit)
                self.daily_losses.append(trade_record)
                self.last_loss_time = datetime.now()
                
                if abs(profit) > self.daily_stats['largest_loss']:
                    self.daily_stats['largest_loss'] = abs(profit)
            
            # Calcular win rate
            profitable_trades = sum(1 for t in self.daily_trades if t['profit'] > 0)
            self.daily_stats['win_rate'] = profitable_trades / len(self.daily_trades) if self.daily_trades else 0
            
            # Verificar se precisa ativar circuit breaker
            self._check_circuit_breaker()
            
            # Atualizar portfólio
            self.portfolio.daily_pnl += profit
            
            # Registrar evento de risco se necessário
            if profit < -50:  # Perda > $50
                self._record_risk_event(
                    'large_loss',
                    'medium',
                    f"Perda significativa de ${abs(profit):.2f} em {execution_result.symbol}",
                    'monitoring',
                    {'profit': profit, 'symbol': execution_result.symbol}
                )
            
            self.logger.info(f"Trade recorded: {execution_result.symbol} - ${profit:.2f}")
            
        except Exception as e:
            self.logger.error(f"Error recording trade result: {e}")
    
    def _is_in_cooldown(self) -> bool:
        """Verificar se está em período de cooldown após perda."""
        if not self.last_loss_time:
            return False
        
        cooldown_end = self.last_loss_time + timedelta(seconds=self.limits.cooldown_after_loss)
        return datetime.now() < cooldown_end
    
    def _get_today_trades_count(self) -> int:
        """Contar trades de hoje."""
        today = datetime.now().date()
        return sum(1 for trade in self.daily_trades if trade['timestamp'].date() == today)
    
    def _get_today_loss(self) -> float:
        """Calcular perda total de hoje."""
        today = datetime.now().date()
        return sum(abs(trade['profit']) for trade in self.daily_losses 
                  if trade['timestamp'].date() == today and trade['profit'] < 0)
    
    def _check_circuit_breaker(self):
        """Verificar se deve ativar circuit breaker."""
        # Ativar se muitas perdas consecutivas
        recent_trades = self.daily_trades[-5:] if len(self.daily_trades) >= 5 else self.daily_trades
        if len(recent_trades) >= 3:
            losing_trades = sum(1 for t in recent_trades if t['profit'] < 0)
            if losing_trades >= 3:
                self.circuit_breaker_active = True
                self._record_risk_event(
                    'circuit_breaker',
                    'critical',
                    "Circuit breaker ativado por perdas consecutivas",
                    'trading_stopped',
                    {'consecutive_losses': losing_trades}
                )
    
    def _record_risk_event(self, risk_type: str, severity: str, description: str, action: str, metadata: Dict):
        """Registrar evento de risco."""
        event = RiskEvent(
            timestamp=datetime.now(),
            risk_type=risk_type,
            severity=severity,
            description=description,
            action_taken=action,
            metadata=metadata
        )
        
        self.risk_events.append(event)
        self.logger.warning(f"Risk event: {description}")
    
    def reset_circuit_breaker(self):
        """Resetar circuit breaker manualmente."""
        self.circuit_breaker_active = False
        self.logger.info("Circuit breaker resetado manualmente")
    
    def get_daily_statistics(self) -> Dict:
        """Obter estatísticas do dia."""
        return {
            **self.daily_stats,
            'net_pnl': self.daily_stats['total_profit'] - self.daily_stats['total_loss'],
            'circuit_breaker_active': self.circuit_breaker_active,
            'cooldown_active': self._is_in_cooldown(),
            'trades_today': self._get_today_trades_count(),
            'losses_today': self._get_today_loss(),
            'portfolio_summary': self.portfolio.get_summary()
        }
    
    def get_risk_report(self) -> Dict:
        """Gerar relatório completo de risco."""
        return {
            'limits': asdict(self.limits),
            'daily_stats': self.get_daily_statistics(),
            'recent_risk_events': [asdict(event) for event in self.risk_events[-10:]],
            'portfolio': self.portfolio.get_summary(),
            'system_status': {
                'circuit_breaker': self.circuit_breaker_active,
                'cooldown': self._is_in_cooldown(),
                'risk_level': self._get_overall_risk_level()
            }
        }
    
    def _get_overall_risk_level(self) -> str:
        """Determinar nível geral de risco."""
        if self.circuit_breaker_active:
            return 'CRITICAL'
        
        daily_loss_ratio = self._get_today_loss() / self.limits.max_daily_loss
        drawdown_ratio = self.portfolio.get_current_drawdown() / self.limits.max_drawdown
        
        if daily_loss_ratio > 0.8 or drawdown_ratio > 0.8:
            return 'HIGH'
        elif daily_loss_ratio > 0.5 or drawdown_ratio > 0.5:
            return 'MEDIUM'
        else:
            return 'LOW'
    
    def save_risk_log(self, filename: str = 'risk_log.json'):
        """Salvar log de risco em arquivo."""
        risk_report = self.get_risk_report()
        risk_report['timestamp'] = datetime.now().isoformat()
        
        with open(filename, 'w') as f:
            json.dump(risk_report, f, indent=2, default=str)

def demo_risk_manager():
    """Demonstração do sistema de risk management."""
    print("🛡️  DEMO: Sistema de Risk Management")
    print("=" * 50)
    
    # Criar risk manager com limites conservadores
    limits = RiskLimits(
        max_trade_amount=100.0,
        max_daily_trades=10,
        max_daily_loss=200.0,
        min_profit_threshold=0.005,
        max_position_size=0.1,
        stop_loss_percentage=0.02
    )
    
    risk_manager = RiskManager(limits)
    
    # Simular portfólio inicial
    risk_manager.portfolio.update_balance('USD', 5000.0)
    
    print("📊 Configuração inicial:")
    print(f"   Máximo por trade: ${limits.max_trade_amount}")
    print(f"   Máximo trades/dia: {limits.max_daily_trades}")
    print(f"   Máxima perda/dia: ${limits.max_daily_loss}")
    print(f"   Threshold lucro: {limits.min_profit_threshold:.2%}")
    
    # Simular oportunidade
    class MockOpportunity:
        def __init__(self, symbol, profit_pct):
            self.symbol = symbol
            self.profit_percentage = profit_pct
            self.buy_exchange = 'binance'
            self.sell_exchange = 'coinbase'
    
    # Teste 1: Trade aprovado
    opportunity1 = MockOpportunity('BTC/USD', 0.008)  # 0.8% profit
    validation = risk_manager.validate_trade(opportunity1, 50.0)
    
    print(f"\n🧪 Teste 1 - Trade normal:")
    print(f"   Oportunidade: {opportunity1.symbol} ({opportunity1.profit_percentage:.2%})")
    print(f"   Aprovado: {validation['approved']}")
    print(f"   Risk Score: {validation['risk_score']:.2f}")
    if validation['warnings']:
        print(f"   Avisos: {validation['warnings']}")
    
    # Teste 2: Trade com lucro baixo
    opportunity2 = MockOpportunity('ETH/USD', 0.003)  # 0.3% profit (below threshold)
    validation2 = risk_manager.validate_trade(opportunity2, 75.0)
    
    print(f"\n🧪 Teste 2 - Lucro baixo:")
    print(f"   Oportunidade: {opportunity2.symbol} ({opportunity2.profit_percentage:.2%})")
    print(f"   Aprovado: {validation2['approved']}")
    if validation2['blocks']:
        print(f"   Bloqueado: {validation2['blocks']}")
    
    # Teste 3: Trade muito grande
    opportunity3 = MockOpportunity('BNB/USD', 0.01)  # 1% profit
    validation3 = risk_manager.validate_trade(opportunity3, 200.0)  # Above max
    
    print(f"\n🧪 Teste 3 - Valor alto:")
    print(f"   Valor solicitado: $200")
    print(f"   Valor ajustado: ${validation3['adjusted_amount']}")
    print(f"   Aprovado: {validation3['approved']}")
    
    # Simular alguns trades executados
    print(f"\n📈 Simulando execução de trades...")
    
    class MockExecution:
        def __init__(self, symbol, profit, status='completed'):
            self.symbol = symbol
            self.actual_profit = profit
            self.expected_profit = profit
            self.execution_time = 2.5
            self.status = status
    
    # Trade lucrativo
    risk_manager.record_trade_result(MockExecution('BTC/USD', 15.50))
    risk_manager.record_trade_result(MockExecution('ETH/USD', -8.20))
    risk_manager.record_trade_result(MockExecution('BNB/USD', 22.10))
    
    # Estatísticas
    stats = risk_manager.get_daily_statistics()
    print(f"\n📊 Estatísticas do dia:")
    print(f"   Trades executados: {stats['trades_count']}")
    print(f"   Taxa de sucesso: {stats['win_rate']:.1%}")
    print(f"   Lucro total: ${stats['total_profit']:.2f}")
    print(f"   Perda total: ${stats['total_loss']:.2f}")
    print(f"   P&L líquido: ${stats['net_pnl']:.2f}")
    print(f"   Nível de risco: {risk_manager._get_overall_risk_level()}")
    
    # Relatório de risco
    print(f"\n🛡️  Status do sistema:")
    print(f"   Circuit breaker: {'ATIVO' if stats['circuit_breaker_active'] else 'INATIVO'}")
    print(f"   Cooldown: {'ATIVO' if stats['cooldown_active'] else 'INATIVO'}")
    print(f"   Drawdown atual: {stats['portfolio_summary']['current_drawdown']:.2%}")

if __name__ == "__main__":
    demo_risk_manager()