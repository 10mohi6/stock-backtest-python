# stock-backtest

[![PyPI](https://img.shields.io/pypi/v/stock-backtest)](https://pypi.org/project/stock-backtest/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![codecov](https://codecov.io/gh/10mohi6/stock-backtest-python/branch/main/graph/badge.svg?token=ODOV9LETK1)](https://codecov.io/gh/10mohi6/stock-backtest-python)
[![Build Status](https://travis-ci.com/10mohi6/stock-backtest-python.svg?branch=main)](https://travis-ci.com/10mohi6/stock-backtest-python)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/stock-backtest)](https://pypi.org/project/stock-backtest/)
[![Downloads](https://pepy.tech/badge/stock-backtest)](https://pepy.tech/project/stock-backtest)

stock-backtest is a python library for stock technical analysis backtest on Python 3.7 and above.


## Installation

    $ pip install stock-backtest

## Usage

### basic run
```python
from stock_backtest import Backtest

class MyBacktest(Backtest):
    def strategy(self):
        fast_ma = self.sma(period=5)
        slow_ma = self.sma(period=25)
        # golden cross
        self.sell_exit = self.buy_entry = (fast_ma > slow_ma) & (
            fast_ma.shift() <= slow_ma.shift()
        )
        # dead cross
        self.buy_exit = self.sell_entry = (fast_ma < slow_ma) & (
            fast_ma.shift() >= slow_ma.shift()
        )

MyBacktest("AAPL").run()
```
![AAPL--.png](https://raw.githubusercontent.com/10mohi6/stock-backtest-python/main/tests/AAPL--.png)

### advanced run
```python
from stock_backtest import Backtest
from pprint import pprint

class MyBacktest(Backtest):
    def strategy(self):
        rsi = self.rsi(period=10)
        ema = self.ema(period=20)
        atr = self.atr(period=20)
        lower = ema - atr
        upper = ema + atr
        self.buy_entry = (rsi < 30) & (self.df.C < lower)
        self.sell_entry = (rsi > 70) & (self.df.C > upper)
        self.sell_exit = ema > self.df.C
        self.buy_exit = ema < self.df.C

bt = MyBacktest(
    "AAPL",  # ticker
    shares=100,  # number of shares (default=1)
    start="2010-01-01",  # start date (default="")
    end="2020-01-01",  # end date (default="")
    data_dir="data",  # data directory (default=.)
)
pprint(bt.run(), sort_dicts=False)
```
```python
{'total profit': -2779.465,
 'total trades': 102,
 'win rate': 66.667,
 'profit factor': 0.641,
 'maximum drawdown': 3147.5,
 'recovery factor': -0.883,
 'riskreward ratio': 0.321,
 'sharpe ratio': -0.085,
 'average return': -68.929,
 'stop loss': 0,
 'take profit': 0}
```
![AAPL-2010-01-01-2020-01-01.png](https://raw.githubusercontent.com/10mohi6/stock-backtest-python/main/tests/AAPL-2010-01-01-2020-01-01.png)


## Supported indicators
- Simple Moving Average 'sma'
- Exponential Moving Average 'ema'
- Moving Average Convergence Divergence 'macd'
- Relative Strenght Index 'rsi'
- Bollinger Bands 'bbands'
- Stochastic Oscillator 'stoch'
- Average True Range 'atr'
