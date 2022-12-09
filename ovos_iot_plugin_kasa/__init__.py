from ovos_PHAL_plugin_commonIOT.devices import GenericDevice, RGBWBulb, RGBBulb, Bulb
from ovos_utils.colors import Color
from ovos_iot_plugin_kasa.kasa import discover_devices, SmartPlug, SmartBulb, tplink_hsv_to_hsv, hsv_to_tplink_hsv


class KasaDevice(GenericDevice):
    def __init__(self, device_id, host, name="generic kasa device", raw_data=None):
        device_id = device_id or f"Kasa:{host}"
        raw_data = raw_data or {"name": name, "description": "uses tplink Kasa app"}
        super().__init__(device_id, host, name, raw_data)

    @property
    def as_dict(self):
        return {
            "host": self.host,
            "name": self.name,
            "model": self.product_model,
            "device_type": "generic tplink kasa device",
            "device_id": self.device_id,
            "state": self.is_on,
            "raw": self.raw_data
        }

    @property
    def product_model(self):
        return self.raw_data.get("model", "kasa")

    @property
    def device_id(self):
        return self.raw_data.get("deviceId")

    @property
    def name(self):
        return self.raw_data["alias"]


class KasaBulb(KasaDevice, Bulb):

    def __init__(self, device_id=None, host=None, name="light bulb", raw_data=None):
        device_id = device_id or f"KasaBulb:{host}"
        super().__init__(device_id, host, name, raw_data)
        self._timer = None
        self._bulb = SmartBulb(self.host)

    @property
    def as_dict(self):
        return {
            "host": self.host,
            "name": self.name,
            "model": self.product_model,
            "device_type": "light bulb",
            "device_id": self.device_id,
            "color": self.color.as_dict,
            "is_color": self.is_color,
            "is_dimmable": self.is_dimmable,
            "is_variable_color_temp": self.is_variable_color_temp,
            "brightness": self.brightness_255,
            "state": self.is_on,
            "raw": self.raw_data
        }

    @property
    def color(self):
        if self.is_off:
            return Color.from_name("black")
        if self._bulb.is_color:
            h, s, v = tplink_hsv_to_hsv(*self._bulb.hsv)
            return Color.from_hsv(h, s, v)
        return Color.from_name("white")

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

    @property
    def as_dict(self):
        return {
            "host": self.host,
            "name": self.name,
            "model": self.product_model,
            "device_type": "rgb light bulb",
            "device_id": self.device_id,
            "color": self.color.as_dict,
            "is_color": self.is_color,
            "is_dimmable": self.is_dimmable,
            "is_variable_color_temp": self.is_variable_color_temp,
            "brightness": self.brightness_255,
            "state": self.is_on,
            "raw": self.raw_data
        }


class KasaRGBWBulb(KasaRGBBulb, RGBWBulb):

    def __init__(self, device_id=None, host=None, name="rgbw light bulb", raw_data=None):
        device_id = device_id or f"KasaRGBWBulb:{host}"
        super().__init__(device_id, host, name, raw_data)

    @property
    def as_dict(self):
        return {
            "host": self.host,
            "name": self.name,
            "model": self.product_model,
            "device_type": "rgbw light bulb",
            "device_id": self.device_id,
            "color": self.color.as_dict,
            "is_color": self.is_color,
            "is_dimmable": self.is_dimmable,
            "is_variable_color_temp": self.is_variable_color_temp,
            "brightness": self.brightness_255,
            "state": self.is_on,
            "raw": self.raw_data
        }


class KasaPlugin:
    def scan(self):
        for d in discover_devices():
            if isinstance(d, SmartBulb):
                if d.is_color:
                    yield KasaRGBWBulb(d.host, d.alias, dict(d.sys_info))
                else:
                    yield KasaBulb(d.host, d.alias, dict(d.sys_info))
            elif isinstance(d, SmartPlug):
                # TODO
                pass

    def get_device(self, ip):
        for device in self.scan():
            if device.host == ip:
                return device
        return None


if __name__ == '__main__':
    from pprint import pprint
    from time import sleep

    plug = KasaPlugin()

    for device in plug.scan():
        pprint(device.as_dict)
        device.toggle()
        exit()
        # print(device.is_off, device.is_on)
        # device.turn_on()
        # device.set_high_brightness()
        device.change_color("cyan")
        # device.blink()
        # device.red_blue_cross_fade()
        sleep(30)
        device.reset()

    # bulb = get_device('192.168.1.64')
    # bulb.color_cycle()
    # sleep(60)
    # bulb.reset()
