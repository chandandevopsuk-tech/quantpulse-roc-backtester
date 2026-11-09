from __future__ import annotations
from dataclasses import dataclass
from datetime import date
from typing import Sequence

@dataclass(frozen=True)
class Candle:
    date: date
    open: float
    high: float
    low: float
    close: float


def validate(candles: Sequence[Candle]):
    if not candles:
        raise ValueError('candles cannot be empty')
    for i, bar in enumerate(candles):
        if min(bar.open,bar.high,bar.low,bar.close)<=0 or bar.high < max(bar.open,bar.close) or bar.low > min(bar.open,bar.close):
            raise ValueError(f'invalid candle at index {i}')
        if i and bar.date <= candles[i-1].date:
            raise ValueError('dates must be strictly ascending')


def signals(candles: Sequence[Candle], period: int = 12) -> list[dict]:
    validate(candles)
    if period < 1:
        raise ValueError('period must be positive')
    previous = None
    found = []
    for i in range(period, len(candles)):
        roc = 100 * (candles[i].close / candles[i-period].close - 1)
        if previous is not None:
            side = 'BUY' if previous <= 0 < roc else ('SELL' if previous >= 0 > roc else None)
            if side:
                found.append({'index':i,'date':candles[i].date.isoformat(),'side':side,'roc':round(roc,6)})
        previous = roc
    return found


def backtest(candles: Sequence[Candle], period: int = 12, units: int = 10, fee_bps: float = 5.0, slippage_bps: float = 2.0, initial_cash: float = 10000.0) -> dict:
    validate(candles)
    if units <= 0 or fee_bps < 0 or slippage_bps < 0 or initial_cash <= 0:
        raise ValueError('invalid backtest parameters')
    events = {item['index']+1:item for item in signals(candles,period) if item['index']+1<len(candles)}
    equity = initial_cash
    position = 0  # +units long, -units short
    entry_price = None
    entry_fee = 0.0
    entry_date = None
    trades = []
    curve=[]

    def execution(price: float, buy: bool) -> float:
        return price*(1+slippage_bps/10000) if buy else price*(1-slippage_bps/10000)

    for i,bar in enumerate(candles):
        action=events.get(i)
        target = units if action and action['side']=='BUY' else (-units if action else position)
        if action and target!=position:
            if position:
                exit_price=execution(bar.open,buy=position<0)
                exit_fee=abs(position)*exit_price*fee_bps/10000
                gross=position*(exit_price-entry_price)
                pnl=gross-entry_fee-exit_fee
                equity+=pnl
                trades.append({'entered':entry_date,'exited':bar.date.isoformat(),'side':'LONG' if position>0 else 'SHORT','entry':round(entry_price,6),'exit':round(exit_price,6),'net_pnl':round(pnl,4)})
            position=target
            entry_price=execution(bar.open,buy=position>0)
            entry_fee=abs(position)*entry_price*fee_bps/10000
            entry_date=bar.date.isoformat()
        mark = equity+(position*(bar.close-entry_price)-entry_fee if position else 0)
        curve.append({'date':bar.date.isoformat(),'equity':round(mark,4)})
    if position:
        last=candles[-1]
        exit_price=execution(last.close,buy=position<0)
        exit_fee=abs(position)*exit_price*fee_bps/10000
        pnl=position*(exit_price-entry_price)-entry_fee-exit_fee
        equity+=pnl
        trades.append({'entered':entry_date,'exited':last.date.isoformat(),'side':'LONG' if position>0 else 'SHORT','entry':round(entry_price,6),'exit':round(exit_price,6),'net_pnl':round(pnl,4)})
        curve[-1]['equity']=round(equity,4)
    peak=initial_cash
    max_drawdown=0.0
    for row in curve:
        peak=max(peak,row['equity'])
        max_drawdown=max(max_drawdown, (peak-row['equity'])/peak)
    return {'period':period,'signals':signals(candles,period),'trades':trades,'final_equity':round(equity,4),'return_pct':round((equity/initial_cash-1)*100,4),'max_drawdown_pct':round(max_drawdown*100,4),'equity_curve':curve}
