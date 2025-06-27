#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票计算器
用于计算股票交易的成本、盈亏、收益率等
"""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional, Dict, Tuple
import json
import os


@dataclass
class Trade:
    """交易记录"""
    date: datetime
    action: str  # 'buy' 或 'sell'
    price: float
    shares: int
    commission: float = 0.0  # 手续费
    description: str = ""

    def __post_init__(self):
        if isinstance(self.date, str):
            self.date = datetime.fromisoformat(self.date)


class StockCalculator:
    """股票计算器"""
    
    def __init__(self, stock_code: str = ""):
        self.stock_code = stock_code
        self.trades: List[Trade] = []
        self.current_shares = 0
        self.total_cost = 0.0
        self.total_commission = 0.0
    
    def add_trade(self, trade: Trade):
        """添加交易记录"""
        self.trades.append(trade)
        self.trades.sort(key=lambda x: x.date)
        self._recalculate_position()
    
    def buy(self, date: datetime, price: float, shares: int, 
            commission: float = 0.0, description: str = ""):
        """买入股票"""
        trade = Trade(date, 'buy', price, shares, commission, description)
        self.add_trade(trade)
    
    def sell(self, date: datetime, price: float, shares: int, 
             commission: float = 0.0, description: str = ""):
        """卖出股票"""
        trade = Trade(date, 'sell', price, shares, commission, description)
        self.add_trade(trade)
    
    def _recalculate_position(self):
        """重新计算持仓"""
        self.current_shares = 0
        self.total_cost = 0.0
        self.total_commission = 0.0
        
        for trade in self.trades:
            if trade.action == 'buy':
                # 买入：增加持仓和成本
                self.current_shares += trade.shares
                self.total_cost += trade.price * trade.shares
                self.total_commission += trade.commission
            elif trade.action == 'sell':
                # 卖出：减少持仓，成本按比例减少
                if self.current_shares > 0:
                    sell_ratio = trade.shares / self.current_shares
                    self.total_cost *= (1 - sell_ratio)
                    self.current_shares -= trade.shares
                    self.total_commission += trade.commission
    
    def get_average_cost(self) -> float:
        """获取平均成本"""
        if self.current_shares <= 0:
            return 0.0
        return self.total_cost / self.current_shares
    
    def get_total_investment(self) -> float:
        """获取总投资金额（包含手续费）"""
        return self.total_cost + self.total_commission
    
    def calculate_profit_loss(self, current_price: float) -> Dict[str, float]:
        """计算盈亏情况"""
        if self.current_shares <= 0:
            return {
                'profit_loss': 0.0,
                'profit_loss_rate': 0.0,
                'market_value': 0.0,
                'total_investment': 0.0
            }
        
        market_value = current_price * self.current_shares
        total_investment = self.get_total_investment()
        profit_loss = market_value - total_investment
        profit_loss_rate = (profit_loss / total_investment) * 100 if total_investment > 0 else 0
        
        return {
            'profit_loss': profit_loss,
            'profit_loss_rate': profit_loss_rate,
            'market_value': market_value,
            'total_investment': total_investment
        }
    
    def get_trade_history(self) -> List[Dict]:
        """获取交易历史"""
        history = []
        for trade in self.trades:
            history.append({
                'date': trade.date.strftime('%Y-%m-%d %H:%M:%S'),
                'action': trade.action,
                'price': trade.price,
                'shares': trade.shares,
                'amount': trade.price * trade.shares,
                'commission': trade.commission,
                'description': trade.description
            })
        return history
    
    def get_position_summary(self) -> Dict:
        """获取持仓摘要"""
        return {
            'stock_code': self.stock_code,
            'current_shares': self.current_shares,
            'average_cost': self.get_average_cost(),
            'total_cost': self.total_cost,
            'total_commission': self.total_commission,
            'total_investment': self.get_total_investment()
        }
    
    def save_to_file(self, filename: str):
        """保存到文件"""
        data = {
            'stock_code': self.stock_code,
            'trades': [
                {
                    'date': trade.date.isoformat(),
                    'action': trade.action,
                    'price': trade.price,
                    'shares': trade.shares,
                    'commission': trade.commission,
                    'description': trade.description
                }
                for trade in self.trades
            ]
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def load_from_file(self, filename: str):
        """从文件加载"""
        if not os.path.exists(filename):
            return
        
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self.stock_code = data.get('stock_code', '')
        self.trades = []
        
        for trade_data in data.get('trades', []):
            trade = Trade(
                date=datetime.fromisoformat(trade_data['date']),
                action=trade_data['action'],
                price=trade_data['price'],
                shares=trade_data['shares'],
                commission=trade_data.get('commission', 0.0),
                description=trade_data.get('description', '')
            )
            self.trades.append(trade)
        
        self._recalculate_position()


class StockPortfolio:
    """股票投资组合"""
    
    def __init__(self):
        self.stocks: Dict[str, StockCalculator] = {}
    
    def add_stock(self, stock_code: str) -> StockCalculator:
        """添加股票"""
        if stock_code not in self.stocks:
            self.stocks[stock_code] = StockCalculator(stock_code)
        return self.stocks[stock_code]
    
    def get_stock(self, stock_code: str) -> Optional[StockCalculator]:
        """获取股票计算器"""
        return self.stocks.get(stock_code)
    
    def get_portfolio_summary(self, current_prices: Dict[str, float]) -> Dict:
        """获取投资组合摘要"""
        total_investment = 0.0
        total_market_value = 0.0
        total_profit_loss = 0.0
        stock_summaries = {}
        
        for stock_code, calculator in self.stocks.items():
            current_price = current_prices.get(stock_code, 0.0)
            profit_loss_info = calculator.calculate_profit_loss(current_price)
            
            stock_summaries[stock_code] = {
                'position': calculator.get_position_summary(),
                'profit_loss': profit_loss_info
            }
            
            total_investment += profit_loss_info['total_investment']
            total_market_value += profit_loss_info['market_value']
            total_profit_loss += profit_loss_info['profit_loss']
        
        total_profit_loss_rate = (total_profit_loss / total_investment) * 100 if total_investment > 0 else 0
        
        return {
            'total_investment': total_investment,
            'total_market_value': total_market_value,
            'total_profit_loss': total_profit_loss,
            'total_profit_loss_rate': total_profit_loss_rate,
            'stocks': stock_summaries
        }
    
    def save_portfolio(self, filename: str):
        """保存投资组合"""
        data = {}
        for stock_code, calculator in self.stocks.items():
            data[stock_code] = {
                'stock_code': calculator.stock_code,
                'trades': [
                    {
                        'date': trade.date.isoformat(),
                        'action': trade.action,
                        'price': trade.price,
                        'shares': trade.shares,
                        'commission': trade.commission,
                        'description': trade.description
                    }
                    for trade in calculator.trades
                ]
            }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def load_portfolio(self, filename: str):
        """加载投资组合"""
        if not os.path.exists(filename):
            return
        
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self.stocks = {}
        for stock_code, stock_data in data.items():
            calculator = StockCalculator(stock_code)
            for trade_data in stock_data.get('trades', []):
                trade = Trade(
                    date=datetime.fromisoformat(trade_data['date']),
                    action=trade_data['action'],
                    price=trade_data['price'],
                    shares=trade_data['shares'],
                    commission=trade_data.get('commission', 0.0),
                    description=trade_data.get('description', '')
                )
                calculator.trades.append(trade)
            
            calculator._recalculate_position()
            self.stocks[stock_code] = calculator


def main():
    """主函数 - 演示使用"""
    print("=== 股票计算器演示 ===\n")
    
    # 创建股票计算器
    calculator = StockCalculator("000001")
    
    # 示例：成本20买入500股，19.88全部卖出，之后又以20.14买入500
    print("交易记录：")
    print("1. 以20.00元买入500股")
    print("2. 以19.88元卖出500股")
    print("3. 以20.14元买入500股")
    print()
    
    # 添加交易记录
    calculator.buy(datetime(2024, 1, 1), 20.00, 500, 5.0, "首次买入")
    calculator.sell(datetime(2024, 1, 15), 19.88, 500, 5.0, "全部卖出")
    calculator.buy(datetime(2024, 1, 20), 20.14, 500, 5.0, "重新买入")
    
    # 显示持仓信息
    position = calculator.get_position_summary()
    print("当前持仓信息：")
    print(f"股票代码: {position['stock_code']}")
    print(f"持仓股数: {position['current_shares']}")
    print(f"平均成本: {position['average_cost']:.4f}元")
    print(f"总成本: {position['total_cost']:.2f}元")
    print(f"总手续费: {position['total_commission']:.2f}元")
    print(f"总投资: {position['total_investment']:.2f}元")
    print()
    
    # 计算不同价格下的盈亏
    test_prices = [19.50, 20.00, 20.14, 20.50, 21.00]
    print("不同价格下的盈亏情况：")
    print("价格\t\t盈亏\t\t盈亏率\t\t市值")
    print("-" * 50)
    
    for price in test_prices:
        result = calculator.calculate_profit_loss(price)
        print(f"{price:.2f}元\t\t{result['profit_loss']:+.2f}元\t\t{result['profit_loss_rate']:+.2f}%\t\t{result['market_value']:.2f}元")
    
    print("\n=== 交易历史 ===")
    history = calculator.get_trade_history()
    for i, trade in enumerate(history, 1):
        print(f"{i}. {trade['date']} - {trade['action']} {trade['shares']}股 @ {trade['price']:.2f}元")
        print(f"   金额: {trade['amount']:.2f}元, 手续费: {trade['commission']:.2f}元")
        if trade['description']:
            print(f"   备注: {trade['description']}")
        print()


if __name__ == "__main__":
    main() 