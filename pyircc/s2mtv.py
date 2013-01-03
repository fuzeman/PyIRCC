import urllib2
import urlparse
from pyircc.spec import InvalidResponseError, NotSupportedError
from pyircc.support import SupportBase, check_support
from pyircc.util import get_xml, class_string, class_string_instance

__author__ = 'Dean Gardiner'


SUPPORTED_VERSIONS = ('1.0',)


class DeviceControl_S2MTV(SupportBase):

    def __init__(self, force=False):
        SupportBase.__init__(self, force=force)
        self._device = None
        self._deviceInfo = None

        #: ( string ) - S2MTV Version
        self.version = None

        self.available = False

    def _setup(self, device):
        self._device = device
        self._deviceInfo = device.deviceInfo

        self.supportedFunctions = ['getDeviceInfo']  # S2MTV has no action/command list

        self.version = self._deviceInfo.s2mtvVersion

        self.available = True

    @check_support
    def getDeviceInfo(self):
        print ">>> getDeviceInfo"

        url = urlparse.urljoin(self._deviceInfo.s2mtvBaseUrl, 'SSDgetDeviceInfo/')
        try:
            xml = get_xml(url)
        except urllib2.HTTPError, e:
            print e
            if e.code == 501:
                raise NotSupportedError()
            raise NotImplementedError()


        return S2MTV_DeviceInfo(xml)

class S2MTV_DeviceInfo():
    def __init__(self, xml_element):
        # Header
        _header = xml_element.find('header')
        self.headerVersion = int(_header.get('version'))
        if self.headerVersion == 1:
            if not _header.findtext('command') == 'SSDgetDeviceInfo':
                raise InvalidResponseError()
            self.headerCode = int(_header.findtext('code'))

        _sony = xml_element.find('sony')  # Only supporting 'sony' devices

        if _sony is not None:
            _product = _sony.find('product')

            if _product is not None:
                self.productId = _product.get('id')

                if self.productId == 'DTV':
                    self.product = S2MTV_Product_DTV(_product)


    def __str__(self):
        return class_string('S2MTV_DeviceInfo',
                            headerVersion=self.headerVersion,
                            headerCode=self.headerCode,
                            productId=self.productId,
                            product=self.product)

    def __repr__(self):
        return self.__str__()

class S2MTV_Product_DTV():
    def __init__(self, xml_element):
        self.referrerId = xml_element.findtext('referrer_id')

        self.features = []
        _features = xml_element.find('features')
        if _features is not None:
            for fe in list(_features):
                if fe.text.lower() == 'true':
                    self.features.append(fe.tag)

        self.iptv = None
        _iptv = xml_element.find('iptv_params')
        if _iptv is not None:
            self.iptv = S2MTV_IPTV_Params(_iptv)

    def __str__(self):
        return class_string('S2MTV_Product_DTV',
                            referrerId=self.referrerId,
                            features=self.features,
                            iptv=self.iptv)

    def __repr__(self):
        return self.__str__()


class S2MTV_IPTV_Params():
    def __init__(self, xml_element):
        self.build = xml_element.findtext('build')
        self.language = xml_element.findtext('language')

        self.rating = int(xml_element.findtext('rating'))
        self.ageRating = int(xml_element.findtext('age_rating'))
        self.mpaaRating = xml_element.findtext('mpaa_rating')
        self.ratingCountry = xml_element.findtext('rating_country')
        self.blockUnrated = xml_element.findtext('block_unrated')

        self.uiType = int(xml_element.findtext('ui_type'))

        self.drmTypes = xml_element.findtext('drm_types').upper().split(',')
        self.configTypes = xml_element.findtext('config_types').upper().split(',')
        self.audioTypes = xml_element.findtext('audio_types').upper().split(',')
        self.streamTypes = xml_element.findtext('stream_types').upper().split(',')
        self.videoTypes = xml_element.findtext('video_types').upper().split(',')
        self.containerTypes = xml_element.findtext('container_types').upper().split(',')
        self.displayTypes = xml_element.findtext('display_types').upper().split(',')
        self.metafileTypes = xml_element.findtext('metafile_types').upper().split(',')

        self.displayWidth = int(xml_element.findtext('display_width'))
        self.displayHeight = int(xml_element.findtext('display_height'))

    def __str__(self):
        return class_string_instance(self, [
            'build', 'language',
            'rating', 'ageRating', 'mpaaRating', 'ratingCountry', 'blockUnrated',
            'uiType',
            'drmTypes', 'configTypes', 'audioTypes', 'streamTypes', 'videoTypes',
            'containerTypes', 'displayTypes', 'metafileTypes',
            'displayWidth', 'displayHeight'
        ])

    def __repr__(self):
        return self.__str__()