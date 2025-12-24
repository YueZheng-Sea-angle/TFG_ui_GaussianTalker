# GaussianTalker Docker 调用说明
## 重要说明
在开始构建docker镜像前，请务必阅读[Docker构建准备指南](./Docker构建指南.md)
## 构建Docker镜像

```bash
cd GaussianTalker
# 将Dockerfile.final重命名为Dockerfile
cp Dockerfile.final Dockerfile

# 将5个预训练模型文件放置到GaussianTalker/目录下：
# - 01_MorphableModel.mat
# - epoch_20.pth
# - resnet50-19c8e357.pth
# - shape_predictor_68_face_landmarks.dat
# - s3fd-619a316812.pth

# 构建Docker镜像（需要较长时间，约30-60分钟）
docker build -t gaussiantalker:latest .
```

## 打包Docker镜像

```bash
docker save -o gaussiantalker.tar gaussiantalker:latest
```

## 从tar导入Docker镜像

```bash
docker load -i gaussiantalker.tar
```

## 脚本文件

`run_gaussiantalker.sh`

## 目录结构

```
当前工作目录/
└── GaussianTalker/              # 自动创建的工作目录
    ├── data/                    # 数据目录
    │   └── {视频名称}/          # 预处理数据文件夹
    │       ├── {视频名称}.mp4   # 原始视频
    │       ├── ori_imgs/        # 视频帧
    │       ├── gt_imgs/         # 裁剪后的人脸图像
    │       ├── parsing/         # 人脸分割
    │       ├── aud.wav          # 提取的音频
    │       ├── aud.npy          # DeepSpeech音频特征
    │       ├── au.csv           # Action Unit特征
    │       └── transforms_*.json # 3DMM参数
    └── output/                  # 输出目录
        └── {视频名称}/          # 训练好的模型
            ├── point_cloud/     # 3D高斯点云
            ├── checkpoints/     # 模型检查点
            └── renders/         # 推理结果
                └── output.mp4   # 生成的视频
```

## 脚本调用命令

### train - 完整训练流程

```bash
./run_gaussiantalker.sh train \
    --video_path <视频文件路径> \
    --gpu <GPU设备> \
    --iterations <迭代次数> \
    [--config <配置文件>] \
    [--au_csv <AU文件>]
```

**参数说明：**
- `--video_path`: 输入视频文件路径（必需）
- `--gpu`: GPU设备（默认: GPU0）
  - `GPU0`, `GPU1`, `GPU2`, ... - 指定GPU
  - `CPU` - 使用CPU
- `--iterations`: 训练迭代次数（默认: 10000）
- `--config`: 配置文件路径（可选，默认: arguments/64_dim_1_transformer.py）
- `--au_csv`: 手动提供的AU文件（可选，如果OpenFace封装失败）

**示例：**
```bash
# 基础训练
./run_gaussiantalker.sh train --video_path ./obama.mp4 --gpu GPU0 --iterations 10000

# 使用自定义配置
./run_gaussiantalker.sh train --video_path ./obama.mp4 --gpu GPU0 --iterations 15000 --config arguments/64_dim_1_transformer.py

# 手动提供AU文件（如果OpenFace失败）
./run_gaussiantalker.sh train --video_path ./obama.mp4 --gpu GPU0 --au_csv ./au.csv
```

### infer - 视频推理

```bash
./run_gaussiantalker.sh infer \
    --model_dir <模型目录名称> \
    --audio_path <音频文件路径> \
    --gpu <GPU设备> \
    [--batch_size <批大小>] \
    [--iteration <检查点迭代次数>]
```

**参数说明：**
- `--model_dir`: 模型目录名称（如：obama）
- `--audio_path`: 驱动音频文件路径
- `--gpu`: GPU设备
- `--batch_size`: 批处理大小（可选，默认: 128）
- `--iteration`: 使用的检查点迭代次数（可选，默认: 10000）

**示例：**
```bash
# 基础推理
./run_gaussiantalker.sh infer \
    --model_dir obama \
    --audio_path speech.wav \
    --gpu GPU0

# 指定batch_size和iteration
./run_gaussiantalker.sh infer \
    --model_dir obama \
    --audio_path speech.wav \
    --gpu GPU0 \
    --batch_size 256 \
    --iteration 15000
```

### evaluate - 评估视频质量

```bash
./run_gaussiantalker.sh evaluate \
    --generated_video <生成视频路径> \
    --data_dir <数据目录> \
    [--output_json <输出JSON文件>]
```

**参数说明：**
- `--generated_video`: 生成的视频路径（必需）
- `--data_dir`: 训练数据目录，包含transforms_val.json和gt_imgs/（必需）
- `--output_json`: 输出结果的JSON文件路径（可选）

**评估指标：**
- **PSNR** (Peak Signal-to-Noise Ratio): 峰值信噪比，越高越好（30+ dB为良好）
- **SSIM** (Structural Similarity Index): 结构相似性，范围0-1，越高越好（0.90+为良好）

**示例：**
```bash
# 基础评估
./run_gaussiantalker.sh evaluate \
    --generated_video ./GaussianTalker/output/obama/renders/output.mp4 \
    --data_dir ./GaussianTalker/data/obama

# 保存评估结果到JSON
./run_gaussiantalker.sh evaluate \
    --generated_video ./GaussianTalker/output/obama/renders/output.mp4 \
    --data_dir ./GaussianTalker/data/obama \
    --output_json evaluation_results.json
```

## 输出文件说明

### 训练完成后
- **数据目录**: `GaussianTalker/data/{视频名称}/`
- **模型目录**: `GaussianTalker/output/{视频名称}/`

### 推理完成后
- **输出视频**: `GaussianTalker/output/{视频名称}/renders/output.mp4`
  - 或: `GaussianTalker/output/{视频名称}/custom/ours_{iteration}/renders/output.mp4`

## 测试模式

在不构建 Docker 镜像的情况下测试脚本逻辑：

```bash
# 启用测试模式
TEST_MODE=1 ./run_gaussiantalker.sh train --video_path ./test.mp4 --gpu GPU0 --iterations 10000
TEST_MODE=1 ./run_gaussiantalker.sh infer --model_dir test --audio_path ./test.wav
```

**示例：**
```
GaussianTalker/data/obama/
GaussianTalker/output/obama/
GaussianTalker/output/obama/renders/output.mp4
```

## 前后端集成说明

### 系统架构

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

### 前端界面 (Vue 3 + Vite)

**技术栈**: Vue 3, Vite, Tailwind CSS, Lucide Icons

1. **首页** (`/`):
   - 系统概览和功能导航
   - 支持日间/夜间主题切换

2. **模型训练页面** (`/model-training`):
   - 选择模型: `GaussianTalker` 或 `SyncTalk`
   - 上传训练视频
   - 选择GPU: 本地 GPU0/GPU1 或 **云端训练 (AutoDL SSH)**
   - 云端训练配置: SSH端口、密码
   - **跳过预处理功能**: 若云端已有预处理数据，可跳过耗时的数据预处理步骤
   - 实时进度推送 (SSE)

3. **视频生成页面** (`/video-generation`):
   - 选择已训练的模型
   - 上传驱动音频，或使用 **TTS 语音克隆**生成音频
   - 选择渲染设备: 本地/云端
   - 实时进度推送 (SSE)

4. **实时对话页面** (`/chat`):
   - 选择数字人模型
   - 上传参考音频（用于语音克隆）
   - 支持麦克风录音或文字输入
   - 自动调用: 语音识别 (Whisper) -> AI 对话 (智谱 AI) -> 语音克隆 (XTTS v2) -> GaussianTalker视频生成
   - 实时进度推送 (SSE)

### 后端逻辑

- **`app.py`**: Flask主入口，处理HTTP请求、文件上传和SSE流
- **`backend/model_trainer.py`**: 模型训练逻辑，支持本地和云端训练
- **`backend/video_generator.py`**: 视频生成逻辑，支持本地和云端渲染
- **`backend/chat_engine.py`**: 对话系统核心，整合ASR、LLM、TTS、GaussianTalker完整流程
- **`backend/cloud_trainer.py`**: 云端训练/渲染 (AutoDL SSH)
- **`backend/voice_cloner.py`**: 语音克隆 (XTTS v2)

### 工作流程

**训练:**
1. 用户在前端选择GaussianTalker并上传视频
2. 选择训练设备（本地GPU或云端AutoDL）
3. 若使用云端训练，配置SSH凭据
4. 可选：勾选"跳过预处理"（需云端已有预处理数据）
5. 后端接收请求 -> `model_trainer.py` 或 `cloud_trainer.py`
6. Docker容器内执行预处理和训练
7. **SSE实时推送**训练进度到前端
8. 训练完成，模型保存到 `GaussianTalker/output/`

**推理:**
1. 用户在前端选择模型
2. 上传音频或使用TTS语音克隆生成音频
3. 选择渲染设备（本地/云端）
4. 后端接收请求 -> `video_generator.py`
5. Docker容器内提取DeepSpeech特征并推理
6. **SSE实时推送**渲染进度到前端
7. 生成视频复制到 `static/videos/` 供前端显示

**实时对话:**
1. 用户录音 -> Whisper语音识别
2. 智谱AI生成回复文本
3. XTTS v2合成语音（支持语音克隆）
4. GaussianTalker生成数字人视频
5. **SSE实时推送**各阶段进度
6. 前端同时播放音频和视频

### 前端开发

```bash
# 安装依赖
cd frontend_vue
npm install

# 开发模式 (http://localhost:5173)
npm run dev

# 构建生产版本
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

## 注意事项

1. **首次使用**需要先构建 Docker 镜像（时间较长）
2. **预训练模型**必须放置在正确位置（详见构建说明）
3. **OpenFace集成**: 如果封装失败，可使用 `process_withoutopenface.py` 或手动上传AU文件绕过
4. **视频格式**: 建议使用常见格式（mp4, avi）
5. **音频格式**: 支持 wav, mp3 等常见格式
6. **GPU要求**: 推荐使用NVIDIA GPU with CUDA 11.7+
7. **云端训练**: 需要有效的 AutoDL SSH 凭据（端口和密码）
8. **语音克隆**: 首次使用时会下载 XTTS v2 模型（约 2GB）
9. **语音识别**: 首次使用时会下载 Whisper 模型
10. **浏览器**: 建议使用 Chrome 或 Edge 浏览器以获得最佳体验

## 性能参考

- **训练时间**: 10K iterations约需30-60分钟（取决于视频长度和GPU性能）
- **推理时间**: 约10-30秒/10秒音频（batch_size=128）
- **显存需求**: 至少8GB（推荐12GB+）
- **评估指标**: PSNR 30+, SSIM 0.90+（良好训练）

## 模型优化说明

本研究对GaussianTalker进行了多项优化，以提升系统的易用性、鲁棒性和实时对话能力。

### 优化1: 无OpenFace数据预处理方案

如果Docker镜像未集成OpenFace，或用户不方便手动上传au.csv文件，现在可以使用 `process_withoutopenface.py` 进行数据预处理。

**原理说明：**
该脚本通过 **AU45优化算法** 自动生成au.csv文件，无需依赖OpenFace工具。AU45（眨眼特征）可通过面部关键点的眼睛纵横比（EAR, Eye Aspect Ratio）计算获得。

**使用方法：**
```bash
# 在Docker容器内使用无OpenFace预处理
python data_utils/process_withoutopenface.py data/{视频名称}
```

**适用场景：**
- OpenFace封装/安装失败
- 快速原型验证
- 无需高精度AU特征的场景

### 优化2: 改进的训练脚本

提供了 `train_fix.py` 训练脚本，调用修复后的损失函数 `loss_utils_fix.py`，实现优化的推理效果。

**使用方法：**
```bash
# 使用优化后的训练脚本
python train_fix.py -s data/{视频名称} --model_path output/{视频名称} --configs arguments/64_dim_1_transformer.py
```

**优化内容：**
- 修复损失函数计算中的潜在问题
- 提升训练稳定性
- 改善最终推理质量

### 优化3: 面向实时TTS应用的推理系统优化


为了支持实时对话系统的集成，本研究针对 Text-to-Speech (TTS) 生成音频的动态特性，对GaussianTalker的推理管线进行了2项关键优化。这些改进解决了环境依赖冲突、跨模态长度不匹配以及显存资源占用过高的问题，确保了系统在生产环境下的鲁棒性。

#### 3.1 DeepSpeech特征提取的NumPy版本兼容性修复

**问题背景：**
在集成实时对话功能时，系统需调用DeepSpeech模块对TTS生成的.wav音频进行实时特征提取。由于项目依赖环境（特别是评估指标计算所需的TensorFlow库）强制将numpy升级至1.24+版本，新版NumPy已彻底移除并弃用了`np.float`数据类型。这导致原有的特征提取脚本在运行时抛出`AttributeError`，造成服务全链路崩溃。

**解决方案：**
对 `data_utils/deepspeech_features/deepspeech_features.py` 进行了优化，将过时的`np.float`显式替换为标准且兼容性更强的`np.float32`。

**优化效果：**
- 消除了版本冲突
- 提升了系统的环境鲁棒性
- 解决了因依赖包迭代导致的"环境腐烂"问题
- 确保模型在现代Python环境及后续版本中能够稳定运行

#### 3.2 任意长度音频驱动的动态帧数对齐 (Cross-Driving Alignment)

**问题背景：**
原版GaussianTalker的推理逻辑设计主要面向Self-driven（自我驱动）场景，预设音频长度与参考视频帧数严格对应。然而，在Real-time Chat（实时对话）场景下，TTS生成的回复音频长度是高度动态的（例如336帧），而模型加载的参考视频位姿（Camera Poses）往往是固定长度的（例如验证集视频为553帧）。

当音频播放结束，若渲染循环继续尝试索引后续的视频帧，会触发`IndexError`或`Tensor Dimension Mismatch`（张量维度不匹配），导致推理中断。

**解决方案：**
在 `scene/talking_dataset_readers.py` 中重构了数据加载逻辑，引入了"动态帧数对齐机制"。系统现在能够自动检测`custom_aud`（自定义音频）模式，并强制将渲染的总帧数限制为输入音频特征的长度，实现"以音频为基准"的截断。

**优化效果：**
- 实现了真正的 **Cross-modal Driving** (跨模态驱动) 能力
- 解除了模型对原视频长度的依赖
- 使其能够接受任意长度、任意内容的TTS语音输入并生成同步口型
- 这是实现"实时流式对话"功能的核心逻辑基石

## 故障排除

### 问题1: OpenFace提取AU失败
**解决方案**: 在前端勾选"手动上传AU文件"，提供预先提取的au.csv

### 问题2: 推理时找不到输出视频
**检查**:
- 模型是否训练完成
- 检查点文件是否存在（`output/{model_name}/checkpoints/`）
- 检查日志输出中的错误信息

### 问题3: 训练过程中断
**解决方案**: GaussianTalker支持从检查点恢复，重新运行train命令即可

### 问题4: Docker镜像构建失败
**检查**:
- 预训练模型是否都已放置
- 网络连接是否正常（需下载依赖包）
- 磁盘空间是否充足（至少20GB+）
