import urllib
import urllib2
import urlparse
from support import supported, SupportBase, NotSupportedError
from util import get_xml, url_query_join, http_get

__author__ = 'Dean Gardiner'

SUPPORTED_VERSIONS = ('1.2',)


UNR_REGISTER_RESULT_OK = 0  # OK
UNR_REGISTER_RESULT_DECLINED = -1  # Registration was declined by device.


class DeviceControl_UNR(SupportBase):
    def __init__(self, deviceInfo):
        SupportBase.__init__(self)
        self.deviceInfo = deviceInfo
        self.version = self.deviceInfo.unrVersion

        self.actionUrls = {}
        self._parseActionList()

        self.headers = {
            'X-CERS-DEVICE-ID': "PyIRCC:00-00-00-00-00-00",
            'X-CERS-DEVICE-INFO': "Android4.0.4/MediaRemoteForAndroid3.4.2/HTC Vision"
        }

        print "construct unr"

    @supported
    def register(self, name="PyIRCC", registrationType='initial', deviceId="PyIRCC:00-00-00-00-00-00"):
        print "register", name, registrationType, deviceId

        if self.version == '1.2':
            resultData = None
            try:
                resultData = http_get(
                    self.actionUrls['register'],
                    self.headers,
                    name=name,
                    registrationType=registrationType,
                    deviceId=deviceId
                )
            except urllib2.HTTPError, e:
                print e
                if e.code == 403:
                    return UNR_REGISTER_RESULT_DECLINED
                else:
                    raise NotImplementedError()

            return UNR_REGISTER_RESULT_OK
        else:
            raise NotSupportedError()

    def _parseActionList(self):
        xml = get_xml(self.deviceInfo.unrCersActionUrl)

        for action in xml.iterfind("action"):
            name = action.get('name').replace('::', '_')

            self.supportedFunctions.append(name)
            if self.actionUrls.has_key(name):
                raise Exception()
            self.actionUrls[name] = action.get('url').replace(':80:80', ':80')