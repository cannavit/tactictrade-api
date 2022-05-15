

from utils.convert_json_to_objects import convertJsonToObject


def messages_customs():

    MESSAGE_RESPONSE = {
        "invalid_authentication_or_invalid_token":"Invalid Authentication or invalid token",
        "trading_parameters_not_found":"Trading parameters not found",
        "strategy_not_active": "Strategy not active",
    }


    messages = convertJsonToObject(MESSAGE_RESPONSE)

    return messages

