import pytest
from stock_backtest import Backtest


@pytest.fixture(scope="module", autouse=True)
def scope_module():
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
            self.stop_loss = 5
            self.take_profit = 10

    yield MyBacktest(
        ticker="9983.T",
        start="2010-01-01",
        data_dir="data",
    )


@pytest.fixture(scope="function", autouse=True)
def backtest(scope_module):
    yield scope_module


# @pytest.mark.skip
def test_backtest(backtest):
    backtest.run()
