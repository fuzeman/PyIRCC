import urllib2
from pyircc.spec import NotSupportedError, NotRegisteredError
from pyircc.support import SupportBase, check_support
from pyircc.util import get_xml, http_get, class_string_instance, http_post
import xml.etree.ElementTree as et

__author__ = 'Dean Gardiner'

SUPPORTED_VERSIONS = ('1.2',)


UNR_REGISTER_RESULT_OK = 0  # OK
UNR_REGISTER_RESULT_DECLINED = -1  # Registration was declined by device.


class DeviceControl_UNR(SupportBase):
    """DeviceControl UNR

    :ivar boolean force: Ignore method support limitations
    """
    def __init__(self, force=False, trace=False):
        SupportBase.__init__(self, force=force)
        self.trace = trace

        self._device = None
        self._deviceInfo = None

        #: ( string ) - UNR Version
        self.version = None

        #: ( `{ actionName: actionURL }` ) - Available action URLs
        self.actionUrls = {}

        self._headers = None

        #: ( string ) - Registered Device ID
        self.deviceId = None  # from register()

        #: ( bool ) - Device currently registered?
        self.registered = False

        #: ( :class:`pyircc.unr.UNR_SystemInformationResult` ) -
        #: System Information from :func:`DeviceControl_UNR.getSystemInformation`
        self.systemInformation = None  # from [getSystemInformation]

        #: ( [ :class:`pyircc.unr.UNR_RemoteCommand` ] ) -
        #: Available remote commands from :func:`DeviceControl_UNR.getRemoteCommandList`
        self.remoteCommands = None  # from [getRemoteCommandList]

        #: (boolean) - Has this control service been setup?
        self.available = False

    def _setup(self, device):
        """Setup the UNR control service. (*PRIVATE*)

        :ivar device.Device device: Connected Device
        """
        self._device = device
        self._deviceInfo = device.deviceInfo

        self.version = self._deviceInfo.unrVersion

        self.actionUrls = {}
        self._parseActionList()

        self.available = True

    @check_support
    def getSystemInformation(self):
        """Get device system information

        :raises: :class:`pyircc.spec.NotSupportedError`, :class:`NotImplementedError`
        """
        if self.trace:
            print ">>> getSystemInformation"

        if self.version == '1.2' or self.force:
            result = None
            try:
                result = http_get(self.actionUrls['getSystemInformation'], {})  # No headers to send yet.
            except urllib2.HTTPError, e:
                if self.trace:
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

        :raises: :class:`pyircc.spec.NotSupportedError`, :class:`NotImplementedError`
        """
        if self.trace:
            print ">>> register", name, registrationType, deviceId

        self.deviceName = name
        self.deviceId = deviceId

        if self.version == '1.2' or self.force:
            try:
                http_get(
                    self.actionUrls['register'],
                    self._getActionHeaders(),
                    name=name,
                    registrationType=registrationType,
                    deviceId=deviceId
                )
            except urllib2.HTTPError, e:
                if self.trace:
                    print e
                if e.code == 403:
                    return UNR_REGISTER_RESULT_DECLINED
                raise NotImplementedError()

            self.registered = True
            return UNR_REGISTER_RESULT_OK
        raise NotSupportedError()

    @check_support
    def getRemoteCommandList(self):
        """Get device remote commands

        :raises: :class:`pyircc.spec.NotSupportedError`, :class:`NotImplementedError`
        """
        if self.trace:
            print ">>> getRemoteCommandList"
        if self.version == '1.2' or self.force:
            result = None
            try:
                result = http_get(self.actionUrls['getRemoteCommandList'],
                                  self._getActionHeaders())
            except urllib2.HTTPError, e:
                if self.trace:
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
        raise NotSupportedError()

    @check_support
    def getText(self):
        """Get text from displayed text input screen, Returns None if there is no text input screen displayed

        :raises: :class:`pyircc.spec.NotSupportedError`, :class:`NotImplementedError`

        :returns: string or Null
        """
        if self.trace:
            print ">>> getText"
        if self.version == '1.2' or self.force:
            result = None
            try:
                result = http_get(self.actionUrls['getText'], self._getActionHeaders())
            except urllib2.HTTPError, e:
                if self.trace:
                    print e
                if e.code == 406:
                    return None
                raise NotImplementedError()

            if not result:
                raise NotImplementedError()

            xml = et.fromstring(result)

            return xml.text
        raise NotSupportedError()

    @check_support
    def sendText(self, text):
        """Send text to replace current text in displayed text input screen

       :raises: :class:`pyircc.spec.NotSupportedError`, :class:`NotImplementedError`

       :returns: boolean
       """
        if self.trace:
            print ">>> sendText"
        if self.version == '1.2' or self.force:
            try:
                http_get(self.actionUrls['sendText'], self._getActionHeaders(),
                                  text=text)
            except urllib2.HTTPError, e:
                if self.trace:
                    print e
                if e.code == 406:
                    return False
                raise NotImplementedError()

            return True
        raise NotSupportedError()

    @check_support
    def getStatus(self):
        """Get current view status

       :raises: :class:`pyircc.spec.NotSupportedError`, :class:`NotImplementedError`

       :returns: :class:`pyircc.unr.UNR_Status`
       """
        if self.trace:
            print ">>> getStatus"
        if self.version == '1.2' or self.force:
            result = None
            try:
                result = http_get(self.actionUrls['getStatus'], self._getActionHeaders())
            except urllib2.HTTPError, e:
                if self.trace:
                    print e
                raise NotImplementedError()

            if not result:
                raise NotImplementedError()

            xml = et.fromstring(result)

            statusList = {}
            for s in xml.iterfind('status'):
                status = UNR_Status(s)
                statusList[status.name] = status
            return statusList
        raise NotSupportedError()

    @check_support
    def getContentUrl(self):
        """Get web browser content url, Returns None if web browser isn't active.

       :raises: :class:`pyircc.spec.NotSupportedError`, :class:`NotImplementedError`

       :returns: :class:`pyircc.unr.UNR_ContentInformation` or None
       """
        if self.trace:
            print ">>> getContentUrl"
        if self.version == '1.2' or self.force:
            result = None
            try:
                result = http_get(self.actionUrls['getContentUrl'], self._getActionHeaders())
            except urllib2.HTTPError, e:
                if self.trace:
                    print e
                if e.code == 503:
                    return None
                raise NotImplementedError()

            if not result:
                raise NotImplementedError()

            xml = et.fromstring(result)

            return UNR_ContentInformation(xml)
        raise NotSupportedError()

    @check_support
    def sendContentUrl(self, url):
        """Set Web Browser content url

       :raises: :class:`pyircc.spec.NotSupportedError`, :class:`NotImplementedError`

       :returns: boolean
       """
        if self.trace:
            print ">>> sendContentUrl"
        if self.version == '1.2' or self.force:
            try:
                xRoot = et.Element('contentUrl')

                xUrl = et.SubElement(xRoot, 'url')
                xUrl.text = url

                post_data = et.tostring(xRoot)

                http_post(self.actionUrls['sendContentUrl'], self._getActionHeaders(), post_data)
            except urllib2.HTTPError, e:
                if self.trace:
                    print e
                raise NotImplementedError()

            return True
        raise NotSupportedError()

    @check_support
    def getContentInformation(self):
        """Get view content information

       :raises: :class:`pyircc.spec.NotSupportedError`, :class:`NotImplementedError`

       :returns: :class:`pyircc.unr.UNR_ContentInformation`
       """
        if self.trace:
            print ">>> getContentInformation"
        if self.version == '1.2' or self.force:
            result = None
            try:
                result = http_get(self.actionUrls['getContentInformation'], self._getActionHeaders())
            except urllib2.HTTPError, e:
                if self.trace:
                    print e
                if e.code == 503:
                    return None
                raise NotImplementedError()

            if not result:
                raise NotImplementedError()

            xml = et.fromstring(result)

            return UNR_ContentInformation(xml)
        raise NotSupportedError()

    def _getActionHeaders(self):
        """Get HTTP Action Headers"""
        if self._headers is None:
            if self.systemInformation is None:
                self.getSystemInformation()  # We need system information to build headers

            if self.deviceId is None:
                raise NotRegisteredError()

            self._headers = {
                'X-' + self.systemInformation.actionHeader: self.deviceId
            }
        return self._headers

    def _parseActionList(self):
        xml = get_xml(self._deviceInfo.unrCersActionUrl)

        for action in xml.iterfind("action"):
            name = action.get('name').replace('::', '_')

            self.supportedFunctions.append(name)
            if self.actionUrls.has_key(name):
                raise Exception()
            self.actionUrls[name] = action.get('url').replace(':80:80', ':80')  # TODO: what is happening here?


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
        return class_string_instance(self, [
            'name', 'generation', 'modelName',
            'area', 'language', 'country',
            'actionHeader',
            'supportedSources',
            'supportedContents',
            'supportedFunctions'
        ])

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
        return class_string_instance(self, ['newLines', 'name', 'type', 'value'])

    def __repr__(self):
        return self.__str__()

class UNR_Status():
    """:func:`DeviceControl_UNR.getStatus` Result Item

    :param xml_element: Result Element Tree
    """
    def __init__(self, xml_element):
        self.name = xml_element.get('name')

        _statusItem = xml_element.find('statusItem')
        if _statusItem is not None:
            if _statusItem.get('field') == 'source':
                self.source = _statusItem.get('value')

    def __str__(self):
        return class_string_instance(self, ['name', 'source'])

    def __repr__(self):
        return self.__str__()

class UNR_ContentInformation():
    """Content Information Result Item

    :param xml_element: Result Element Tree
    """
    def __init__(self, xml_element):

        _url = xml_element.find('url')
        if _url is not None:
            self.url = _url.text

        self.info = {}

        if xml_element.tag == 'contentInformation':
            _contentInformation = xml_element
        else:
            _contentInformation = xml_element.find('contentInformation')

        if _contentInformation is not None:
            for i in _contentInformation.iterfind('infoItem'):
                field = i.get('field')
                value = i.get('value')
                if field is not None and value is not None:
                    self.info[field] = value

    def __str__(self):
        return class_string_instance(self, ['url', 'info'])

    def __repr__(self):
        return self.__str__()