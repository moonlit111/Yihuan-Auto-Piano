"""
MIDI 文件解析模块
使用 mido 库解析 MIDI 文件，提取音符事件并转换为时间线
"""

from dataclasses import dataclass
from typing import List, Optional, Union
import mido


@dataclass
class NoteEvent:
    """一个音符事件"""
    note: int           # MIDI 音符号 (0-127)
    start_time: float   # 开始时间（秒）
    duration: float     # 持续时间（秒）
    velocity: int       # 力度 (0-127)

    def end_time(self) -> float:
        return self.start_time + self.duration


def list_tracks(file_path: str) -> list:
    """列出 MIDI 文件中的所有轨道信息"""
    mid = mido.MidiFile(file_path)
    result = []
    for i, track in enumerate(mid.tracks):
        name = track.name if track.name else f"轨道 {i}"
        note_count = sum(1 for msg in track if msg.type == 'note_on' and msg.velocity > 0)
        result.append({'index': i, 'name': name, 'note_count': note_count})
    return result


def _build_tempo_map(mid) -> list:
    """
    构建全局 tempo 映射表: [(abs_tick, tempo)]
    从所有轨道中收集 tempo 变更事件，按 tick 排序
    """
    changes = [(0, 500000)]  # 默认 120 BPM
    for track in mid.tracks:
        tick = 0
        for msg in track:
            tick += msg.time
            if msg.type == 'set_tempo':
                changes.append((tick, msg.tempo))
    changes.sort(key=lambda x: x[0])
    return changes


def _tick_to_sec(tick: int, tempo_map: list, tpb: int) -> float:
    """将绝对 tick 位置转换为秒（分段计算，处理 tempo 变更）"""
    sec = 0.0
    prev = 0
    tempo = 500000
    for t, tp in tempo_map:
        if t > tick:
            break
        if t > prev:
            sec += mido.tick2second(t - prev, tpb, tempo)
            prev = t
        tempo = tp
    if tick > prev:
        sec += mido.tick2second(tick - prev, tpb, tempo)
    return sec


def parse_midi(file_path: str, octave_shift: int = 0,
               track_index: Optional[Union[int, List[int]]] = None) -> List[NoteEvent]:
    """
    解析 MIDI 文件，返回音符事件列表

    Args:
        file_path: MIDI 文件路径
        octave_shift: 八度偏移量
        track_index: 指定播放的轨道索引，None 表示全部轨道，可以是单个 int 或 List[int]

    Returns:
        按开始时间排序的 NoteEvent 列表
    """
    mid = mido.MidiFile(file_path)
    tempo_map = _build_tempo_map(mid)
    tpb = mid.ticks_per_beat

    events = []
    if track_index is None:
        tracks = range(len(mid.tracks))
    elif isinstance(track_index, list):
        tracks = track_index
    else:
        tracks = [track_index]

    for i in tracks:
        track = mid.tracks[i]
        abs_tick = 0
        active_notes = {}  # (note, channel) -> start_time

        for msg in track:
            abs_tick += msg.time
            t = _tick_to_sec(abs_tick, tempo_map, tpb)

            if msg.type == 'note_on' and msg.velocity > 0:
                key = (msg.note + octave_shift * 12, msg.channel)
                active_notes[key] = t

            elif msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
                note = msg.note + octave_shift * 12
                key = (note, msg.channel)
                if key in active_notes:
                    start = active_notes.pop(key)
                    duration = t - start
                    if duration > 0:
                        events.append(NoteEvent(
                            note=note,
                            start_time=start,
                            duration=duration,
                            velocity=msg.velocity if msg.type == 'note_on' else 64
                        ))

    events.sort(key=lambda e: (e.start_time, e.note))
    return events


def get_midi_info(file_path: str, events: List[NoteEvent] = None) -> dict:
    mid = mido.MidiFile(file_path)
    if events is None:
        events = parse_midi(file_path)

    if not events:
        return {
            'tracks': len(mid.tracks),
            'duration': 0,
            'note_count': 0,
            'note_range': (0, 0),
            'ticks_per_beat': mid.ticks_per_beat,
        }

    return {
        'tracks': len(mid.tracks),
        'duration': max(e.end_time() for e in events),
        'note_count': len(events),
        'note_range': (min(e.note for e in events), max(e.note for e in events)),
        'ticks_per_beat': mid.ticks_per_beat,
    }


def export_midi(src_path: str, dst_path: str,
                selected_tracks: Optional[List[int]] = None,
                speed: float = 1.0,
                octave_shift: int = 0):
    """
    导出修改后的 MIDI 文件

    Args:
        src_path: 源 MIDI 文件路径
        dst_path: 目标 MIDI 文件路径
        selected_tracks: 要导出的轨道索引列表，None 表示全部
        speed: 播放速度（通过缩放 tempo 实现）
        octave_shift: 八度偏移
    """
    mid = mido.MidiFile(src_path)

    # 创建新 MIDI 文件
    new_mid = mido.MidiFile(ticks_per_beat=mid.ticks_per_beat)

    if selected_tracks is None:
        selected_tracks = list(range(len(mid.tracks)))
    else:
        selected_tracks = set(selected_tracks)

    for i, track in enumerate(mid.tracks):
        if i not in selected_tracks:
            continue
        new_track = mido.MidiTrack()
        new_track.name = track.name

        for msg in track:
            new_msg = msg.copy()

            # 应用八度偏移到音符消息
            if hasattr(new_msg, 'note') and new_msg.type in ('note_on', 'note_off'):
                new_msg.note = new_msg.note + octave_shift * 12

            # 缩放 tempo（速度 > 1 时 tempo 变小 = 更快）
            if new_msg.type == 'set_tempo':
                new_msg.tempo = int(new_msg.tempo / speed)

            new_track.append(new_msg)

        new_mid.tracks.append(new_track)

    new_mid.save(filename=dst_path)
