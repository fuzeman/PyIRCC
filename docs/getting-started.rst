Getting Started
=======================

1. Determine the UPnP IRCC-enabled device to connect to, We can use PyUPnP for this::

    SSDP_MSearch.search(cbFoundDevice=foundDevice, cbFinishedSearching=finishedSearching,
                        target='urn:schemas-sony-com:service:IRCC:1')
    
    def foundDevice(device):
        pass
    
    def finishedSearching(devices):
        device = devices[0]  # Just pick the first device
        service = d.get_service('schemas.sony.com/IRCC/1')
        
        connect_to(device, service)

2. Connect to the IRCC Device::

    def connect_to(device, service):
        irccDevice = Device.connect(device.location, service.SCPDURL, service.controlURL)

3. Register with the device::

    def connect_to(device, service):
        ...
        if irccDevice.register("My IRCC Controller") != unr.UNR_REGISTER_RESULT_OK:
            print "Registration Failed"
            return

4. Commands/Requests can now be sent to the device::

    def connect_to(device, service):
        ...
        irccDevice.ircc.sendIRCC('MuteOn')