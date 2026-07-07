import httpx
from pyrogram import Client, filters
from pyrogram.enums import ChatAction
from config import Config
from ISTKHAR_CHATBOT.modules.db import get_user_context, save_user_context

# --- Source-Hopping AI Engines ---
async def call_openai(messages: list) -> str:
    """Primary GPT Engine with smart memory"""
    if not Config.OPENAI_API_KEY:
        raise Exception("OpenAI Key Missing")
    url = "https://api.openai.com/v1/chat/completions"
    headers = {"Authorization": f"Bearer {Config.OPENAI_API_KEY}"}
    payload = {"model": "gpt-4o-mini", "messages": messages}
    async with httpx.AsyncClient() as client:
        res = await client.post(url, json=payload, headers=headers, timeout=15.0)
        res.raise_for_status()
        return res.json()['choices'][0]['message']['content']

async def call_gemini(prompt: str) -> str:
    """Fallback Gemini Engine"""
    if not Config.GEMINI_API_KEY:
        raise Exception("Gemini Key Missing")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={Config.GEMINI_API_KEY}"
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    async with httpx.AsyncClient() as client:
        res = await client.post(url, json=payload, timeout=15.0)
        res.raise_for_status()
        return res.json()['candidates'][0]['content']['parts'][0]['text']

# --- Main Command Handler ---
@Client.on_message(filters.command(["gemini", "ai", "ask", "chatgpt"], prefixes=[".", "/"]))
async def advanced_ai_handler(client: Client, message):
    # Improved Command Parsing to handle both '.' and '/' prefixes safely
    command_prefix = message.text[0] # captures '.' or '/'
    bot_username = client.me.username if client.me else "ISTKHAR_CHATBOT"
    
    if message.text.startswith(f"{command_prefix}{message.command[0]}@{bot_username}") and len(message.command) > 1:
        user_input = message.text.split(" ", 1)[1]
    elif message.reply_to_message and message.reply_to_message.text:
        user_input = message.reply_to_message.text
    else:
        if len(message.command) > 1:
            user_input = " ".join(message.command[1:])
        else:
            await message.reply_text(f"💡 ᴇxᴀᴍᴘʟᴇ :- `{command_prefix}ask who is Narendra Modi`")
            return

    await client.send_chat_action(message.chat.id, ChatAction.TYPING)
    user_id = message.from_user.id
    
    # Context Processing
    history = await get_user_context(user_id)
    if not history:
        # System prompt defines the AI's core personality
        history.append({
            "role": "system", 
            "content": "You are a highly advanced AI developed by THE SHIV. Your persona is sharp, efficient, and carries a futuristic cyberpunk vibe. Provide accurate, helpful answers."
        })
    history.append({"role": "user", "content": user_input})
    
    ai_reply = ""
    
    # Auto-Fallback System
    try:
        # Puraani chats ke sath primary engine (OpenAI) ko try karega
        ai_reply = await call_openai(history)
    except Exception as e:
        print(f"[LOG] Primary API Failed: {e}")
        try:
            # Source-hop to Gemini if OpenAI blocks or fails
            ai_reply = await call_gemini(user_input) 
        except Exception as e2:
            print(f"[LOG] Fallback Failed: {e2}")
            error_msg = (
                "⚠️ sᴏʀʀʏ sɪʀ! ᴀʟʟ ᴀɪ ɴᴇᴛᴡᴏʀᴋs ᴀʀᴇ ᴄᴜʀʀᴇɴᴛʟʏ ᴅᴏᴡɴ. ᴘʟᴇᴀsᴇ ᴛʀʏ ᴀɢᴀɪɴ ʟᴀᴛᴇʀ.\n\n"
                "🛠️ **ᴘʟᴇᴀsᴇ ᴄᴏɴᴛᴀᴄᴛ sᴜᴘᴘᴏʀᴛ ᴛᴇᴀᴍ:** @betabot_support"
            )
            await message.reply_text(error_msg)
            return

    # History Save & Reply
    history.append({"role": "assistant", "content": ai_reply})
    await save_user_context(user_id, history)
    await message.reply_text(ai_reply, quote=True)
