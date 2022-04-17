# Control for connect with the differs brokers.

from apps.broker.brokers_connections.alpaca.broker_close_trade import \
    broker_close_trade_alpaca
from apps.broker.brokers_connections.alpaca.long_buy import \
    broker as broker_alpaca
from apps.broker.brokers_connections.paper_trade.long_buy import \
    broker as papertrade
from apps.broker.brokers_connections.paper_trade.short import \
    broker as papertrade_short
from utils.convert_json_to_objects import convertJsonToObject


class broker_selector():

    # Init data
    def __init__(self,
                 trading_config=None,
                 strategyNewsId=None,
                 follower_id=None,
                 strategyData=None,
                 transaction_is_open=False,
                 transaction_obj=None,
                 ):


        options = {
            "owner_id": follower_id,
            "strategyNews_id": strategyNewsId,
            "quantityUSD": trading_config.quantityUSDLong,
            "use": trading_config.useLong,
            "stopLoss": trading_config.stopLossLong,
            "takeProfit": trading_config.takeProfitLong,
            "consecutiveLosses": trading_config.consecutiveLossesLong,
            "brokerCapital": trading_config.broker.capital,
            "symbol": strategyData.symbol.symbolName_corrected
        }

        self.trading_config = trading_config
        self.strategyData = strategyData
        self.options = convertJsonToObject(options)
        self.transaction_is_open = transaction_is_open
        self.transaction_obj = transaction_obj

    # Login for Long Trade
    def long_trade(self, order='buy', broker_name='paperTrade', is_active_long=False, results={}):
        
        self.options.order = 'buy'

        # Open Long Trade
        if order == 'buy' and  is_active_long == True and not self.transaction_is_open:

            # Open Paper Trade (paperTrade)
            if broker_name == 'paperTrade':

                # Open Long Trade [PAPERTRADE-BUY]
                results = papertrade(
                    trading=self.trading_config,
                    strategy=self.strategyData,
                    operation='long'
                ).long_buy(
                    options=self.options,
                    results=results
                )

            # Open Long Trade [ALPACA-BUY]
            elif broker_name == 'alpaca':

                results = broker_alpaca(
                    options=self.options,
                    strategy=self.strategyData,
                    trading=self.trading_config,
                    results=results,
                    operation='long',
                    transactionLast=self.transaction_obj
                ).long_buy()


        # Close Long Trade

        if order == 'sell' and is_active_long == True and self.transaction_is_open:

            # Close Paper Trade (paperTrade)
            if broker_name == 'paperTrade':

                # Open Short Trade [PAPERTRADE-SELL]

                results = papertrade(
                    trading=self.trading_config,
                    strategy=self.strategyData,
                    operation='long',
                    transaction_obj=self.transaction_obj
                ).close_position(
                    options=self.options,
                    results=results,
                )

            # Close Long Trade [ALPACA-SELL]
            elif broker_name == 'alpaca':

                results = broker_alpaca(
                    options=self.options,
                    strategy=self.strategyData,
                    trading=self.trading_config,
                    results=results,
                    operation='long',
                ).close_position()


        return results

    def short_trade(self, order='sell', broker_name='paperTrade', is_active_short=False, results={}):

        self.options.order = 'sell'

        #! Open Short Trade
        if order == 'sell' and is_active_short == True:

            # Open Short Paper Trade (paperTrade)
            if broker_name == 'paperTrade':

                results = papertrade_short(
                    trading=self.trading_config,
                    strategy=self.strategyData,
                    options=self.options,
                    results=results
                ).short_buy()

            # if broker_name == 'alpaca':

                # TODO The short is pending

                # broker_sell_short_alpaca({
                #             "order": "sell",
                #             "owner_id": follow.id,
                #             "strategyNews_id": strategyNewsConfig.values()[0]['id'],
                #             "quantityUSD": quantityUSD,
                #             "use": use,
                #             "stopLoss": stopLoss,
                #             "takeProfit": takeProfit,
                #             "consecutiveLosses": consecutiveLosses,
                #             "brokerCapital": brokerCapital,
                #             "symbol": strategyData.symbol.symbolName_corrected
                #         },
                #             strategyData,
                #             tradingConfig,
                #             results)

        #!Close Short Trade
        if order == 'buy' and is_active_short == True:

            # Close Short Paper Trade (paperTrade)
            if broker_name == 'paperTrade':

                results = papertrade_short(
                    trading=self.trading_config,
                    strategy=self.strategyData,
                    options=self.options,
                    results=results
                ).close_position()

            # Close Short Trade [ALPACA-SELL]
            if broker_name == 'alpaca':

                broker_close_trade_alpaca(self.options,
                                          self.strategyData,
                                          self.trading_config,
                                          results,
                                          operation='short'
                                          )
        
        return results
