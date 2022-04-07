from .models import symbol


# Create if not exist and return the symbolName
def get_symbolName(symbolName):

    try:
        symbolNameResponse = symbol.objects.filter(symbol=symbolName).values()[0]
        
    except BaseException as e:
        print(e)
        symbolNameResponse = symbol.objects.create(symbol=symbolName)
        symbolNameResponse = symbol.objects.filter(symbol=symbolName).values()[0]

        pass

    return symbolNameResponse