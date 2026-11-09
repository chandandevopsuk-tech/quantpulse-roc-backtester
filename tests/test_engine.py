from datetime import date,timedelta
from fastapi.testclient import TestClient
from quantpulse.api import app
from quantpulse.engine import Candle,signals,backtest

def series(closes):
    return [Candle(date(2026,1,1)+timedelta(days=i),float(p),float(p)+1,float(p)-1,float(p)) for i,p in enumerate(closes)]

def test_roc_cross_requires_prior_roc():
    candles=series([100,90,95,105,80,110,120])
    result=signals(candles,period=2)
    assert any(s['side']=='BUY' for s in result)
    assert any(s['side']=='SELL' for s in result)
    assert all(s['index']>=3 for s in result)

def test_next_open_execution_and_fee():
    candles=series([100,95,90,110,120,80,70,100])
    result=backtest(candles,period=2,units=1,fee_bps=0,slippage_bps=0)
    assert result['trades']
    assert all(trade['entered']!=result['signals'][0]['date'] for trade in result['trades'])
    assert result['final_equity'] == round(10000+sum(t['net_pnl'] for t in result['trades']),4)

def test_signal_history_not_affected_by_future():
    past=series([100,95,90,110,120,80])
    history=signals(past,period=2)
    extended=signals(past+[Candle(date(2026,1,7),1,2,0.5,1)],period=2)
    assert extended[:len(history)]==history

def test_api_validation():
    client=TestClient(app)
    assert client.get('/healthz').status_code==200
    assert client.post('/v1/backtest',json={'candles':[{'date':'2026-01-01','open':100,'high':99,'low':90,'close':100},{'date':'2026-01-02','open':101,'high':102,'low':100,'close':101}]}).status_code==422
