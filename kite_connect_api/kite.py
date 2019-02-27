import logging
import time

from kiteconnect import KiteConnect
from kiteconnect.exceptions import NetworkException, KiteException, DataException
from requests.exceptions import Timeout, ConnectionError


class Kite(object):
    def __init__(self, **kite_credentials):
        self.kite = KiteConnect(**kite_credentials)
        self.sw_place_order = time.time()
        self.nb_place_order = 0

    def exec(self, func_name, *args, **kwargs):
        logger = logging.getLogger(__name__)
        response = None
        while True:
            try:
                if func_name == 'place_order':
                    if self.nb_place_order >= 5:
                        self.nb_place_order = 0
                        if (time.time() - self.sw_place_order) < 1.0:
                            time.sleep(max(0.0, 1.0 - (time.time() - self.sw_place_order)))

                    response = getattr(self.kite, func_name)(*args, **kwargs)
                    self.nb_place_order += 1
                    if self.nb_place_order == 0:
                        self.sw_place_order = time.time()
                else:
                    response = getattr(self.kite, func_name)(*args, **kwargs)
                break
            except ConnectionError as ex:
                logger.warning("requests.exceptions.ConnectionError @ [{}]".format(repr(ex)), exc_info=True)
            except Timeout as ex:
                logger.warning("requests.exceptions.Timeout @ [{}]".format(repr(ex)), exc_info=True)
            except NetworkException as ex:
                logger.warning("kiteconnect.exceptions.NetworkException @ [{}]".format(repr(ex)), exc_info=True)
                time.sleep(1)
            except DataException as ex:
                logger.warning("kiteconnect.exceptions.DataException @ [{}]".format(repr(ex)), exc_info=True)
                time.sleep(1)
            except KiteException as ex:
                logger.warning("kiteconnect.exceptions.KiteException @ [{}]".format(repr(ex)), exc_info=True)
                break
        return response
