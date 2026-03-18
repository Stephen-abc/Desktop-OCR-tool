# 本地OCR截图工具

一个轻量级的Windows本地OCR工具，支持全局快捷键截图、文字识别、自动复制到剪贴板。

## 特性

- **全局热键**: 默认 Ctrl+Alt+S 触发截图（支持自定义）
- **鼠标右键**: 也可右键直接触发截图
- **高效OCR**: 使用RapidOCR，模型仅60-100MB，中文准确率高
- **自动复制**: 识别结果自动复制到剪贴板
- **系统托盘**: 最小化到托盘，不占用任务栏
- **可配置**: 设置窗口可修改热key、OCR语言等
- **完全离线**: 无需网络即可使用OCR

## 安装

### 1. 环境要求

- Windows 10/11
- Python 3.10+ (建议3.12)
- 首次运行会自动下载ONNX模型文件（约60-100MB）

### 2. 安装依赖

```bash
cd ocr_tool
pip install -r requirements.txt
```

### 3. 运行

```bash
python main.py
```

或使用启动脚本：

```cmd
run.bat
```

## 使用方法

1. **启动程序**
   - 运行后会在系统托盘显示蓝色"OCR"图标
   - 控制台窗口可以最小化

2. **截图OCR**
   - 按 `Ctrl+Alt+S`（默认快捷键）
   - 或**鼠标右键**点击任意位置
   - 拖拽选择字幕或文字区域
   - 右键确认，ESC取消
   - 识别完成后自动复制，托盘显示通知

3. **修改设置**
   - 右键点击托盘图标 → "打开设置"
   - 可修改：截图热key、OCR语言、通知开关等
   - 修改后立即生效

4. **退出**
   - 右键托盘 → "退出"
   - 或按 Ctrl+C（如果控制台可见）

## 配置

配置文件位置：`~/.ocr_tool/config.json`

```json
{
  "hotkey": "Ctrl+Alt+S",
  "ocr_lang": "ch",
  "show_notification": true,
  "auto_start": false
}
```

### OCR语言选项

- `ch`: 中文识别（默认）
- `en`: 英文识别
- `mixed`: 中英混合识别

## 快捷键说明

### 格式

- 修饰键: `Ctrl`、`Alt`、`Shift`、`Win`
- 组合: `Ctrl+Alt+S`、`Ctrl+Shift+S` 等
- 最多支持4个键（3个修饰+1个主键）

### 支持

- 默认: `Ctrl+Alt+S`
- 右键: 始终可用（不受热key限制）
- 可自定义: 在设置窗口中修改

## 打包为exe

使用PyInstaller打包为单文件：

```bash
pip install pyinstaller
cd ocr_tool
pyinstaller --onefile --windowed --icon=assets\icon.ico main.py
```

生成的exe在 `dist/main.exe`

## 常见问题

### Q1: 初次启动慢？

首次运行RapidOCR会自动下载ONNX模型文件（约60-100MB），请耐心等待。模型保存在 `~/.ocr_tool/models/`

### Q2: 热key冲突？

如果其他程序占用相同快捷键，设置窗口会提示。请修改为其他组合。

### Q3: OCR准确率低？

- 选择清晰、高分辨率的文字图片
- 调整截图选区，尽量只包含文字区域
- 确保OCR语言设置正确
- 复杂背景或艺术字体识别率会降低

### Q4: 托盘图标不显示？

某些Windows主题可能需要重启资源管理器，或尝试以管理员运行。

### Q5: 内存占用？

- OCR引擎初始化后约500MB-1GB
- 识别完成后可以保持或重启释放

## 性能

- 截图响应: < 200ms
- OCR识别: 1-3秒（取决于CPU）
- 模型大小: ~100MB
- 安装包大小: ~300MB（含onnxruntime）

## 技术栈

- **OCR**: rapidocr-onnxruntime
- **截图**: pillow + mss
- **热键**: pynput
- **剪贴板**: pyperclip
- **托盘**: pystray
- **GUI**: tkinter（内置）

## 开发

项目结构：
```
ocr_tool/
├── main.py              # 主程序
├── config.py            # 配置管理
├── ocr_engine.py        # OCR引擎封装
├── screenshot.py        # 截图功能
├── clipboard.py         # 剪贴板
├── tray_icon.py         # 托盘
├── settings_window.py   # 设置窗口
├── hotkey.py            # 热键监听
├── requirements.txt     # 依赖
├── assets/
│   └── icon.ico         # 图标
└── create_icon.py       # 图标生成脚本
```

## 许可证

MIT License

## 致谢

- [RapidOCR](https://github.com/hiroi-sora/RapidOCR-json) - 轻量OCR方案
- [PaddlePaddle](https://www.paddlepaddle.org.cn/) - 深度学习框架
