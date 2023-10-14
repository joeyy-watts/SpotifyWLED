"""
Effects to add to Spotify album cover
"""
import math
from typing import Callable


class Effect():
    def __init__(self, width: int, height: int, resolution: int = 100):
        """
        Base class for all effects

        :param width: LED matrix width
        :param height: LED matrix height
        :param resolution: maximum resolution allowed for effects
            The actual resolution depends on the effect calculation, as they are
            calculated according to each effect's formula to avoid the waveform
            being clipped.
        """
        # a fixed factor to multiply image RGB values with
        # this is pre-calculated by _calculate_factors and is bound to the class
        self.factors = []
        self.resolution = resolution

    def _get_effect(self, mode):
        """
        calculates the effect, and returns the factor
        :return:
        """
        raise NotImplementedError

    def stop_effect(self):
        """
        stops the effect
        :return:
        """
        raise NotImplementedError

    def _calculate_factors(self, function: Callable[..., list[float]], *args, **kwargs):
        """
        calculates the factors for the effect

        :param resolution: effect resolution
        :param function: function used to calculate factors
        :param args: arguments for `function`
        :param kwargs: keyword arguments for `function`
        :return: a list of RGB values to multiply the image with
        """
        for i in range(0, self.resolution):
            self.factors.append(function(i, *args, **kwargs))


class PulsateEffect(Effect):
    """
    Pulsate Effect

    Varies the brightness of the image according to the mode, currently supported types:
        - Sinusoidal
        - Sawtooth
        - Traingular
    """
    def sinus_pulse(self, a: float = 0.5, p: float = 2 * math.pi, v: float = 0.5):
        """
        Generates sinusoidal pulsate effect.
        Defaults generate a standard sin-wave with 0.5 vertical offset, and 2pi period

        :param a: amplitude
        :param p: period
        :param v: vertical shift
        """
        def func(i):
            # TODO: revisit this so period and resolution are independent
            # my math has gotten worse after graduating..
            return a * math.sin(2 * math.pi / p * (i * (p / self.resolution))) + v

        self._calculate_factors(func)
        print(self.factors)
        return self.factors
