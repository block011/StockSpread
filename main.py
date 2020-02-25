import Robinhood
import os
import datetime
import asyncio 

COLLATORAL_THRESHHOLD = 500
MAX_PROCESSES = int(os.environ.get("NUMBER_OF_PROCESSORS")) - 1

stocks = ['SPY',
          'S',
          'TBLT',
          'AMD',
          'VXX',
          'GDX',
          'EEM',
          'QQQ',
          'F',
          'TOCA',
          'XLF',
          'MSFT',
          'DBX',
          'BAC',
          'SPCE',
          'CHK',
          'GE',
          'NIO',
          'VALE',
          'ZOM',
          'SQQQ',
          'ABEV',
          'FXI',
          'UVXY',
          'AAPL',
          'PFE',
          'ET',
          'MS',
          'GRPN',
          'EWZ',
          'T',
          'XOP',
          'MU',
          'USO',
          'TQQQ',
          'DUST',
          'IAU',
          'RTTR',
          'PLUG',
          'EFA',
          'AUY',
          'KGC',
          'HYG',
          'TVIX',
          'PBR'
          ]

class StockOption:
    def __init__(self, stockDictionary):
        try:
            self.askPrice = float(stockDictionary["ask_price"])          #0.12
            self.bidPrice = float(stockDictionary["bid_price"])
            self.strikePrice = float(stockDictionary["strike_price"])             #60.00
            self.profitChance = float(stockDictionary["chance_of_profit_short"])   #0.7823
            self.type = stockDictionary["type"].upper()                     #call or put
            self.ticker = stockDictionary["chain_symbol"].upper()           #VSAT
        except Exception as e:
            print("failed to create StockOption")
            print(e)
            self.type = "FAILED"

    def option_sort(self):
        return self.strikePrice

    def getBreakEven(self):
        return (self.strikePrice + self.bidPrice) if self.type == 'CALL' else (self.strikePrice - self.bidPrice)
        
    def calculateProfit(self, otherStock):
        if otherStock.bidPrice == 0:
            return -10000

        if self.type != otherStock.type or self.type == "FAILED":
            return -10000
        
        if self.type == "CALL":
            if self.getBreakEven() > otherStock.getBreakEven():
                return -10000

            maxPremium = (self.bidPrice - otherStock.askPrice) * 100
            stockDifference = otherStock.strikePrice - self.strikePrice

            maxLoss = -1 * (stockDifference * 100) * (1 - otherStock.profitChance)
            maxGain = maxPremium * self.profitChance
            mixed = ((((maxLoss * otherStock.strikePrice)/ (2 * stockDifference)) - 
                    ((maxLoss * self.strikePrice)/ (2 * stockDifference))) / 
                    stockDifference)

            if stockDifference * 100 > COLLATORAL_THRESHHOLD:
                return -10000

            return sum((maxLoss, maxGain, mixed))
        else:
            pass



    def displayStockOption(self):
        print("----- {} {} STOCK OPTION -----".format(self.ticker, self.type))
        print("Ask --- {}   | Bid --- {}".format(self.askPrice, self.bidPrice))
        print("Strike Price --- {}".format(self.strikePrice))
        print("Probability  --- {}".format(self.profitChance))
        print("---------------------------------")

def ConnectToRobinhood():
    try:
        user = os.environ["ROBINHOODUSER"]
        pw = os.environ["ROBINHOODPASSWORD"]

    except Exception as e:
        print(e)
        print("Failed to recieve system variables.")
        print("Did you set system variables for ROBINHOODUSER and ROBINHOODPASSWORD?")
        return False
    
    success = Robinhood.login(user, pw)
    if success is False:
        print("Failed to connect to Robinhood.")
        print("Either user/pw combination failed, or the api is down.")
    else:
        return True

async def generateBestSpread(listOfTickers):
    curTasks = []
    maxTasks = MAX_PROCESSES
    bestDeal = [-10000, 0, 0]
    
    for i in range(maxTasks):
        ticker = listOfTickers.pop()
        task = asyncio.ensure_future(generateSpread(ticker))
        curTasks.append(task)
        if i > len(listOfTickers):
            break
    
    for f in asyncio.as_completed(curTasks):
        t = await f
        result = t
        if result[0] > bestDeal[0]:
            bestDeal = result



    return bestDeal


async def generateSpread(ticker):
    date = findEarliestOptionExpiration(ticker)
    myList = Robinhood.find_options_for_stock_by_expiration(ticker,date,optionType="call")

    myOptions = [StockOption(x) for x in myList]
    myOptions.sort(key= lambda data : data.option_sort())

    if len(myOptions) >= 2:
        bestDeal = [-10000, myOptions[0], myOptions[1]]
    else:
        return None

    for first in range(len(myOptions) - 1):
        for second in range(first + 1,len(myOptions)):
            temp = myOptions[first].calculateProfit(myOptions[second])
            if temp > bestDeal[0]:
                bestDeal = [temp, myOptions[first], myOptions[second]]
    
    return bestDeal



if __name__ == '__main__':
    main()