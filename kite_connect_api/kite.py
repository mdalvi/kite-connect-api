import logging
import time

from kiteconnect import KiteConnect
from kiteconnect.exceptions import NetworkException, KiteException
from requests.exceptions import Timeout, ConnectionError


class Kite(object):
    def __init__(self, **kite_credentials):
        self.kite = KiteConnect(**kite_credentials, debug=True)
        self.sw_place_order = time.time()
        self.nb_place_order = 0

    def exec(self, func_name, *args, **kwargs):
        logger = logging.getLogger(__name__)
        response = None
        while True:
            try:
                if func_name == 'place_order':
                    if self.nb_place_order >= 5:
                        if (time.time() - self.sw_place_order) < 1.0:
                            time.sleep(max(0.0, 1.0 - (time.time() - self.sw_place_order)))
                        self.nb_place_order = 0

                    response = getattr(self.kite, func_name)(*args, **kwargs)
                    if self.nb_place_order == 0:
                        self.sw_place_order = time.time()
                    self.nb_place_order += 1
                else:
                    response = getattr(self.kite, func_name)(*args, **kwargs)
                break
            except ConnectionError as ex:
                logger.warning("requests.exceptions.ConnectionError @ [{}]".format(repr(ex)))
            except Timeout as ex:
                logger.warning("requests.exceptions.Timeout @ [{}]".format(repr(ex)))
            except NetworkException as ex:
                logger.warning("kiteconnect.exceptions.NetworkException @ [{}]".format(repr(ex)))
                time.sleep(1)
            except KiteException as ex:
                logger.warning("kiteconnect.exceptions.KiteException @ [{}]".format(repr(ex)))
                break
        return response
