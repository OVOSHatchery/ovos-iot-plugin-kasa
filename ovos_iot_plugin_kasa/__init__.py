import time

from lingua_franca.util.colors import Color
from ovos_PHAL_plugin_commonIOT.opm.base import Sensor, IOTScannerPlugin, Plug
from ovos_PHAL_plugin_commonIOT.opm.lights import Bulb, RGBBulb, RGBWBulb

from ovos_iot_plugin_kasa.kasa import discover_devices, SmartPlug as _SP, SmartBulb as _SB, tplink_hsv_to_hsv, \
    hsv_to_tplink_hsv


class KasaDevice(Sensor):
    def __init__(self, device_id, host, name="generic kasa device", raw_data=None):
        device_id = device_id or f"Kasa:{host}"
        raw_data = raw_data or {"name": name, "description": "uses tplink Kasa app"}
        super().__init__(device_id, host, name, raw_data)


class KasaPlug(KasaDevice, Plug):

    def __init__(self, device_id=None, host=None, name="smart plug", raw_data=None):
        device_id = device_id or f"KasaPlug:{host}"
        super().__init__(device_id, host, name, raw_data)
        self._plug = _SP(self.host)


class KasaBulb(KasaDevice, Bulb):

    def __init__(self, device_id=None, host=None, name="light bulb", raw_data=None):
        device_id = device_id or f"KasaBulb:{host}"
        super().__init__(device_id, host, name, raw_data)
        self._timer = None
        self._bulb = _SB(self.host)

    @property
    def as_dict(self):
        data = super().as_dict
        data.update({
            "color": self.color.rgb255,
            "is_color": self.is_color,
            "is_dimmable": self.is_dimmable,
            "is_variable_color_temp": self.is_variable_color_temp,
            "brightness": self.brightness_255
        })
        return data

    @property
    def color(self):
        if self.is_off:
            return Color.from_rgb(0, 0, 0)
        if self._bulb.is_color:
            h, s, v = tplink_hsv_to_hsv(*self._bulb.hsv)
            return Color.from_hsv(h, s, v)
        return Color.from_rgb(255, 255, 255)

    @property
    def light_state(self):
        return self.raw_data["light_state"]

    @property
    def is_color(self):
        return self._bulb.is_color

    @property
    def is_dimmable(self):
        return self._bulb.is_dimmable

    @property
    def is_variable_color_temp(self):
        return self._bulb.is_variable_color_temp

    @property
    def is_on(self):
        return self._bulb.is_on

    @property
    def brightness(self):
        return self._bulb.brightness

    @property
    def color_temperatures(self):
        return self._bulb.color_temp

    @property
    def current_consumption(self):
        return self._bulb.get_emeter_realtime()

    @property
    def daily_consumption(self, year=None, month=None):
        return self._bulb.get_emeter_daily(year=year, month=month)

    @property
    def monthly_consumption(self, year=None):
        return self._bulb.get_emeter_monthly(year=year)

    # status change
    def turn_on(self):
        self._bulb.turn_on()

    def turn_off(self):
        self._bulb.turn_off()

    def change_brightness(self, value, percent=True):
        if not percent:
            raise NotImplementedError
        if self._bulb.is_dimmable:
            self._bulb.brightness = value

    def change_color_temperatures(self, value, percent=True):
        if not percent:
            raise NotImplementedError
        if self._bulb.is_variable_color_temp:
            self._bulb.color_temp = value

    def change_color(self, name):
        if isinstance(name, Color):
            if name.rgb == (0, 0, 0):
                self.turn_off()
            else:
                if self.is_off:
                    self.turn_on()
                if self._bulb.is_color:
                    self._bulb.hsv = hsv_to_tplink_hsv(*name.hsv)
        else:
            color = Color.from_name(name)
            self.change_color(color)


class KasaRGBBulb(KasaBulb, RGBBulb):

    def __init__(self, device_id=None, host=None, name="rgb light bulb", raw_data=None):
        device_id = device_id or f"KasaRGBBulb:{host}"
        super().__init__(device_id, host, name, raw_data)


class KasaRGBWBulb(KasaRGBBulb, RGBWBulb):

    def __init__(self, device_id=None, host=None, name="rgbw light bulb", raw_data=None):
        device_id = device_id or f"KasaRGBWBulb:{host}"
        super().__init__(device_id, host, name, raw_data)


class KasaPlugin(IOTScannerPlugin):
    def scan(self):
        for d in discover_devices():
            device_id = f"{d.alias}:{d.host}"
            try:
                raw = dict(d.sys_info)
            except:  # sometimes times out, next scan will pick it up
                continue
            raw["last_seen"] = time.time()
            if isinstance(d, _SB):
                if d.is_color:
                    yield KasaRGBWBulb(device_id, d.host, d.alias, raw_data=raw)
                else:
                    yield KasaBulb(device_id, d.host, d.alias, raw_data=raw)
            elif isinstance(d, _SP):
                yield KasaPlug(device_id, d.host, d.alias, raw_data=raw)

    def get_device(self, ip):
        for device in self.scan():
            if device.host == ip:
                return device
        return None


if __name__ == '__main__':
    from pprint import pprint
    from ovos_utils.messagebus import FakeBus
    from ovos_utils import wait_for_exit_signal


    def cb(device):
        pprint(device.as_dict)


    plug = KasaPlugin(FakeBus(), new_device_callback=cb, lost_device_callback=cb)
    plug.start()

    wait_for_exit_signal()
    # bulb = get_device('192.168.1.64')
    # bulb.color_cycle()
    # sleep(60)
    # bulb.reset()
