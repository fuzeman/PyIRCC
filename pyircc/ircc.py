from pysimplesoap.client import SoapClient, SoapFault
from pyircc.support import SupportBase, check_support
from pyircc.unr import UNR_RemoteCommand
from pyircc.util import get_xml, http_get
from pyircc.spec import UPNP_XML_SCHEMA_SERVICE as S_SER, SONY_UPNP_URN_IRCC, NotSupportedError, InvalidArgumentError

__author__ = 'Dean Gardiner'

SUPPORTED_VERSIONS = ('1.0',)


class DeviceControl_IRCC(SupportBase):
    """DeviceControl IRCC

    :ivar boolean force: Ignore method support limitations
    """

    def __init__(self, force=False):
        SupportBase.__init__(self, force=force)

        self._device = None
        self._deviceInfo = None

        #: ( string ) - IRCC Version
        self.version = None

        self._controlUrl = None
        self._client = None

        #: (`{actionName: {argumentName: argumentDirection}}`) - Available Actions
        self.actionInfo = {}

        #: (boolean) - Has this control service been setup?
        self.available = False

    def _setup(self, device, descriptionUrl, controlUrl):
        """Setup the IRCC control service. (*PRIVATE*)

        :ivar device.Device device: Connected Device
        :ivar string descriptionUrl: IRCC Service Description URL
        :ivar string controlUrl: IRCC Service Control URL
        """
        self._device = device
        self._deviceInfo = device.deviceInfo
        self.version = self._deviceInfo.irccVersion

        self._controlUrl = controlUrl

        self._parseDescription(descriptionUrl)

        self.available = True

    def _load(self):
        if self._device.unr.remoteCommands is None:
            if not self._device.unr.isFunctionSupported(self._device.unr.getRemoteCommandList):
                print "'getRemoteCommandList' not supported"
                raise NotSupportedError()
            self._device.unr.getRemoteCommandList()

        if self._client is None and self._device.unr.remoteCommands:
            self._client = SoapClient(
                location=self._controlUrl,
                action=SONY_UPNP_URN_IRCC,
                namespace=SONY_UPNP_URN_IRCC,
                soap_ns='soap', ns=False
            )

    @check_support
    def sendIRCC(self, codeName):
        """Send Remote Command

        :param codeName: Command Name
        :type codeName: string

        :raises: :class:`pyircc.spec.InvalidArgumentError`, NotImplementedError
        """
        print ">>> sendIRCC", codeName

        if codeName is None:
            raise InvalidArgumentError()

        if self.version == '1.0' or self.force:
            self._load()

            if not self._device.unr.remoteCommands.has_key(codeName):
                raise InvalidArgumentError()

            command = self._device.unr.remoteCommands[codeName]

            if command.type == UNR_RemoteCommand.TYPE_IRCC:
                try:
                    self._client.call('X_SendIRCC', IRCCCode=command.value)
                    return
                except SoapFault, e:
                    if e.faultcode == 's:Client' and e.faultstring == 'UPnPError':
                        raise InvalidArgumentError()

                    print e.faultcode, e.faultstring
                    raise NotImplementedError()
            else:
                http_get(command.value, self._device.unr._getActionHeaders())
                return
        raise NotSupportedError()

    def _parseDescription(self, descriptionUrl):
        xml = get_xml(descriptionUrl)
        if xml is None:
            raise Exception()

        xActionList = xml.find(S_SER + 'actionList')

        for xAction in xActionList.iterfind(S_SER + 'action'):
            actionName = xAction.findtext(S_SER + 'name')

            if self.actionInfo.has_key(actionName):  # Action already exists
                raise Exception()
            self.actionInfo[actionName] = {}

            xArgumentList = xAction.find(S_SER + 'argumentList')
            for xArgument in xArgumentList.iterfind(S_SER + 'argument'):
                argumentName = xArgument.findtext(S_SER + 'name')
                argumentDirection = xArgument.findtext(S_SER + 'direction')

                if self.actionInfo[actionName].has_key(argumentName):
                    raise Exception()
                self.actionInfo[actionName][argumentName] = argumentDirection

        for ak, action in self.actionInfo.items():
            funcName = ak[ak.index('X_') + 2:]
            funcName = funcName[0].lower() + funcName[1:]

            self.supportedFunctions.append(funcName)