"""
MIDI 音符到键盘按键的映射表
游戏钢琴覆盖 3 个八度 C3-B5，共 36 键

白键布局:
  QWERTYU = 高音 1-7 (C5-B5)
  ASDFGHJ = 中音 1-7 (C4-B4)
  ZXCVBNM = 低音 1-7 (C3-B3)

黑键布局:
  Shift+Q/R/T/A/F/G/Z/V/B = 对应白键的升音 (C#/F#/G#)
  Ctrl+E/U/D/J/C/M = 对应白键的降音 (D#/A#)
"""

import ctypes

# Virtual key codes
VK_SHIFT = 0xA0       # Left Shift
VK_CONTROL = 0xA2     # Left Control
VK_MENU = 0xA4        # Alt

# MIDI 范围
MIDI_MIN = 48  # C3
MIDI_MAX = 83  # B5

# 音符名称（用于显示）
NOTE_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']


def note_name(midi_note: int) -> str:
    """将 MIDI 音符号转换为可读名称，如 C4, F#5"""
    name = NOTE_NAMES[midi_note % 12]
    octave = (midi_note // 12) - 1
    return f"{name}{octave}"


# 完整映射表: MIDI note number -> (vk_code, modifier_vk or None)
KEY_MAP = {
    # === 低音区 (C3-B3) ===
    # 白键: ZXCVBNM
    48: (0x5A, None),   # Z -> C3
    50: (0x58, None),   # X -> D3
    52: (0x43, None),   # C -> E3
    53: (0x56, None),   # V -> F3
    55: (0x42, None),   # B -> G3
    57: (0x4E, None),   # N -> A3
    59: (0x4D, None),   # M -> B3
    # 黑键: Shift+Z/V/B, Ctrl+C/M
    49: (0x5A, VK_SHIFT),   # Shift+Z -> C#3
    54: (0x56, VK_SHIFT),   # Shift+V -> F#3
    56: (0x42, VK_SHIFT),   # Shift+B -> G#3
    51: (0x43, VK_CONTROL), # Ctrl+C -> D#3
    58: (0x4D, VK_CONTROL), # Ctrl+M -> A#3

    # === 中音区 (C4-B4) ===
    # 白键: ASDFGHJ
    60: (0x41, None),   # A -> C4
    62: (0x53, None),   # S -> D4
    64: (0x44, None),   # D -> E4
    65: (0x46, None),   # F -> F4
    67: (0x47, None),   # G -> G4
    69: (0x48, None),   # H -> A4
    71: (0x4A, None),   # J -> B4
    # 黑键: Shift+A/F/G, Ctrl+D/J
    61: (0x41, VK_SHIFT),   # Shift+A -> C#4
    66: (0x46, VK_SHIFT),   # Shift+F -> F#4
    68: (0x47, VK_SHIFT),   # Shift+G -> G#4
    63: (0x44, VK_CONTROL), # Ctrl+D -> D#4
    70: (0x4A, VK_CONTROL), # Ctrl+J -> A#4

    # === 高音区 (C5-B5) ===
    # 白键: QWERTYU
    72: (0x51, None),   # Q -> C5
    74: (0x57, None),   # W -> D5
    76: (0x45, None),   # E -> E5
    77: (0x52, None),   # R -> F5
    79: (0x54, None),   # T -> G5
    81: (0x59, None),   # Y -> A5
    83: (0x55, None),   # U -> B5
    # 黑键: Shift+Q/R/T, Ctrl+E/U
    73: (0x51, VK_SHIFT),   # Shift+Q -> C#5
    78: (0x52, VK_SHIFT),   # Shift+R -> F#5
    80: (0x54, VK_SHIFT),   # Shift+T -> G#5
    75: (0x45, VK_CONTROL), # Ctrl+E -> D#5
    82: (0x55, VK_CONTROL), # Ctrl+U -> A#5
}


def get_key_info(midi_note: int, octave_shift: int = 0):
    """
    获取 MIDI 音符对应的按键信息

    Args:
        midi_note: MIDI 音符号 (0-127)
        octave_shift: 八度偏移量，用于将超范围音符平移到可演奏范围

    Returns:
        (vk_code, modifier) 元组，如果音符无法映射则返回 None
    """
    shifted = midi_note + octave_shift * 12
    if shifted in KEY_MAP:
        return KEY_MAP[shifted]

    # 尝试自动八度平移
    if MIDI_MIN <= midi_note <= MIDI_MAX:
        return KEY_MAP.get(midi_note)

    # 自动寻找最近的八度
    while shifted < MIDI_MIN:
        shifted += 12
    while shifted > MIDI_MAX:
        shifted -= 12

    return KEY_MAP.get(shifted)


def get_all_mapped_notes() -> list:
    """返回所有已映射的 MIDI 音符号（排序后）"""
    return sorted(KEY_MAP.keys())
