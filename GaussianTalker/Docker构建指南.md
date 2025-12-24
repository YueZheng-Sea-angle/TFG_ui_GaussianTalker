# docker_resources 文件夹结构说明

本文档说明在构建 Docker 镜像之前，需要在 `docker_resources` 文件夹中预先准备的文件和目录结构。

## 文件夹结构

```
docker_resources/
├── pytorch-2.0.1-cuda11.7.tar          # PyTorch 2.0.1 CUDA 11.7 版本 (约 6.4GB)
├── deepspeech-0_1_0-b90017e8.pb.zip    # DeepSpeech 模型文件 (约 434MB)
├── pretrained_weights/                 # 预训练权重文件夹
│   ├── 01_MorphableModel.mat
│   ├── 79999_iter.pth
│   ├── alexnet-owt-7be5be79.pth
│   ├── resnet18-5c106cde.pth
│   └── vgg16-397923af.pth
└── OpenFace 2.2.0/                     # OpenFace 2.2.0 目录
    └── TadasBaltrusaitis-OpenFace-658a6a1/
        └── (完整的 OpenFace 项目文件)
```

## 文件下载链接

### 根目录文件

#### pytorch-2.0.1-cuda11.7.tar
- **文件大小**: 约 6.4GB
- **下载链接**: [待填写]

#### deepspeech-0_1_0-b90017e8.pb.zip
- **文件大小**: 约 434MB
- **下载链接**: [待填写]

### pretrained_weights 目录文件

#### 01_MorphableModel.mat
- **下载链接**: [待填写]

#### 79999_iter.pth
- **下载链接**: [待填写]

#### alexnet-owt-7be5be79.pth
- **下载链接**: [待填写]

#### resnet18-5c106cde.pth
- **下载链接**: [待填写]

#### vgg16-397923af.pth
- **下载链接**: [待填写]

### OpenFace 2.2.0 目录

#### OpenFace 2.2.0 完整项目
- **下载链接**: [待填写]
- **说明**: 需要下载完整的 OpenFace 2.2.0 项目，解压后放置在 `OpenFace 2.2.0/TadasBaltrusaitis-OpenFace-658a6a1/` 目录下

## 文件处理说明

### 自动处理的文件

除了 `pytorch-2.0.1-cuda11.7.tar` 之外，以下所有文件在构建 Docker 镜像时会被自动处理：

- `deepspeech-0_1_0-b90017e8.pb.zip`
- `pretrained_weights/` 目录下的所有文件
- `OpenFace 2.2.0/` 目录下的所有文件

这些文件只需放置在 `docker_resources` 文件夹中，Docker 构建过程会自动识别并处理它们。

### 需要手动加载的文件

**pytorch-2.0.1-cuda11.7.tar** 需要手动加载到 Docker 中。此文件不会在 Docker 构建过程中自动处理，您需要单独将其加载到 Docker 环境。

#### 加载命令

在终端中执行以下命令来加载 PyTorch 镜像：

```bash
docker load -i docker_resources/pytorch-2.0.1-cuda11.7.tar
```

或者使用完整路径：

```bash
docker load -i /path/to/docker_resources/pytorch-2.0.1-cuda11.7.tar
```

**说明**：
- 确保在执行此命令前，文件已下载到 `docker_resources` 目录中
- 加载完成后，可以使用 `docker images` 命令查看已加载的镜像
- 此操作可能需要几分钟时间，请耐心等待

## 构建 Docker 镜像步骤

按照以下步骤构建完整的 Docker 镜像：

### 步骤 1：准备所有必需文件

确保 `docker_resources` 文件夹中包含以下所有文件：

- [ ] `pytorch-2.0.1-cuda11.7.tar`
- [ ] `deepspeech-0_1_0-b90017e8.pb.zip`
- [ ] `pretrained_weights/` 目录及其所有文件
- [ ] `OpenFace 2.2.0/` 目录及其完整内容

### 步骤 2：加载 PyTorch 镜像

在终端中执行以下命令加载 PyTorch 基础镜像：

```bash
docker load -i docker_resources/pytorch-2.0.1-cuda11.7.tar
```

**说明**：
- 加载完成后，可以使用 `docker images` 命令验证镜像是否已加载
- 此操作可能需要几分钟时间

### 步骤 3：进入项目根目录

```bash
cd GaussianTalker
```

### 步骤 4：构建 Docker 镜像

执行以下命令开始构建：

```bash
docker build -f Dockerfile.final -t gaussiantalker:latest .
```

**可选**：如果需要确保使用最新依赖（不使用缓存），可以添加 `--no-cache` 参数：

```bash
docker build --no-cache -f Dockerfile.final -t gaussiantalker:latest .
```

### 步骤 5：等待构建完成

**重要提示**：
- 构建过程会编译 OpenFace、dlib 以及自定义 CUDA 扩展，这些步骤非常耗时
- 整个构建过程可能需要 **1-3 小时**，具体时间取决于您的硬件配置
- 构建过程中会下载和编译大量依赖，请确保网络连接稳定
- **请耐心等待，不要中断构建过程**

### 步骤 6：验证构建结果

构建完成后，使用以下命令验证镜像是否创建成功：

```bash
docker images | grep gaussiantalker
```

如果看到镜像列表，说明构建成功！

### 步骤 7：验证 PyTorch 和 CUDA

进一步检查 PyTorch 和 CUDA 是否正常：

```bash
docker run --rm --gpus all gaussiantalker:latest \
  python -c "import torch; print('PyTorch:', torch.__version__); print('CUDA available:', torch.cuda.is_available())"
```

### 步骤 8：验证 OpenFace（FeatureExtraction）

为了保证后续 `run_gaussiantalker.sh` 能正确调用 OpenFace 提取 AU，推荐在构建完成后，进入容器内测试一次 `FeatureExtraction`：

```bash
docker run --rm -it gaussiantalker:latest bash
```

在容器内执行：

```bash
FeatureExtraction -h 2>&1 | head -1 || echo "OpenFace still broken"
```

**预期结果**：
- 如果看到的是 OpenFace 的帮助信息或提示（例如 `Could not find the HAAR face detector location`），说明 OpenFace 的二进制已经正常启动。

**如果遇到错误，请参考以下解决方法：**

#### 错误 1：缺少 `libwebp.so.7`

**错误信息**：
```text
FeatureExtraction: error while loading shared libraries: libwebp.so.7: cannot open shared object file: No such file or directory
```

**解决方法（容器内执行）**：

```bash
apt-get update
apt-get install -y libwebp-dev

cd /usr/lib/x86_64-linux-gnu
ls libwebp*
# 如果只有 libwebp.so.6 / libwebp.so.6.0.2 等，没有 libwebp.so.7：
ln -s libwebp.so.6 libwebp.so.7
ldconfig
```

#### 错误 2：缺少 `libmkl_rt.so.2`（MKL 动态库）

**错误信息**：
```text
FeatureExtraction: error while loading shared libraries: libmkl_rt.so.2: cannot open shared object file: No such file or directory
```

**解决方法（容器内执行）**：

```bash
# 确认 MKL 在 conda 中
find / -name "libmkl_rt.so*" 2>/dev/null
# 通常会看到 /opt/conda/lib/libmkl_rt.so.2

ln -s /opt/conda/lib/libmkl_rt.so.2 /usr/lib/x86_64-linux-gnu/libmkl_rt.so.2
ldconfig
```

#### 错误 3：缺少 OpenFace 自己的动态库（例如 `libLandmarkDetector.so`）

**错误信息**：
```text
FeatureExtraction: error while loading shared libraries: libLandmarkDetector.so: cannot open shared object file: No such file or directory
```

**解决方法（容器内执行）**：

```bash
unset LD_LIBRARY_PATH
export LD_LIBRARY_PATH=/opt/OpenFace/build/lib
```

然后再次测试：

```bash
FeatureExtraction -h 2>&1 | head -1
```

#### 错误 4：`ffi_type_uint32` / `LIBFFI_BASE_7.0` 相关的符号错误

**错误信息**：
```text
FeatureExtraction: symbol lookup error: /lib/x86_64-linux-gnu/libgobject-2.0.so.0: undefined symbol: ffi_type_uint32, version LIBFFI_BASE_7.0
```

通常是因为把 `/opt/conda/lib` 整体加入了 `LD_LIBRARY_PATH`，导致 conda 版本的 `libffi` 覆盖了系统版本。

**解决方法（容器内执行）**：

```bash
unset LD_LIBRARY_PATH
export LD_LIBRARY_PATH=/opt/OpenFace/build/lib
# 如果还需要 MKL，仅通过软链接暴露 libmkl_rt.so.2（见上文），不要把 /opt/conda/lib 整包加进去
```

#### 验证修复结果

修复后再次运行：

```bash
FeatureExtraction -h 2>&1 | head -1
```

不再出现缺少 `.so` 或符号错误，而是输出帮助信息 / 模型路径提示，则可以认为 **OpenFace 环境正常**，后续 `run_gaussiantalker.sh` 中的 AU 提取（生成 `<video_name>.csv` 和 `au.csv`）就可以正常工作。

### 完成

如果以上所有验证步骤都能正常执行，说明 Docker 环境已经准备好，可以进入训练/推理阶段。
