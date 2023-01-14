import pprint
import asyncio
import matplotlib.pyplot as plt

from sqlalchemy import create_engine
import pandas as pd
from binance.client import Client

with open('secret.cfg', 'r') as f:
    test_api_key = f.readline().strip()
    test_api_secret = f.readline().strip()

client = Client(test_api_key,test_api_secret, testnet=True)
engine = create_engine('sqlite:///BTCUSDTstream.db')
profit = []
totalProfit = []

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
                    buy_price = float(order['cummulativeQuoteQty'])
                    print(order)
                    open_position = True


        if open_position:
            price = float(order['fills'][0]['price'])
            TSL = round(price * 0.998, 2)
            TTP = round(price * 1.001, 2)
            dfprice = df.iloc[-1].Price
            if dfprice <= TSL or dfprice >= TTP:
                order = client.create_order(symbol='BTCUSDT',
                                            side=Client.SIDE_SELL,
                                            type=Client.ORDER_TYPE_MARKET,
                                            quantity=qty)
                sell_price = float(order['cummulativeQuoteQty'])
                Profit = sell_price - buy_price

                # Create lists of profit values and timestamps
                profit.append(Profit)
                timestamps = [pd.to_datetime(pd.Timestamp.now()) for _ in range(len(profit))]

                totalProfit.append(sum(profit))

                # Create the DataFrame
                dff = pd.DataFrame({'profit': totalProfit, 'timestamp': timestamps})

                dff.to_csv('Profit.csv', index=True)
                # Read the CSV file into a DataFrame
                df = pd.read_csv('Profit.csv')

                # plot the graph of price column
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                df['time_hm'] = df['timestamp'].dt.strftime('%H:%M')
                df.plot(x='time_hm', y='profit', kind='line')
                plt.show()

                print(order)
                open_position = False


if __name__== '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(strategy(0.001, 50, 0.01))


