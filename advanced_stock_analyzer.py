#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
高级股票分析器
包含技术指标计算、风险评估、投资建议等功能
"""

import math
import statistics
from typing import List, Dict, Tuple, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
from stock_calculator import StockCalculator


@dataclass
class PricePoint:
    """价格点"""
    date: datetime
    price: float
    volume: int = 0


class TechnicalIndicators:
    """技术指标计算"""
    
    @staticmethod
    def calculate_sma(prices: List[float], period: int) -> List[float]:
        """计算简单移动平均线"""
        if len(prices) < period:
            return []
        
        sma = []
        for i in range(period - 1, len(prices)):
            sma.append(sum(prices[i-period+1:i+1]) / period)
        return sma
    
    @staticmethod
    def calculate_rsi(prices: List[float], period: int = 14) -> List[float]:
        """计算相对强弱指数"""
        if len(prices) < period + 1:
            return []
        
        gains = []
        losses = []
        
        for i in range(1, len(prices)):
            change = prices[i] - prices[i-1]
            gains.append(max(change, 0))
            losses.append(max(-change, 0))
        
        rsi = []
        for i in range(period, len(prices)):
            avg_gain = sum(gains[i-period:i]) / period
            avg_loss = sum(losses[i-period:i]) / period
            
            if avg_loss == 0:
                rsi.append(100)
            else:
                rs = avg_gain / avg_loss
                rsi.append(100 - (100 / (1 + rs)))
        
        return rsi


class RiskAnalyzer:
    """风险分析器"""
    
    @staticmethod
    def calculate_volatility(prices: List[float]) -> float:
        """计算波动率"""
        if len(prices) < 2:
            return 0.0
        
        returns = []
        for i in range(1, len(prices)):
            returns.append((prices[i] - prices[i-1]) / prices[i-1])
        
        return statistics.stdev(returns) * math.sqrt(252)  # 年化波动率
    
    @staticmethod
    def calculate_max_drawdown(prices: List[float]) -> float:
        """计算最大回撤"""
        if len(prices) < 2:
            return 0.0
        
        peak = prices[0]
        max_dd = 0.0
        
        for price in prices:
            if price > peak:
                peak = price
            else:
                dd = (peak - price) / peak
                if dd > max_dd:
                    max_dd = dd
        
        return max_dd


class InvestmentAdvisor:
    """投资建议器"""
    
    @staticmethod
    def analyze_trend(prices: List[float], short_period: int = 5, long_period: int = 20) -> str:
        """分析趋势"""
        if len(prices) < long_period:
            return "数据不足"
        
        short_sma = TechnicalIndicators.calculate_sma(prices, short_period)
        long_sma = TechnicalIndicators.calculate_sma(prices, long_period)
        
        if not short_sma or not long_sma:
            return "数据不足"
        
        current_short = short_sma[-1]
        current_long = long_sma[-1]
        prev_short = short_sma[-2] if len(short_sma) > 1 else current_short
        prev_long = long_sma[-2] if len(long_sma) > 1 else current_long
        
        if current_short > current_long and prev_short <= prev_long:
            return "强烈买入信号（金叉）"
        elif current_short < current_long and prev_short >= prev_long:
            return "强烈卖出信号（死叉）"
        elif current_short > current_long:
            return "多头趋势"
        else:
            return "空头趋势"
    
    @staticmethod
    def analyze_rsi_signal(prices: List[float]) -> str:
        """分析RSI信号"""
        rsi = TechnicalIndicators.calculate_rsi(prices)
        
        if not rsi:
            return "数据不足"
        
        current_rsi = rsi[-1]
        
        if current_rsi > 70:
            return "超买信号，考虑卖出"
        elif current_rsi < 30:
            return "超卖信号，考虑买入"
        elif current_rsi > 50:
            return "强势区间"
        else:
            return "弱势区间"
    
    @staticmethod
    def get_comprehensive_advice(calculator, current_price: float, historical_prices: List[float]) -> Dict:
        """获取综合投资建议"""
        if not historical_prices:
            return {"error": "历史数据不足"}
        
        position = calculator.get_position_summary()
        profit_loss = calculator.calculate_profit_loss(current_price)
        
        trend = InvestmentAdvisor.analyze_trend(historical_prices)
        rsi_signal = InvestmentAdvisor.analyze_rsi_signal(historical_prices)
        
        volatility = RiskAnalyzer.calculate_volatility(historical_prices)
        max_dd = RiskAnalyzer.calculate_max_drawdown(historical_prices)
        
        advice = []
        risk_level = "低"
        
        if profit_loss['profit_loss'] > 0:
            if profit_loss['profit_loss_rate'] > 20:
                advice.append("当前盈利较高，可考虑部分止盈")
            else:
                advice.append("当前盈利，可继续持有")
        else:
            if profit_loss['profit_loss_rate'] < -20:
                advice.append("当前亏损较大，注意风险控制")
                risk_level = "高"
            else:
                advice.append("当前亏损，可考虑补仓或止损")
                risk_level = "中"
        
        if "买入" in trend:
            advice.append("技术面显示买入信号")
        elif "卖出" in trend:
            advice.append("技术面显示卖出信号")
        
        if volatility > 0.5:
            advice.append("波动率较高，注意风险")
            risk_level = "高"
        
        return {
            "position_summary": position,
            "profit_loss": profit_loss,
            "technical_analysis": {
                "trend": trend,
                "rsi_signal": rsi_signal
            },
            "risk_analysis": {
                "volatility": volatility,
                "max_drawdown": max_dd,
                "risk_level": risk_level
            },
            "advice": advice
        }


class StockAnalyzer:
    """股票分析器主类"""
    
    def __init__(self, calculator):
        self.calculator = calculator
        self.price_history: List[PricePoint] = []
    
    def add_price_history(self, date: datetime, price: float, volume: int = 0):
        """添加价格历史"""
        self.price_history.append(PricePoint(date, price, volume))
        self.price_history.sort(key=lambda x: x.date)
    
    def get_price_list(self) -> List[float]:
        """获取价格列表"""
        return [point.price for point in self.price_history]
    
    def analyze_stock(self, current_price: float) -> Dict:
        """分析股票"""
        prices = self.get_price_list()
        if not prices:
            prices = [current_price]
        
        return InvestmentAdvisor.get_comprehensive_advice(self.calculator, current_price, prices)
    
    def generate_report(self, current_price: float) -> str:
        """生成分析报告"""
        analysis = self.analyze_stock(current_price)
        
        report = f"""
=== 股票分析报告 ===
股票代码: {analysis['position_summary']['stock_code']}

【持仓信息】
当前持仓: {analysis['position_summary']['current_shares']}股
平均成本: {analysis['position_summary']['average_cost']:.4f}元
总投资: {analysis['position_summary']['total_investment']:.2f}元

【盈亏分析】
当前价格: {current_price:.2f}元
盈亏金额: {analysis['profit_loss']['profit_loss']:+.2f}元
盈亏率: {analysis['profit_loss']['profit_loss_rate']:+.2f}%
市值: {analysis['profit_loss']['market_value']:.2f}元

【技术分析】
趋势分析: {analysis['technical_analysis']['trend']}
RSI信号: {analysis['technical_analysis']['rsi_signal']}

【风险分析】
波动率: {analysis['risk_analysis']['volatility']:.2%}
最大回撤: {analysis['risk_analysis']['max_drawdown']:.2%}
风险等级: {analysis['risk_analysis']['risk_level']}

【投资建议】
"""
        
        for i, advice in enumerate(analysis['advice'], 1):
            report += f"{i}. {advice}\n"
        
        return report


def demo_advanced_analysis():
    """演示高级分析功能"""
    print("=== 高级股票分析器演示 ===\n")
    
    calculator = StockCalculator("000001")
    
    calculator.buy(datetime(2024, 1, 1), 20.00, 500, 5.0, "首次买入")
    calculator.sell(datetime(2024, 1, 15), 19.88, 500, 5.0, "全部卖出")
    calculator.buy(datetime(2024, 1, 20), 20.14, 500, 5.0, "重新买入")
    
    analyzer = StockAnalyzer(calculator)
    
    base_price = 20.00
    for i in range(30):
        date = datetime(2024, 1, 1) + timedelta(days=i)
        price = base_price + (i % 10 - 5) * 0.1 + (i % 3 - 1) * 0.05
        analyzer.add_price_history(date, price, 1000)
    
    current_price = 20.50
    report = analyzer.generate_report(current_price)
    print(report)


if __name__ == "__main__":
    demo_advanced_analysis() 