import httpx
from pyrogram import Client, filters
from pyrogram.enums import ChatAction
from config import Config
from ISTKHAR_CHATBOT.modules.db import get_user_context, save_user_context, reset_user_context

async def call_openrouter(messages: list) -> str:
    """OpenRouter Engine with Auto Key-Shifting Logic"""
    if not Config.OPENROUTER_KEYS:
        raise Exception("OpenRouter Keys Missing from config!")

    url = "https://openrouter.ai/api/v1/chat/completions"
    
    # OpenRouter mein aap 'openai/gpt-4o-mini' ya koi bhi free/paid model use kar sakte hain
    payload = {
        "model": "openai/gpt-4o-mini", 
        "messages": messages
    }

    # Yeh loop 1 by 1 saari keys try karega
    for idx, api_key in enumerate(Config.OPENROUTER_KEYS):
        headers = {
            "Authorization": f"Bearer {api_key}",
            "HTTP-Referer": "https://t.me/betabot_support", # Optional but recommended by OpenRouter
            "X-Title": "IstkharChatbot"                     # Optional but recommended
        }
        
        try:
            async with httpx.AsyncClient() as client:
                res = await client.post(url, json=payload, headers=headers, timeout=15.0)
                res.raise_for_status() # Agar API limit/balance khatam hai toh error dega
                return res.json()['choices'][0]['message']['content']
                
        except Exception as e:
            print(f"[LOG] OpenRouter Key {idx + 1} Failed: {e}")
            # Agar error aaya, toh loop continue hoga aur NEXT key try karega
            continue

    # Agar loop yahan tak pohoch gaya, matlab TEENO keys fail ho chuki hain
    raise Exception("All 3 OpenRouter API Keys Failed.")


@Client.on_message(filters.command(["gemini", "ai", "ask", "chatgpt"], prefixes=[".", "/"]))
async def advanced_ai_handler(client: Client, message):
    command_prefix = message.text[0]
    bot_username = client.me.username if client.me else "ISTKHAR_CHATBOT"
    
    if message.text.startswith(f"{command_prefix}{message.command[0]}@{bot_username}") and len(message.command) > 1:
        user_input = message.text.split(" ", 1)[1]
    elif message.reply_to_message and message.reply_to_message.text:
        user_input = message.reply_to_message.text
    else:
        if len(message.command) > 1:
            user_input = " ".join(message.command[1:])
        else:
            await message.reply_text(f"💡 ᴇxᴀᴍᴘʟᴇ :- `{command_prefix}ask what is AI?`")
            return

    await client.send_chat_action(message.chat.id, ChatAction.TYPING)
    user_id = message.from_user.id
    
    # Memory Context Fetch
    history = await get_user_context(user_id)
    if not history:
        history.append({
            "role": "system", 
            "content": "You are a highly advanced AI developed by THE SHIV. Your persona is sharp, efficient, and carries a futuristic cyberpunk vibe. Provide accurate, helpful answers."
        })
    history.append({"role": "user", "content": user_input})
    
    try:
        # Call OpenRouter (Jo khud 3 keys handle karega)
        ai_reply = await call_openrouter(history)
    except Exception as e:
        print(f"[LOG] System Error: {e}")
        error_msg = (
            "⚠️ sᴏʀʀʏ sɪʀ! ᴀʟʟ ᴀɪ ɴᴇᴛᴡᴏʀᴋs ᴀʀᴇ ᴄᴜʀʀᴇɴᴛʟʏ ᴅᴏᴡɴ. ᴘʟᴇᴀsᴇ ᴛʀʏ ᴀɢᴀɪɴ ʟᴀᴛᴇʀ.\n\n"
            "🛠️ **ᴘʟᴇᴀsᴇ ᴄᴏɴᴛᴀᴄᴛ sᴜᴘᴘᴏʀᴛ ᴛᴇᴀᴍ:** @betabot_support"
        )
        await message.reply_text(error_msg)
        return

    # Memory Save & Reply
    history.append({"role": "assistant", "content": ai_reply})
    await save_user_context(user_id, history)
    await message.reply_text(ai_reply, quote=True)


@Client.on_message(filters.command(["reset", "history"], prefixes=[".", "/"]))
async def reset_command_handler(client, message):
    user_id = message.from_user.id
    await reset_user_context(user_id)
    await message.reply_text("🧠 **Chat History Cleared!**\n\nMeri memory refresh ho gayi hai. Ab aap naye sire se sawaal pooch sakte hain. join kra - @betabot_hub and @betabot_support")
