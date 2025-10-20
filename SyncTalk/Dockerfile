FROM nvidia/cuda:11.3.1-cudnn8-devel-ubuntu20.04

# 设置Python版本
ENV PYTHON_VERSION=3.8
ENV PYTHONUNBUFFERED=1

# 设置非交互式
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Asia/Shanghai

# 预先设置时区
RUN ln -fs /usr/share/zoneinfo/Asia/Shanghai /etc/localtime

# 安装系统依赖和Python
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    g++ \
    gcc \
    python3.8 \
    python3.8-dev \
    python3-pip \
    python3.8-venv \
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
    build-essential \
    portaudio19-dev \
    && rm -rf /var/lib/apt/lists/*

# 设置Python3.8为默认
RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.8 1
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.8 1

# 升级pip
RUN python3 -m pip install --upgrade pip

# 设置 CUDA 架构环境变量
ENV TORCH_CUDA_ARCH_LIST="6.0 6.1 7.0 7.5 8.0 8.6+PTX"

# 设置工作目录
WORKDIR /SyncTalk

# 克隆SyncTalk仓库
COPY . .

# # 克隆预训练模型
# COPY ./.cache/checkpoints /root/.cache/torch/hub/checkpoints

# 安装依赖
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install torch==1.12.1+cu113 torchvision==0.13.1+cu113 torchaudio==0.12.1 --extra-index-url https://download.pytorch.org/whl/cu113
# RUN pip install --no-index --find-links ./packages \
#     torch==1.12.1+cu113 torchvision==0.13.1+cu113 torchaudio==0.12.1 --extra-index-url https://download.pytorch.org/whl/cu113
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -r requirements.txt
# RUN pip install --no-index --find-links ./packages \
#     -r requirements.txt
RUN pip install --no-index --no-cache-dir pytorch3d \
    -f https://dl.fbaipublicfiles.com/pytorch3d/packaging/wheels/py38_cu113_pyt1121/download.html
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install tensorflow-gpu==2.8.1
# RUN pip install --no-index --find-links ./packages \
#     tensorflow-gpu==2.8.1

# 安装本地包
RUN pip install ./freqencoder
RUN pip install ./shencoder
RUN pip install ./gridencoder
RUN pip install ./raymarching

# 安装后删除 packages 节省空间
RUN rm -rf ./packages/

# 在安装后清理
RUN apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* && \
    pip cache purge

# 设置环境变量
ENV PYTHONPATH=/SyncTalk

# 默认命令
CMD ["python", "--help"]