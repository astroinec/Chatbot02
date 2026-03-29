import requests
from google import genai
from fastapi import FastAPI, Request
import logging
import os
import io
import json
import datetime
from PIL import Image
from dotenv import load_dotenv

# 1. 环境初始化
load_dotenv()
app = FastAPI()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
MAKE_WEBHOOK_URL = os.getenv("MAKE_WEBHOOK_URL")

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

# 2. 初始化 Gemini 客户端
client = genai.Client(api_key=GEMINI_API_KEY)

def push_to_pipeline(res_json: dict):
    """
    【数据中台】将结构化数据推送到 Make.com 管道实现入库
    """
    if not MAKE_WEBHOOK_URL:
        logging.warning("⚠️ MAKE_WEBHOOK_URL 未配置，数据将无法存入 Google Sheets")
        return

    try:
        # 自动分流：根据字段特征判断文档类型
        doc_type = "Resume" if "name" in res_json else "Invoice"
        
        # 封装 Payload
        payload = {
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "doc_type": doc_type,
            "data": res_json
        }
        
        # 执行发射
        response = requests.post(MAKE_WEBHOOK_URL, json=payload, timeout=5)
        logging.info(f"🚀 管道发射成功 | 类型: {doc_type} | HTTP: {response.status_code}")
    except Exception as e:
        logging.error(f"❌ 管道发射失败: {e}")

@app.post("/webhook")
async def handle_webhook(request: Request):
    data = await request.json()
    message = data.get("message", {})
    chat_id = message.get("chat", {}).get("id")
    
    # 3. 图像获取逻辑
    image_data = None
    if "photo" in message:
        logging.info("📝 接收到业务图像，启动处理流...")
        file_id = message["photo"][-1]["file_id"]
        # ✅ 正确代码（纯净的 URL 字符串）
        file_info = requests.get(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getFile?file_id={file_id}").json()
        image_data = requests.get(f"https://api.telegram.org/file/bot{TELEGRAM_TOKEN}/{file_info['result']['file_path']}").content
    try:
        if image_data:
            # 4. 调用 Gemini 3.1 多模态能力
            # 注意：此处使用的 SOP 已包含在 system_instruction 中
            response = client.models.generate_content(
                model="gemini-3.1-flash-lite-preview",
                contents=[Image.open(io.BytesIO(image_data))],
                config={
                    'system_instruction': "你是一个企业级 OCR 审计专家。识别发票或简历并提取 JSON。发票字段：vendor, amount, currency, date, confidence_score, audit_status。简历字段：name, email, match_score, confidence_score, audit_status。只输出纯 JSON。",
                    'response_mime_type': 'application/json' 
                }
            )
            
            raw_text = response.text
            if raw_text:
                # 5. 数据解析与分流
                res_json = json.loads(raw_text)
                
                # 异步推送到 Google Sheets 管道
                push_to_pipeline(res_json)
                
                # 6. 生成用户回执
                doc_type_tag = "📄 简历" if "name" in res_json else "🧾 发票"
                status_icon = "✅" if res_json.get("audit_status") in ["Auto-Verified", "HR-Review"] else "⚠️"
                
                ai_reply = (
                    f"{status_icon} {doc_type_tag} 处理并入库成功！\n"
                    f"状态: `{res_json.get('audit_status')}`\n\n"
                    f"```json\n{json.dumps(res_json, indent=2, ensure_ascii=False)}\n```"
                )
            else:
                ai_reply = "🤖 无法解析图像内容，请重试。"
        else:
            ai_reply = "👋 你好！我是 Bot 02。请上传发票或简历照片，我将为您自动完成结构化入库。"

    except Exception as e:
        logging.error(f"❌ 系统异常: {e}")
        ai_reply = "🚨 业务流水线繁忙，请稍后再试。"

    # 7. 回传消息给用户
    requests.post(f"[https://api.telegram.org/bot](https://api.telegram.org/bot){TELEGRAM_TOKEN}/sendMessage", 
                  json={"chat_id": chat_id, "text": ai_reply, "parse_mode": "Markdown"})
    
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)