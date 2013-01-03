__author__ = 'Dean Gardiner'

# XML Schema
SONY_XML_SCHEMA_AV = '{urn:schemas-sony-com:av}'
UPNP_XML_SCHEMA_SERVICE = '{urn:schemas-upnp-org:service-1-0}'

# UPnP URNs (Unique Resource Names)
SONY_UPNP_URN_IRCC = 'urn:schemas-sony-com:service:IRCC:1'

class InvalidResponseError(BaseException):
    pass

class InvalidArgumentError(BaseException):
    pass

class InvalidFunctionError(BaseException):
    pass


class NotSupportedError(BaseException):
    pass

class NotRegisteredError(BaseException):
    pass