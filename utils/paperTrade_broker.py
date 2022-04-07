from yahoo_fin import stock_info as si


price_closed = si.get_live_price('SOL-USD')

print(price_closed)