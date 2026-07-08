from motor.motor_asyncio import AsyncIOMotorClient
from config import Config

# Multiple Mongo Clients for Load Balancing
clients = [AsyncIOMotorClient(url) for url in Config.MONGO_URLS]
collections = [client["AdvancedBotDB"]["user_history"] for client in clients]

def get_collection(user_id: int):
    """Assigns user to one of the 3 databases automatically"""
    if not collections:
        raise Exception("Database Error: MongoDB URL missing!")
    db_index = user_id % len(collections)
    return collections[db_index]

async def get_user_context(user_id: int) -> list:
    collection = get_collection(user_id)
    user_data = await collection.find_one({"user_id": user_id})
    if user_data:
        return user_data.get("history", [])
    return []

async def save_user_context(user_id: int, history: list):
    """Limits history to last 100 messages for deep context"""
    trimmed_history = history[-100:] 
    collection = get_collection(user_id)
    await collection.update_one(
        {"user_id": user_id},
        {"$set": {"history": trimmed_history}},
        upsert=True
    )
    
async def reset_user_context(user_id: int):
    """Wipes memory for a specific user"""
    collection = get_collection(user_id)
    await collection.delete_one({"user_id": user_id})
