
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
        
