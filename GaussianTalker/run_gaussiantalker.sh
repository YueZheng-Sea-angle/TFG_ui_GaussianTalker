#!/bin/bash
# run_gaussiantalker.sh

set -e  # 遇到错误立即退出

# 基础变量
IMAGE_NAME="gaussiantalker:latest"
WORKSPACE="/GaussianTalker"
GAUSSIANTALKER_DIR="./GaussianTalker"  # 宿主机GaussianTalker目录

# 测试模式开关
TEST_MODE=${TEST_MODE:-0}

# 模拟Docker命令的函数
mock_docker() {
    if [ "$TEST_MODE" -eq 1 ]; then
        echo "[MOCK DOCKER] 模拟执行: $*"
        echo "  工作目录: $(pwd)"
        echo "  挂载点: $WORKSPACE"
        return 0
    else
        # 真实执行Docker命令
        docker "$@"
    fi
}

# 获取视频/目录名称
get_basename() {
    local file_path="$1"
    local basename=$(basename "$file_path")
    echo "${basename%.*}"
}

# 智能解析GPU参数
parse_gpu_arg() {
    local gpu_arg="$1"
    
    # 转换为大写方便处理
    local upper_arg=$(echo "$gpu_arg" | tr '[:lower:]' '[:upper:]')
    
    # 处理CPU情况
    if [[ "$upper_arg" == "CPU" ]]; then
        echo ""
        return 0
    fi
    
    # 处理GPU情况（格式：GPU0, GPU1, GPU2...）
    if [[ "$upper_arg" =~ ^GPU[0-9]+$ ]]; then
        local gpu_num=$(echo "$upper_arg" | sed 's/GPU//')
        echo "--gpus device=$gpu_num"
    else
        # 默认使用GPU0
        echo "--gpus device=0"
    fi
}

# 确保GaussianTalker目录结构存在
ensure_gaussiantalker_dirs() {
    mkdir -p "$GAUSSIANTALKER_DIR/data"
    mkdir -p "$GAUSSIANTALKER_DIR/output"
    mkdir -p "$GAUSSIANTALKER_DIR/audio"
    echo "GaussianTalker目录结构已创建: $GAUSSIANTALKER_DIR"
}

# 数据预处理函数
preprocess_only() {
    local video_path=""
    local gpu_arg="GPU0"
    
    # 解析参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            --video_path)
                video_path="$2"
                shift 2
                ;;
            --gpu)
                gpu_arg="$2"
                shift 2
                ;;
            *)
                echo "未知参数: $1"
                usage
                exit 1
                ;;
        esac
    done
    
    if [ -z "$video_path" ]; then
        echo "错误: 必须指定视频路径(--video_path)"
        usage
        exit 1
    fi
    
    if [ ! -f "$video_path" ]; then
        echo "错误: 视频文件不存在: $video_path"
        exit 1
    fi

    # 确保目录结构
    ensure_gaussiantalker_dirs

    # 获取视频名称
    local video_name=$(get_basename "$video_path")
    local data_dir="$GAUSSIANTALKER_DIR/data/${video_name}"
    
    # 解析GPU参数
    local gpu_param=$(parse_gpu_arg "$gpu_arg")
    
    echo "开始数据预处理..."
    echo "  - 输入视频: $video_path"
    echo "  - 数据目录: $data_dir"
    echo "  - GPU设置: $gpu_arg -> $gpu_param"
    
    # 创建数据目录
    mkdir -p "$data_dir"

    # 复制原视频到数据目录
    echo "复制原视频文件..."
    rsync -u "$video_path" "$data_dir/"
    
    # 获取GaussianTalker目录的绝对路径
    local gaussiantalker_abs=$(realpath "$GAUSSIANTALKER_DIR")
    
    # 执行预处理
    mock_docker run --rm $gpu_param \
        -v "$gaussiantalker_abs/data:$WORKSPACE/data" \
        $IMAGE_NAME \
        python data_utils/process.py "$WORKSPACE/data/${video_name}/$(basename "$video_path")"
    
    echo "预处理完成!"
    echo "数据保存在: $data_dir"
}

# 仅训练函数
train_only() {
    local data_dir=""
    local gpu_arg="GPU0"
    local iterations="10000"
    local config="arguments/64_dim_1_transformer.py"
    
    # 解析参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            --data_dir)
                data_dir="$2"
                shift 2
                ;;
            --gpu)
                gpu_arg="$2"
                shift 2
                ;;
            --iterations)
                iterations="$2"
                shift 2
                ;;
            --config)
                config="$2"
                shift 2
                ;;
            *)
                echo "未知参数: $1"
                usage
                exit 1
                ;;
        esac
    done
    
    if [ -z "$data_dir" ]; then
        echo "错误: 必须指定数据目录(--data_dir)"
        usage
        exit 1
    fi

    # 确保目录结构
    ensure_gaussiantalker_dirs

    local data_name=$(basename "$data_dir")
    local full_data_dir="$GAUSSIANTALKER_DIR/data/${data_name}"
    
    if [ ! -d "$full_data_dir" ]; then
        echo "错误: 数据目录不存在: $full_data_dir"
        echo "请先运行预处理步骤"
        exit 1
    fi
    
    local model_dir="$GAUSSIANTALKER_DIR/output/${data_name}"
    
    # 创建模型目录
    mkdir -p "$model_dir"
    
    # 解析GPU参数
    local gpu_param=$(parse_gpu_arg "$gpu_arg")
    
    echo "GaussianTalker开始模型训练..."
    echo "  - 数据目录: $full_data_dir"
    echo "  - 模型目录: $model_dir"
    echo "  - GPU设置: $gpu_arg -> $gpu_param"
    echo "  - 训练迭代数: $iterations"
    echo "  - 配置文件: $config"
    
    # 获取GaussianTalker目录的绝对路径
    local gaussiantalker_abs=$(realpath "$GAUSSIANTALKER_DIR")
    
    # 执行训练
    mock_docker run --rm $gpu_param \
        -v "$gaussiantalker_abs/data:$WORKSPACE/data" \
        -v "$gaussiantalker_abs/output:$WORKSPACE/output" \
        $IMAGE_NAME \
        python train.py \
        -s "$WORKSPACE/data/${data_name}" \
        --model_path "$WORKSPACE/output/${data_name}" \
        --configs "$config" \
        --iterations $iterations
    
    echo "GaussianTalker训练完成!"
    echo "模型保存在: $model_dir"
}

# 完整训练流程（预处理+训练）
train() {
    local video_path=""
    local gpu_arg="GPU0"
    local iterations="10000"
    local config="arguments/64_dim_1_transformer.py"
    
    # 解析参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            --video_path)
                video_path="$2"
                shift 2
                ;;
            --gpu)
                gpu_arg="$2"
                shift 2
                ;;
            --iterations)
                iterations="$2"
                shift 2
                ;;
            --config)
                config="$2"
                shift 2
                ;;
            *)
                echo "未知参数: $1"
                usage
                exit 1
                ;;
        esac
    done
    
    if [ -z "$video_path" ]; then
        echo "错误: 必须指定视频路径(--video_path)"
        usage
        exit 1
    fi
    
    echo "开始完整训练流程..."
    
    # 1. 首先进行预处理
    echo "步骤1: 数据预处理"
    preprocess_only --video_path "$video_path" --gpu "$gpu_arg"
    
    # 2. 然后进行训练
    echo "步骤2: 模型训练"
    local video_name=$(get_basename "$video_path")
    train_only --data_dir "$video_name" --gpu "$gpu_arg" --iterations "$iterations" --config "$config"
    
    echo "完整训练流程完成!"
    echo "GaussianTalker目录: $GAUSSIANTALKER_DIR"
}

# 推理函数
infer() {
    local model_dir=""
    local audio_path=""
    local gpu_arg="GPU0"
    local batch_size="128"
    local iteration="10000"
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --model_dir)
                model_dir="$2"
                shift 2
                ;;
            --audio_path)
                audio_path="$2"
                shift 2
                ;;
            --gpu)
                gpu_arg="$2"
                shift 2
                ;;
            --batch_size)
                batch_size="$2"
                shift 2
                ;;
            --iteration)
                iteration="$2"
                shift 2
                ;;
            *)
                echo "未知参数: $1"
                usage
                exit 1
                ;;
        esac
    done
    
    if [ -z "$model_dir" ]; then
        echo "错误: 必须指定模型目录(--model_dir)"
        usage
        exit 1
    fi
    
    if [ -z "$audio_path" ]; then
        echo "错误: 必须指定音频路径(--audio_path)"
        usage
        exit 1
    fi
    
    if [ ! -f "$audio_path" ]; then
        echo "错误: 音频文件不存在: $audio_path"
        exit 1
    fi
    
    # 确保目录结构
    ensure_gaussiantalker_dirs

    # 解析GPU参数
    local gpu_param=$(parse_gpu_arg "$gpu_arg")
    
    # 获取音频文件名称（不含扩展名）
    local audio_name=$(get_basename "$audio_path")
    
    # 获取模型目录名称
    local model_name=$(basename "$model_dir")
    local data_dir="$GAUSSIANTALKER_DIR/data/${model_name}"
    local full_model_dir="$GAUSSIANTALKER_DIR/output/${model_name}"
    
    if [ ! -d "$data_dir" ]; then
        echo "错误: 数据目录不存在: $data_dir"
        echo "请确保对应的预处理数据存在"
        exit 1
    fi
    
    if [ ! -d "$full_model_dir" ]; then
        echo "错误: 模型目录不存在: $full_model_dir"
        echo "请确保模型已训练完成"
        exit 1
    fi
    
    # 复制音频文件到数据目录
    local audio_dir="$data_dir"
    echo "复制音频文件到数据目录..."
    cp "$audio_path" "$audio_dir/"
    local audio_filename=$(basename "$audio_path")
    
    # 提取音频特征（假设是wav文件）
    local audio_basename="${audio_filename%.*}"
    
    echo "开始推理..."
    echo "  - GPU设置: $gpu_arg -> $gpu_param"
    echo "  - 模型目录: $full_model_dir"
    echo "  - 数据目录: $data_dir"
    echo "  - 音频文件: $audio_filename"
    echo "  - Batch Size: $batch_size"
    echo "  - Iteration: $iteration"
    
    # 获取GaussianTalker目录的绝对路径
    local gaussiantalker_abs=$(realpath "$GAUSSIANTALKER_DIR")
    
    # 首先需要提取音频特征
    echo "提取音频特征..."
    # 这里需要调用deepspeech特征提取
    # 为简化，假设用户已提前准备好.npy特征文件
    
    # 执行推理
    mock_docker run --rm $gpu_param \
        -v "$gaussiantalker_abs/data:$WORKSPACE/data" \
        -v "$gaussiantalker_abs/output:$WORKSPACE/output" \
        $IMAGE_NAME \
        python render.py \
        -s "$WORKSPACE/data/${model_name}" \
        --model_path "$WORKSPACE/output/${model_name}" \
        --configs arguments/64_dim_1_transformer.py \
        --iteration $iteration \
        --batch $batch_size \
        --custom_aud "${audio_basename}.npy" \
        --custom_wav "${audio_basename}.wav" \
        --skip_train \
        --skip_test
    
    # 输出视频位置
    local output_video="$full_model_dir/custom/ours_${iteration}/renders/output.mp4"
    
    echo "推理完成!"
    echo "输出视频: $output_video"
}

usage() {
    echo "用法: $0 <任务类型> [参数]"
    echo "可用任务:"
    echo "  train             - 完整训练流程（预处理+训练）"
    echo "  preprocess_only   - 仅数据预处理"
    echo "  train_only        - 仅训练（需要已有预处理数据）"
    echo "  infer             - 推理生成视频"
    echo ""
    echo "示例:"
    echo "  $0 train --video_path ./video.mp4 --gpu GPU0 --iterations 10000"
    echo "  $0 preprocess_only --video_path ./video.mp4 --gpu GPU1"
    echo "  $0 train_only --data_dir video_data --gpu GPU0 --iterations 5000"
    echo "  $0 infer --model_dir video_data --audio_path speech.wav --gpu GPU0"
}

# 主函数
main() {
    if [ $# -eq 0 ]; then
        usage
        exit 1
    fi
    
    case $1 in
        "train")
            shift
            train "$@"
            ;;
        "preprocess_only")
            shift
            preprocess_only "$@"
            ;;
        "train_only")
            shift
            train_only "$@"
            ;;
        "infer")
            shift
            infer "$@"
            ;;
        "-h"|"--help")
            usage
            ;;
        *)
            echo "错误: 未知任务 '$1'"
            usage
            exit 1
            ;;
    esac
}

main "$@"

