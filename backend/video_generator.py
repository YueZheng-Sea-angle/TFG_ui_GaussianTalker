import os
import time

def generate_video(data):
    """
    模拟视频生成逻辑：接收来自前端的参数，并返回一个视频路径。
    """
    print("[backend.video_generator] 收到数据：")
    for k, v in data.items():
        print(f"  {k}: {v}")

    
    if data['model_choice'] == "SyncTalk":
        # 模拟视频生成过程
        time.sleep(2)

    # 假设我们后端生成了视频：output.mp4
    # 实际中你可以将模型生成结果保存到这里
    video_path = os.path.join("static", "videos", "out.mp4")

    print(f"[backend.video_generator] 视频生成完成，路径：{video_path}")
    return video_path
