import ircc
from spec import SONY_XML_SCHEMA_AV as S_AV
import unr
from util import get_xml

__author__ = 'Dean Gardiner'


class Device():
    """Control Device"""

    def __init__(self):
        #: (:class:`device.DeviceInfo`) Device Information
        self.deviceInfo = DeviceInfo()

        #: (:class:`ircc.DeviceControl_IRCC`) IRCC Service
        self.ircc = None

        #: (:class:`unr.DeviceControl_UNR`) UNR Service
        self.unr = None

    @staticmethod
    def connect(deviceDescriptionURL, irccServiceDescURL=None, irccServiceControlURL=None):
        """Connect to device.

        :param deviceDescriptionURL: UPnP Device Description URL (device location)
        :type deviceDescriptionURL: string

        :param irccServiceDescURL: IRCC Service Description URL (service SCPDURL)
        :type irccServiceDescURL: string or None

        :param irccServiceControlURL: IRCC Service Control URL (service controlURL)
        :type irccServiceControlURL: string or None

        :rtype: Device
        """
        print "Device.connect(", deviceDescriptionURL, ",", irccServiceDescURL, ",", irccServiceControlURL, ")"

        device = Device()
        device._parseDeviceDescription(deviceDescriptionURL)

        # UNR / CERS
        if device.deviceInfo.unrVersion in unr.SUPPORTED_VERSIONS:
            device.unr = unr.DeviceControl_UNR(device)

        # IRCC
        if device.deviceInfo.irccVersion in ircc.SUPPORTED_VERSIONS and\
           irccServiceDescURL is not None and\
           irccServiceControlURL is not None:
            device.ircc = ircc.DeviceControl_IRCC(device, irccServiceDescURL, irccServiceControlURL)

        return device

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
    """Control Device Information"""

    def __init__(self):
        # IRCC
        self.irccVersion = None  #: IRCC Service Version *(X_IRCC_Version)*
        self.irccCategories = None #: IRCC Categories *(X_IRCC_Category)*

        # UNR / CERS
        self.unrVersion = None  #: UNR Service Version *(X_UNR_Version)*
        self.unrCersActionUrl = None  #: UNR Cers Action URL *(X_CERS_ActionList_URL)*

        #  RDIS
        self.rdisVersion = None  #: RDIS Service Version *(X_RDIS_Version)*
        self.rdisSessionControl = None  #: RDIS Session Control Enabled *(X_RDIS_SESSION_CONTROL)*
        self.rdisEntryPort = None  #: RDIS Session Entry Port *(X_RDIS_ENTRY_PORT)*

        # S2MTV
        self.s2mtvVersion = None  #: S2MTV Service Version *(X_S2MTV_Version)*
        self.s2mtvBaseUrl = None  #: S2MTV Base URL *(X_S2MTV_BaseURL)*

        # Other
        self.maxBgmCount = None  #: Max BGM Count *(X_MaxBGMCount)*
        self.standardDmr = None  #: Standard DMR Version *(X_StandardDMR)*