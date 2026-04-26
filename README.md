# NTE_Piano_player — Windows 端使用指南

## 环境要求

- Windows 10/11
- Python 3.8+
- 目标游戏窗口（逆水寒钢琴界面）

## 快速开始

### 1. 安装依赖

在项目目录下打开终端，执行：

```bash
pip install -r requirements.txt
```

### 2. 运行程序

```bash
python main.py
```

也可以直接传入 MIDI 文件路径：

```bash
python main.py "你的文件.mid"
```

### 3. 编译为 exe（可选）

```bash
pyinstaller build.spec
```

生成的文件在 `dist/NTE_Piano_player.exe`。

## 使用步骤

1. **加载 MIDI 文件**：点击"浏览"选择 `.mid` 文件，点击"加载"
2. **选择目标窗口**：在下拉列表中找到游戏窗口并选中，点击"刷新"可重新枚举
3. **调整参数**：
   - 速度滑块：0.25x ~ 3.0x（默认 1.0x）
   - 八度偏移：-2 ~ +2（当 MIDI 音域超出钢琴范围时使用）
4. **开始演奏**：点击"▶ 播放"或按 `F5`

## 快捷键

| 按键 | 功能 |
|------|------|
| F5   | 播放 |
| F6   | 暂停/继续 |
| F7   | 停止 |

## 键位映射说明

游戏钢琴覆盖 3 个八度（C3-B5），共 36 键：

### 白键（21个）

| 高音 (C5-B5) | 中音 (C4-B4) | 低音 (C3-B3) |
|--------------|--------------|--------------|
| Q = 高音1    | A = 中音1    | Z = 低音1    |
| W = 高音2    | S = 中音2    | X = 低音2    |
| E = 高音3    | D = 中音3    | C = 低音3    |
| R = 高音4    | F = 中音4    | V = 低音4    |
| T = 高音5    | G = 中音5    | B = 低音5    |
| Y = 高音6    | H = 中音6    | N = 低音6    |
| U = 高音7    | J = 中音7    | M = 低音7    |

### 黑键（15个）

**Shift 修饰（升音）：**
- Shift+Q=C#5, Shift+R=F#5, Shift+T=G#5
- Shift+A=C#4, Shift+F=F#4, Shift+G=G#4
- Shift+Z=C#3, Shift+V=F#3, Shift+B=G#3

**Ctrl 修饰（降音）：**
- Ctrl+E=D#5, Ctrl+U=A#5
- Ctrl+D=D#4, Ctrl+J=A#4
- Ctrl+C=D#3, Ctrl+M=A#3

## 在 Claude Code 中操作

### 方式一：直接运行

在 Claude Code 中进入项目目录并运行：

```
cd /path/to/midi-piano-player
pip install -r requirements.txt
python main.py
```

### 方式二：让 Claude Code 帮你操作

在 Claude Code 对话中，你可以直接说：

- "帮我运行 midi-piano-player"
- "把这个项目编译成 exe"
- "帮我找一个测试用的 MIDI 文件"
- "修改速度默认值为 1.5x"

### 方式三：命令行快速播放（无 GUI）

如果你想在 Claude Code 中直接测试 MIDI 解析而不打开 GUI：

```bash
python -c "
from midi_parser import parse_midi, get_midi_info
from key_mapper import note_name

info = get_midi_info('你的文件.mid')
events = parse_midi('你的文件.mid')
print(f'音符数: {info[\"note_count\"]}')
print(f'时长: {info[\"duration\"]:.1f}秒')
print(f'音域: {note_name(info[\"note_range\"][0])} - {note_name(info[\"note_range\"][1])}')
for e in events[:20]:
    print(f'  {note_name(e.note):>4s}  {e.start_time:.3f}s  {e.duration:.3f}s')
"
```

## 常见问题

### Q: 窗口列表中没有游戏窗口？
点击"刷新"按钮，确保游戏窗口处于打开状态（不需要置顶，后台即可）。

### Q: 播放后游戏没有反应？
- 确认选择了正确的游戏窗口（不是启动器或其他窗口）
- 确认游戏内钢琴界面已打开
- 部分游戏需要窗口获得过一次焦点后才能接收 PostMessage

### Q: 很多音符没有播放？
- 检查 MIDI 文件的音域范围，如果超出 C3-B5 则需要调整"八度偏移"
- 加载时会显示"映射范围内"的音符数量，用于判断

### Q: 播放速度不对？
使用速度滑块调节。MIDI 文件的 BPM 可能与游戏不匹配，建议从 0.8x 开始微调。

## 项目结构

```
midi-piano-player/
├── main.py              # GUI 主程序（tkinter）
├── midi_parser.py       # MIDI 文件解析
├── key_mapper.py        # 音符→按键映射
├── player.py            # 后台键鼠演奏引擎
├── build.spec           # PyInstaller 打包配置
├── requirements.txt     # Python 依赖
└── README.md            # 本文档
```
