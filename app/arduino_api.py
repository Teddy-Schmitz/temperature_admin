import requests


class Arduino:
    """This class implements the api calls to an arduino running aREST.

        But it can be used with any system that implements these endpoints.

        /turnOn - turns on the A/C system
        /turnOff - turns off the A/C system
        /temperature - returns the temperature in json format like this.
            {"temperature": 24.80}
        /humidity - returns the humidity in json format like this.
        {"humidity": 52.80}


    """

    def __init__(self, app=None):
        if app is not None:
            self.app = app

    def init_app(self, app):
        self.app = app

    @property
    def _arduino_ip(self):
        return self.app.config['ARDUINO_IP']

    def _req(self, endpoint):
        response = requests.get(endpoint)
        result = response.json()
        return result

    def turn_on(self):
        """Signal Arduino to turn on AC """
        return self._req('http://{}/turnOn'.format(self._arduino_ip))

    def turn_off(self):
        """Signal Arduino to turn off AC """
        return self._req('http://{}/turnOff'.format(self._arduino_ip))

    def check_temps(self):
        """Retrieve current temperature from Arduino """
        res = self._req('http://{}/temperature'.format(self._arduino_ip))
        return res['temperature']

    def check_humidity(self):
        """Retrieve current humidity from Arduino """
        res = self._req('http://{}/humidity'.format(self._arduino_ip))
        return res['humidity']
