# -*- coding: utf-8 -*-
try:
    from json import JSONDecodeError
except ImportError:
    JSONDecodeError = ValueError


class BaseResponse(object):

    def __init__(self, response, data=None, json_output=True,
                 status_code=None, success_code=None, **kwargs):
        self.raw = response
        print(self.raw.content)
        self.data = data or (
            response.json() if json_output else response.content.decode('UTF-8')
        )
        self.status_code = status_code or response.status_code
        for k in kwargs:
            setattr(self, k, kwargs[k])
        self._compute_is_ok(success_code)

    def _compute_is_ok(self, success_code):
        if isinstance(success_code, dict):
            method = self.raw.request.method
            success_codes = success_code.get(method, [])
        else:
            success_codes = (
                success_code if isinstance(success_code, list) else
                [success_code]
            )

        self.is_ok = self.status_code in success_codes

    def __repr__(self):
        is_ok_str = 'OK' if self.is_ok else 'Failed'
        return '<{}: Status: {}>'.format(self.__class__.__name__, is_ok_str)


class OCSResponse(BaseResponse):
    """ Response class for OCS api methods """

    def __init__(self, response, json_output=True, success_code=None):
        data = None
        full_data = None
        meta = None

        if (success_code or json_output):
            try:
                full_data = response.json()
                meta = full_data['ocs']['meta']
                status_code = meta['statuscode']
                if json_output:
                    data = full_data['ocs']['data']
            except JSONDecodeError:
                data = {'message': 'Unable to parse JSON response'}
                status_code = -1

        super(OCSResponse, self).__init__(response, data=data,
                                          json_output=json_output,
                                          full_data=full_data,
                                          status_code=status_code,
                                          meta=meta,
                                          success_code=success_code)


class WebDAVResponse(BaseResponse):
    """ Response class for WebDAV api methods """

    def __init__(self, response, data=None, success_code=None, json_output=False):
        super(WebDAVResponse, self).__init__(response, data=data,
                                             json_output=json_output,
                                             success_code=success_code)
