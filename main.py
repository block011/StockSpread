import Robinhood
import os



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


def main():
    success = ConnectToRobinhood() #sets connection
    
    if success is False:
        print("Failed to connect, aborting")
        exit()

    data = Robinhood.get_market_options()

    print(data)


    






if __name__ == '__main__':
    main()