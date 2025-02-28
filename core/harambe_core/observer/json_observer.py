import json

from harambe_core.observer.serialization_observer import SerializationObserver


class JsonStdoutObserver(SerializationObserver):
    def __init__(self):
        super().__init__(sink=print, serializer=json.dumps)
