# 说话人脸生成对话系统

## 系统流程

```
[用户点击“生成视频”按钮]
        ↓
[前端 JS 捕获表单数据并用 fetch 发送 POST 请求]
        ↓
[Flask 路由接收 request.form]
        ↓
[调用 backend/video_generator.py 中的函数 generate_video()]
        ↓
[后端函数返回生成视频的路径]
        ↓
[Flask 把路径以 JSON 形式返回给前端]
        ↓
[前端 JS 接收到路径 → 替换 <video> 标签的 src → 自动播放视频]
```

## Demo 使用方法

1. 安装依赖：
   ```bash
   pip install flask
   ```

2. 启动应用：
   ```bash
   python app.py
   ```

3. 访问应用：
   打开 http://127.0.0.1:5000

4. 点击探索功能