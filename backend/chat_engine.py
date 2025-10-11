import os
import time

def chat_response(data):
    """
    模拟实时对话系统视频生成逻辑。
    """
    print("[backend.chat_engine] 收到数据：")
    for k, v in data.items():
        print(f"  {k}: {v}")

    time.sleep(2)
    video_path = os.path.join("static", "videos", "chat_response.mp4")
    print(f"[backend.chat_engine] 生成视频路径：{video_path}")
    return video_path
