#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票计算器Web应用
使用Flask框架提供Web界面
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for
from datetime import datetime
import json
import os
from stock_calculator import StockCalculator, StockPortfolio
from advanced_stock_analyzer import StockAnalyzer

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

# 全局变量存储投资组合
portfolio = StockPortfolio()

@app.route('/')
def index():
    """主页"""
    return render_template('index.html')

@app.route('/calculator')
def calculator():
    """股票计算器页面"""
    return render_template('calculator.html')

@app.route('/portfolio')
def portfolio_view():
    """投资组合页面"""
    return render_template('portfolio.html')

@app.route('/analysis')
def analysis():
    """分析页面"""
    return render_template('analysis.html')

@app.route('/api/add_trade', methods=['POST'])
def add_trade():
    """添加交易记录API"""
    try:
        data = request.get_json()
        stock_code = data.get('stock_code', '')
        action = data.get('action', '')
        price = float(data.get('price', 0))
        shares = int(data.get('shares', 0))
        commission = float(data.get('commission', 0))
        description = data.get('description', '')
        date_str = data.get('date', datetime.now().strftime('%Y-%m-%d'))
        
        # 解析日期
        trade_date = datetime.strptime(date_str, '%Y-%m-%d')
        
        # 获取或创建股票计算器
        calculator = portfolio.add_stock(stock_code)
        
        # 添加交易记录
        if action == 'buy':
            calculator.buy(trade_date, price, shares, commission, description)
        elif action == 'sell':
            calculator.sell(trade_date, price, shares, commission, description)
        
        return jsonify({'success': True, 'message': '交易记录添加成功'})
    
    except Exception as e:
        return jsonify({'success': False, 'message': f'错误: {str(e)}'})

@app.route('/api/get_position/<stock_code>')
def get_position(stock_code):
    """获取持仓信息API"""
    try:
        calculator = portfolio.get_stock(stock_code)
        if not calculator:
            return jsonify({'success': False, 'message': '股票不存在'})
        
        position = calculator.get_position_summary()
        history = calculator.get_trade_history()
        
        return jsonify({
            'success': True,
            'position': position,
            'history': history
        })
    
    except Exception as e:
        return jsonify({'success': False, 'message': f'错误: {str(e)}'})

@app.route('/api/calculate_profit_loss', methods=['POST'])
def calculate_profit_loss():
    """计算盈亏API"""
    try:
        data = request.get_json()
        stock_code = data.get('stock_code', '')
        current_price = float(data.get('current_price', 0))
        
        calculator = portfolio.get_stock(stock_code)
        if not calculator:
            return jsonify({'success': False, 'message': '股票不存在'})
        
        result = calculator.calculate_profit_loss(current_price)
        
        return jsonify({
            'success': True,
            'result': result
        })
    
    except Exception as e:
        return jsonify({'success': False, 'message': f'错误: {str(e)}'})

@app.route('/api/get_portfolio_summary', methods=['POST'])
def get_portfolio_summary():
    """获取投资组合摘要API"""
    try:
        data = request.get_json()
        current_prices = data.get('current_prices', {})
        
        summary = portfolio.get_portfolio_summary(current_prices)
        
        return jsonify({
            'success': True,
            'summary': summary
        })
    
    except Exception as e:
        return jsonify({'success': False, 'message': f'错误: {str(e)}'})

@app.route('/api/analyze_stock', methods=['POST'])
def analyze_stock():
    """分析股票API"""
    try:
        data = request.get_json()
        stock_code = data.get('stock_code', '')
        current_price = float(data.get('current_price', 0))
        price_history = data.get('price_history', [])
        
        calculator = portfolio.get_stock(stock_code)
        if not calculator:
            return jsonify({'success': False, 'message': '股票不存在'})
        
        analyzer = StockAnalyzer(calculator)
        
        # 添加价格历史
        for price_data in price_history:
            date = datetime.strptime(price_data['date'], '%Y-%m-%d')
            price = float(price_data['price'])
            volume = int(price_data.get('volume', 0))
            analyzer.add_price_history(date, price, volume)
        
        analysis = analyzer.analyze_stock(current_price)
        
        return jsonify({
            'success': True,
            'analysis': analysis
        })
    
    except Exception as e:
        return jsonify({'success': False, 'message': f'错误: {str(e)}'})

@app.route('/api/save_portfolio', methods=['POST'])
def save_portfolio():
    """保存投资组合API"""
    try:
        data = request.get_json()
        filename = data.get('filename', 'portfolio.json')
        
        portfolio.save_portfolio(filename)
        
        return jsonify({'success': True, 'message': '投资组合保存成功'})
    
    except Exception as e:
        return jsonify({'success': False, 'message': f'错误: {str(e)}'})

@app.route('/api/load_portfolio', methods=['POST'])
def load_portfolio():
    """加载投资组合API"""
    try:
        data = request.get_json()
        filename = data.get('filename', 'portfolio.json')
        
        portfolio.load_portfolio(filename)
        
        return jsonify({'success': True, 'message': '投资组合加载成功'})
    
    except Exception as e:
        return jsonify({'success': False, 'message': f'错误: {str(e)}'})

@app.route('/api/get_all_stocks')
def get_all_stocks():
    """获取所有股票列表API"""
    try:
        stocks = list(portfolio.stocks.keys())
        return jsonify({
            'success': True,
            'stocks': stocks
        })
    
    except Exception as e:
        return jsonify({'success': False, 'message': f'错误: {str(e)}'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080) 