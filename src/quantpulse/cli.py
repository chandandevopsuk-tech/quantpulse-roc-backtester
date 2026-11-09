import argparse
import csv
import json
from datetime import date
from .engine import Candle,backtest

def main():
    parser=argparse.ArgumentParser(description='Backtest ROC zero-cross on OHLC daily CSV')
    parser.add_argument('csv_path')
    parser.add_argument('--period',type=int,default=12)
    parser.add_argument('--output',default='backtest.json')
    args=parser.parse_args()
    with open(args.csv_path,newline='',encoding='utf-8-sig') as source:
        candles=[Candle(date=date.fromisoformat(row['date']),**{name:float(row[name]) for name in ('open','high','low','close')}) for row in csv.DictReader(source)]
    result=backtest(candles,period=args.period)
    with open(args.output,'w',encoding='utf-8') as dest:json.dump(result,dest,indent=2)
    print(f"Wrote {args.output}: {len(result['trades'])} trades, {result['return_pct']}% return")

if __name__=='__main__':main()
