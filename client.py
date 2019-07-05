import requests
import logging

class CptchNet:

    __serviceIn = 'https://cptch.net/in.php' #POST
    __serviceOut = 'https://cptch.net/res.php' #GET

    def __init__(self, key, proxy = None):
        assert (type(key) is str), "Key must be a string"
        self.key = key
        self.payload = {
            'key': key,
            'json': 1,
            'soft_id': 93 #my reference id <3
        }
        self.session = requests.Session()

    def getBalance(self):
        self.payload['action'] = 'getbalance'
        with self.session.post(self.__serviceOut, data=self.payload) as r:
            assert (r.status_code == 200), 'Problem connection to service with status_code: {}'.format(r.status_code)
            try:
                data = r.json()
            except Exception as e:
                logging.error('Can not resolve response as json')
            finally:
                assert (data['status'] == 1), 'Failed to get balance with error: "{}"'.format(data['request'])
                return float(data['request'])

    def resolveByImgUrl(self, url):
        pass

    def resolveByImgFile(self, file):
        pass

    
