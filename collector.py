import asyncio
import time
import pprint

from  collections import deque
import pandas as pd
import sqlalchemy
from binance.client import Client
from binance import BinanceSocketManager, AsyncClient


async def main():
    with open('secret.cfg', 'r') as f:
        test_api_key = f.readline().strip()
        test_api_secret = f.readline().strip()

    i=0
    client = await AsyncClient.create()
    bm = BinanceSocketManager(client)
    # start any sockets here, i.e a trade socket
    ts = bm.trade_socket('BTCUSDT')
    engine = sqlalchemy.create_engine('sqlite:///BTCUSDTstream.db')
    # then start receiving messages
    async with ts as tscm:
        print('collection started')
        while True:
            msg = await tscm.recv()
            if msg:
                frame = createframe(msg)
                frame.to_sql('BTCUSDT', engine, if_exists='append', index=False)

                if i == 100:
                    pprint.pprint(createframe(msg))
                    df = pd.read_sql('BTCUSDT', engine)
                    if len(df) > 10000:
                        con = engine.connect()
                        con.execute('DELETE FROM BTCUSDT WHERE rowid IN (SELECT rowid FROM BTCUSDT LIMIT 9000)')
                        con.close()
                    i = 0
                i += 1
            time.sleep(0.1)

    await client.close_connection()

def createframe(msg):
    df = pd.DataFrame([msg])
    df = df.loc[:,['s','E','p']]
    df.columns = ['symbol','Time','Price']
    df.Price = df.Price.astype(float)
    df.Time =pd.to_datetime(df.Time, unit='ms')
    return df

if __name__ == "__main__":

    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
