from flask import Flask, render_template, request, jsonify
import os
import uuid
import threading
from backend.video_generator import generate_video
from backend.model_trainer import train_model
from backend.chat_engine import chat_response, chat_pipeline

app = Flask(__name__)

# 简单的内存任务存储（生产环境请替换为持久化/队列）
TASKS = {}

def _process_chat_task(task_id, data):
    try:
        TASKS[task_id]["stage"] = "processing"
        # 确保目录
        os.makedirs('./static/audios', exist_ok=True)
        os.makedirs('./static/videos', exist_ok=True)

        # 执行主流程（内部会读取 ./static/audios/input.wav 等）
        video_path = chat_response(data)
        video_url = "/" + video_path.replace("\\", "/")
        TASKS[task_id]["stage"] = "completed"
        TASKS[task_id]["video_url"] = video_url
        TASKS[task_id]["status"] = "success"
    except Exception as e:
        TASKS[task_id]["stage"] = "error"
        TASKS[task_id]["status"] = "error"
        TASKS[task_id]["error"] = str(e)

# 首页
@app.route('/')
def index():
    return render_template('index.html')

# 视频生成界面
@app.route('/video_generation', methods=['GET', 'POST'])
def video_generation():
    if request.method == 'POST':
        data = {
            "model_name": request.form.get('model_name'),
            "model_param": request.form.get('model_param'),
            "ref_audio": request.form.get('ref_audio'),
            "gpu_choice": request.form.get('gpu_choice'),
            "target_text": request.form.get('target_text'),
        }

        video_path = generate_video(data)
        return jsonify({'status': 'success', 'video_path': video_path})

    return render_template('video_generation.html')


# 模型训练界面
@app.route('/model_training', methods=['GET', 'POST'])
def model_training():
    if request.method == 'POST':
        data = {
            "model_choice": request.form.get('model_choice'),
            "ref_video": request.form.get('ref_video'),
            "gpu_choice": request.form.get('gpu_choice'),
            "epoch": request.form.get('epoch'),
            "custom_params": request.form.get('custom_params')
        }

        video_path = train_model(data)
        video_path = "/" + video_path.replace("\\", "/")

        return jsonify({'status': 'success', 'video_path': video_path})

    return render_template('model_training.html')


# 实时对话系统界面
@app.route('/chat_system', methods=['GET', 'POST'])
def chat_system():
    if request.method == 'POST':
        data = {
            "model_name": request.form.get('model_name'),
            "model_param": request.form.get('model_param'),
            "voice_clone": request.form.get('voice_clone'),
            "api_choice": request.form.get('api_choice'),
        }

        try:
            result = chat_pipeline(data)
            tts_url = "/" + result["tts_audio_path"].replace("\\", "/") if result.get("tts_audio_path") else None
            video_url = "/" + result["video_path"].replace("\\", "/") if result.get("video_path") else None
            return jsonify({
                'status': 'success',
                'recognized_text': result.get('recognized_text'),
                'ai_text': result.get('ai_text'),
                'tts_audio_url': tts_url,
                'video_path': video_url
            })
        except Exception as e:
            return jsonify({'status': 'error', 'message': str(e)}), 500

    return render_template('chat_system.html')

@app.route('/chat/once', methods=['POST'])
def chat_once():
    # 接收音频（可选）与参数
    model_name = request.form.get('model_name', 'GaussianTalker')
    model_param = request.form.get('model_param', '')
    voice_clone = request.form.get('voice_clone')
    api_choice = request.form.get('api_choice')
    gpu_choice = request.form.get('gpu_choice', '0')
    iteration = request.form.get('iteration', '10000')

    # 处理音频文件（如果上传）
    if 'audio' in request.files and request.files['audio'] and request.files['audio'].filename:
        audio_file = request.files['audio']
        os.makedirs('./static/audios', exist_ok=True)
        # 为兼容现有 chat_engine，先固定写入 input.wav
        save_path = './static/audios/input.wav'
        audio_file.save(save_path)

    task_id = str(uuid.uuid4())
    TASKS[task_id] = {
        "task_id": task_id,
        "status": "queued",
        "stage": "queued",
        "video_url": None,
        "error": None
    }

    data = {
        "model_name": model_name,
        "model_param": model_param,
        "voice_clone": voice_clone,
        "api_choice": api_choice,
        "gpu_choice": gpu_choice,
        "iteration": iteration
    }

    t = threading.Thread(target=_process_chat_task, args=(task_id, data), daemon=True)
    t.start()

    return jsonify({"task_id": task_id, "status": "queued"})

@app.route('/chat/status', methods=['GET'])
def chat_status():
    task_id = request.args.get('id')
    if not task_id or task_id not in TASKS:
        return jsonify({"status": "error", "message": "invalid task id"}), 400
    return jsonify(TASKS[task_id])

@app.route('/save_audio', methods=['POST'])
def save_audio():
    if 'audio' not in request.files:
        return jsonify({'status': 'error', 'message': '没有音频文件'})
    
    audio_file = request.files['audio']
    if audio_file.filename == '':
        return jsonify({'status': 'error', 'message': '没有选择文件'})
    
    # 确保目录存在
    os.makedirs('./static/audios', exist_ok=True)
    
    # 保存文件
    audio_file.save('./static/audios/input.wav')
    
    return jsonify({'status': 'success', 'message': '音频保存成功'})


if __name__ == '__main__':
    # 关闭 reloader 以规避 watchdog 与 werkzeug 的不兼容导致的导入错误
    app.run(debug=True, port=5001, use_reloader=False)
