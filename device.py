import ircc
from spec import SCHEMA_SONY_AV as S_AV
import unr
from util import get_xml

__author__ = 'Dean Gardiner'


class Device():
    def __init__(self):
        self.deviceInfo = DeviceInfo()

        self.ircc = None
        self.unr = None

    def connect(self, deviceDescriptionURL, irccServiceDescURL=None, irccServiceControlURL=None):
        print "Device.connect(", deviceDescriptionURL, ",", irccServiceDescURL, ",", irccServiceControlURL, ")"
        self._parseDeviceDescription(deviceDescriptionURL)

        if self.deviceInfo.irccVersion in ircc.SUPPORTED_VERSIONS and\
                irccServiceDescURL is not None and\
                irccServiceControlURL is not None:
            self.ircc = ircc.DeviceControl_IRCC(self.deviceInfo, irccServiceDescURL, irccServiceControlURL)

        if self.deviceInfo.unrVersion in unr.SUPPORTED_VERSIONS:
            self.unr = unr.DeviceControl_UNR(self.deviceInfo)

    def _parseDeviceDescription(self, deviceDescriptionURL):
        xml = get_xml(deviceDescriptionURL)
        if xml is None:
            raise Exception()

        xDevice = xml.find('{urn:schemas-upnp-org:device-1-0}device')

        xIrccDevice = xDevice.find(S_AV + 'X_IRCC_DeviceInfo')
        self.deviceInfo.irccVersion = xIrccDevice.findtext(S_AV + 'X_IRCC_Version')
        self.deviceInfo.irccCategories = []
        categoryList = xIrccDevice.find(S_AV + 'X_IRCC_CategoryList')
        if categoryList is not None:
            for irccCategory in categoryList.iterfind(S_AV + 'X_IRCC_Category'):
                self.deviceInfo.irccCategories.append(irccCategory.findtext(S_AV + 'X_CategoryInfo'))

        xUnrDevice = xDevice.find(S_AV + 'X_UNR_DeviceInfo')
        self.deviceInfo.unrVersion = xUnrDevice.findtext(S_AV + 'X_UNR_Version')
        self.deviceInfo.unrCersActionUrl = xUnrDevice.findtext(S_AV + 'X_CERS_ActionList_URL')

        xRdisDevice = xDevice.find(S_AV + 'X_RDIS_DeviceInfo')
        self.deviceInfo.rdisVersion = xRdisDevice.findtext(S_AV + 'X_RDIS_Version')
        self.deviceInfo.rdisSessionControl = bool(xRdisDevice.findtext(S_AV + 'X_RDIS_SESSION_CONTROL'))
        self.deviceInfo.rdisEntryPort = xRdisDevice.findtext(S_AV + 'X_RDIS_ENTRY_PORT')

        xS2mtvDevice = xDevice.find(S_AV + 'X_S2MTV_DeviceInfo')
        self.deviceInfo.s2mtvVersion = xS2mtvDevice.findtext(S_AV + 'X_S2MTV_Version')
        self.deviceInfo.s2mtvBaseUrl = xS2mtvDevice.findtext(S_AV + 'X_S2MTV_BaseURL')

        self.deviceInfo.maxBgmCount = int(xDevice.findtext(S_AV + 'X_MaxBGMCount'))
        self.deviceInfo.standardDmr = xDevice.findtext(S_AV + 'X_StandardDMR')


class DeviceInfo():
    def __int__(self):
        # IRCC
        self.irccVersion = None
        self.irccCategories = None

        # UNR / CERS
        self.unrVersion = None
        self.unrCersActionUrl = None

        #  RDIS
        self.rdisVersion = None
        self.rdisSessionControl = None
        self.rdisEntryPort = None

        # S2MTV
        self.s2mtvVersion = None
        self.s2mtvBaseUrl = None

        # Other
        self.maxBgmCount = None
        self.standardDmr = None