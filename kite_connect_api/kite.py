import logging
import time

from kiteconnect import KiteConnect
from kiteconnect.exceptions import NetworkException, KiteException
from requests.exceptions import Timeout, ConnectionError


class Kite(object):
    def __init__(self, **kite_credentials):
        self.kite = KiteConnect(**kite_credentials, debug=True)
        self.sw_place_order = time.time()

    def exec(self, func_name, *args, **kwargs):
        logger = logging.getLogger(__name__)
        while True:
            try:
                if func_name == 'place_order':
                    if (time.time() - self.sw_place_order) < 0.2:
                        time.sleep(max(0.0, 0.2 - (time.time() - self.sw_place_order)))
                    self.sw_place_order = time.time()

                return getattr(self.kite, func_name)(*args, **kwargs)
            except ConnectionError as ex:
                logger.warning("requests.exceptions.ConnectionError @ [{}]".format(repr(ex)))
                time.sleep(0.1)
            except Timeout as ex:
                logger.warning("requests.exceptions.Timeout @ [{}]".format(repr(ex)))
                time.sleep(0.1)
            except NetworkException as ex:
                logger.warning("kiteconnect.exceptions.NetworkException @ [{}]".format(repr(ex)))
                time.sleep(1)
            except KiteException as ex:
                logger.warning("kiteconnect.exceptions.KiteException @ [{}]".format(repr(ex)))
                break
        return None
