__author__ = 'Dean Gardiner'


SUPPORTED_VERSIONS = ('1.0',)


class DeviceControl_IRCC():
    def __init__(self, deviceInfo, descriptionUrl, controlUrl):
        self.deviceInfo = deviceInfo

        print "construct ircc", descriptionUrl, controlUrl