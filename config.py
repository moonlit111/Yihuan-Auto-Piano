"""
配置文件模块
为每个 MIDI 文件保存/加载播放参数（速度、八度偏移、轨道选择）
"""

import json
import os
from typing import Optional, List


def _config_path(midi_path: str) -> str:
    """根据 MIDI 文件路径生成配置文件路径"""
    return midi_path + ".cfg"


def save_config(midi_path: str, speed: float, octave_shift: int,
                selected_tracks: Optional[List[int]] = None,
                select_all: bool = True):
    """
    保存播放参数到配置文件

    Args:
        midi_path: MIDI 文件路径
        speed: 播放速度
        octave_shift: 八度偏移
        selected_tracks: 选中的轨道索引列表，None 表示全部
        select_all: 是否全选
    """
    cfg = {
        "speed": speed,
        "octave_shift": octave_shift,
        "selected_tracks": selected_tracks,
        "select_all": select_all,
    }
    path = _config_path(midi_path)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2, ensure_ascii=False)


def load_config(midi_path: str) -> Optional[dict]:
    """
    加载播放参数，如果配置文件不存在则返回 None

    Returns:
        包含 speed, octave_shift, selected_tracks, select_all 的字典
    """
    path = _config_path(midi_path)
    if not os.path.exists(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return None
