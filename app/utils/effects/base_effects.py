"""
Classes for low-level effects (i.e. effects from pure waveforms)
"""
import math
from typing import Callable, final

from confs.global_confs import TARGET_FPS
from handlers.spotify_api_handler import AudioFeatures
from utils.effects.effects_utils import is_black


# TODO: move math-related functions to dedicated module
# TODO: refactor so that wave functions can be plugged into effects
# TODO: effect layering
class EffectData:
    """
    Data class for effects.
        - factors: list containing brightness factors for each frame
        - period: period of the waveform (in seconds)
    """
    def __init__(self, factors: list[float], period: float):
        self.factors = factors
        self.period = period

    def apply(self, image):
        """
        applies effect to image
        :param image: image to apply effect to
        :return: image with effect frames precalculated
        """
        frames = []

        for i in self.factors:
            frames.append(tuple([(int(r * i), int(g * i), int(b * i))
                        if not is_black((r, g, b)) else
                       (int(r), int(g), int(b))
                        for r, g, b in image]))

        return tuple(frames)

class Effect:
    def __init__(self, width: int, height: int):
        """
        Base class for all effects

        :param width: LED matrix width
        :param height: LED matrix height
        :param resolution: maximum resolution allowed for effects
            The actual resolution depends on the effect calculation, as they are
            calculated according to each effect's formula to avoid the waveform
            being clipped.
        """
        self.target_fps = TARGET_FPS

    @final
    def _calculate_effect(self, function: Callable[..., list[float]], period):
        """
        Calculates the required data for effects.

        Number of brightness factors is always equal to the target FPS.

        :param function: function used to calculate factors
        :param period: the period of the effect's waveform
        :return: EffectData object with brightness factors and period
        """
        num_factors = int(self.target_fps * period)

        factors = []
        for i in range(0, num_factors):
            factors.append(function(period * (i / num_factors)))
        return EffectData(factors, period)


class WaveformEffects(Effect):
    """
    Waveform-based effects.
    Varies the brightness of the entire image, currently supported types:
        - Sinusoidal
        - Sawtooth
        - Triangular

    To avoid confusion, "period" refers to the mathematical definition of:
        - Given the equation y = sin(Ax), Period = 2pi / |A|
    Hence the funny-looking equations.
    """
    def sinus_raw(self, a: float = 0.5, p: float = 2, v: float = 0.5, h: float = 0, e: float = 1):
        """
        Generates sinusoidal pulsate effect in raw waveform.
        Defaults generate a standard sin-wave with 0.5 vertical offset, and 2pi period

        :param a: amplitude
        :param p: period
        :param v: vertical shift
        :param h: horizontal shift
        :param e: exponential factor, higher values result in more sudden changes
        """

        def func(i):
            return a * (math.sin((2 * math.pi / p) * i - h) ** e) + v

        return self._calculate_effect(func, p)

    def trunc_sinus_raw(self, a: float = 0.5, p: float = 2, v: float = 0.5, h: float = 0, e: float = 1, invert: bool = False):
        """
        Generates truncated sinusoidal pulsate effect.
        Defaults generate a standard sin-wave with 0.5 vertical offset, and 2pi period

        :param a: amplitude
        :param p: period
        :param v: vertical shift
        :param h: horizontal shift
        :param e: exponential factor, higher values result in more sudden changes
        :param invert: if True, returns the lower half of the sinusoidal wave
        """
        invert_factor = -1 if invert else 1

        def func(i):
            return invert_factor * abs(a * (math.sin((2 * math.pi / p) * i - h) ** e)) + v

        return self._calculate_effect(func, p)

    def sinus_bpm(self, bpm: float, a: float = 0.5, v: float = 0.5):
        """
        Generates a sinusoidal pulsate effect corresponding to the given BPM.

        :param bpm: beats-per-minute (float)
        :param a: amplitude of the sin wave
        :param v: vertical shift of the sin wave
        """
        period = 1 / (bpm / 60)
        def func(i):
            return a * math.sin((2 * math.pi / period) * i) + v

        return self._calculate_effect(func, period)

    def trunc_sinuc_bpm(self, bpm: float, a: float = 0.5, v: float = 0.5, h: float = 0, e: float = 1, invert: bool = False):
        """
        Generates truncated sinusoidal pulsate effect.
        Each crest corresponds to one single beat.

        :param bpm: beats-per-minute (float)
        :param a: amplitude
        :param v: vertical shift
        :param h: horizontal shift
        :param invert: if True, inverts the waveform
        """
        invert_factor = -1 if invert else 1
        period = 1 / (bpm / (60 * 2))

        def func(i):
            return invert_factor * abs(a * (math.sin((2 * math.pi / period) * i) ** e)) + v

        return self._calculate_effect(func, period)

    def trunc_sinus_features(self, features: AudioFeatures, invert: bool = False):
        """
        Generates sinusoidal effect based on audio features.

        :param features: AudioFeatures object
        :param invert: if True, inverts the waveform
        """

        return self.trunc_sinuc_bpm(features.tempo, 0.3, 0.6, 0, 10 * features.energy, invert)


    def sawtooth(self, a, p, v):
        """
        Generates a sawtooth pulsate effect.

        :param a: amplitude
        :param p: period
        :param v: vertical shift
        """
        period = 1

        def func(i):
            # need this to shift sawtooth so it starts at 0
            phase_shifted_i = i - 0.5
            return a * (2 * (phase_shifted_i - math.floor(0.5 + phase_shifted_i))) + v

        return self._calculate_effect(func, period)

class ScaleEffects(Effect):
    """
    Image-scaling based effects.
    Currently planned:
        - Zoom
    """
    pass

class OverlayEffects(Effect):
    """
    Effects that add elements on top of the image.
    Currently planned:
        - Bar (solid colored bar that wipes across image)
        - Noise (solid noise overlay)
        - Twinkle
        - Fireworks; random fireworks according to beat

    refer to Jinx for additional ideas
    """
    pass
