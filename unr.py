__author__ = 'Dean Gardiner'


SUPPORTED_VERSIONS = ('1.2',)


class DeviceControl_UNR():
    def __init__(self, deviceInfo):
        self.deviceInfo = deviceInfo
        print "construct unr"