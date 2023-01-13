import pprint
import asyncio

from sqlalchemy import create_engine
import pandas as pd
from binance.client import Client

with open('secret.cfg', 'r') as f:
    test_api_key = f.readline().strip()
    test_api_secret = f.readline().strip()

client = Client(test_api_key,test_api_secret, testnet=True)
engine = create_engine('sqlite:///BTCUSDTstream.db')


#Trendfollowing

def strategy(entry, lookback, qty, open_position=False):
    while True:
        df = pd.read_sql('BTCUSDT', engine)
        if not open_position:
            lookbackperiod = df.iloc[-lookback:]
            cumret = (lookbackperiod.Price.pct_change() + 1).cumprod() - 1
            if not open_position:
                if cumret [cumret.last_valid_index()] > entry:
                    order = client.create_order(symbol='BTCUSDT',
                                                side=Client.SIDE_BUY,
                                                type=Client.ORDER_TYPE_MARKET,
                                                quantity=qty)
                    print(order)
                    open_position = True

        if open_position:
            price = float(order['fills'][0]['price'])
            TSL = round(price * 0.9998, 2)
            TTP = round(price * 1.0001, 2)
            dfprice = df.iloc[-1].Price
            if dfprice <= TSL or dfprice >= TTP:
                order = client.create_order(symbol='BTCUSDT',
                                            side=Client.SIDE_SELL,
                                            type=Client.ORDER_TYPE_MARKET,
                                            quantity=qty)
                print(order)
                open_position = False

        # if open_position:
        #     df = pd.read_sql('BTCUSDT', engine)
        #     sincebuy = df.loc[df.Time > pd.to_datetime(order['transactTime'],
        #                                                     unit='ms')]
        #     if len(sincebuy) > 1:
        #         sincebuyret = (sincebuy.Price.pct_change() +1).cumprod() - 1
        #         last_entry = sincebuyret[sincebuyret.last_valid_index()]
        #         if last_entry > 0.00015 or last_entry < -0.00015:
        #             order = client.create_order(symbol='BTCUSDT',
        #                                             side=Client.SIDE_SELL,
        #                                             type=Client.ORDER_TYPE_MARKET,
        #                                             quantity=qty)
        #             print(order)
        #             open_position = False


if __name__== '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(strategy(0.0001, 50, 0.01))

