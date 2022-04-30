import json
from random import randint
from time import sleep
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.generic.websocket import WebsocketConsumer
from yahoo_fin import stock_info as si



class WSConsumer(WebsocketConsumer):

    def connect(self):

        self.accept()

        symbol = 'ETH-USD'

        continue_loop = True
        while continue_loop:
            
            try:
                price = si.get_live_price(symbol)
            except Exception as e:
                print(e)
                continue_loop = False

                data = {
                    "socket_type": "live_assets",
                    "asset": symbol,
                    "value": 0,
                    "error": "Error: " + str(e)
                }

                self.send(text_data=json.dumps(data))
                break

            data = {
                "socket_type": "live_assets",
                "asset": symbol,
                "value": price,
            }

            self.send(text_data=json.dumps(data))
            # self.accept()
            sleep(4)


    def stop(self):
        self.terminate = True
