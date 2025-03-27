import os
from dotenv import load_dotenv
from supabase import create_client, Client
from typing import Optional, Dict

# Load environment variables
load_dotenv()

# Initialize Supabase client
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(supabase_url, supabase_key)

class SupabaseDB:
    async def get_user(self, username: str) -> Optional[Dict]:
        """Get a user by username from Supabase"""
        response = supabase.table("users").select("*").eq("username", username).execute()
        users = response.data
        
        if not users or len(users) == 0:
            return None
        
        return users[0]
    
    async def create_user(self, username: str, hashed_password: str, full_name: str, email: str) -> Dict:
        """Create a new user in Supabase"""
        user_data = {
            "username": username,
            "hashed_password": hashed_password,
            "full_name": full_name,
            "email": email,
            "disabled": False
        }
        
        response = supabase.table("users").insert(user_data).execute()
        return response.data[0]

# Create a database instance
db = SupabaseDB()