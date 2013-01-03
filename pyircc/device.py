from pyircc import s2mtv, unr, ircc, rdis
from pyircc.spec import SONY_XML_SCHEMA_AV as S_AV
from pyircc.util import get_xml

__author__ = 'Dean Gardiner'


class Device():
    """Control Device"""

    def __init__(self, force=False):
        #: (:class:`pyircc.device.DeviceInfo`) Device Information
        self.deviceInfo = DeviceInfo()

        #: (:class:`pyircc.ircc.DeviceControl_IRCC`) IRCC Service
        self.ircc = ircc.DeviceControl_IRCC(force=force)

        #: (:class:`pyircc.unr.DeviceControl_UNR`) UNR Service
        self.unr = unr.DeviceControl_UNR(force=force)

        #: (:class:`pyircc.s2mtv.DeviceControl_S2MTV`) S2MTV Service
        self.s2mtv = s2mtv.DeviceControl_S2MTV(force=force)

        #: (:class:`pyircc.s2mtv.DeviceControl_RDIS`) RDIS Service
        self.rdis = rdis.DeviceControl_RDIS(force=force)

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
            device.unr._setup(device)

        # IRCC
        if device.deviceInfo.irccVersion in ircc.SUPPORTED_VERSIONS and\
           irccServiceDescURL is not None and\
           irccServiceControlURL is not None:
            device.ircc._setup(device, irccServiceDescURL, irccServiceControlURL)

        # S2MTV
        if device.deviceInfo.s2mtvVersion in s2mtv.SUPPORTED_VERSIONS:
            device.s2mtv._setup(device)

        # RDIS
        if device.deviceInfo.rdisVersion in rdis.SUPPORTED_VERSIONS:
            device.rdis._setup(device)

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
        self.deviceInfo.rdisEntryPort = int(xRdisDevice.findtext(S_AV + 'X_RDIS_ENTRY_PORT'))

        xS2mtvDevice = xDevice.find(S_AV + 'X_S2MTV_DeviceInfo')
        self.deviceInfo.s2mtvVersion = xS2mtvDevice.findtext(S_AV + 'X_S2MTV_Version')
        self.deviceInfo.s2mtvBaseUrl = xS2mtvDevice.findtext(S_AV + 'X_S2MTV_BaseURL')
        if self.deviceInfo.s2mtvBaseUrl[-1] != '/':
            self.deviceInfo.s2mtvBaseUrl += '/'

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