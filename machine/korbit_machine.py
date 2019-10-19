import time
import requests
import configparser

from machine.base_machine import Machine

class KorbitMachine:
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
        if currency_type is None:
            raise Exception("Need to currency_type")

        time.sleep(1)

        params = {"currency_pair":currency_type}
        ticker_api_path = "/v1/ticker/detailed"
        url_path = self.BASE_API_URL + ticker_api_path
        res = requests.get(url_path, params=params)
        response_json = res.json()
        result = {}
        result["timstamp"] = str(response_json["timestamp"])
        result["last"] = response_json["last"]
        result["bid"] = response_json["bid"]
        result["ask"] = response_json["ask"]
        result["high"] = response_json["high"]
        result["low"] = response_json["low"]
        result["volume"] = response_json["volume"]
        return result

    def get_filled_orders(self, currency_type=None, per="minute"):
        """ 채결 정보를 구하는 메서드 입니다. """

        if currency_type is None:
            raise Exception("Need to currency_type")
        time.sleep(1)
        params = {"currency_pair":currency_type, "time":per}
        orders_api_path = "/v1/transactions"
        url_path = self.BASE_API_URL + orders_api_path
        res = requests.get(url_path, params=params)
        result = res.json()
        return result

    def get_wallet_status(self):
        """ 사용자의 지갑정보를 조회하는 메서드 입니다. """

        time.sleep(1)
        wallet_status_api_path = "/v1/user/balances"
        url_path = self.BASE_API_URL + wallet_status_api_path
        if self.access_token is None:
            self.set_token()
        headers = {"Authorization":"Bearer " + self.access_token}
        res = requests.get(url_path, headers=headers)
        result = res.json()
        wallet_status = {}
        for currency in self.TRADE_CURRENCY_TYPE:
            wallet_status[currency] = {}
            wallet_status[currency]["available"] = result[currency]["available"]
            wallet_status[currency]["trade_in_use"] = float(result[currency]["trade_in_use"])
            wallet_status[currency]["withdrawal_in_use"] = float(result[currency]["withdrawal_in_use"])
            wallet_status[currency]["balance"] = float(result[currency]["trade_in_use"]) + float(result[currency]["withdrawal_in_use"])
            
        return wallet_status

    def buy_order(self, currency_type: str, price: str, qty: str,
                  order_type="limit"):
        """ 매수 주문 실행.
        지정가 거래 지원 
        price : 1개 수량 주문 원화 (krw) 값
        qty : 주문 수량
        """

        time.sleep(1)
        if currency_type is None or price is None or qty is None:
            raise Exception("Need to param")
        buy_order_api_path = "/v1/user/orders/buy"
        url_path = self.BASE_API_URL + buy_order_api_path
        if self.access_token is None:
            self.set_token()
        headers = {"Authorization":"Bearer " + self.access_token}
        data = {
            "currency_pair":currency_type, "type":order_type,
            "price":price, "coin_amount":qty,
            "nonce":self.get_nonce()
        }
        res = requests.post(url_path, headers=headers, data=data)
        result = res.json()
        return result

    def sell_order(self, currency_type: str, price: str, qty: str,
                   order_type="limit"):
        """ 매도 주문 실행 메소드 

        price : 1개 주문 수량 원화
        qty : 주문 수량
        """
        time.sleep(1)
        if price is None or qty is None or currency_type is None:
            raise Exception("Need to params")
        if order_type != "limit":
            raise Exception("check order type")
        sell_order_api_path = "/v1/user/orders/sell"
        url_path = self.BASE_API_URL + sell_order_api_path
        if self.access_token is None:
            self.set_token()
        headers = {"Authorization":"Bearer " + self.access_token}
        data = {
            "currency_pair":currency_type, "type":order_type,
            "price":price, "coin_amount":qty,
            "nonce":self.get_nonce()
        }
        res = requests.post(url_path, headers=headers, data=data)
        result = res.json()
        return result

    def get_nonce(self):
        return str(int(time.time()))