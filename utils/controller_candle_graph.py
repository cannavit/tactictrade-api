

# Data 

#  Control  |      period     [               interval              ]
#    hour   | hour (1h)   >>   1d  3d  1w   2w   1mo  3mo   6mo  1y  2y   (default 2w)
#    minute | minute (1m) >>   1d  3d  1wk  2wk  3wk  4wk  5wk 6mk 7mk  (default 2wk)
#    day    | day (1d)    >>   2wk 3wk 1mo  3mo  5mo  6mo  8mo 1y  2y   (default 3mo)
#    week   | week (1wk)  >>   1mo 3mo 5mo  6mo  8mo  10mo 1y  2y       (default 6mo)
#    year   | year (1y)   >>   2y  3y  4y   5y                          (default 5y)

def candle_controller_default(strategy_period='hour'):

    controller_candle = {
        'hour': {
                    "title": "1 weeks",
                    "period": "1wk",
                    "interval": "1h",
                },
        'minute': {
                    "title": "3 hours",
                    "period": "3h",
                    "interval": "1m",
                },
        'day': {
                    "title": "3 months",
                    "period": "3mo",
                    "interval": "1d",
                },
        'week': {
                    "title": "6 months",
                    "period": "6mo",
                    "interval": "1wk",
                },
        'month': {
                    "title": "5 years",
                    "period": "5y",
                    "interval": "1mo",
                },
    }

    return controller_candle[strategy_period]



def candle_controller_graph(strategy_period='hour'):


    controller_candle_graph = {
            'hour': [
                {
                    "title": "1 day",
                    "period": "1d",
                    "interval": "1h",
                },
                {
                    "title": "3 days",
                    "period": "3d",
                    "interval": "1h",
                },
                {
                    "title": "1 week",
                    "period": "1wk",
                    "interval": "1h",
                },
                {
                    "title": "2 weeks",
                    "period": "2wk",
                    "interval": "1h",
                },
                {
                    "title": "1 month",
                    "period": "1mo",
                    "interval": "1h",
                },
                {
                   "title": "3 months",
                    "period": "3mo",
                    "interval": "1h",
                },
                {
                    "title": "6 months",
                    "period": "6mo",
                    "interval": "1h",
                },
                {
                    "title": "1 year",
                    "period": "1y",
                    "interval": "1h",
                },
                {
                    "title": "2 years",
                    "period": "2y",
                    "interval": "1h",
                },
            ],
            'minute': [
                {
                    "title": "1 day",
                    "period": "1d",
                    "interval": "1m",
                },
                {
                    "title": "3 days",
                    "period": "3d",
                    "interval": "1m",
                },
                {
                    "title": "1 week",
                    "period": "1wk",
                    "interval": "1m",
                },
                {
                    "title": "2 weeks",
                    "period": "2wk",
                    "interval": "1m",
                },
                {
                    "title": "3 week",
                    "period": "3wk",
                    "interval": "1m",
                },
                {
                    "title": "4 week",
                    "period": "4wk",
                    "interval": "1m",
                },
                {
                    "title": "5 week",
                    "period": "5wk",
                    "interval": "1m",
                },
                {
                    "title": "6 week",
                    "period": "6wk",
                    "interval": "1m",
                },
                {
                    "title": "7 week",
                    "period": "7wk",
                    "interval": "1m",
                },
            ],

            'day': [
                {
                    "title": "2 weeks",
                    "period": "2wk",
                    "interval": "1d",
                },
                {
                    "title": "3 week",
                    "period": "3wk",
                    "interval": "1d",
                },
                {
                    "title": "1 month",
                    "period": "1mo",
                    "interval": "1d",
                },
                {
                    "title": "3 months",
                    "period": "3mo",
                    "interval": "1d",
                },
                {
                    "title": "5 mounts",
                    "period": "5mo",
                    "interval": "1d",
                },
                {
                    "title": "6 months",
                    "period": "6mo",
                    "interval": "1d",
                },
                {
                    "title": "8 mounts",
                    "period": "8mo",
                    "interval": "1d",
                },
                {
                    "title": "1 year",
                    "period": "1y",
                    "interval": "1d",
                },
                {
                    "title": "2 years",
                    "period": "2y",
                    "interval": "1d",
                },
            ],
            'week': [
                {
                    "title": "1 month",
                    "period": "1mo",
                    "interval": "1wk",
                },
                {
                    "title": "3 months",
                    "period": "3mo",
                    "interval": "1wk",
                },
                {
                    "title": "5 mounts",
                    "period": "5mo",
                    "interval": "1wk",
                },
                {
                    "title": "6 months",
                    "period": "6mo",
                    "interval": "1wk",
                },
                {
                    "title": "8 mounts",
                    "period": "8mo",
                    "interval": "1wk",
                },
                {
                    "title": "10 mounts",
                    "period": "10mo",
                    "interval": "1wk",
                },
                {
                    "title": "1 year",
                    "period": "1y",
                    "interval": "1wk",
                },
                {
                    "title": "2 years",
                    "period": "2y",
                    "interval": "1wk",
                },
            ],
            'year': [
                {
                    "title": "2 years",
                    "period": "2y",
                    "interval": "1y",
                },
                {
                    "title": "3 years",
                    "period": "3y",
                    "interval": "1y",
                },
                {
                    "title": "4 years",
                    "period": "4y",
                    "interval": "1y",
                },
                {
                    "title": "5 years",
                    "period": "5y",
                    "interval": "1y",
                },
            ],

        }
    
    return controller_candle_graph[strategy_period]







