
from dataclasses import dataclass, field
from typing import Optional
from dataclasses import asdict

CompressorSettingsMapping = {
    'threshold': 'Threshold',
    'ratio': 'Ratio',
    'attack': 'Attack',
    'release': 'Release',
    'pre_comp': 'Pre-comp',
    'resvd': 'resvd',
    'lowpass': 'Lowpass',
    'hipass': 'Hipass',
    'signin': 'SignIn',
    'audin': 'AudIn',
    'dry': 'Dry',
    'wet': 'Wet',
    'filter_preview': 'Filter Preview',
    'rms_size': 'RMS size',
    'knee': 'Knee',
    'auto_make_up_gain': 'Auto Make Up Gain',
    'auto_release': 'Auto Release',
    'legacy_attack_knee_options': 'Legacy Attack/Knee Options',
    'deprecated_broken_anti_alias': 'Deprecated Broken Anti-Alias',
    'multichannel_mode': 'Multichannel Mode',
    'metering_index': 'Metering Index',
    'bypass': 'Bypass',
    'delta': 'Delta'
}

EqSettingsMapping = {
    'freq_low_shelf': 'Freq-Low Shelf',
    'gain_low_shelf': 'Gain-Low Shelf',
    'bw_low_shelf': 'BW-Low Shelf',
    'freq_band_2': 'Freq-Band 2',
    'gain_band_2': 'Gain-Band 2',
    'bw_band_2': 'BW-Band 2',
    'freq_band_3': 'Freq-Band 3',
    'gain_band_3': 'Gain-Band 3',
    'bw_band_3': 'BW-Band 3',
    'freq_high_shelf_4': 'Freq-High Shelf 4',
    'gain_high_shelf_4': 'Gain-High Shelf 4',
    'bw_high_shelf_4': 'BW-High Shelf 4',
    'freq_high_pass_5': 'Freq-High Pass 5',
    'gain_high_pass_5': 'Gain-High Pass 5',
    'bw_high_pass_5': 'BW-High Pass 5',
    'global_gain': 'Global Gain',
    'bypass': 'Bypass',
    'wet': 'Wet',
    'delta': 'Delta'
}

ReverbSettingsMapping = {
    "wet": "Wet",
    "dry": "Dry",
    "pre_verb": "Pre-verb",
    "max_fft_size": "Max FFT size",
    "width": "Width",
    "pan": "Pan",
    "zl_mode": "ZL mode",
    "ll_mode": "LL mode",
    "bypass": "Bypass",
    "delta": "Delta"
}
DelaySettingsMapping = {
    "wet": "Wet",
    "dry": "Dry",
    "enabled": "1: Enabled",
    "length_time": "1: Length (time)",
    "length_musical": "1: Length (musical)",
    "feedback": "1: Feedback",
    "lowpass": "1: Lowpass",
    "hipass": "1: Hipass",
    "resolution": "1: Resolution",
    "stereo_width": "1: Stereo width",
    "volume": "1: Volume",
    "pan": "1: Pan",
    "bypass": "Bypass",
    "delta": "Delta"
}

ReverbSettingsMapping = {
    "wet":         "Wet",
    "dry":         "Dry",
    "room_size":   "Room size",
    "dampening":   "Dampening",
    "width":       "Width",
    "delay":       "Delay",
    "lowpass":     "Lowpass",
    "hipass":      "Hipass",
    "bypass":      "Bypass",
    "delta":       "Delta",
}




@dataclass
class CompressorSettings:
    threshold: Optional[float] = None
    ratio: Optional[float] = None
    attack: Optional[float] = None
    release: Optional[float] = None
    pre_comp: Optional[float] = None
    resvd: Optional[float] = None
    lowpass: Optional[float] = None
    hipass: Optional[float] = None
    dry: Optional[float] = None
    wet: Optional[float] = None
    rms_size: Optional[float] = None
    knee: Optional[float] = None
    mapping: dict = field(default_factory=lambda: CompressorSettingsMapping.copy())

    def _to_dict(self)-> dict:
        return {self.mapping[k]: v for k, v in asdict(self).items() if v is not None and k != "mapping"}


@dataclass
class EQSettings:
    freq_low_shelf: Optional[float] = None
    gain_low_shelf: Optional[float] = None
    bw_low_shelf: Optional[float] = None

    freq_band_2: Optional[float] = None
    gain_band_2: Optional[float] = None
    bw_band_2: Optional[float] = None

    freq_band_3: Optional[float] = None
    gain_band_3: Optional[float] = None
    bw_band_3: Optional[float] = None

    freq_high_shelf_4: Optional[float] = None
    gain_high_shelf_4: Optional[float] = None
    bw_high_shelf_4: Optional[float] = None

    freq_high_pass_5: Optional[float] = None
    gain_high_pass_5: Optional[float] = None
    bw_high_pass_5: Optional[float] = None

    global_gain: Optional[float] = None
    wet: Optional[float] = None

    mapping: dict = field(default_factory=lambda: EqSettingsMapping.copy())

    def _to_dict(self)-> dict:
        return {self.mapping[k]: v for k, v in asdict(self).items() if v is not None and k != "mapping"}
    



@dataclass
class ReverbSettings:
    wet: Optional[float]       = None
    dry: Optional[float]       = None
    room_size: Optional[float] = None
    dampening: Optional[float] = None
    width: Optional[float]     = None
    delay: Optional[float]     = None
    lowpass: Optional[float]   = None
    hipass: Optional[float]    = None
    bypass: Optional[float]    = None
    delta: Optional[float]     = None


    mapping: dict = field(default_factory=lambda: ReverbSettingsMapping.copy())

    def _to_dict(self) -> dict:
 
        return {self.mapping[k]: v for k, v in asdict(self).items() if v is not None and k != "mapping"}
    
@dataclass
class DelaySettings:
    wet: Optional[float] = None
    dry: Optional[float] = None
    enabled: Optional[float] = None
    length_time: Optional[float] = None
    length_musical: Optional[float] = None
    feedback: Optional[float] = None
    lowpass: Optional[float] = None
    hipass: Optional[float] = None
    resolution: Optional[float] = None
    stereo_width: Optional[float] = None
    volume: Optional[float] = None
    pan: Optional[float] = None
    bypass: Optional[float] = None
    delta: Optional[float] = None

    mapping: dict = field(default_factory=lambda: DelaySettingsMapping.copy())

    def _to_dict(self) -> dict:
 
        return {self.mapping[k]: v for k, v in asdict(self).items() if v is not None and k != "mapping"}