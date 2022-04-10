# Library for Convert json to object
from types import SimpleNamespace
import json

def convertJsonToObject(json_data):

    data = json.dumps(json_data)

    data_object = json.loads(data, object_hook=lambda d: SimpleNamespace(**d))

    return data_object