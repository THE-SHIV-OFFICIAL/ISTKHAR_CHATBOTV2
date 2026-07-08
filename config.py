import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Aapki provided details (Hardcoded & .env variables)
    API_ID = int(os.getenv("API_ID", "6435225"))
    API_HASH = os.getenv("API_HASH", "4e984ea35f854762dcde906dce426c2d")
    BOT_TOKEN = os.getenv("BOT_TOKEN", None)
    STRING1 = os.getenv("STRING_SESSION", None)
    
    # Owner & Support Details
    OWNER_ID = int(os.getenv("OWNER_ID", "7995626429"))
    SUPPORT_GRP = "ARISHFA_UPDATE"
    UPDATE_CHNL = "THUNDERDEVS"
    OWNER_USERNAME = "ll_ISTKHAR_BABY_lll"

    # --- ADVANCED V2 FEATURES BELOW ---

    # OpenRouter API Keys (3 Keys for Auto-Fallback)
    OPENROUTER_KEYS = [
        os.getenv("OPENROUTER_KEY_1", ""),
        os.getenv("OPENROUTER_KEY_2", ""),
        os.getenv("OPENROUTER_KEY_3", "")
    ]
    OPENROUTER_KEYS = [key for key in OPENROUTER_KEYS if key]
    
    # MongoDB Load Balancing (Primary + 2 Extras)
    MONGO_URLS = [
        os.getenv("MONGO_URL", ""),     # Aapka primary URL
        os.getenv("MONGO_URL_2", ""),   # Load balancer URL 2
        os.getenv("MONGO_URL_3", "")    # Load balancer URL 3
    ]
    MONGO_URLS = [url for url in MONGO_URLS if url]
