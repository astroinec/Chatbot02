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

load_dotenv()
app = FastAPI()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
MAKE_WEBHOOK_URL = os.getenv("MAKE_WEBHOOK_URL")

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
client = genai.Client(api_key=GEMINI_API_KEY)

# ==================== 【对齐表头的企业级 SOP】 ====================
BUSINESS_SOP = """
### 任务 ###
识别图片类型并提取 JSON。必须严格遵守以下 Schema 以匹配 Google Sheets 表头。

### 提取 Schema ###
#### 1. 如果是发票 (Invoices 表) ####
- vendor: 供应商名称 (对应 Vendor)
- amount: 数字 (对应 Amount)
- currency: 货币代码 (对应 Currency)
- date: YYYY-MM-DD (对应 Date)
- audit_status: 状态 (对应 Status)，置信度 > 0.8 设为 "已支付"，否则 "待处理"
- confidence_score: 0.0-1.0 (对应 Confidence)

#### 2. 如果是简历 (Resumes 表) ####
- name: 姓名 (对应 Name)
- contact: 邮箱 (对应 Contact)
- skills: 核心技能关键词 (对应 Skills)
- education: 最高学历 (对应 Education)
- match_score: 1-100 整数 (对应 Match_Score)
- audit_status: 统一设为 "初筛中" (对应 Status)
- confidence_score: 0.0-1.0 (内部审计用)

### 规则 ###
- 只输出纯净 JSON，严禁 Markdown 标签。
- 缺失字段填 null。
"""
# ==================================================================

def push_to_pipeline(res_json: dict):
    if not MAKE_WEBHOOK_URL: return
    try:
        doc_type = "Resume" if "name" in res_json else "Invoice"
        payload = {
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "doc_type": doc_type,
            "data": res_json
        }
        requests.post(MAKE_WEBHOOK_URL, json=payload, timeout=5)
    except Exception as e:
        logging.error(f"❌ 管道发射失败: {e}")

@app.post("/webhook")
async def handle_webhook(request: Request):
    data = await request.json()
    message = data.get("message", {})
    chat_id = message.get("chat", {}).get("id")
    
    image_data = None
    if "photo" in message:
        try:
            file_id = message["photo"][-1]["file_id"]
            info_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getFile?file_id={file_id}"
            file_info = requests.get(info_url).json()
            file_path = file_info['result']['file_path']
            download_url = f"https://api.telegram.org/file/bot{TELEGRAM_TOKEN}/{file_path}"
            image_data = requests.get(download_url).content
        except Exception: pass

    try:
        if image_data:
            response = client.models.generate_content(
                model="gemini-3.1-flash-lite-preview",
                contents=[Image.open(io.BytesIO(image_data))],
                config={'system_instruction': BUSINESS_SOP, 'response_mime_type': 'application/json'}
            )
            raw_text = response.text
            if raw_text:
                res_json = json.loads(raw_text)
                push_to_pipeline(res_json)
                
                doc_type = "📄 简历" if "name" in res_json else "🧾 发票"
                ai_reply = f"✅ {doc_type} 已同步至 Google Sheets\n\n```json\n{json.dumps(res_json, indent=2, ensure_ascii=False)}\n```"
            else: ai_reply = "🤖 无法解析图像。"
        else: ai_reply = "👋 请发送发票或简历照片。"
    except Exception: ai_reply = "🚨 系统繁忙。"

    send_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(send_url, json={"chat_id": chat_id, "text": ai_reply, "parse_mode": "Markdown"})
    return {"status": "ok"}