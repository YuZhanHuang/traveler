class TravelerError(Exception):
    """
    Base error
    """

    def __init__(self, message='TravelerError'):
        super().__init__(message)


class BaseError(Exception):
    def __init__(self, msg=None, error_code=50000):
        Exception.__init__(self)
        self.code = 500  # http status code
        self.error_code = error_code  # customize code
        self.error_msg = msg

    def to_dict(self):
        return {'code': self.error_code, 'message': self.error_msg}


class APIError(TravelerError):
    """
    :message 錯誤的詳細描述信息
    :type: 錯誤類型
            - invalid_request_error
            - api_error
            - channel_error
            - connection_time_out
            - unexpected_error
            - request_error
            - parse_error

    :code 錯誤碼，由第三方返回的錯誤代碼
    :param 發生錯誤時返回的出錯的參數名
    """
    status_code = 400
    type = 'invalid_request_error'
    message = ''
    code = '400'

    def __init__(self, msg=None, status=None, payload=None):
        if msg is None:
            msg = self.message
        if status is None:
            status = self.status_code
        self.status_code = status
        self.message = msg
        if payload is None:
            payload = {
                'failure_code': self.code,
                'failure_msg': self.message,
            }
        self.payload = payload
        super(APIError, self).__init__(self.message)

    def to_dict(self):
        return dict(
            type=self.type,
            message=self.message,
            code=self.code,
            payload=self.payload)


class ValidationError(APIError):
    """客户端錯誤"""
    code = 40001
    message = "參數錯誤"
    type = "invalid_request"