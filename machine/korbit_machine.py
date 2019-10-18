
import requests
import configparser

from machine.base_machine import Machine

class KorbitMachine(Machine):
    """ 코빗 거래소와의 거래를 위한 클래스입니다.
    BASE_API_URL 은 REST API 호출을 위한 기본 URL 입니다.
    TRADE_CURRENCY_TYPE 은 코빗에서 거래가 가능한 화폐의 종류입니다.
    """

    BASE_API_URL = "https://api.korbit.co.kr"
    TRADE_CURRENCY_TYPE = ["btc", "bch", "btg", "eth", "etc", "xrp", "krw"]

    def __init__(self):
        """ conf.ini 에서 정보 읽어옴 """
        config = configparser.ConfigParser()
        config.read("conf/config.ini")
        self.CLIENT_ID = config["KORBIT"]["client_id"]
        self.CLIENT_SECRET = config["KORBIT"]["client_secret"]
        self.USER_NAME = config["KORBIT"]["username"]
        self.PASSWROD = config["KORBIT"]["password"]
        self.access_token = None
        self.refresh_token = None
        self.token_type = None

    def set_token(self, grant_type="client_credentials"):
        """ 액세스 토큰 정보를 만들기 위한 메서드 입니다. """

        token_api_path = "/v1/oauth2/access_token"
        url_path = self.BASE_API_URL + token_api_path

        if grant_type == "client_credentials":
            data = {
                "client_id":self.CLIENT_ID,
                "client_secret":self.CLIENT_SECRET,
                "grant_type":grant_type
            }
        elif grant_type == "refresh_token":
            data = {
                "client_id":self.CLIENT_ID,
                "client_secret":self.CLIENT_SECRET,
                "grant_type":grant_type,
                "refresh_token":self.refresh_token
            }
        else:
            raise Exception("Unexpected grant_type")

        res = requests.post(url_path, data=data)
        result = res.json()
        self.access_token = result["access_token"]
        self.token_type = result["token_type"]
        self.refresh_token = result["refresh_token"]
        self.expire = result["expires_in"]
        return self.expire, self.access_token, self.refresh_token

    def get_token(self):
        """ 액세스 토큰 정볼를 받기 위한 메서드 입니다. """

        if self.access_token is not None:
            return self.access_token
        else:
            raise Exception("Need to set_token")

    def get_ticker(self, currency_type=None):
        """ 마지막 결제정보(Tick)를 구하는 메서드입니다. """

        
