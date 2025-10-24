FROM nvidia/cuda:11.3.1-cudnn8-devel-ubuntu20.04

# 设置环境变量
ENV PYTHON_VERSION=3.7 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive \
    TZ=Asia/Shanghai \
    TORCH_CUDA_ARCH_LIST="6.0 6.1 7.0 7.5 8.0 8.6+PTX" \
    PYTHONPATH=/GaussianTalker

# 安装系统依赖
RUN ln -fs /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && \
    apt-get update && apt-get install -y \
    build-essential \
    cmake \
    g++ \
    gcc \
    python3.7 \
    python3.7-dev \
    python3-pip \
    python3.7-venv \
    python3-tk \
    tk-dev \
    ffmpeg \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgl1-mesa-glx \
    git \
    wget \
    curl \
    unzip \
    portaudio19-dev \
    libgomp1 \
    && update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.7 1 \
    && update-alternatives --install /usr/bin/python python /usr/bin/python3.7 1 \
    && python3 -m pip install --upgrade pip \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# 设置工作目录
WORKDIR /GaussianTalker

# 复制项目文件
COPY . .

# 克隆预训练模型，避免每次启动容器重新下载
COPY ./.cache/torch/hub/checkpoints /root/.cache/torch/hub/checkpoints

# 安装所有Python依赖
RUN pip install torch==1.13.1+cu117 torchvision==0.14.1+cu117 torchaudio==0.13.1 --extra-index-url https://download.pytorch.org/whl/cu117 && \
    pip install -r requirements.txt && \
    pip install "git+https://github.com/facebookresearch/pytorch3d.git" && \
    pip install tensorflow-gpu==2.8.0 && \
    pip install --upgrade "protobuf<=3.20.1" && \
    pip install -e submodules/custom-bg-depth-diff-gaussian-rasterization && \
    pip install -e submodules/simple-knn && \
    rm -rf ./.cache/ && \
    pip cache purge

# 默认命令
CMD ["python", "--help"]

