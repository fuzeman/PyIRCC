import urllib2
from support import SupportBase, NotSupportedError, check_support
from util import get_xml, http_get, class_string
import xml.etree.ElementTree as et

__author__ = 'Dean Gardiner'

SUPPORTED_VERSIONS = ('1.2',)


UNR_REGISTER_RESULT_OK = 0  # OK
UNR_REGISTER_RESULT_DECLINED = -1  # Registration was declined by device.


class NotRegisteredError(BaseException):
    pass


class DeviceControl_UNR(SupportBase):
    """DeviceControl UNR

    :ivar device.Device device: Connected Device
    :ivar boolean force: Ignore method support limitations
    """
    def __init__(self, device, force=False):
        SupportBase.__init__(self, force=force)
        self.device = device
        self.deviceInfo = device.deviceInfo

        #: ( string ) - UNR Version
        self.version = self.deviceInfo.unrVersion

        #: ( `{ actionName: actionURL }` ) - Available action URLs
        self.actionUrls = {}
        self._parseActionList()

        self.headers = None

        #: ( string ) - Registered Device ID
        self.deviceId = None  # from register()

        #: ( bool ) - Device currently registered?
        self.registered = False

        #: ( :class:`unr.UNR_SystemInformationResult` ) -
        #: System Information from :func:`DeviceControl_UNR.getSystemInformation`
        self.systemInformation = None  # from [getSystemInformation]

        #: ( [ :class:`unr.UNR_RemoteCommand` ] ) -
        #: Available remote commands from :func:`DeviceControl_UNR.getRemoteCommandList`
        self.remoteCommands = None  # from [getRemoteCommandList]

        print "construct unr"

    @check_support
    def getSystemInformation(self):
        """Get Device System Information

        :raises: :class:`support.NotSupportedError`, :class:`NotImplementedError`
        """
        print ">>> getSystemInformation"

        if self.version == '1.2' or self.force:
            result = None
            try:
                result = http_get(self.actionUrls['getSystemInformation'], {})  # No headers to send yet.
            except urllib2.HTTPError, e:
                print e
                raise NotImplementedError()

            xml = et.fromstring(result)
            if xml is None:
                return None

            self.systemInformation = UNR_SystemInformationResult(xml)
            return self.systemInformation
        raise NotSupportedError()

    @check_support
    def register(self, name="PyIRCC", registrationType='initial', deviceId="PyIRCC:00-00-00-00-00-00"):
        """Register with Device

        :param name: Control Name
        :type name: string

        :param registrationType: Control Registration Type
        :type registrationType: 'initial'

        :param deviceId: Control Device ID
        :type deviceId: string

        :raises: :class:`support.NotSupportedError`, :class:`NotImplementedError`
        """
        print ">>> register", name, registrationType, deviceId

        self.deviceName = name
        self.deviceId = deviceId

        if self.version == '1.2' or self.force:
            try:
                http_get(
                    self.actionUrls['register'],
                    self.getActionHeaders(),
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

            self.registered = True
            return UNR_REGISTER_RESULT_OK
        raise NotSupportedError()

    @check_support
    def getRemoteCommandList(self):
        """Get Device Remote Commands

        :raises: :class:`support.NotSupportedError`, :class:`NotImplementedError`
        """
        print ">>> getRemoteCommandList"
        if self.version == '1.2' or self.force:
            result = None
            try:
                result = http_get(self.actionUrls['getRemoteCommandList'],
                                  self.getActionHeaders())
            except urllib2.HTTPError, e:
                print e
                raise NotImplementedError()

            if not result:
                raise NotImplementedError()

            xml = et.fromstring(result)

            self.remoteCommands = {}
            for commandElement in xml.iterfind("command"):
                command = UNR_RemoteCommand(commandElement)
                self.remoteCommands[command.name] = command

            return self.remoteCommands

    def getActionHeaders(self):
        """Get HTTP Action Headers"""
        if self.headers is None:
            if self.systemInformation is None:
                self.getSystemInformation()  # We need system information to build headers

            if self.deviceId is None:
                raise NotRegisteredError()

            self.headers = {
                'X-' + self.systemInformation.actionHeader: self.deviceId
            }

            print "headers built"
        return self.headers

    def _parseActionList(self):
        xml = get_xml(self.deviceInfo.unrCersActionUrl)

        for action in xml.iterfind("action"):
            name = action.get('name').replace('::', '_')

            self.supportedFunctions.append(name)
            if self.actionUrls.has_key(name):
                raise Exception()
            self.actionUrls[name] = action.get('url').replace(':80:80', ':80')  # TODO: what is happening here?

            print "unr supported:", name


class UNR_SystemInformationResult():
    """:func:`DeviceControl_UNR.getSystemInformation` Result

    :param xml_element: Result Element Tree
    """
    def __init__(self, xml_element):
        self.name = xml_element.findtext('name')
        self.generation = xml_element.findtext('generation')
        self.modelName = xml_element.findtext('modelName')

        self.area = xml_element.findtext('area')
        self.language = xml_element.findtext('language')
        self.country = xml_element.findtext('country')

        self.actionHeader = xml_element.find('actionHeader').get('name')

        self.supportedSources = []
        for e in xml_element.find('supportSource').iterfind('source'):
            self.supportedSources.append(e.text.lower())

        self.supportedContents = []
        for e in xml_element.find('supportContentsClass').iterfind('class'):
            self.supportedContents.append(e.text.lower())

        self.supportedFunctions = []
        for e in xml_element.find('supportFunction').iterfind('function'):
            self.supportedFunctions.append(e.get('name').lower())

    def __str__(self):
        return class_string('UNR_SystemInformationResult',
                            name=self.name,
                            generation=self.generation,
                            modelName=self.modelName,
                            area=self.area,
                            languge=self.language,
                            country=self.country,
                            actionHeader=self.actionHeader,
                            supportedSources=self.supportedSources,
                            supportedContents=self.supportedContents,
                            supportedFunctions=self.supportedFunctions)

    def __repr__(self):
        return self.__str__()


class UNR_RemoteCommand():
    """:func:`DeviceControl_UNR.getRemoteCommandList` Result Item

    :param xml_element: Result Element Tree
    """
    TYPE_IRCC = 0
    TYPE_URL = 1

    def __init__(self, xml_element):
        self.name = xml_element.get('name')

        self.type = xml_element.get('type')
        if str(self.type).lower() == 'ircc':
            self.type = UNR_RemoteCommand.TYPE_IRCC
        elif str(self.type).lower() == 'url':
            self.type = UNR_RemoteCommand.TYPE_URL
        else:
            raise NotImplementedError()

        self.value = xml_element.get('value')
        if self.type == UNR_RemoteCommand.TYPE_URL:
            self.value = self.value.replace(':80:80', ':80')  # TODO: what is happening here?

    def __str__(self):
        return class_string('UNR_RemoteCommand',
                            newLines=False,
                            name=self.name,
                            type=self.type,
                            value=self.value)

    def __repr__(self):
        return self.__str__()