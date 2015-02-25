import requests
import logging
from enum import Enum


# Logger settings
# logger = logging.getLogger('ipcam')
# formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
# hdlr.setFormatter(formatter)
# logger.addHandler(hdlr)
# logger.setLevel(logging.DEBUG)


# this list is meant to be accessed by the status code returned
# so the order matters,
# eg: ddns_status[0] returns 'No action', because status 0 means 'No action'
ddns_status = ['No Action',
               'It\'s connecting...',
               'Can\'t connect to the Server',
               'Dyndns Succeed',
               'DynDns Failed: Dyndns.org Server Error',
               'DynDns Failed: Incorrect User or Password',
               'DynDns Failed: Need Credited User',
               'DynDns Failed: Illegal Host Format',
               'DynDns Failed: The Host Does not Exist',
               'DynDns Failed: The Host Does not Belong to You',
               'DynDns Failed: Too Many or Too Few Hosts',
               'DynDns Failed: The Host is Blocked for Abusing',
               'DynDns Failed: Bad Reply from Server',
               'DynDns Failed: Bad Reply from Server',
               'Oray Failed: Bad Reply from Server',
               'Oray Failed: Incorrect User or Password',
               'Oray Failed: Incorrect Hostname',
               'Oray Succeed',
               'Reserved',
               'Reserved',
               'Reserved',
               'Reserved']


# this list is meant to be accessed by the status code returned
# so the order matters
upnp_status = ['No Action',
               'Succeed',
               'Device System Error',
               'Errors in Network Communication',
               'Errors in Chat with UPnP Device',
               'Rejected by UPnP Device, Maybe Port Conflict']


# this list is meant to be accessed by the status code returned
# so the order matters
alarm_status = ['No Alarm',
                'Motion Alarm',
                'Input Alarm']


class upnp(Enum):
    """Values to set UPnP settings"""
    disable = 0
    enable = 1


class api(Enum):
    """Device cgi APIs"""
    snapshot = 'snapshot.cgi'
    videostream = 'videostream.cgi'
    videostream_asf = 'videostream.asf'
    get_status = 'get_status.cgi'
    decoder_control = 'decoder_control.cgi'
    camera_control = 'camera_control.cgi'
    reboot = 'reboot.cgi'
    restore_factory = 'restore_factory.cgi'
    get_params = 'get_params.cgi'
    upgrade_firmware = 'upgrade_firmware.cgi'
    upgrade_htmls = 'upgrade_htmls.cgi'
    set_alias = 'set_alias.cgi'
    set_datetime = 'set_datetime.cgi'
    set_users = 'set_users.cgi'
    set_devices = 'set_devices.cgi'
    set_network = 'set_network.cgi'
    set_wifi = 'set_wifi.cgi'
    set_pppoe = 'set_pppoe.cgi'
    set_upnp = 'set_upnp.cgi'
    set_ddns = 'set_ddns.cgi'
    set_ftp = 'set_ftp.cgi'
    set_mail = 'set_mail.cgi'
    set_alarm = 'set_alarm.cgi'
    comm_write = 'comm_write.cgi'
    set_forbidden = 'set_forbidden.cgi'
    set_misc = 'set_misc.cgi'
    get_misc = 'get_misc.cgi'
    set_decoder = 'set_decoder.cgi'


class decoderctl(Enum):
    """
    Decoder control commands.
    """
    up = 0
    stop_up = 1  # stop ?
    down = 2
    stop_down = 3
    left = 4
    stop_left = 5
    right = 6
    stop_right = 7
    center = 25
    vertical_patrol = 26
    stop_vertical_patrol = 27
    horizon_patrol = 28
    stop_horizon_patrol = 29
    up_left = 90
    up_right = 91
    down_left = 92
    down_right = 93
    io_output_high = 94
    io_output_low = 95

def _parse_status_response(response):
    """
    Parses the reponse from get_status cgi call.
    :param response: (Required) String response from get_status cgi call.
    """
    import re
    d = dict()
    p = re.compile('var (\S+)=(\S+);')
    for i in response.text.splitlines():
        k, v = p.match(i).groups()
        d[k] = v
       
    for k, v in d.items():
        print '{} = {}'.format(k, v)
    
    return d
#     print response.url
#     print response.content
#     return dict(now='', alarm_status=alarm_status[0],
#                 ddns_status=ddns_status[0], upnp_status=upnp_status[0])


class IPCam(object):
    def __init__(self, ip, port='80', user='admin', password=''):
        self.ip = ip
        self.port = port
        self.user = user
        self.password = password
        
    def build_url(self, cmd, **request_params):
        url = 'http://{ip}:{port}/{cmd}'.format(ip=self.ip, port=self.port, cmd=cmd.value)
        return url

    def send_command(self, cmd, **request_params):
        """
        Performs the cgi command call.
        :param cmd: (Required) The cgi command to call.
        :param request_params: (Optional) key=value params to send to the cgi command
        """
        url = 'http://{ip}:{port}/{cmd}'.format(ip=self.ip, port=self.port, cmd=cmd.value)
        request_params['user'] = self.user
        request_params['pwd'] = self.password

        r = requests.get(url, params=request_params)
        print r.url
        if int(r.headers['content-length']) < 100:
            print r.content
            if r.content == 'error: illegal params.':
                raise Exception('Error: illegal params.')
            elif r.content == 'ok.':
                return True
        return r.content

    def snapshot(self, name=None):
        """
        Obtains a snapshot from the camera.
        Requires visitor permission.
        :param name: (Optional) Snapshot's name. Defaults to 'device_id(Alias)_Currenttime.jpg'
        """
        # Use "next_url" (for example:next_url=1
        # will name the photo: 1.jpg)
        params = dict(next_url=name)  if name else {}
        self.send_command(api.snapshot, **params)

    def videostream(self, resolution='640*480'):
        """
        Use server push mode to send videostream to Client APP.
        Requires visitor permission.
        :param resolution: (Optional) Output's resolution. Can be either 320*240 or 640*480.
        """
        params = dict(resolution=resolution, stream=True)
        return self.send_command(api.videostream)

    def videostream_asf(self, resolution='640*480'):
        """
        Ipcam send videostream of asf format, only support vlc player and mplayer.
        Requires visitor permission.
        :param resolution: (Optional) Output's resolution. Can be either 320*240 or 640*480.
        """
        self.send_command(api.videostream_asf, resolution=resolution)

    def move_a_little(self, direction):
        """
        
        add onestep=1
        """
        params = dict(command=direction)
        self.send_command(api.decoder_control, **params)

    def get_status(self):
        """
        Obtains the device status info.
        Requires visitor permission.
        """
        return _parse_status_response(self.send_command(api.get_status))

    def reboot(self):
        """
        Reboots device.
        Requires administrator permission.
        """
        self.send_command(api.reboot)

    def set_alias(self, alias):
        """
        Sets device alias.
        Requires administrator permission.
        :param alias: (Optional) New device alias. Defaults to 'IPCAM'.
        """
        self.send_command(api.set_alias, alias='IPCAM')

    def decoder_control(self, command):
        """
        Sends a control command to operate the device.
        Requires operator permission.
        :param command: (Required) Control command to operate the device.
        """
        self.send_command(api.decoder_control, command=command)

    def restore_factory(self):
        """
        Restores factory settings.
        Requires administrator permission.
        """
        self.send_command(api.restore_factory)

    def set_upnp(self, status):
        """
        Enables/Disables the UPnP settings.
        Requires administrator permission.
        :param status: (Required) upnp.enable or upnp.disable
        """
        self.send_command(api.set_upnp, enable=status)

    def set_resolution(self, resolution=8):
        """
        Controls camera sensor parameters.
        Requires operator permission.
        :param resolution: (Optional) Possible values: 8:QVGA or 32:VGA. Default QVGA.
        """
        self.send_command(api.camera_control, param=0, value=resolution)

    def set_brightness(self, brightness=125):
        """
        Controls camera sensor parameters.
        Requires operator permission.
        :param brightness: (Optional) From 0 to 255. Default 125.
        """
        self.send_command(api.camera_control, param=1, value=brightness)

    def set_contrast(self, contrast=3):
        """
        Controls camera sensor parameters.
        Requires operator permission.
        :param contrast: (Optional) From 0 to 6. Default 3.
        """
        self.send_command(api.camera_control, param=2, value=contrast)

    def set_mode(self, mode=1):
        """
        Controls camera sensor parameters.
        Requires operator permission.
        :param mode: (Optional) Possible values: 0:50hz, 1:60hz, 2:Outdoor. Default 50hz.
        """
        self.send_command(api.camera_control, param=3, value=mode)

    def flip_and_mirror(self, value=0):
        """
        Controls camera sensor parameters.
        Requires operator permission.
        :param flip_and_mirror: (Optional) Possible values: 0:default, 1:flip, 2:mirror, 3:flip+mirror. Default default.
        """
        self.send_command(api.camera_control, param="5", value=value)

    def upgrade_firmware(self):
        """
        Upgrades device firmware.
        Requires administrator permission.
        """
        # FIXME uses post
        self.send_command(api.upgrade_firmware)
