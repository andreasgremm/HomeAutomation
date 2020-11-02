import pandas as pd


class prepareLightTempData(object):
    def __init__(self, light_csv, temp_csv):
        self.__native_light = None
        self.__temp = pd.read_csv(
            temp_csv, sep=";", index_col=0, parse_dates=True,
        )
        self.__light = pd.read_csv(
            light_csv, sep=";", index_col=0, parse_dates=True,
        )
        self.__temp_light = (
            self.__temp.join(self.__light)
            .drop(
                columns=[
                    "Temperatur.temperatur {room: AUTO}",
                    "Temperatur.temperatur {room: Wohnzimmer}",
                    "Helligkeit.light {room: AUTO}",
                    "Helligkeit.light {room: Wohnzimmer}",
                    "Temperatur_nativ.temperatur_n {room: AUTO}",
                    "Temperatur_nativ.temperatur_n {room: Wohnzimmer}",
                ]
            )
            .dropna(
                subset=[
                    "M_Temperatur.m_temperatur {room: AUTO}",
                    "M_Temperatur.m_temperatur {room: Wohnzimmer}",
                    "M_Helligkeit.m_light {room: AUTO}",
                    "M_Helligkeit.m_light {room: Wohnzimmer}",
                ]
            )
        )

    def add_NativeTemp(self, native_csv):
        self.__native = pd.read_csv(
            native_csv, sep=";", index_col=0, parse_dates=True,
        )
        self.__native_light = (
            self.__native.join(self.__light)
            .drop(
                columns=[
                    "Helligkeit.light {room: AUTO}",
                    "Helligkeit.light {room: Wohnzimmer}",
                    "Temperatur_nativ.temperatur_n {room: AUTO}",
                    "Temperatur_nativ.temperatur_n {room: Wohnzimmer}",
                ]
            )
            .dropna(
                subset=[
                    "M_Temperatur_nativ.m_temperatur_n {room: AUTO}",
                    "M_Temperatur_nativ.m_temperatur_n {room: Wohnzimmer}",
                    "M_Helligkeit.m_light {room: AUTO}",
                    "M_Helligkeit.m_light {room: Wohnzimmer}",
                ]
            )
        )

    def get_Dataframe(self):
        return self.__temp_light

    def get_NativeDataframe(self):
        return self.__native_light

    def get_X(self):
        return self.__temp_light[
            [
                "M_Temperatur.m_temperatur {room: Wohnzimmer}",
                "M_Helligkeit.m_light {room: Wohnzimmer}",
            ]
        ]

    def get_y(self):
        return self.__temp_light[["M_Temperatur.m_temperatur {room: AUTO}"]]

    def get_Xn(self):
        return self.__native_light[
            [
                "M_Temperatur_nativ.m_temperatur_n {room: Wohnzimmer}",
                "M_Helligkeit.m_light {room: Wohnzimmer}",
            ]
        ]

    def get_yn(self):
        return self.__native_light[
            ["M_Temperatur_nativ.m_temperatur_n {room: AUTO}"]
        ]
