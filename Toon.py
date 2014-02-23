import re
import json
import sys
import uuid
import pprint
import requests

""" The Toon module impersonates the Eneco Toon mobile app, and implements
similar functionality. """


class Toon:
        """ Log in to the Toon API, and do stuff. """
        def __init__(self, username, password):
                self.username = username
                self.password = password
                self.toonstate = None
                self.sessiondata = None
                self.debug = 0

        def login(self):
                """ Log in to the toon API, and set up a session. """
                # First we open the login page, to get the agreement
                # details.
                # Agreement details and user details are stored in the
                # sessiondata variable.
                formdata = {"username": self.username,
                            "password": self.password}
                r = requests.get("https://toonopafstand.eneco.nl/toonMobileBackendWeb/client/login",
                                 params=formdata)
                self.sessiondata = r.json()

                # Now re-use the agreement details to do the actual
                # authentication. This establishes a session, and allows
                # state to be retrieved.
                # TODO: check for variable existence / throw exception on
                # failure
                formdata = {"clientId": self.sessiondata["clientId"],
                            "clientIdChecksum": self.sessiondata["clientIdChecksum"],
                            "agreementId": self.sessiondata["agreements"][0]["agreementId"],
                            "agreementIdChecksum": self.sessiondata["agreements"][0]["agreementIdChecksum"],
                            "random": uuid.uuid1()}
                r = requests.get("https://toonopafstand.eneco.nl/toonMobileBackendWeb/client/auth/start", params=formdata)

        def logout(self):
                """ Log out of the API.
                This is needed, as toon keeps a maximum amount of display clients.
                Too many logins lead to 500 responses from the API. """
                formdata = {"clientId": self.sessiondata["clientId"],
                            "clientIdChecksum": self.sessiondata["clientIdChecksum"],
                            "random": uuid.uuid1()}
                r = requests.get("https://toonopafstand.eneco.nl/toonMobileBackendWeb/client/auth/logout", params=formdata)
                self.toonstate = None
                self.sessiondata = None

        def retrieve_toon_state(self):
                if self.toonstate is not None:
                        return
                formdata = {"clientId": self.sessiondata["clientId"],
                            "clientIdChecksum": self.sessiondata["clientIdChecksum"],
                            "random": uuid.uuid1()}
                r = requests.get("https://toonopafstand.eneco.nl/toonMobileBackendWeb/client/auth/retrieveToonState", params=formdata)
                self.toonstate = r.json()

        def refresh_toon_state(self):
                self.toonstate = None
                self.retrieve_toon_state()

        def get_gas_usage(self):
                self.retrieve_toon_state()
                return self.toonstate["gasUsage"]

        def get_power_usage(self):
                self.retrieve_toon_state()
                return self.toonstate["powerUsage"]

        def get_thermostat_info(self):
                self.retrieve_toon_state()
                return self.toonstate["thermostatInfo"]

        def get_thermostat_states(self):
                self.retrieve_toon_state()
                return self.toonstate["thermostatStates"]

        def set_thermostat(self, temperature):
                targettemp = int(temperature)*100
                formdata = {"clientId": self.sessiondata["clientId"],
                            "clientIdChecksum": self.sessiondata["clientIdChecksum"],
                            "value": targettemp,
                            "random": uuid.uuid1()}
                r = requests.get("https://toonopafstand.eneco.nl/toonMobileBackendWeb/client/auth/setPoint", params=formdata)

	def get_program_state(self):
		self.retrieve_toon_state()
		return self.toonstate["thermostatInfo"]["programState"]

	def set_program_state(self,targetstate):
                formdata = {"clientId": self.sessiondata["clientId"],
                            "clientIdChecksum": self.sessiondata["clientIdChecksum"],
                            "state": 2,
                            "temperatureState": targetstate,
                            "random": uuid.uuid1()}
                r = requests.get("https://toonopafstand.eneco.nl/toonMobileBackendWeb/client/auth/schemeState", params=formdata)

