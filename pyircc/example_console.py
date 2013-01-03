#noinspection PyPackageRequirements
from twisted.internet import reactor
from pyircc.device import Device
from pyupnp import SSDP_MSearch, UPnP
from pyircc.spec import SONY_UPNP_URN_IRCC
from pyircc import unr

__author__ = 'Dean Gardiner'


def main():
    def foundDevice(device):
        print "foundDevice", device

    def finishedSearching(devices):
        irccCompatible = []
        x = 1
        for dk, dv in devices.items():
            UPnP.deviceDescription(dv)
            ircc_service = dv.get_service('schemas.sony.com/IRCC/1')
            if ircc_service:
                print '[' + str(x) + ']', dv.friendlyName
                print '\t\tControl URL:', ircc_service.controlURL
                print '\t\tSCPD URL:', ircc_service.SCPDURL
                x += 1
                irccCompatible.append((dv, ircc_service))

        if len(irccCompatible) == 0:
            reactor.stop()
            return

        n = selectService(len(irccCompatible))
        device, service = irccCompatible[n - 1]
        print device, service

        tr = None  # Temporary variable for results

        print

        c = Device.connect(device.location, service.SCPDURL, service.controlURL)
        print "ircc available:", c.ircc.available
        print "unr available:", c.unr.available
        print "s2mtv available", c.s2mtv.available

        # register
        if not c.unr.isFunctionSupported(c.unr.register):
            print "'register' not supported"
            return
        tr = c.unr.register("PyIRCC Console")
        if tr != unr.UNR_REGISTER_RESULT_OK:
            print "registration declined by device"
            return

        # Send IRCC Command (X_SendIRCC)
        if not c.ircc.isFunctionSupported(c.ircc.sendIRCC):
            print "'sendIRCC' not supported"
            return
        tr = c.ircc.sendIRCC('Tv_Radio')

        tr = c.s2mtv.getDeviceInfo()
        print str(tr)

        print 'rdis', c.rdis.sessionControlEnabled, c.rdis.entryPort

        print 'getText:', c.unr.getText()

#        print 'sendText result:', c.unr.sendText('hello world')

        print c.unr.getStatus()

        print 'getContentUrl:', c.unr.getContentUrl()

#        print c.unr.sendContentUrl('http://www.trademe.co.nz')

        print c.unr.getContentInformation()

    def selectService(numServices):
        deviceNum = None
        while deviceNum is None:
            n = raw_input('>>> ')
            try:
                n = int(n)
                if 0 < n <= numServices:
                    deviceNum = n
            except ValueError:
                continue
        return deviceNum

    print "searching..."
    SSDP_MSearch.search(
        cbFoundDevice=foundDevice, cbFinishedSearching=finishedSearching,
        target=SONY_UPNP_URN_IRCC, debug=True, stopDelay=5)

    reactor.run()

if __name__ == '__main__':
    main()