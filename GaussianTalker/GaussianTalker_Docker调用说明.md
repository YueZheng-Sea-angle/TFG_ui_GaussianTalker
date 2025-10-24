# GaussianTalker Docker 调用说明

## 简介

GaussianTalker是一个基于3D Gaussian Splatting的实时高保真说话人脸合成系统。本文档说明如何使用Docker容器化部署和运行GaussianTalker。

## 构建Docker镜像

```bash
cd GaussianTalker
./download_pretrained.sh
# 按指引下载01_MorphableModel.mat到data_utils/face_tracking/3DMM/
docker build -t gaussiantalker .
```

**注意:** 构建过程可能需要较长时间（30分钟-1小时），因为需要编译CUDA扩展和安装PyTorch3D。

## 打包Docker镜像

```bash
docker save -o gaussiantalker.tar gaussiantalker
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
    │       ├── gt_imgs/         # Ground truth图像
    │       ├── ori_imgs/        # 原始图像
    │       ├── parsing/         # 人脸解析结果
    │       ├── torso_imgs/      # 躯干图像
    │       ├── au.csv           # 眼睛眨眼AU特征
    │       ├── aud_ds.npy       # DeepSpeech音频特征
    │       ├── aud.wav          # 音频文件
    │       └── transforms_*.json # 相机变换参数
    ├── output/                  # 模型输出目录
    │   └── {视频名称}/          # 训练好的模型
    │       ├── point_cloud/     # 点云数据
    │       ├── cfg_args         # 配置参数
    │       └── test/            # 测试结果
    │           └── ours_{N}/    # 推理结果
    │               └── renders/ # 渲染视频
    └── audio/                   # 推理用音频文件目录
```

## 脚本调用命令

### train - 完整训练流程

```bash
./run_gaussiantalker.sh train \
    --video_path <视频文件路径> \
    --gpu <GPU设备> \
    --iterations <训练迭代数> \
    --config <配置文件>
```

**参数说明：**
- `--video_path`: 输入视频文件路径（必需）
- `--gpu`: GPU设备（默认: GPU0）
  - `GPU0`, `GPU1`, `GPU2`, ... - 指定GPU
  - `CPU` - 使用CPU（不推荐，训练非常慢）
- `--iterations`: 训练迭代数（默认: 10000）
- `--config`: 配置文件路径（默认: arguments/64_dim_1_transformer.py）

**示例：**
```bash
./run_gaussiantalker.sh train \
    --video_path ./my_video.mp4 \
    --gpu GPU0 \
    --iterations 10000 \
    --config arguments/64_dim_1_transformer.py
```

### preprocess_only - 仅数据预处理

```bash
./run_gaussiantalker.sh preprocess_only \
    --video_path <视频文件路径> \
    --gpu <GPU设备>
```

**示例：**
```bash
./run_gaussiantalker.sh preprocess_only \
    --video_path ./training_video.mp4 \
    --gpu GPU0
```

**预处理步骤包括：**
1. 人脸检测和关键点提取
2. 人脸解析（segmentation）
3. 3DMM参数拟合
4. 音频特征提取（DeepSpeech）
5. 生成训练用的transforms文件

### train_only - 仅模型训练

```bash
./run_gaussiantalker.sh train_only \
    --data_dir <数据目录名称> \
    --gpu <GPU设备> \
    --iterations <训练迭代数> \
    --config <配置文件>
```

**注意：** 需要先运行预处理步骤生成数据

**示例：**
```bash
./run_gaussiantalker.sh train_only \
    --data_dir my_video \
    --gpu GPU0 \
    --iterations 10000 \
    --config arguments/64_dim_1_transformer.py
```

### infer - 视频推理

```bash
./run_gaussiantalker.sh infer \
    --model_dir <模型目录名称> \
    --audio_path <音频文件路径> \
    --gpu <GPU设备> \
    --batch_size <批处理大小> \
    --iteration <检查点迭代数>
```

**参数说明：**
- `--model_dir`: 模型目录名称（与数据目录名称相同）
- `--audio_path`: 驱动音频文件路径（支持.wav格式）
- `--gpu`: GPU设备（默认: GPU0）
- `--batch_size`: 批处理大小（默认: 128，根据显存调整）
- `--iteration`: 使用的检查点迭代数（默认: 10000）

**示例：**
```bash
./run_gaussiantalker.sh infer \
    --model_dir my_video \
    --audio_path ./speech.wav \
    --gpu GPU0 \
    --batch_size 128 \
    --iteration 10000
```

**推理前准备：**
1. 确保音频文件为.wav格式
2. 需要提前提取音频的DeepSpeech特征（.npy文件）
3. 音频文件和特征文件应放在数据目录中

## 输出文件说明

### 训练完成后
- **数据目录**: `GaussianTalker/data/{视频名称}/`
- **模型目录**: `GaussianTalker/output/{视频名称}/`
- **点云文件**: `GaussianTalker/output/{视频名称}/point_cloud/iteration_{N}/point_cloud.ply`

### 推理完成后
- **输出视频**: `GaussianTalker/output/{视频名称}/custom/ours_{N}/renders/output.mp4`

## 配置文件说明

GaussianTalker提供两种主要配置：

1. **64_dim_1_transformer.py** - 使用1层Transformer（推荐，速度快）
2. **64_dim_2_transformer.py** - 使用2层Transformer（质量更高，速度稍慢）

可以根据需求选择不同的配置文件。

## 测试模式

在不构建Docker镜像的情况下测试脚本逻辑：

```bash
# 启用测试模式
TEST_MODE=1 ./run_gaussiantalker.sh train \
    --video_path ./test.mp4 \
    --gpu GPU0 \
    --iterations 1000

TEST_MODE=1 ./run_gaussiantalker.sh infer \
    --model_dir test \
    --audio_path ./test.wav
```

## 注意事项

### 系统要求
- **GPU**: NVIDIA GPU with CUDA 11.3+（推荐RTX 3090或更高）
- **显存**: 至少12GB VRAM（24GB推荐）
- **内存**: 至少16GB RAM
- **存储**: 每个训练项目约需5-10GB空间

### 训练建议
1. **视频要求**：
   - 分辨率: 至少720p，推荐1080p
   - 时长: 3-5分钟（足够学习人脸特征）
   - 内容: 单人正面说话视频，光照稳定
   - 格式: mp4, avi, mov等常见格式

2. **训练参数**：
   - 迭代数10000次通常足够（约1-2小时）
   - 可以根据中间结果调整迭代数
   - 使用较小的batch_size如果显存不足

3. **音频处理**：
   - 音频采样率: 16kHz推荐
   - 格式: .wav（未压缩）
   - 需要提前提取DeepSpeech特征

### 常见问题

**Q: 预处理时提示找不到人脸？**
A: 确保视频中人脸清晰可见，光照充足。可以尝试提高视频分辨率。

**Q: 训练过程中显存溢出？**
A: 减小batch_size或使用更大的GPU。

**Q: 推理时提示找不到检查点文件？**
A: 确保训练已完成，检查`output/{model_name}/point_cloud/`目录中是否有对应迭代数的检查点。

**Q: 如何提取DeepSpeech特征？**
A: 使用`data_utils/deepspeech_features/extract_ds_features.py`脚本提取音频特征。

## 完整工作流程示例

```bash
# 1. 准备训练视频
# 视频应为3-5分钟的单人说话视频

# 2. 完整训练（预处理+训练）
./run_gaussiantalker.sh train \
    --video_path ./obama.mp4 \
    --gpu GPU0 \
    --iterations 10000

# 3. 等待训练完成（约1-2小时）

# 4. 准备推理音频
# 将音频文件复制到数据目录，并提取特征

# 5. 执行推理
./run_gaussiantalker.sh infer \
    --model_dir obama \
    --audio_path ./speech.wav \
    --gpu GPU0 \
    --batch_size 128

# 6. 查看结果视频
# 输出在: GaussianTalker/output/obama/custom/ours_10000/renders/output.mp4
```

## 性能优化

1. **训练优化**：
   - 使用更强大的GPU（如A100, RTX 4090）
   - 启用混合精度训练（需修改配置）
   - 使用多GPU并行训练（需修改脚本）

2. **推理优化**：
   - 增大batch_size利用GPU并行能力
   - 减少渲染分辨率（如果不需要高分辨率）

3. **存储优化**：
   - 定期清理中间训练结果
   - 压缩完成的模型文件

## 技术支持

如遇到问题，请检查：
1. Docker日志: `docker logs <container_id>`
2. 模型训练日志: `GaussianTalker/output/{model_name}/`
3. 系统资源使用: `nvidia-smi`

## 引用

如果使用GaussianTalker，请引用原论文：
```
@inproceedings{cho2024gaussiantalker,
  title={Gaussiantalker: Real-time talking head synthesis with 3d gaussian splatting},
  author={Cho, Kyusun and Lee, Joungbin and Yoon, Heeji and Hong, Yeobin and Ko, Jaehoon and Ahn, Sangjun and Kim, Seungryong},
  booktitle={Proceedings of the 32nd ACM International Conference on Multimedia},
  pages={10985--10994},
  year={2024}
}
```

## 许可证

GaussianTalker采用非商业研究许可证。详见LICENSE.md。

