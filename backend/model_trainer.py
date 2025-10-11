import os
import time

def train_model(data):
    """
    模拟模型训练逻辑。
    """
    print("[backend.model_trainer] 收到数据：")
    for k, v in data.items():
        print(f"  {k}: {v}")

    print("[backend.model_trainer] 模型训练中...")
    if data['model_choice'] == "SyncTalk":
        time.sleep(3)  # 模拟训练过程
    video_path = os.path.join("static", "videos", "train_result.mp4")
    print(f"[backend.model_trainer] 训练完成，结果视频：{video_path}")
    return video_path
