# /usr/bin/env python3
import requests
from lxml import objectify


class FSAPI(object):
    RW_MODES = {
        0: "internet",
        1: "spotify",
        2: "music",
        3: "dab",
        4: "fm",
        5: "aux",
    }

    RO_MODES = {
        6: "dmr",
        7: "network",
    }

    PLAY_STATES = {
        0: "stopped",
        1: "unknown",
        2: "playing",
        3: "paused",
    }

    EQS = {
        0: "custom",
        1: "normal",
        2: "flat",
        3: "jazz",
        4: "rock",
        5: "movie",
        6: "classic",
        7: "pop",
        8: "news",
    }

    def __init__(self, fsapi_device_url, pin):
        self.pin = pin
        self.sid = None
        self.webfsapi = None
        self.fsapi_device_url = fsapi_device_url

        self.webfsapi = self.get_fsapi_endpoint()
        self.sid = self.create_session()

    def get_fsapi_endpoint(self):
        r = requests.get(self.fsapi_device_url)
        doc = objectify.fromstring(r.content)
        return doc.webfsapi.text

    def create_session(self):
        doc = self.call("CREATE_SESSION")
        return doc.sessionId.text

    def call(self, path, extra=None):
        if not self.webfsapi:
            raise Exception("No server found")

        if type(extra) is not dict:
            extra = dict()

        params = dict(pin=self.pin, sid=self.sid,)

        params.update(**extra)

        r = requests.get("%s/%s" % (self.webfsapi, path), params=params)
        #        print r.content
        return objectify.fromstring(r.content)

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.call("DELETE_SESSION")

    # Read-only ###############################################################

    @property
    def version(self):
        doc = self.call("GET/netRemote.sys.info.version")
        return doc.value.c8_array.text

    @property
    def play_status(self):
        doc = self.call("GET/netRemote.play.status")
        return self.PLAY_STATES.get(doc.value.u8)

    @property
    def play_info_artist(self):
        doc = self.call("GET/netRemote.play.info.artist")
        return doc.value.c8_array.text or ""

    @property
    def play_info_album(self):
        doc = self.call("GET/netRemote.play.info.album")
        return doc.value.c8_array.text or ""

    @property
    def play_info_track(self):
        doc = self.call("GET/netRemote.play.info.name")
        return doc.value.c8_array.text or ""

    @property
    def play_info_duration(self):
        doc = self.call("GET/netRemote.play.info.duration")
        return doc.value.u32.text or -1

    @property
    def play_info_text(self):
        doc = self.call("GET/netRemote.play.info.text")
        return doc.value.c8_array.text or ""

    @property
    def eq_bands(self):
        doc = self.call(
            "LIST_GET_NEXT/netRemote.sys.caps.eqBands/-1", dict(maxItems=100,)
        )
        if not doc.status == "FS_OK":
            return None

        ret = list()
        for index, item in enumerate(list(doc.iterchildren("item"))):
            temp = dict(band=index)
            for field in list(item.iterchildren()):
                temp[field.get("name")] = list(field.iterchildren()).pop()
            ret.append(temp)

        return ret

    @property
    def nav_list(self):
        doc = self.call(
            "LIST_GET_NEXT/netRemote.nav.list/-1", dict(maxItems=100,)
        )
        if not doc.status == "FS_OK":
            return list()

        ret = list()
        for item in list(doc.iterchildren("item")):
            temp = dict(key=item.get("key"))
            for field in list(item.iterchildren()):
                temp[field.get("name")] = list(field.iterchildren()).pop()
            ret.append(temp)

        return ret

    @property
    def notifications(self):
        doc = self.call("GET_NOTIFIES")
        if doc.status != "FS_OK":
            return None
        return {
            "node": doc.notify.get("node"),
            "value": list(doc.notify.value.iterchildren()).pop(),
        }

    @property
    def nav_status(self):
        doc = self.call("GET/netRemote.nav.status")
        return doc.value.u8

    @property
    def num_listitems(self):
        doc = self.call("GET/netRemote.nav.numitems")
        return doc.value.s32

    # Write-only ##############################################################

    def set_nav_selectitem(self, value):
        doc = self.call(
            "SET/netRemote.nav.action.selectItem", dict(value=int(value))
        )
        return doc.status == "FS_OK"

    nav_selectitem = property(None, set_nav_selectitem)

    def set_nav_action_navigate(self, value):
        doc = self.call(
            "SET/netRemote.nav.action.navigate", dict(value=int(value))
        )
        return doc.status == "FS_OK"

    nav_action_navigate = property(None, set_nav_selectitem)

    # Read-write ##############################################################
    def get_volume(self):
        doc = self.call("GET/netRemote.sys.audio.volume")
        return doc.value.u8.text

    def set_volume(self, value):
        doc = self.call("SET/netRemote.sys.audio.volume", dict(value=value))
        return doc.status == "FS_OK"

    volume = property(get_volume, set_volume)

    def get_friendly_name(self):
        doc = self.call("GET/netRemote.sys.info.friendlyName")
        return doc.value.c8_array.text

    def set_friendly_name(self, value):
        doc = self.call(
            "SET/netRemote.sys.info.friendlyName", dict(value=value)
        )
        return doc.status == "FS_OK"

    friendly_name = property(get_friendly_name, set_friendly_name)

    def get_mute(self):
        doc = self.call("GET/netRemote.sys.audio.mute")
        return bool(doc.value.u8)

    def set_mute(self, value=False):
        if type(value) is not bool:
            raise RuntimeError("Mute must be boolean")
        doc = self.call("SET/netRemote.sys.audio.mute", dict(value=int(value)))
        return doc.status == "FS_OK"

    mute = property(get_mute, set_mute)

    def get_power(self):
        doc = self.call("GET/netRemote.sys.power")
        return bool(doc.value.u8)

    def set_power(self, value=False):
        if type(value) is not bool:
            raise RuntimeError("Mute must be boolean, not `%s`" % type(value))

        doc = self.call("SET/netRemote.sys.power", dict(value=int(value)))
        return doc.status == "FS_OK"

    power = property(get_power, set_power)

    def get_mode(self):
        doc = self.call("GET/netRemote.sys.mode")
        modes = self.RW_MODES
        modes.update(self.RO_MODES)
        return modes.get(doc.value.u32)

    def set_mode(self, value):
        modes = {v: k for k, v in list(self.RW_MODES.items())}
        if value not in modes:
            raise RuntimeError("Not allowed to set mode to `%s`" % value)

        doc = self.call("SET/netRemote.sys.mode", dict(value=modes.get(value)))
        return doc.status == "FS_OK"

    mode = property(get_mode, set_mode)

    def get_eq_preset(self):
        doc = self.call("GET/netRemote.sys.audio.eqPreset")
        return self.EQS.get(doc.value.u8)

    def set_eq_preset(self, value):
        eqs = {v: k for k, v in list(self.EQS.items())}
        if value not in eqs:
            raise RuntimeError("Not allowed to set EQ to `%s`" % value)

        doc = self.call(
            "SET/netRemote.sys.audio.eqPreset", dict(value=eqs.get(value))
        )
        return doc.status == "FS_OK"

    eq_preset = property(get_eq_preset, set_eq_preset)

    def eq_custom(self, band, value=None):
        if type(value) is int:
            doc = self.call(
                "SET/netRemote.sys.audio.eqCustom.param%s" % band,
                dict(value=value,),
            )
            return doc.status == "FS_OK"

        doc = self.call("GET/netRemote.sys.audio.eqCustom.param%s" % band)
        return doc.value.s16

    def get_nav_state(self):
        doc = self.call("GET/netRemote.nav.state")
        return doc.value.u8

    def set_nav_state(self, value):
        doc = self.call("SET/netRemote.nav.state", dict(value=value))
        return doc.status == "FS_OK"

    nav_state = property(get_nav_state, set_nav_state)

    def get_play_control(self):
        doc = self.call("GET/netRemote.play.control")
        return doc.value.u8

    def set_play_control(self, value):
        doc = self.call("SET/netRemote.play.control", dict(value=value))
        return doc.status == "FS_OK"

    play_control = property(get_play_control, set_play_control)
