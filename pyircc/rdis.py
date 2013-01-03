from pyircc.support import SupportBase

__author__ = 'Dean Gardiner'


SUPPORTED_VERSIONS = ('1.0',)


class DeviceControl_RDIS(SupportBase):
    def __init__(self, force=False, trace=False):
        SupportBase.__init__(self, force=force)
        self.trace = trace

        self._device = None
        self._deviceInfo = None

        self.sessionControlEnabled = False
        self.entryPort = None

        #: ( string ) - RDIS Version
        self.version = None

        self.available = False

    def _setup(self, device):
        self._device = device
        self._deviceInfo = device.deviceInfo

        self.sessionControlEnabled = self._deviceInfo.rdisSessionControl
        self.entryPort = self._deviceInfo.rdisEntryPort

        self.supportedFunctions = []

        self.version = self._deviceInfo.rdisVersion

        self.available = True