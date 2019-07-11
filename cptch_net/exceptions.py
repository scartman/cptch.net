class MainException(Exception):
    def __init__(self, message: str, errors: dict = {}):
        super().__init__(message)
        self.errors = errors

class KeyDoesNotExist(MainException):
    pass

class WrongUserKey(MainException):
    pass

class ZeroBalance(MainException):
    def __init__(self):
        message = 'Out of balance. Please pays before resolve'
        super().__init__(message)

class ZeroCaptchaFileZile(MainException):
    pass

class TooBigCaptchaFileSize(MainException):
    pass

class ErrorUpload(MainException):
    pass

class CaptchaUnsolvable(MainException):
    pass

class WrongCaptchaId(MainException):
    pass

class UnvailableArguments(MainException):
    pass

class InvalidKeyType(TypeError):
    pass

class InvalidResponse(TypeError):
    pass

class FailedConnection(MainException):
    pass