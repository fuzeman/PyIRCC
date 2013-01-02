from twisted.internet import reactor
from device import Device
from lib.PyUPnP import SSDP_MSearch, UPnP
from spec import SONY_UPNP_URN_IRCC
import unr

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

        c = Device.connect(device.location, service.SCPDURL, service.controlURL)

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