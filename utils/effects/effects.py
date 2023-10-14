"""
Classes for high-level effects
"""
from math import floor

from utils.effects.base_effects import WaveformEffects


class PlaybackEffects(WaveformEffects):
    """
    Effects related to music playback.
    """
    def pause(self, breathe_count: int = 2):
        """
        Slowly pulsates image, with a "breathing" animation.

        :param breathe_count: number of times to "breathe"
        :return: list of brightness factors
        """
        main_pulse = self.sinus(a=0.5, p=2, v=0.5)
        breathe_pulse = self.trunc_sinus(a=0.3, p=0.0001, v=0.7)
        crest_idx = floor(len(main_pulse) / 4)

        # splice the main pulse with breathing at the crest
        return main_pulse[:crest_idx] + (breathe_pulse * breathe_count) + main_pulse[crest_idx:]

    def generic_play(self, period: float = 0.5):
        """
        A generic playing animation, pulsates the image continuously.
        :param period:
        :return: list of brightness factors
        """
        return self.sinus(a=0.3, p=period, v=0.5)

    def bpm_play(self, bpm: int):
        """
        A playing animation that pulsates according to the music BPM
        :param bpm:
        :return: list of brightness factors
        """
        raise NotImplementedError
