"""
Trading Engine - Sistema de execução automática de trades para arbitragem.
"""

import asyncio
import logging
import time
import hmac
import hashlib
import base64
import json
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import aiohttp
from decimal import Decimal, ROUND_DOWN

@dataclass
class Trade:
    """Representa uma operação de trade."""
    id: str
    symbol: str
    side: str  # 'buy' or 'sell'
    amount: float
    price: float
    exchange: str
    timestamp: datetime
    status: str  # 'pending', 'filled', 'cancelled', 'failed'
    order_id: Optional[str] = None
    actual_price: Optional[float] = None
    actual_amount: Optional[float] = None
    fees: Optional[float] = None
    error: Optional[str] = None

@dataclass
class ArbitrageExecution:
    """Representa uma execução completa de arbitragem."""
    opportunity_id: str
    symbol: str
    buy_trade: Trade
    sell_trade: Trade
    expected_profit: float
    actual_profit: Optional[float] = None
    execution_time: Optional[float] = None
    status: str = 'pending'  # 'pending', 'executing', 'completed', 'failed'
    
    def to_dict(self):
        return {
            **asdict(self),
            'buy_trade': asdict(self.buy_trade),
            'sell_trade': asdict(self.sell_trade)
        }

class ExchangeAPI:
    """Base class for exchange API implementations."""
    
    def __init__(self, api_key: str, secret_key: str, sandbox: bool = True):
        self.api_key = api_key
        self.secret_key = secret_key
        self.sandbox = sandbox
        self.session = None
        self.logger = logging.getLogger(f"{self.__class__.__name__}")
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def get_balance(self, currency: str) -> float:
        """Get balance for a specific currency."""
        raise NotImplementedError
    
    async def place_order(self, symbol: str, side: str, amount: float, price: float) -> str:
        """Place a limit order."""
        raise NotImplementedError
    
    async def get_order_status(self, order_id: str, symbol: str) -> Dict:
        """Get order status."""
        raise NotImplementedError
    
    async def cancel_order(self, order_id: str, symbol: str) -> bool:
        """Cancel an order."""
        raise NotImplementedError

class BinanceAPI(ExchangeAPI):
    """Binance API implementation for trading."""
    
    def __init__(self, api_key: str, secret_key: str, sandbox: bool = True):
        super().__init__(api_key, secret_key, sandbox)
        self.base_url = "https://testnet.binance.vision" if sandbox else "https://api.binance.com"
    
    def _generate_signature(self, params: str) -> str:
        """Generate signature for Binance API."""
        return hmac.new(
            self.secret_key.encode('utf-8'),
            params.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
    
    async def _request(self, method: str, endpoint: str, params: Dict = None, signed: bool = False) -> Dict:
        """Make authenticated request to Binance API."""
        url = f"{self.base_url}{endpoint}"
        headers = {"X-MBX-APIKEY": self.api_key}
        
        if params is None:
            params = {}
        
        if signed:
            params['timestamp'] = int(time.time() * 1000)
            query_string = '&'.join([f"{k}={v}" for k, v in params.items()])
            signature = self._generate_signature(query_string)
            params['signature'] = signature
        
        try:
            async with self.session.request(method, url, params=params, headers=headers) as response:
                data = await response.json()
                
                if response.status != 200:
                    raise Exception(f"Binance API error: {data}")
                
                return data
        except Exception as e:
            self.logger.error(f"Binance API request failed: {e}")
            raise
    
    async def get_balance(self, currency: str) -> float:
        """Get balance for a specific currency."""
        try:
            account_info = await self._request("GET", "/api/v3/account", signed=True)
            
            for balance in account_info.get('balances', []):
                if balance['asset'] == currency.upper():
                    return float(balance['free'])
            
            return 0.0
        except Exception as e:
            self.logger.error(f"Error getting balance for {currency}: {e}")
            return 0.0
    
    async def place_order(self, symbol: str, side: str, amount: float, price: float) -> str:
        """Place a limit order on Binance."""
        try:
            # Convert symbol format (BTC/USD -> BTCUSDT)
            binance_symbol = symbol.replace('/', '').replace('USD', 'USDT')
            
            params = {
                'symbol': binance_symbol,
                'side': side.upper(),
                'type': 'LIMIT',
                'timeInForce': 'GTC',
                'quantity': f"{amount:.8f}",
                'price': f"{price:.8f}"
            }
            
            result = await self._request("POST", "/api/v3/order", params, signed=True)
            return result['orderId']
            
        except Exception as e:
            self.logger.error(f"Error placing order: {e}")
            raise
    
    async def get_order_status(self, order_id: str, symbol: str) -> Dict:
        """Get order status from Binance."""
        try:
            binance_symbol = symbol.replace('/', '').replace('USD', 'USDT')
            
            params = {
                'symbol': binance_symbol,
                'orderId': order_id
            }
            
            return await self._request("GET", "/api/v3/order", params, signed=True)
            
        except Exception as e:
            self.logger.error(f"Error getting order status: {e}")
            return {}
    
    async def cancel_order(self, order_id: str, symbol: str) -> bool:
        """Cancel an order on Binance."""
        try:
            binance_symbol = symbol.replace('/', '').replace('USD', 'USDT')
            
            params = {
                'symbol': binance_symbol,
                'orderId': order_id
            }
            
            await self._request("DELETE", "/api/v3/order", params, signed=True)
            return True
            
        except Exception as e:
            self.logger.error(f"Error cancelling order: {e}")
            return False

class CoinbaseAPI(ExchangeAPI):
    """Coinbase Pro API implementation for trading."""
    
    def __init__(self, api_key: str, secret_key: str, passphrase: str, sandbox: bool = True):
        super().__init__(api_key, secret_key, sandbox)
        self.passphrase = passphrase
        self.base_url = "https://api-public.sandbox.pro.coinbase.com" if sandbox else "https://api.pro.coinbase.com"
    
    def _generate_signature(self, timestamp: str, method: str, path: str, body: str = '') -> str:
        """Generate signature for Coinbase Pro API."""
        message = timestamp + method + path + body
        signature = hmac.new(
            base64.b64decode(self.secret_key),
            message.encode('utf-8'),
            hashlib.sha256
        ).digest()
        return base64.b64encode(signature).decode('utf-8')
    
    async def _request(self, method: str, endpoint: str, data: Dict = None) -> Dict:
        """Make authenticated request to Coinbase Pro API."""
        url = f"{self.base_url}{endpoint}"
        timestamp = str(time.time())
        body = json.dumps(data) if data else ''
        
        signature = self._generate_signature(timestamp, method, endpoint, body)
        
        headers = {
            'CB-ACCESS-KEY': self.api_key,
            'CB-ACCESS-SIGN': signature,
            'CB-ACCESS-TIMESTAMP': timestamp,
            'CB-ACCESS-PASSPHRASE': self.passphrase,
            'Content-Type': 'application/json'
        }
        
        try:
            kwargs = {'headers': headers}
            if data:
                kwargs['json'] = data
            
            async with self.session.request(method, url, **kwargs) as response:
                response_data = await response.json()
                
                if response.status != 200:
                    raise Exception(f"Coinbase API error: {response_data}")
                
                return response_data
        except Exception as e:
            self.logger.error(f"Coinbase API request failed: {e}")
            raise
    
    async def get_balance(self, currency: str) -> float:
        """Get balance for a specific currency."""
        try:
            accounts = await self._request("GET", "/accounts")
            
            for account in accounts:
                if account['currency'] == currency.upper():
                    return float(account['available'])
            
            return 0.0
        except Exception as e:
            self.logger.error(f"Error getting balance for {currency}: {e}")
            return 0.0
    
    async def place_order(self, symbol: str, side: str, amount: float, price: float) -> str:
        """Place a limit order on Coinbase Pro."""
        try:
            # Convert symbol format (BTC/USD -> BTC-USD)
            product_id = symbol.replace('/', '-')
            
            order_data = {
                'type': 'limit',
                'side': side.lower(),
                'product_id': product_id,
                'size': f"{amount:.8f}",
                'price': f"{price:.2f}"
            }
            
            result = await self._request("POST", "/orders", order_data)
            return result['id']
            
        except Exception as e:
            self.logger.error(f"Error placing order: {e}")
            raise
    
    async def get_order_status(self, order_id: str, symbol: str) -> Dict:
        """Get order status from Coinbase Pro."""
        try:
            return await self._request("GET", f"/orders/{order_id}")
        except Exception as e:
            self.logger.error(f"Error getting order status: {e}")
            return {}
    
    async def cancel_order(self, order_id: str, symbol: str) -> bool:
        """Cancel an order on Coinbase Pro."""
        try:
            await self._request("DELETE", f"/orders/{order_id}")
            return True
        except Exception as e:
            self.logger.error(f"Error cancelling order: {e}")
            return False

class TradingEngine:
    """Main trading engine for executing arbitrage opportunities."""
    
    def __init__(self, config: Dict):
        self.config = config
        self.logger = logging.getLogger('TradingEngine')
        
        # Risk management parameters
        self.max_trade_amount = config.get('max_trade_amount', 1000)  # USD
        self.min_profit_threshold = config.get('min_profit_threshold', 0.005)  # 0.5%
        self.max_slippage = config.get('max_slippage', 0.002)  # 0.2%
        self.execution_timeout = config.get('execution_timeout', 30)  # seconds
        
        # Exchange APIs
        self.exchanges = {}
        self.active_executions = {}
        self.execution_history = []
        
        # Statistics
        self.stats = {
            'total_executions': 0,
            'successful_executions': 0,
            'failed_executions': 0,
            'total_profit': 0.0,
            'total_fees': 0.0
        }
    
    def add_exchange(self, name: str, api: ExchangeAPI):
        """Add an exchange API to the trading engine."""
        self.exchanges[name] = api
        self.logger.info(f"Added exchange: {name}")
    
    async def validate_opportunity(self, opportunity) -> bool:
        """Validate if opportunity is still viable for execution."""
        try:
            # Check profit threshold
            if opportunity.profit_percentage < self.min_profit_threshold:
                self.logger.info(f"Opportunity {opportunity.symbol} below profit threshold")
                return False
            
            # Check if we have necessary balances
            buy_exchange = self.exchanges.get(opportunity.buy_exchange)
            sell_exchange = self.exchanges.get(opportunity.sell_exchange)
            
            if not buy_exchange or not sell_exchange:
                self.logger.warning(f"Missing exchange APIs for {opportunity.symbol}")
                return False
            
            # Calculate trade amount based on available balance
            base_currency = opportunity.symbol.split('/')[0]
            quote_currency = opportunity.symbol.split('/')[1]
            
            # Check USD balance for buying
            usd_balance = await buy_exchange.get_balance(quote_currency)
            trade_amount_usd = min(self.max_trade_amount, usd_balance * 0.95)  # Use 95% of balance
            
            if trade_amount_usd < 10:  # Minimum $10 trade
                self.logger.info(f"Insufficient balance for {opportunity.symbol}: ${usd_balance}")
                return False
            
            # Check if we have the asset to sell on the other exchange
            crypto_balance = await sell_exchange.get_balance(base_currency)
            required_crypto = trade_amount_usd / opportunity.buy_price
            
            if crypto_balance < required_crypto:
                self.logger.info(f"Insufficient {base_currency} balance on {opportunity.sell_exchange}")
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error validating opportunity: {e}")
            return False
    
    async def execute_arbitrage(self, opportunity) -> Optional[ArbitrageExecution]:
        """Execute arbitrage opportunity automatically."""
        execution_id = f"{opportunity.symbol}_{int(time.time())}"
        
        try:
            self.logger.info(f"🚀 Executing arbitrage: {opportunity.symbol} ({opportunity.profit_percentage:.3%})")
            
            # Validate opportunity
            if not await self.validate_opportunity(opportunity):
                return None
            
            # Calculate trade amounts
            base_currency = opportunity.symbol.split('/')[0]
            quote_currency = opportunity.symbol.split('/')[1]
            
            trade_amount_usd = min(self.max_trade_amount, 100)  # Start with $100 for safety
            crypto_amount = trade_amount_usd / opportunity.buy_price
            
            # Create trades
            buy_trade = Trade(
                id=f"{execution_id}_buy",
                symbol=opportunity.symbol,
                side='buy',
                amount=crypto_amount,
                price=opportunity.buy_price,
                exchange=opportunity.buy_exchange,
                timestamp=datetime.now(),
                status='pending'
            )
            
            sell_trade = Trade(
                id=f"{execution_id}_sell",
                symbol=opportunity.symbol,
                side='sell',
                amount=crypto_amount,
                price=opportunity.sell_price,
                exchange=opportunity.sell_exchange,
                timestamp=datetime.now(),
                status='pending'
            )
            
            execution = ArbitrageExecution(
                opportunity_id=execution_id,
                symbol=opportunity.symbol,
                buy_trade=buy_trade,
                sell_trade=sell_trade,
                expected_profit=opportunity.profit_amount * crypto_amount,
                status='executing'
            )
            
            self.active_executions[execution_id] = execution
            execution_start = time.time()
            
            # Execute trades simultaneously
            buy_task = self._execute_trade(buy_trade, opportunity.buy_exchange)
            sell_task = self._execute_trade(sell_trade, opportunity.sell_exchange)
            
            # Wait for both trades with timeout
            try:
                await asyncio.wait_for(
                    asyncio.gather(buy_task, sell_task),
                    timeout=self.execution_timeout
                )
            except asyncio.TimeoutError:
                self.logger.error(f"Execution timeout for {execution_id}")
                await self._cancel_execution(execution)
                return execution
            
            execution.execution_time = time.time() - execution_start
            
            # Calculate actual profit
            if buy_trade.status == 'filled' and sell_trade.status == 'filled':
                actual_profit = (sell_trade.actual_price * sell_trade.actual_amount) - \
                               (buy_trade.actual_price * buy_trade.actual_amount) - \
                               (buy_trade.fees or 0) - (sell_trade.fees or 0)
                
                execution.actual_profit = actual_profit
                execution.status = 'completed'
                
                self.stats['successful_executions'] += 1
                self.stats['total_profit'] += actual_profit
                self.stats['total_fees'] += (buy_trade.fees or 0) + (sell_trade.fees or 0)
                
                self.logger.info(f"✅ Arbitrage completed: ${actual_profit:.2f} profit in {execution.execution_time:.2f}s")
            else:
                execution.status = 'failed'
                self.stats['failed_executions'] += 1
                self.logger.error(f"❌ Arbitrage failed: {execution_id}")
            
            self.stats['total_executions'] += 1
            self.execution_history.append(execution)
            del self.active_executions[execution_id]
            
            return execution
            
        except Exception as e:
            self.logger.error(f"Error executing arbitrage {execution_id}: {e}")
            if execution_id in self.active_executions:
                self.active_executions[execution_id].status = 'failed'
                del self.active_executions[execution_id]
            return None
    
    async def _execute_trade(self, trade: Trade, exchange_name: str):
        """Execute individual trade on exchange."""
        try:
            exchange_api = self.exchanges[exchange_name]
            
            # Place order
            order_id = await exchange_api.place_order(
                trade.symbol, 
                trade.side, 
                trade.amount, 
                trade.price
            )
            
            trade.order_id = order_id
            trade.status = 'placed'
            
            # Monitor order status
            max_wait = 20  # 20 seconds max wait
            start_time = time.time()
            
            while (time.time() - start_time) < max_wait:
                order_status = await exchange_api.get_order_status(order_id, trade.symbol)
                
                if order_status.get('status') == 'FILLED' or order_status.get('status') == 'filled':
                    trade.status = 'filled'
                    trade.actual_price = float(order_status.get('price', trade.price))
                    trade.actual_amount = float(order_status.get('executedQty', trade.amount))
                    
                    # Calculate fees (estimated)
                    trade.fees = trade.actual_price * trade.actual_amount * 0.001  # 0.1% fee estimate
                    break
                
                await asyncio.sleep(1)
            
            if trade.status != 'filled':
                # Cancel unfilled order
                await exchange_api.cancel_order(order_id, trade.symbol)
                trade.status = 'cancelled'
                
        except Exception as e:
            trade.status = 'failed'
            trade.error = str(e)
            self.logger.error(f"Trade execution failed: {e}")
    
    async def _cancel_execution(self, execution: ArbitrageExecution):
        """Cancel an ongoing execution."""
        try:
            # Cancel both orders
            if execution.buy_trade.order_id:
                buy_exchange = self.exchanges[execution.buy_trade.exchange]
                await buy_exchange.cancel_order(execution.buy_trade.order_id, execution.buy_trade.symbol)
            
            if execution.sell_trade.order_id:
                sell_exchange = self.exchanges[execution.sell_trade.exchange]
                await sell_exchange.cancel_order(execution.sell_trade.order_id, execution.sell_trade.symbol)
            
            execution.status = 'cancelled'
            
        except Exception as e:
            self.logger.error(f"Error cancelling execution: {e}")
    
    def get_statistics(self) -> Dict:
        """Get trading statistics."""
        success_rate = (self.stats['successful_executions'] / max(1, self.stats['total_executions'])) * 100
        
        return {
            **self.stats,
            'success_rate': success_rate,
            'avg_profit_per_trade': self.stats['total_profit'] / max(1, self.stats['successful_executions']),
            'active_executions': len(self.active_executions),
            'net_profit': self.stats['total_profit'] - self.stats['total_fees']
        }
    
    def save_execution_log(self, filename: str = 'trading_log.json'):
        """Save execution history to file."""
        log_data = {
            'statistics': self.get_statistics(),
            'executions': [execution.to_dict() for execution in self.execution_history],
            'timestamp': datetime.now().isoformat()
        }
        
        with open(filename, 'w') as f:
            json.dump(log_data, f, indent=2, default=str)

# Demo/Test implementation
class MockExchangeAPI(ExchangeAPI):
    """Mock exchange API for testing."""
    
    def __init__(self, name: str):
        self.name = name
        self.balances = {'BTC': 1.0, 'ETH': 10.0, 'USD': 10000.0, 'USDT': 10000.0}
        self.orders = {}
        self.order_counter = 0
    
    async def get_balance(self, currency: str) -> float:
        return self.balances.get(currency.upper(), 0.0)
    
    async def place_order(self, symbol: str, side: str, amount: float, price: float) -> str:
        self.order_counter += 1
        order_id = f"{self.name}_{self.order_counter}"
        
        self.orders[order_id] = {
            'status': 'FILLED',  # Simulate immediate fill for demo
            'price': price,
            'executedQty': amount,
            'symbol': symbol,
            'side': side
        }
        
        # Update mock balances
        base_currency = symbol.split('/')[0]
        quote_currency = symbol.split('/')[1]
        
        if side.lower() == 'buy':
            self.balances[quote_currency] -= amount * price
            self.balances[base_currency] += amount
        else:
            self.balances[base_currency] -= amount
            self.balances[quote_currency] += amount * price
        
        return order_id
    
    async def get_order_status(self, order_id: str, symbol: str) -> Dict:
        return self.orders.get(order_id, {})
    
    async def cancel_order(self, order_id: str, symbol: str) -> bool:
        if order_id in self.orders:
            self.orders[order_id]['status'] = 'CANCELLED'
            return True
        return False

async def demo_trading_engine():
    """Demonstrate trading engine functionality."""
    print("🚀 DEMO: Trading Engine com Execução Automática")
    print("=" * 60)
    
    # Configure trading engine
    config = {
        'max_trade_amount': 100,  # $100 max per trade for demo
        'min_profit_threshold': 0.005,  # 0.5%
        'max_slippage': 0.002,
        'execution_timeout': 30
    }
    
    engine = TradingEngine(config)
    
    # Add mock exchanges
    engine.add_exchange('binance', MockExchangeAPI('binance'))
    engine.add_exchange('coinbase', MockExchangeAPI('coinbase'))
    
    # Create a mock arbitrage opportunity
    class MockOpportunity:
        def __init__(self):
            self.symbol = 'BTC/USD'
            self.buy_exchange = 'binance'
            self.sell_exchange = 'coinbase'
            self.buy_price = 50000.0
            self.sell_price = 50250.0
            self.profit_percentage = 0.005  # 0.5%
            self.profit_amount = 250.0
    
    opportunity = MockOpportunity()
    
    print(f"💰 Oportunidade detectada:")
    print(f"   {opportunity.symbol}: {opportunity.profit_percentage:.3%} lucro")
    print(f"   Comprar em {opportunity.buy_exchange}: ${opportunity.buy_price:,.2f}")
    print(f"   Vender em {opportunity.sell_exchange}: ${opportunity.sell_price:,.2f}")
    
    # Execute arbitrage
    print(f"\n🚀 Executando arbitragem...")
    execution = await engine.execute_arbitrage(opportunity)
    
    if execution:
        print(f"\n✅ Resultado da Execução:")
        print(f"   Status: {execution.status}")
        print(f"   Lucro esperado: ${execution.expected_profit:.2f}")
        print(f"   Lucro real: ${execution.actual_profit:.2f}")
        print(f"   Tempo de execução: {execution.execution_time:.2f}s")
        
        print(f"\n📊 Trade de Compra:")
        buy = execution.buy_trade
        print(f"   {buy.side.upper()} {buy.amount:.6f} {buy.symbol} em {buy.exchange}")
        print(f"   Preço: ${buy.actual_price:.2f} | Status: {buy.status}")
        
        print(f"\n📊 Trade de Venda:")
        sell = execution.sell_trade
        print(f"   {sell.side.upper()} {sell.amount:.6f} {sell.symbol} em {sell.exchange}")
        print(f"   Preço: ${sell.actual_price:.2f} | Status: {sell.status}")
    
    # Show statistics
    stats = engine.get_statistics()
    print(f"\n📈 Estatísticas:")
    print(f"   Execuções totais: {stats['total_executions']}")
    print(f"   Taxa de sucesso: {stats['success_rate']:.1f}%")
    print(f"   Lucro total: ${stats['total_profit']:.2f}")
    print(f"   Lucro líquido: ${stats['net_profit']:.2f}")

if __name__ == "__main__":
    asyncio.run(demo_trading_engine())