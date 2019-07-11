import requests
import logging
import base64
import time
import os
from .objects import Resolve
from .exceptions import *


class CptchNet:

    """
    key*: your API key
    session: is instance of requests.Session
    headers: dict
    proxy: dict like '{ 'http': 'type://ip:port', 'https': 'type://ip:port' }'
    cookies: dict (optional if session did not set)
    max_retries: int - count tries to get Result from server
    delay: int - time (seconds) to sleep per try
    """

    #Service urls
    __serviceIn = 'https://cptch.net/in.php' #POST
    __serviceOut = 'https://cptch.net/res.php' #GET

    #Default attrs
    __key = None
    __session = None
    __headers = None
    __proxy = None
    __cookies = None
    __maxRetries = 10
    __sleep = 6
    __lastTaskId = None

    
    def __init__(self, key: int, **kwargs):
        #set methods
        setters = {
            'session': self.setSession,
            'headers': self.setHeaders,
            'proxy': self.setHeaders,
            'cookies': self.setCookies,
            'max_retries': self.setMaxRetries,
            'sleep':  self.setSleep
        }

        self.__requestExceptions = {
            'ERROR_WRONG_USER_KEY': WrongUserKey,
            'ERROR_KEY_DOES_NOT_EXIST': KeyDoesNotExist,
            'ERROR_ZERO_BALANCE': ZeroBalance,
            'ERROR_ZERO_CAPTCHA_FILESIZE': ZeroCaptchaFileZile,
            'ERROR_TOO_BIG_CAPTCHA_FILESIZE': TooBigCaptchaFileSize,
            'ERROR_UPLOAD': ErrorUpload,
            'ERROR_CAPTCHA_UNSOLVABLE': CaptchaUnsolvable,
            'ERROR_WRONG_CAPTCHA_ID': WrongCaptchaId,
        }

        self.setKey(key)
        for key, value in kwargs.items():
            if key not in setters:
                raise UnvailableArguments('Argument "{}" is not in available'.format(key))
            setters[key](value)


    def setKey(self, key: int):
        if type(key) is not str: 
            raise InvalidKeyType("Key must be a string type")
        self.__key = key

    def getKey(self) -> str:
        return self.__key

    def getSession(self) -> requests.Session():
        return self.__session

    def getLastTaskId(self) -> int:
        return self.__lastTaskId

    def setHeaders(self, headers: dict):
        if type(headers) is dict:
            self.__headers = headers
        else:
            return None

    def setSession(self, session):
        if session:
            if not isinstance(session, requests.Session):
                raise UnvailableArguments('Session must be instance of requests.Session', errors={ 'session': type(requests.Session()) })
            self.__session = session
        else:
            self.__session = requests.Session()

    def setMaxRetries(self, max_retries: int):
        if type(max_retries) is not int:
            raise UnvailableArguments('max_retries must be int type')
        self.__maxRetries = max_retries

    def setSleep(self, sleep: int):
        if type(sleep) is not int:
            raise UnvailableArguments('sleep must be int')
        self.__sleep = sleep

    def setProxy(self, proxy: dict):
        if type(proxy) is dict:
            assert ('http' not in proxy or 'https' not in proxy), "Proxy must be dict like '{ 'http': 'type://ip:port', 'https': 'type://ip:port' }'"
            self.__proxy = proxy
        else:
            self.__proxy = None

    def setCookies(self, cookies: dict):
        if type(cookies) is dict:
            self.__cookies = cookies
        else:
            self.__cookies = None


    def getBalance(self) -> float:
        payload = self.__getDefaultPayload().copy()
        payload['action'] = 'getbalance'
        with self.__session.post(self.__serviceOut, data=payload) as r:
            if r.status_code != 200:
                raise FailedConnection('Problem connection to service with status_code: {}'.format(r.status_code))
            try:
                data = r.json()
            except:
                logging.error('Can not resolve response as json')
                raise InvalidResponse('Can not resolve response as json')
            finally:
                if data['status'] != 1:
                    if self.__requestExceptions[data['request']]:
                        self.__requestExceptions[data['request']]()
                    else:
                        raise MainException('Problem connection to service with status_code: {}'.format(r.status_code))
                return float(data['request'])

    def resolveByImgUrl(self, url: str) -> Resolve:
        if type(url) is not str:
            raise UnvailableArguments('"Url" must be str type')
        dFile = self.__downloadImgFromUrl(url)
        img = base64.b64encode(dFile)
        payload = self.__preparePaylodResolveRequest(img)
        taskId = self.__postRequest(payload)
        resolve = Resolve()
        resolve.start_time = time.time()
        resolve.fileSize = len(dFile)
        resolve.taskId = taskId
        resolve.result = self.getResolveResult(taskId)
        return resolve

     
    def __resolveByImgFile(self, file: bytes) -> Resolve:
        assert (type(file) == bytes), 'File must be bytes type'
        img = base64.b64encode(file)
        resolve = Resolve()
        resolve.fileSize = len(file)  
        payload = self.__preparePaylodResolveRequest(img)
        resolve.taskId = self.__postRequest(payload)
        resolve.start_time = time.time()
        resolve.result = self.getResolveResult(resolve.taskId)
        resolve.end_time = time.time()
        resolve.total_time = resolve.end_time - resolve.start_time
        return resolve


    def resolveByImgPath(self, filePath) -> Resolve:
        assert (type(filePath) == str), 'FilePath must be str type'
        if os.path.getsize(filePath) > 100*100: #max filesize is 100 kbytes
            raise TooBigCaptchaFileSize('Max size of file is 100 kbytes, yours: {} kbytes'.format(os.path.getsize(filePath)))
        with open(filePath, 'rb') as f:
            return self.__resolveByImgFile(f.read())


    def resolveRecaptcha(self, googlekey: str, pageurl: str) -> str:
        assert (googlekey and pageurl and type(googlekey) is str and type(pageurl) is str), 'GoogleKey and PageUrl can not be empty, must be str type'
        payload = {
            'method': 'userrecaptcha',
            'googlekey': googlekey,
            'pageurl': pageurl
        }
        payload.update(self.__getDefaultPayload().copy())
        resolve = Resolve()
        resolve.taskId = self.__postRequest(payload)
        resolve.result = self.getResolveResult(resolve)
        return resolve



    def getResolveResult(self, task_id: int = None):
        if not task_id:
            task_id = self.__lastTaskId
        payload = self.__getDefaultPayload().copy()
        payload['action'] = 'get'
        payload['id'] = task_id
        step = 0
        while step <= self.__maxRetries:
            step += 1
            time.sleep(self.__sleep)
            response = self.__getRequest(payload)
            if response:
                return response
        raise RuntimeError('Failed connection to service, max retries exceed')

    
    def __preparePaylodResolveRequest(self, img: bytes) -> dict:
        assert (type(img) == bytes), 'Img must be bytes type'
        payload = {
            'body': img,
            'method': 'base64'
        }
        payload.update(self.__getDefaultPayload().copy())
        return payload

    
    def __getRequest(self, payload) -> str:
        with self.__session.get(self.__serviceOut, params=payload) as r:
            assert (r.status_code == 200), 'Failed to get img by url with status code: {}'.format(r.status_code)
            try:
                data = r.json() 
            except Exception as e:
                logging.error('Can not resolve response as json')
                raise ValueError('Failed to get json obj from response') from e
            if(data['request'] == 'CAPCHA_NOT_READY'):
                return False
            assert (data['status'] == 1), 'Failed to get result by task id: "{}"'.format(data['request'])
            return data['request']


    def __postRequest(self, data) -> str:
        with self.__session.post(self.__serviceIn, data=data) as r:
            assert (r.status_code == 200), 'Problem connection to service with status_code: {}'.format(r.status_code)
            try:
                data = r.json()
                print(data)
            except:
                logging.error('Can not resolve response as json')
            finally:
                # assert (data['status'] == 1), 'Failed to get response from service with error: "{}"'.format(data['request'])
                if data['status'] is not 1:
                    raise self.__requestExceptions[data['request']]()
                self.__lastTaskId = data['request']
                return data['request']

    
    def __downloadImgFromUrl(self, url) -> bytes:
        # try:
        with self.__session.get(url, headers=self.__headers, timeout=(10,10), proxies=self.__proxy, cookies=self.__cookies, stream=True) as r:
            assert (r.status_code == 200), 'Failed to get img by url with status code: {}'.format(r.status_code)
            if len(r.content) > 100*100: #max filesize is 100 kbytes
                raise TooBigCaptchaFileSize('Max size of file is 100 kbytes, yours: {} kbytes'.format(len(r.content)/100))
            return r.content
        # except Exception as e:
        #     logging.error('Can not connect to server: {}'.format(e))
        #     raise ValueError('Can not connect to server: {}'.format(e)) from e
            
                
    def __getDefaultPayload(self) -> dict:
        return {
            'key': self.__key,
            'json': 1,
            'soft_id': 93 #my reference id <3
        }     
              


