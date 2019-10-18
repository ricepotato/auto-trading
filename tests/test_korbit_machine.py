import unittest
from machine.korbit_machine import KorbitMachine
import inspect

class KorbitMachineTestCase(unittest.TestCase):
    def setUp(self):
        self.korbit_machine = KorbitMachine()

    def tearDown(self):
        pass

    def test_set_token(self):
        print(inspect.stack()[0][3])
        expire, access_token, refresh_token = self.korbit_machine.set_token(grant_type="client_credentials")
        assert access_token
        print("Expire:", expire, "Access_token:", access_token, "Refresh_token:", refresh_token)