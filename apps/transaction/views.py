import re

from apps.authentication.models import User
from django.conf import settings
from rest_framework import filters, generics, permissions, status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response

from apps.strategy.models import strategyNews
from apps.authentication.models import User
from apps.broker.broker_close_trade import broker_close_trade_alpaca
from apps.transaction.models import transactions
from apps.transaction.serializers import (TransactionSelectSerializers,
                                          TransactionSelectSerializersGet,
                                          closeTransactionSerializers)


class TransactionsView(generics.ListAPIView):


    serializer_class = TransactionSelectSerializers
    queryset = transactions.objects.all()
    permissions_classes = (permissions.IsAuthenticated,)
    model = transactions

    def get_queryset(self):

        if self.request.auth== None:

            return Response({
                "status": "error",
                "message": "Authentication required or invalid token"
            }, status=status.HTTP_400_BAD_REQUEST)

        user = self.request.user

        return transactions.objects.filter(owner_id=user.id, isClosed__in=[False])


class TransactionRecordsView(generics.ListAPIView):


    serializer_class = TransactionSelectSerializersGet
    queryset = transactions.objects.all()
    permissions_classes = (permissions.IsAuthenticated,)
    model = transactions
# request, *args, **kwargs

    def get_queryset(self):

        if self.request.auth== None:

            return Response({
                "status": "error",
                "message": "Authentication required or invalid token"
            }, status=status.HTTP_400_BAD_REQUEST)

        # user = self.request.user
        strategy_id = self.kwargs['pk']

        strategy = strategyNews.objects.filter(id=strategy_id)

        if strategy.count() == 0:
                return Response({
                "status": "error",
                "message": "Strategy not found"
            }, status=status.HTTP_400_BAD_REQUEST)


        # body = self.request.data
        # Disabled 
        # if body['private'] == True: #TODO check this part
        if False == True:
            user_id = self.request.user.id
        else:
            strategy_value = strategy.values()[0]
            email_bot = strategy_value['email_bot']
            user_bot = User.objects.get(email=email_bot)

            user_id = user_bot.id

        return transactions.objects.filter(owner_id=user_id, strategyNews_id=strategy_id,isClosed__in=[True]).order_by('-id')



# closeTransactionSerializers

class closeTransactionsView(generics.UpdateAPIView):


    serializer_class = closeTransactionSerializers
    queryset = transactions.objects.all()
    permissions_classes = (permissions.IsAuthenticated,)
    model = transactions

    def update(self, request, *args, **kwargs):

        if self.request.auth== None:

            return Response({
                "status": "error",
                "message": "Authentication required or invalid token"
            }, status=status.HTTP_400_BAD_REQUEST)

        user = self.request.user

        idTransaction = kwargs['pk']

        trasactionLast = transactions.objects.get(id=idTransaction, owner_id=user.id)

        price_closed = si.get_live_price(trasactionLast.symbol.symbolName)

        broker = trasactionLast.broker.broker

        if trasactionLast.operation == 'short' and broker == 'paperTrade':

            qty = trasactionLast.base_cost/price_closed
            current_value = trasactionLast.qty_open * price_closed
            base_cost = trasactionLast.qty_open * trasactionLast.price_open
            profit = current_value - base_cost
            profit_percentage = (current_value  - base_cost)/base_cost
            profit_percentage = profit_percentage * 100

            is_winner = False
            if profit > 0:
                is_winner = True

        if trasactionLast.operation == 'long' and broker == 'paperTrade':

            base_cost = trasactionLast.base_cost
            price_short = trasactionLast.number_stock * price_closed
            profit = base_cost - price_short
            current_value = trasactionLast.qty_open * price_closed

            profit_percentage = (current_value  - base_cost)/base_cost
            profit_percentage = profit_percentage * 100

            is_winner = False
            if profit > 0:
                is_winner = True

        if broker == 'alpaca':
            
            broker_close_trade_alpaca({
                            "order": "sell",
                            "owner_id": user.id,
                            "strategyNews_id": trasactionLast.strategyNews.id,
                            "quantityUSD": trasactionLast.qty_open,
                            "use":  trasactionLast.operation == 'long',
                            "stopLoss":  trasactionLast.stop_loss,
                            "takeProfit": trasactionLast.take_profit,
                            "consecutiveLosses": consecutiveLosses,
                            "brokerCapital": brokerCapital,
                            "symbol": strategyData.symbol.symbolName
                        },
                        strategyData,
                        tradingConfig,
                        results,
                        operation='long'
                        )
        

        transactions.objects.filter(id=idTransaction).update(
                base_cost=base_cost,
                profit=profit,
                profit_percentage=profit_percentage,
                isClosed=True,
                price_closed=price_closed,
                is_winner=is_winner,
                closeType='manual'
            )

        return Response({
            "status": "success",
            "message": "Transaction closed",
            "results": {
                "symbol": trasactionLast.symbol.symbolName,
                "profit": profit,
                "profit_percentage": profit_percentage,
                "is_winner": is_winner,
            }
        }, status=status.HTTP_200_OK)



        


       
