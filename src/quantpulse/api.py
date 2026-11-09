from datetime import date
from fastapi import FastAPI
from pydantic import BaseModel,Field,model_validator
from .engine import Candle,backtest

app=FastAPI(title='QuantPulse ROC Backtesting API',version='0.1.0')

class CandlePayload(BaseModel):
    date:date
    open:float=Field(gt=0)
    high:float=Field(gt=0)
    low:float=Field(gt=0)
    close:float=Field(gt=0)

    @model_validator(mode='after')
    def validate_ohlc(self):
        if self.low>min(self.open,self.close) or self.high<max(self.open,self.close):
            raise ValueError('OHLC inconsistent')
        return self

class BacktestRequest(BaseModel):
    candles:list[CandlePayload]=Field(min_length=2,max_length=20000)
    period:int=Field(default=12,ge=1,le=1000)
    units:int=Field(default=10,ge=1,le=10000)
    fee_bps:float=Field(default=5,ge=0,le=1000)
    slippage_bps:float=Field(default=2,ge=0,le=1000)

    @model_validator(mode='after')
    def ordered(self):
        if any(self.candles[i].date <= self.candles[i-1].date for i in range(1,len(self.candles))):
            raise ValueError('candles must be sorted and unique by date')
        return self

@app.get('/healthz')
def health():return {'status':'ok'}

@app.post('/v1/backtest')
def run(data:BacktestRequest):
    candles=[Candle(**x.model_dump()) for x in data.candles]
    return backtest(candles,period=data.period,units=data.units,fee_bps=data.fee_bps,slippage_bps=data.slippage_bps)
