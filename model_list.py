from google import genai

GEMINI_API_KEY = "AIzaSyDbkfYfcdYpzmjnjJ2Uw40Oa8pZdx9nG4U"
client = genai.Client(api_key=GEMINI_API_KEY)

print("🔍 --- 正在扫描你的全量 AI 军械库 ---")
for model in client.models.list():
    name = model.name or ""
    actions = model.supported_actions or []
    
    # 只要支持聊天（generateContent），我们就把它列出来
    if 'generateContent' in actions:
        model_id = name.split('/')[-1]
        display = model.display_name
        
        # 标注一下是不是“视觉/多模态”高手
        capability = "✅ 支持文字+视觉" if "flash" in model_id or "pro" in model_id else "✍️ 仅文字"
        
        print(f"ID: {model_id:<30} | {capability} | 名称: {display}")

    if '2.5' in name and 'generateContent' in actions:
        real_id = name.split('/')[-1]
        print(f"✨ 找到了！请把 MODEL_ID 改为: '{real_id}'")
        print(f"完整名称: {model.display_name}")