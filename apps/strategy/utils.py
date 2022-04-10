from .models import symbolStrategy as symbol
import requests
from django.db.models import Q
from bs4 import BeautifulSoup
# import yahoo
from yahoo_fin import stock_info as si
# Create if not exist and return the symbolName


def get_symbolName(symbolName):

    symbolOriginalName = symbolName
    is_crypto = False

    # Convert to capital letters
    symbolName = symbolName.upper()
    # Delete spaces
    symbolName = symbolName.replace(" ", "")
    symbolName_corrected = symbolName

    price = None
    symbolName_corrected = symbolName
    try:
        price = si.get_live_price(symbolOriginalName)
    except Exception as e:
        is_crypto = True
        symbolName_corrected = symbolName[0:3] + \
            "-" + symbolName[3:len(symbolName)]
        try:
            price = si.get_live_price(symbolName_corrected)
        except Exception as e:
            return False

    symbolNameResponse = symbol.objects.filter(
        Q(symbolName=symbolName) | Q(symbolName_corrected=symbolName) | Q(
            symbolName_corrected=symbolName_corrected) | Q(symbolName=symbolName_corrected)
    )

    if symbolNameResponse.count() == 0:
        # TODO create one control for check if the symbol is a crypto or not
        WHITE_LIST_BTC = ['BTCUSD', 'BITUSD', 'BTC-USD', 'BIT-USD']
        WHITE_LIST_ETH = ['ETH', 'ETHUSD', 'ETH-USD']
        WHITE_LIST_SOL = ['SOL', 'SOLUSD', 'SOL-USD']

        if symbolName in WHITE_LIST_BTC:
            url = 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRA-QEjLZgfa6TEfrIfiFwmu_waNJQm2cERTA&usqp=CAU'
        elif symbolName in WHITE_LIST_ETH:
            url = 'https://icons.iconarchive.com/icons/cjdowner/cryptocurrency-flat/1024/Ethereum-ETH-icon.png'
        elif symbolName in WHITE_LIST_SOL:
            url = 'https://images.fineartamerica.com/images/artworkimages/medium/3/solana-crypto-logo-sol-paulo-augusto-transparent.png'
        else:
            url = 'https://universal.hellopublic.com/companyLogos/' + symbolName + '@2x.png'

        payload = {}
        headers = {}
        response = requests.request("GET", url, headers=headers, data=payload)

        status_code = response.status_code

        symbol_data = symbolOriginalName.replace("-", "")

        if status_code != 200:
            return {
                'status_code': status_code,
                'message': 'Symbol not found',
                'error': True,
                'symbolName': symbol_data,
                'symbolName_corrected': symbolName,
                'symbol': symbol_data
            }
        else:
            try:
                symbolNameResponse = symbolNameResponse.create(
                    symbolName=symbolOriginalName,
                    symbolName_corrected=symbolName_corrected,
                    url=url,
                    is_crypto=is_crypto,
                )
            except Exception as e:
                print(e)

        symbol_id = symbolNameResponse.id

    else:
        symbolNameResponse = symbolNameResponse.values()[0]
        symbol_id = symbolNameResponse['id']

    return {
        'status_code': 200,
        'message': 'Symbol found',
        'error': False,
        'symbolNameResponse': symbolNameResponse,
        'symbolName': symbolOriginalName,
        'symbolName_corrected': symbolName,
        'symbol_id': symbol_id,
        'price': price
    }
