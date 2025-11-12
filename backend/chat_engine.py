import os
import subprocess
import speech_recognition as sr
from zhipuai import ZhipuAI
import pyttsx3
from backend.voice_cloner import synthesize_with_clone

def chat_response(data):
    """
    实时对话系统：ASR -> LLM -> TTS（本地）
    现阶段仍返回占位视频，后续可接入视频生成。
    """
    print("[backend.chat_engine] 收到数据：")
    for k, v in data.items():
        print(f"  {k}: {v}")

    # 确保目录存在
    os.makedirs('./static/audios', exist_ok=True)
    os.makedirs('./static/text', exist_ok=True)

    # 语音转文字（使用用户上传的录音）
    input_audio = "./static/audios/input.wav"
    input_text = "./static/text/input.txt"
    recognized_text = audio_to_text(input_audio, input_text)
    if not recognized_text:
        # 当识别失败时，写入一个默认文本，避免后续读取文件报错
        fallback_text = "你好，我的麦克风音频可能无效，请继续以文字方式交流。"
        with open(input_text, 'w', encoding='utf-8') as f:
            f.write(fallback_text)
        recognized_text = fallback_text

    # 大模型回答
    output_text = "./static/text/output.txt"
    api_key = "59086bcdaac941d18fd92545b7417739.OSRp1IXGkA3OMKAQ"
    model = "glm-4.5-flash"
    ai_response = get_ai_response(input_text, output_text, api_key, model)

    # 文本转语音（本地 TTS）
    output_audio = "./static/audios/ai_response.wav"
    text_to_speech(ai_response, output_audio)

    
    video_path = os.path.join("static", "videos", "chat_response.mp4")
    print(f"[backend.chat_engine] 生成视频路径：{video_path}")
    return video_path

def chat_pipeline(data):
    os.makedirs('./static/audios', exist_ok=True)
    os.makedirs('./static/text', exist_ok=True)

    input_audio = "./static/audios/input.wav"
    input_text = "./static/text/input.txt"
    recognized_text = audio_to_text(input_audio, input_text)
    if not recognized_text:
        fallback_text = "你好，我的麦克风音频可能无效，请继续以文字方式交流。"
        with open(input_text, 'w', encoding='utf-8') as f:
            f.write(fallback_text)
        recognized_text = fallback_text

    output_text = "./static/text/output.txt"
    api_key = ""
    model = "glm-4-flash"
    ai_response = get_ai_response(input_text, output_text, api_key, model)

    # 选择TTS：优先尝试语音克隆，失败则回退到本地pyttsx3
    output_audio = "./static/audios/ai_response.wav"
    tts_audio_path = None

    # 解析语音克隆参数
    voice_clone = (data.get('voice_clone') or '').strip() if isinstance(data, dict) else ''
    ref_audio_path = None
    if voice_clone:
        # 预设：cloneA/cloneB -> static/voices/{name}.wav
        if voice_clone.lower() in ("clonea", "cloneb"):
            preset_dir = os.path.join("static", "voices")
            preset_path = os.path.join(preset_dir, f"{voice_clone}.wav")
            if os.path.exists(preset_path):
                ref_audio_path = preset_path
        # 使用当前录音作为参考
        elif voice_clone.lower() in ("use_input", "input", "current"):
            if os.path.exists(input_audio):
                ref_audio_path = input_audio
        # 若传入自定义路径
        elif os.path.exists(voice_clone):
            ref_audio_path = voice_clone

    if ref_audio_path and os.path.exists(ref_audio_path):
        try:
            tts_audio_path = synthesize_with_clone(ai_response, ref_audio_path, output_audio, language='zh')
        except Exception as e:
            print(f"[backend.chat_engine] 语音克隆失败，将回退到本地TTS。原因: {e}")

    if not tts_audio_path:
        tts_audio_path = text_to_speech(ai_response, output_audio)

    video_path = os.path.join("static", "videos", "chat_response.mp4")
    return {
        "recognized_text": recognized_text,
        "ai_text": ai_response,
        "tts_audio_path": tts_audio_path if tts_audio_path else (output_audio if os.path.exists(output_audio) else None),
        "video_path": video_path,
    }

def _ffmpeg_convert_to_pcm16_mono_16k(src_path, dst_path):
    """尝试用 ffmpeg 转为 16k/16bit mono PCM WAV。返回 True/False。"""
    try:
        cmd = [
            'ffmpeg', '-y', '-i', src_path,
            '-ac', '1', '-ar', '16000', '-c:a', 'pcm_s16le',
            dst_path
        ]
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode == 0 and os.path.exists(dst_path) and os.path.getsize(dst_path) > 0:
            print('[backend.chat_engine] 已使用 ffmpeg 规范化音频为 PCM16 mono 16k')
            return True
        else:
            print('[backend.chat_engine] ffmpeg 转码失败:', result.stderr[-500:])
            return False
    except FileNotFoundError:
        print('[backend.chat_engine] 未找到 ffmpeg，请安装或加入 PATH 后再试')
        return False
    except Exception as e:
        print('[backend.chat_engine] ffmpeg 调用异常:', e)
        return False


def audio_to_text(input_audio, input_text):
    try:
        # 初始化识别器
        recognizer = sr.Recognizer()
        
        def _recognize_from_file(path):
            with sr.AudioFile(path) as source:
                # 调整环境噪声
                recognizer.adjust_for_ambient_noise(source)
                # 读取音频数据
                audio_data = recognizer.record(source)
                print("正在识别语音...")
                # 使用Google语音识别
                return recognizer.recognize_google(audio_data, language='zh-CN')

        # 第一次尝试直接读取
        try:
            text = _recognize_from_file(input_audio)
        except Exception as e:
            print('[backend.chat_engine] 直接读取音频失败，将尝试转码。原因:', e)
            # 若失败，尝试用 ffmpeg 转码后再识别
            tmp_converted = os.path.join(os.path.dirname(input_audio), '__converted_tmp__.wav')
            if _ffmpeg_convert_to_pcm16_mono_16k(input_audio, tmp_converted):
                text = _recognize_from_file(tmp_converted)
                try:
                    os.remove(tmp_converted)
                except Exception:
                    pass
            else:
                # 转码失败则抛给外层 except 流程
                raise
        
        # 将结果写入文件
        with open(input_text, 'w', encoding='utf-8') as f:
            f.write(text)
        print(f"语音识别完成！结果已保存到: {input_text}")
        print(f"识别结果: {text}")
        return text
            
    except sr.UnknownValueError:
        print("无法识别音频内容")
    except sr.RequestError as e:
        print(f"语音识别服务错误: {e}")
    except FileNotFoundError:
        print(f"音频文件不存在: {input_audio}")
    except Exception as e:
        print(f"发生错误: {e}")

def get_ai_response(input_text, output_text, api_key, model):
    try:
        # 优先从环境变量读取密钥，若无则使用传入值
        api_key_env = os.getenv('ZHIPUAI_API_KEY')
        api_key_eff = (api_key_env if api_key_env else api_key or '').strip()
        # 关键校验：智谱密钥一般为 "{id}.{secret}" 两段形式
        if '.' not in api_key_eff or len(api_key_eff.split('.')) != 2:
            raise ValueError("无效的 ZHIPUAI_API_KEY：应为 id.secret 的两段形式，且不要包含引号/空格")
        client = ZhipuAI(api_key=api_key_eff)
        with open(input_text, 'r', encoding='utf-8') as file:
            content = file.read().strip()

        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": content}]
        )
        output = response.choices[0].message.content

        with open(output_text, 'w', encoding='utf-8') as file:
            file.write(output)

        print(f"答复已保存到: {output_text}")
        return output
    except Exception as e:
        # 失败兜底：直接把用户文本回声，避免整体 500
        print(f"[backend.chat_engine] 调用大模型失败，使用兜底回复。原因: {e}")
        try:
            with open(input_text, 'r', encoding='utf-8') as f:
                fallback = f.read().strip()
            if not fallback:
                fallback = "抱歉，目前无法连接大模型服务。"
        except Exception:
            fallback = "抱歉，目前无法连接大模型服务。"
        try:
            with open(output_text, 'w', encoding='utf-8') as f:
                f.write(fallback)
        except Exception:
            pass
        return fallback

def text_to_speech(text, output_audio_path):
    """
    使用本地 TTS 引擎（pyttsx3）将文本合成为语音文件。
    Windows 默认使用 SAPI5，无需联网。
    """
    try:
        if not text:
            print("[backend.chat_engine] TTS 跳过：文本为空")
            return None

        os.makedirs(os.path.dirname(output_audio_path), exist_ok=True)

        engine = pyttsx3.init()
        # 基础参数可按需调整
        engine.setProperty('rate', 160)
        engine.setProperty('volume', 0.9)

        engine.save_to_file(text, output_audio_path)
        engine.runAndWait()

        print(f"[backend.chat_engine] 语音合成成功: {output_audio_path}")
        return output_audio_path
    except Exception as e:
        print(f"[backend.chat_engine] TTS 错误: {e}")
        return None