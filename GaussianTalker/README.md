# 说话人脸生成对话系统

基于 GaussianTalker 和 SyncTalk 的数字人视频生成系统，支持模型训练、视频生成和实时对话功能。

## 📖 关键文档

| 文档 | 说明 |
|------|------|
| [GaussianTalker Docker 调用说明](./GaussianTalker_Docker调用说明.md) | 容器化部署、脚本调用方法、前后端集成说明 |
| [Docker 构建指南](./Docker构建指南.md) | Docker 镜像构建步骤、预训练模型配置 |
| [语音克隆使用说明](./语音克隆使用说明.md) | XTTS v2 语音克隆功能的配置与使用 |


## 系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                    前端 (Vue 3 + Vite)                       │
│  ┌─────────┐  ┌─────────────┐  ┌──────────────┐             │
│  │ 首页    │  │ 模型训练    │  │ 视频生成     │             │
│  └────┬────┘  └──────┬──────┘  └──────┬───────┘             │
│       │              │                │                      │
│  ┌────┴──────────────┴────────────────┴───────┐             │
│  │           实时对话系统                      │             │
│  └────────────────────┬───────────────────────┘             │
└───────────────────────┼─────────────────────────────────────┘
                        │ SSE 实时进度推送
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                    后端 (Flask)                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐          │
│  │model_trainer│  │video_generator│ │chat_engine │          │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘          │
│         │                │                │                  │
│  ┌──────┴────────────────┴────────────────┴──────┐          │
│  │           云端训练/渲染 (AutoDL SSH)           │          │
│  └───────────────────────────────────────────────┘          │
└─────────────────────────────────────────────────────────────┘
```

## 核心功能

### 1. 模型训练
- 支持 **GaussianTalker** 和 **SyncTalk** 两种模型
- 支持本地 GPU 和云端训练（AutoDL SSH）
- **跳过预处理功能**：若云端已有预处理数据，可跳过耗时的数据预处理步骤
- 实时进度推送（SSE）

### 2. 视频生成
- 上传音频或使用 TTS 语音克隆生成音频
- 支持本地渲染和云端渲染
- 实时进度推送（SSE）

### 3. 实时对话
- 语音识别（Whisper）
- AI 对话（智谱 AI）
- 语音克隆（XTTS v2）
- 数字人视频生成
- 实时进度推送（SSE）

## 快速开始

### 1. 安装后端依赖

```bash
pip install flask paramiko scp
# 可选：语音识别、TTS 等依赖
pip install openai-whisper TTS pyttsx3 zhipuai speech_recognition
```

### 2. 安装前端依赖并构建

```bash
cd frontend_vue
npm install
npm run build
```

> 构建后的静态文件会输出到项目根目录的 `static/` 目录

⚠️ **重要**：构建完成后，需要手动将根目录下生成的 HTML 文件移动到 `templates/` 目录：

```bash
# Windows
move *.html templates\

# Linux/Mac
mv *.html templates/
```

### 3. 启动后端服务

```bash
python app.py
```

### 4. 访问应用

打开浏览器访问：http://127.0.0.1:5001

## 前端开发模式

如需进行前端开发调试：

```bash
cd frontend_vue
npm run dev
```

开发服务器会在 http://localhost:5173 启动，并代理 API 请求到后端。

## 目录结构

```
TFG_ui_GaussianTalker/
├── app.py                 # Flask 主入口
├── backend/
│   ├── model_trainer.py   # 模型训练逻辑
│   ├── video_generator.py # 视频生成逻辑
│   ├── chat_engine.py     # 对话系统核心
│   ├── cloud_trainer.py   # 云端训练/渲染
│   └── voice_cloner.py    # 语音克隆
├── frontend_vue/          # Vue 前端源码
│   ├── src/
│   │   ├── views/         # 页面组件
│   │   ├── components/    # 通用组件
│   │   └── assets/        # 样式资源
│   └── vite.config.js
├── static/                # 静态资源
│   ├── audios/            # 音频文件
│   ├── videos/            # 视频文件
│   ├── js/                # 构建后的 JS
│   └── css/               # 构建后的 CSS
├── GaussianTalker/        # GaussianTalker 模型
└── SyncTalk/              # SyncTalk 模型
```

## 功能使用说明

### 模型训练

1. 选择模型类型（GaussianTalker / SyncTalk）
2. 上传训练视频
3. 选择 GPU（本地 GPU0/GPU1 或 云端）
4. 若使用云端训练，配置 SSH 端口和密码
5. **跳过预处理（可选）**：若云端已有预处理数据，勾选此项并填写模型名称即可跳过预处理步骤
6. 点击开始训练，实时查看进度

### 视频生成

1. 选择已训练的模型
2. 上传驱动音频，或使用 TTS 语音克隆
3. 选择渲染设备（本地/云端）
4. 点击生成，实时查看进度

### 实时对话

1. 选择数字人模型
2. 上传参考音频（用于语音克隆）
3. 点击麦克风录音或输入文字
4. 系统自动进行语音识别 → AI 回复 → 语音合成 → 视频生成

## 主题切换

前端支持日间/夜间模式切换，点击右上角的主题按钮即可切换。

## 注意事项

- 云端训练需要有效的 AutoDL SSH 凭据
- 首次使用语音克隆功能时会下载 XTTS v2 模型（约 2GB）
- 首次使用语音识别时会下载 Whisper 模型
- 建议使用 Chrome 或 Edge 浏览器以获得最佳体验

## 技术栈

- **前端**: Vue 3, Vite, Tailwind CSS, Lucide Icons
- **后端**: Flask, Python
- **AI 模型**: GaussianTalker, SyncTalk, Whisper, XTTS v2, 智谱 AI

## GaussianTalker 模型说明

本项目中的 GaussianTalker 模型经过独特优化，包括数据预处理流程改进、Docker 容器化部署等。

📖 **详细文档**：
- [GaussianTalker_Docker 调用说明](./GaussianTalker_Docker调用说明.md) - 容器化部署与调用方法
