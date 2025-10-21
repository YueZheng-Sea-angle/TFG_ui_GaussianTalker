from flask import Flask, render_template, request, jsonify
import os
from backend.video_generator import generate_video
from backend.model_trainer import train_model
from backend.chat_engine import chat_response

app = Flask(__name__)

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
            "ref_audio": request.form.get('ref_audio'),
            "voice_clone": request.form.get('voice_clone'),
            "api_choice": request.form.get('api_choice'),
        }

        video_path = chat_response(data)
        video_path = "/" + video_path.replace("\\", "/")

        return jsonify({'status': 'success', 'video_path': video_path})

    return render_template('chat_system.html')


if __name__ == '__main__':
    app.run(debug=True, port = 5001)
