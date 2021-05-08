from typing import Tuple
import numpy as np
import pandas as pd
import os
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import yfinance as yf


class Backtest(object):
    def __init__(
        self,
        ticker: str,
        *,
        shares: float = 1,
        interval: str = "1d",  # 1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo
        start: str = "",
        end: str = "",
        data_dir: str = ".",
    ) -> None:
        self.start = start
        self.end = end
        self.ticker = ticker
        self.interval = interval
        self.data_dir = data_dir
        self.take_profit = 0
        self.stop_loss = 0
        self.buy_entry = (
            self.buy_exit
        ) = self.sell_entry = self.sell_exit = pd.DataFrame()
        self.shares = shares
        if not os.path.exists(data_dir):
            os.mkdir(data_dir)
        f = "{}/{}-{}-{}.csv".format(data_dir, ticker, start, end)
        overtime = True
        if os.path.exists(f):
            overtime = datetime.now() > (
                datetime.fromtimestamp(os.path.getmtime(f)) + timedelta(days=1)
            )
        if overtime:
            if start != "" or end != "":
                if start == "":
                    start = "1985-01-01"
                if end == "":
                    end = datetime.now().strftime("%Y-%m-%d")
                self.df = yf.download(
                    ticker,
                    start=start,
                    end=end,
                    interval=interval,
                ).set_axis(["O", "H", "L", "C", "AC", "V"], axis=1)
                self.df.index.names = ["T"]
            else:
                self.df = yf.download(ticker, period="max", interval=interval).set_axis(
                    ["O", "H", "L", "C", "AC", "V"], axis=1
                )
                self.df.index.names = ["T"]
            self.df.to_csv(f)
        else:
            self.df = pd.read_csv(f, index_col="T", parse_dates=True)

    def strategy(self) -> None:
        pass

    def run(self) -> dict:
        self.strategy()
        o = self.df.O.values
        L = self.df.L.values
        h = self.df.H.values
        N = len(self.df)
        long_trade = np.zeros(N)
        short_trade = np.zeros(N)

        # buy entry
        buy_entry_s = np.hstack((False, self.buy_entry[:-1]))  # shift
        long_trade[buy_entry_s] = o[buy_entry_s]
        # buy exit
        buy_exit_s = np.hstack((False, self.buy_exit[:-2], True))  # shift
        long_trade[buy_exit_s] = -o[buy_exit_s]
        # sell entry
        sell_entry_s = np.hstack((False, self.sell_entry[:-1]))  # shift
        short_trade[sell_entry_s] = o[sell_entry_s]
        # sell exit
        sell_exit_s = np.hstack((False, self.sell_exit[:-2], True))  # shift
        short_trade[sell_exit_s] = -o[sell_exit_s]

        long_pl = pd.Series(np.zeros(N))  # profit/loss of buy position
        short_pl = pd.Series(np.zeros(N))  # profit/loss of sell position
        buy_price = sell_price = 0
        long_rr = []  # long return rate
        short_rr = []  # short return rate
        stop_loss = take_profit = 0

        for i in range(1, N):
            # buy entry
            if long_trade[i] > 0:
                if buy_price == 0:
                    buy_price = long_trade[i]
                    short_trade[i] = -buy_price  # sell exit
                else:
                    long_trade[i] = 0

            # sell entry
            if short_trade[i] > 0:
                if sell_price == 0:
                    sell_price = short_trade[i]
                    long_trade[i] = -sell_price  # buy exit
                else:
                    short_trade[i] = 0

            # buy exit
            if long_trade[i] < 0:
                if buy_price != 0:
                    long_pl[i] = (
                        -(buy_price + long_trade[i]) * self.shares
                    )  # profit/loss fixed
                    long_rr.append(
                        round(long_pl[i] / buy_price * 100, 2)
                    )  # long return rate
                    buy_price = 0
                else:
                    long_trade[i] = 0

            # sell exit
            if short_trade[i] < 0:
                if sell_price != 0:
                    short_pl[i] = (
                        sell_price + short_trade[i]
                    ) * self.shares  # profit/loss fixed
                    short_rr.append(
                        round(short_pl[i] / sell_price * 100, 2)
                    )  # short return rate
                    sell_price = 0
                else:
                    short_trade[i] = 0

            # close buy position with stop loss
            if buy_price != 0 and self.stop_loss > 0:
                stop_price = buy_price - self.stop_loss
                if L[i] <= stop_price:
                    long_trade[i] = -stop_price
                    long_pl[i] = (
                        -(buy_price + long_trade[i]) * self.shares
                    )  # profit/loss fixed
                    long_rr.append(
                        round(long_pl[i] / buy_price * 100, 2)
                    )  # long return rate
                    buy_price = 0
                    stop_loss += 1

            # close buy positon with take profit
            if buy_price != 0 and self.take_profit > 0:
                limit_price = buy_price + self.take_profit
                if h[i] >= limit_price:
                    long_trade[i] = -limit_price
                    long_pl[i] = (
                        -(buy_price + long_trade[i]) * self.shares
                    )  # profit/loss fixed
                    long_rr.append(
                        round(long_pl[i] / buy_price * 100, 2)
                    )  # long return rate
                    buy_price = 0
                    take_profit += 1

            # close sell position with stop loss
            if sell_price != 0 and self.stop_loss > 0:
                stop_price = sell_price + self.stop_loss
                if h[i] >= stop_price:
                    short_trade[i] = -stop_price
                    short_pl[i] = (
                        sell_price + short_trade[i]
                    ) * self.shares  # profit/loss fixed
                    short_rr.append(
                        round(short_pl[i] / sell_price * 100, 2)
                    )  # short return rate
                    sell_price = 0
                    stop_loss += 1

            # close sell position with take profit
            if sell_price != 0 and self.take_profit > 0:
                limit_price = sell_price - self.take_profit
                if L[i] <= limit_price:
                    short_trade[i] = -limit_price
                    short_pl[i] = (
                        sell_price + short_trade[i]
                    ) * self.shares  # profit/loss fixed
                    short_rr.append(
                        round(short_pl[i] / sell_price * 100, 2)
                    )  # short return rate
                    sell_price = 0
                    take_profit += 1

        win_trades = np.count_nonzero(long_pl.clip(lower=0)) + np.count_nonzero(
            short_pl.clip(lower=0)
        )
        lose_trades = np.count_nonzero(long_pl.clip(upper=0)) + np.count_nonzero(
            short_pl.clip(upper=0)
        )
        trades = (np.count_nonzero(long_trade) // 2) + (
            np.count_nonzero(short_trade) // 2
        )
        gross_profit = long_pl.clip(lower=0).sum() + short_pl.clip(lower=0).sum()
        gross_loss = long_pl.clip(upper=0).sum() + short_pl.clip(upper=0).sum()
        profit_pl = gross_profit + gross_loss
        self.equity = (long_pl + short_pl).cumsum()
        mdd = (self.equity.cummax() - self.equity).max()
        self.return_rate = pd.Series(short_rr + long_rr)

        fig = plt.figure(figsize=(8, 4))
        fig.subplots_adjust(
            wspace=0.2, hspace=0.5, left=0.095, right=0.95, bottom=0.095, top=0.95
        )
        ax1 = fig.add_subplot(3, 1, 1)
        ax1.plot(self.df.C, label="close")
        ax1.legend()
        ax2 = fig.add_subplot(3, 1, 2)
        ax2.plot(self.equity, label="equity")
        ax2.legend()
        ax3 = fig.add_subplot(3, 1, 3)
        ax3.hist(self.return_rate, 50, rwidth=0.9)
        ax3.axvline(
            sum(self.return_rate) / len(self.return_rate),
            color="orange",
            label="average return",
        )
        ax3.legend()
        plt.savefig(
            "{}/{}-{}-{}.png".format(self.data_dir, self.ticker, self.start, self.end)
        )

        r = {
            "total profit": round(profit_pl, 3),
            "total trades": trades,
            "win rate": round(win_trades / trades * 100, 3),
            "profit factor": round(-gross_profit / gross_loss, 3),
            "maximum drawdown": round(mdd, 3),
            "recovery factor": round(profit_pl / mdd, 3),
            "riskreward ratio": round(
                -(gross_profit / win_trades) / (gross_loss / lose_trades), 3
            ),
            "sharpe ratio": round(self.return_rate.mean() / self.return_rate.std(), 3),
            "average return": round(self.return_rate.mean(), 3),
            "stop loss": stop_loss,
            "take profit": take_profit,
        }
        with open(
            "{}/{}-{}-{}.json".format(self.data_dir, self.ticker, self.start, self.end),
            "w",
        ) as f:
            f.write(str(r))
        return r

    def sma(self, *, period: int, price: str = "C") -> pd.DataFrame:
        return self.df[price].rolling(period).mean()

    def ema(self, *, period: int, price: str = "C") -> pd.DataFrame:
        return self.df[price].ewm(span=period).mean()

    def bbands(
        self, *, period: int = 20, band: int = 2, price: str = "C"
    ) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        std = self.df[price].rolling(period).std()
        mean = self.df[price].rolling(period).mean()
        return mean + (std * band), mean, mean - (std * band)

    def macd(
        self,
        *,
        fast_period: int = 12,
        slow_period: int = 26,
        signal_period: int = 9,
        price: str = "C",
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        macd = (
            self.df[price].ewm(span=fast_period).mean()
            - self.df[price].ewm(span=slow_period).mean()
        )
        signal = macd.ewm(span=signal_period).mean()
        return macd, signal

    def stoch(
        self, *, k_period: int = 5, d_period: int = 3
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        k = (
            (self.df.C - self.df.L.rolling(k_period).min())
            / (self.df.H.rolling(k_period).max() - self.df.L.rolling(k_period).min())
            * 100
        )
        d = k.rolling(d_period).mean()
        return k, d

    def rsi(self, *, period: int = 14, price: str = "C") -> pd.DataFrame:
        return 100 - 100 / (
            1
            - self.df[price].diff().clip(lower=0).rolling(period).mean()
            / self.df[price].diff().clip(upper=0).rolling(period).mean()
        )

    def atr(self, *, period: int = 14, price: str = "C") -> pd.DataFrame:
        a = (self.df.H - self.df.L).abs()
        b = (self.df.H - self.df[price].shift()).abs()
        c = (self.df.L - self.df[price].shift()).abs()

        df = pd.concat([a, b, c], axis=1).max(axis=1)
        return df.ewm(span=period).mean()
