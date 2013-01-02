from pysimplesoap.client import SoapClient, SoapFault
from support import SupportBase, supported, NotSupportedError
from unr import UNR_RemoteCommand
from util import get_xml, http_get
from spec import UPNP_XML_SCHEMA_SERVICE as S_SER, SONY_UPNP_URN_IRCC

__author__ = 'Dean Gardiner'

SUPPORTED_VERSIONS = ('1.0',)


class InvalidArgumentError(BaseException):
    pass


class DeviceControl_IRCC(SupportBase):
    """DeviceControl IRCC

    :ivar device.Device device: Connected Device

    :ivar string descriptionUrl: IRCC Service Description URL
    :ivar string controlUrl: IRCC Service Control URL
    :ivar boolean force: Ignore method support limitations
    """

    def __init__(self, device, descriptionUrl, controlUrl, force=False):
        SupportBase.__init__(self, force=force)
        self.device = device
        self.deviceInfo = device.deviceInfo
        #: (`string`) - IRCC Version
        self.version = self.deviceInfo.irccVersion

        self.controlUrl = controlUrl

        self.client = None

        #: (`{actionName: {argumentName: argumentDirection}}`) - Available Actions
        self.actionInfo = {}
        self._parseDescription(descriptionUrl)

        print "construct ircc", descriptionUrl, controlUrl

    def _load(self):
        if self.device.unr.remoteCommands is None:
            if not self.device.unr.isFunctionSupported(self.device.unr.getRemoteCommandList):
                print "'getRemoteCommandList' not supported"
                raise NotSupportedError()
            self.device.unr.getRemoteCommandList()
            print "remoteCommands loaded"

        if self.client is None and self.device.unr.remoteCommands:
            self.client = SoapClient(
                location=self.controlUrl,
                action=SONY_UPNP_URN_IRCC,
                namespace=SONY_UPNP_URN_IRCC,
                soap_ns='soap', ns=False
            )
            print "client loaded"

    @supported
    def sendIRCC(self, codeName):
        """Send Remote Command

        :param codeName: Command Name
        :type codeName: string

        :raises: :class:`ircc.InvalidArgumentError`, NotImplementedError
        """
        print ">>> sendIRCC", codeName

        if codeName is None:
            return

        if self.version == '1.0':
            self._load()

            if not self.device.unr.remoteCommands.has_key(codeName):
                raise InvalidArgumentError()

            command = self.device.unr.remoteCommands[codeName]

            if command.type == UNR_RemoteCommand.TYPE_IRCC:
                try:
                    self.client.call('X_SendIRCC', IRCCCode=command.value)
                except SoapFault, e:
                    if e.faultcode == 's:Client' and e.faultstring == 'UPnPError':
                        raise InvalidArgumentError()

                    print e.faultcode, e.faultstring
                    raise NotImplementedError()
            else:
                result = http_get(command.value,
                                  self.device.unr.getActionHeaders())
                print result

    def _parseDescription(self, descriptionUrl):
        print "_parseDescription", descriptionUrl

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

        #pprint.pprint(self.actionInfo)

        for ak, action in self.actionInfo.items():
            funcName = ak[ak.index('X_') + 2:]
            funcName = funcName[0].lower() + funcName[1:]

            self.supportedFunctions.append(funcName)