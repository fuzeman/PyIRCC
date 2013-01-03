from pyircc.support import SupportBase, check_support

__author__ = 'Dean Gardiner'


SUPPORTED_VERSIONS = ('1.0',)


class DeviceControl_S2MTV(SupportBase):

    def __init__(self, device, force=False):
        SupportBase.__init__(self, force=force)
        self.device = device
        self.deviceInfo = device.deviceInfo

        #: ( string ) - S2MTV Version
        self.version = self.deviceInfo.s2mtvVersion

    @check_support
    def getDeviceInfo(self):
        print ">>> getDeviceInfo"