from binance.client import Client
from binance.enums import *
import dotenv
import os
import time

dotenv.load_dotenv()

API_KEY = os.environ["API_KEY"]
SECRET_KEY = os.environ["SECRET_KEY"]

client = Client(API_KEY, SECRET_KEY)
# CAPITAL = float(client.get_asset_balance(asset="USDT")['free'])

# Initialising the bounds for the grid strategy
UPPER_BOUND = 1.20
LOWER_BOUND = 0.80
GRIDS = 8
PRICE_CHANGE = round((UPPER_BOUND - LOWER_BOUND)/GRIDS, 2)
PER_BUY = 70
BUY_PRICES = []
CREATED = []
PAIR = "STXUSDT"

# Initiating buy order prices
for i in range(GRIDS):
    price = LOWER_BOUND + i * PRICE_CHANGE
    BUY_PRICES.append(round(price,2))

print(BUY_PRICES)
# SELL_PRICES = [i+50 for i in BUY_PRICES]


# Initialising empty dictionary to keep track of current positions
positions = {}

# Function to create buy order
def buy_order(buy_price, qty):
    order = client.order_limit_buy(
        symbol=PAIR,
        quantity=qty,
        price=str(buy_price))
    create_buy_position(buy_price, order["orderId"])

    return order["orderId"]

def create_buy_position(buy_price, order_id):

    data = {
        "buy_orderId": order_id,
        "buy_created": True,
        "buy_executed": False,
        "sell_price": round(buy_price + PRICE_CHANGE,2),
        "sell_created": False,
        "sell_executed": False
    }

    positions[str(buy_price)] = data

def buy_executed(buy_price, sell_orderId):

    global positions
    positions[buy_price]['buy_executed'] = True
    positions[buy_price]['sell_created'] = True
    positions[buy_price]["sell_orderId"] = sell_orderId


def sell_executed(buy_price):
    global positions

    positions[buy_price]['sell_executed'] = True

ok = True

while ok:
    # Getting current price of ETH and amount of ETH to be purchased
    price = float(client.get_avg_price(symbol="STXUSDT")['price'])
    print(price)

    # CREATING BUYS IF NEEDED
    for i in BUY_PRICES:
        if i <= price:
            if i not in CREATED:
                qty = round(PER_BUY / i)
                buy1 = buy_order(i, qty)
                print(f"Buy order created at {i}")
                CREATED.append(i)
                print(CREATED)
            else:
                continue

    # CHECKING STATUS OF POSITIONS (BUY EXECUTION)
    for j in positions.keys():
        order_id = positions[j]['buy_orderId']
        status = client.get_order(symbol=PAIR, orderId=order_id)

        if status["status"] == "FILLED":
            if positions[j]["sell_created"] == False:
                order = client.order_limit_sell(
                    symbol=PAIR,
                    quantity=str(float(status["executedQty"])-0.02),
                    price=(float(status['price']) + PRICE_CHANGE))

                buy_executed(j, order["orderId"])
                print(f"Sell order created at {positions[j]['sell_price']}")
            else:
                continue

    # CHECKING STATUS OF POSITIONS (SELL EXECUTION)
    for j in positions.keys():
        try:
            order_id = positions[j]['sell_orderId']
            status = client.get_order(symbol=PAIR, orderId=order_id)

            if status["status"] == "FILLED":
                CREATED.remove(j)
                del positions[j]
        except KeyError:
            print(f"Sell order not created at price {positions[j]['sell_price']}.")
    print(positions)
    print('End of loop.')
    time.sleep(10)



































