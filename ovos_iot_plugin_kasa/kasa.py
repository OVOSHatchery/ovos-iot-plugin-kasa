from pyHS100 import Discover, SmartPlug, SmartBulb
from time import sleep
import logging
from webcolors import name_to_rgb, rgb_to_name, hex_to_rgb
from colorsys import rgb_to_hsv, hsv_to_rgb

LOG = logging.getLogger("simpleKasa")


def hsv_to_name(h, s, v):
    rgb = hsv_to_rgb(h, s, v)
    try:
        return rgb_to_name(rgb)
    except ValueError: # color has no official name
        # TODO find closest named color
        return "unknown color name"


def name_to_hsv(name):
    r, g, b = name_to_rgb(name)
    return rgb_to_hsv(r, g, b)


def hex_to_hsv(hex_color):
    r, g, b = hex_to_rgb(hex_color)
    h, s, v = rgb_to_hsv(r, g, b)
    return h, s, v


def discover_devices():
    devices = []
    for ip, dev in Discover.discover().items():
        devices.append(dev)
    return devices


def find_host_from_device_name(devicename, timeout=3, attempts=3,
                               return_dev=False):
    """Discover devices in the network."""
    LOG.info("Trying to discover %s using %s attempts of %s seconds" %
             (devicename, attempts, timeout))
    for attempt in range(1, attempts):
        LOG.info("Attempt %s of %s" % (attempt, attempts))
        found_devs = Discover.discover(timeout=timeout).items()
        for ip, dev in found_devs:
            if dev.alias.lower() == devicename.lower():
                if return_dev:
                    return dev
                host = dev.host
                return host
    return None


# smart plugs


def get_plug_hw_info(ip=None, device=None):
    if ip is None and device is None:
        raise AttributeError("no device specified")
    if device is None:
        plug = SmartPlug(ip)
    else:
        plug = device
    return plug.hw_info


def get_plug_sys_info(ip=None, device=None):
    if ip is None and device is None:
        raise AttributeError("no device specified")
    if device is None:
        plug = SmartPlug(ip)
    else:
        plug = device
    return plug.get_sysinfo()


def plug_turn_off(ip=None, device=None):
    if ip is None and device is None:
        raise AttributeError("no device specified")
    if device is None:
        plug = SmartPlug(ip)
    else:
        plug = device
    return plug.turn_off()


def plug_turn_on(ip=None, device=None):
    if ip is None and device is None:
        raise AttributeError("no device specified")
    if device is None:
        plug = SmartPlug(ip)
    else:
        plug = device
    return plug.turn_on()


def get_plug_state(ip=None, device=None):
    if ip is None and device is None:
        raise AttributeError("no device specified")
    if device is None:
        plug = SmartPlug(ip)
    else:
        plug = device
    return plug.state


def get_plug_current_consumption(ip=None, device=None):
    if ip is None and device is None:
        raise AttributeError("no device specified")
    if device is None:
        plug = SmartPlug(ip)
    else:
        plug = device
    return plug.get_emeter_realtime()


def get_plug_daily_consumption(ip=None, device=None, year=None, month=None):
    if ip is None and device is None:
        raise AttributeError("no device specified")
    if device is None:
        plug = SmartPlug(ip)
    else:
        plug = device
    return plug.get_emeter_daily(year=year, month=month)


def get_plug_monthly_consumption(ip=None, device=None, year=None):
    if ip is None and device is None:
        raise AttributeError("no device specified")
    if device is None:
        plug = SmartPlug(ip)
    else:
        plug = device
    return plug.get_emeter_monthly(year=year)


def plug_led(ip=None, device=None, state=True):
    if ip is None and device is None:
        raise AttributeError("no device specified")
    if device is None:
        plug = SmartPlug(ip)
    else:
        plug = device
    plug.led = state


def plug_led_on(ip=None, device=None):
    plug_led(ip, device, True)


def plug_led_off(ip=None, device=None):
    plug_led(ip, device, False)


def plug_reboot(ip=None, device=None):
    if ip is None and device is None:
        raise AttributeError("no device specified")
    if device is None:
        plug = SmartPlug(ip)
    else:
        plug = device
    # TODO Turn off, check state, when off, turn on maybe even with an
    # optional time to off?
    plug_turn_off(device=plug)
    # state = get_plug_state(device=plug)
    sleep(1)
    plug_turn_on(device=plug)


# smart bulbs


def get_bulb_hw_info(ip=None, device=None):
    if ip is None and device is None:
        raise AttributeError("no device specified")
    if device is None:
        bulb = SmartBulb(ip)
    else:
        bulb = device
    return bulb.hw_info


def get_bulb_sys_info(ip=None, device=None):
    if ip is None and device is None:
        raise AttributeError("no device specified")
    if device is None:
        bulb = SmartBulb(ip)
    else:
        bulb = device
    return bulb.get_sysinfo()


def bulb_turn_off(ip=None, device=None):
    if ip is None and device is None:
        raise AttributeError("no device specified")
    if device is None:
        bulb = SmartBulb(ip)
    else:
        bulb = device
    return bulb.turn_off()


def bulb_turn_on(ip=None, device=None):
    if ip is None and device is None:
        raise AttributeError("no device specified")
    if device is None:
        bulb = SmartBulb(ip)
    else:
        bulb = device
    return bulb.turn_on()


def get_bulb_state(ip=None, device=None):
    if ip is None and device is None:
        raise AttributeError("no device specified")
    if device is None:
        bulb = SmartBulb(ip)
    else:
        bulb = device
    return bulb.state


def get_bulb_current_consumption(ip=None, device=None):
    if ip is None and device is None:
        raise AttributeError("no device specified")
    if device is None:
        bulb = SmartBulb(ip)
    else:
        bulb = device
    return bulb.get_emeter_realtime()


def get_bulb_daily_consumption(ip=None, device=None, year=None, month=None):
    if ip is None and device is None:
        raise AttributeError("no device specified")
    if device is None:
        bulb = SmartBulb(ip)
    else:
        bulb = device
    return bulb.get_emeter_daily(year=year, month=month)


def get_bulb_monthly_consumption(ip=None, device=None, year=None):
    if ip is None and device is None:
        raise AttributeError("no device specified")
    if device is None:
        bulb = SmartBulb(ip)
    else:
        bulb = device
    return bulb.get_emeter_monthly(year=year)


def set_bulb_brightness(ip=None, device=None, percentage=100):
    percentage = int(percentage)
    if percentage > 100:
        percentage = 100
    if percentage < 0:
        percentage = 0

    if ip is None and device is None:
        raise AttributeError("no device specified")
    if device is None:
        bulb = SmartBulb(ip)
    else:
        bulb = device
    if bulb.is_dimmable:
        bulb.brightness = percentage


def get_bulb_brightness(ip=None, device=None):
    if ip is None and device is None:
        raise AttributeError("no device specified")
    if device is None:
        bulb = SmartBulb(ip)
    else:
        bulb = device
    return bulb.brightness


def set_bulb_color_temperature(ip=None, device=None, value=3000):
    value = int(value)
    if value > 100:
        value = 100
    if value < 0:
        value = 0

    if ip is None and device is None:
        raise AttributeError("no device specified")
    if device is None:
        bulb = SmartBulb(ip)
    else:
        bulb = device
    if bulb.is_variable_color_temp:
        bulb.color_temp = value


def get_bulb_color_temperature(ip=None, device=None):
    if ip is None and device is None:
        raise AttributeError("no device specified")
    if device is None:
        bulb = SmartBulb(ip)
    else:
        bulb = device
    return bulb.color_temp


def set_bulb_color(ip=None, device=None, hex_color=None, color_name=None):
    if hex_color is None and color_name is None:
        raise AttributeError("no color specified")
    if hex_color is None:
        h, s, v = name_to_hsv(color_name)
    else:
        h, s, v = hex_to_hsv(hex_color)
    set_bulb_hsv(ip, device, h, s, v)
    return color_name


def set_bulb_hsv(ip=None, device=None, hue=0.5, saturation=1, value=255):
    if ip is None and device is None:
        raise AttributeError("no device specified")

    hue, saturation, value = hsv_to_tplink_hsv(hue, saturation, value)

    if device is None:
        bulb = SmartBulb(ip)
    else:
        bulb = device
    if bulb.is_color:
        bulb.hsv = (hue, saturation, value)


def tplink_hsv_to_hsv(h, s, v):
    # 0 < h < 360 <- tplink
    # 0 < h < 1 <- colorsys hsv
    h = h / 360
    # 0 < h < 100 <- tplink
    # 0 < h < 1 <- colorsys
    s = s / 100
    # 0 < v < 100 <- tplink
    # 0 < v < 255 <- colorsys hsv
    v = v / 100 * 255
    return h, s, int(v)


def hsv_to_tplink_hsv(h, s, v):
    # 0 < h < 360 <- tplink
    # 0 < h < 1 <- colorsys hsv
    h = h * 360
    # 0 < h < 100 <- tplink
    # 0 < h < 1 <- colorsys
    s = s * 100
    # 0 < v < 100 <- tplink
    # 0 < v < 255 <- colorsys hsv
    v = v * 100 / 255
    return int(h), int(s), int(v)


def get_bulb_hsv(ip=None, device=None):
    if ip is None and device is None:
        raise AttributeError("no device specified")
    if device is None:
        bulb = SmartBulb(ip)
    else:
        bulb = device
    if bulb.is_color:
        return bulb.hsv


def get_bulb_color_name(ip=None, device=None):
    if ip is None and device is None:
        raise AttributeError("no device specified")
    if device is None:
        bulb = SmartBulb(ip)
    else:
        bulb = device
    if bulb.is_color:
        h, s, v = bulb.hsv
        return hsv_to_name(h, s, v)
    return "unknown color"
