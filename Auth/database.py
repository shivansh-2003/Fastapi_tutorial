import os
from dotenv import load_dotenv
from supabase import create_client, Client
from typing import Optional, Dict, List
import uuid

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
    
    async def get_user_by_email(self, email: str) -> Optional[Dict]:
        """Get a user by email from Supabase"""
        response = supabase.table("users").select("*").eq("email", email).execute()
        users = response.data
        
        if not users or len(users) == 0:
            return None
        
        return users[0]
    
    async def create_user(self, username: str, hashed_password: str, full_name: str, email: str) -> Dict:
        """Create a new user in Supabase"""
        verification_code = str(uuid.uuid4())
        user_data = {
            "username": username,
            "hashed_password": hashed_password,
            "full_name": full_name,
            "email": email,
            "disabled": False,
            "verified": False,
            "verification_code": verification_code
        }
        
        response = supabase.table("users").insert(user_data).execute()
        return response.data[0]
    
    async def update_user(self, username: str, data: Dict) -> Optional[Dict]:
        """Update user data in Supabase"""
        response = supabase.table("users").update(data).eq("username", username).execute()
        if not response.data:
            return None
        return response.data[0]
    
    async def verify_user(self, verification_code: str) -> bool:
        """Verify a user's email using verification code"""
        response = supabase.table("users").select("*").eq("verification_code", verification_code).execute()
        users = response.data
        
        if not users or len(users) == 0:
            return False
        
        user = users[0]
        update_response = supabase.table("users").update({"verified": True}).eq("id", user["id"]).execute()
        
        return bool(update_response.data)
    
    async def store_reset_token(self, email: str, reset_token: str) -> bool:
        """Store a password reset token for a user"""
        user = await self.get_user_by_email(email)
        if not user:
            return False
        
        response = supabase.table("password_resets").insert({
            "user_id": user["id"],
            "reset_token": reset_token,
            "expires_at": "NOW() + interval '1 hour'"
        }).execute()
        
        return bool(response.data)
    
    async def validate_reset_token(self, reset_token: str) -> Optional[str]:
        """Validate a password reset token and return the associated user ID"""
        response = supabase.table("password_resets").select("user_id").eq("reset_token", reset_token).gte("expires_at", "NOW()").execute()
        
        if not response.data or len(response.data) == 0:
            return None
        
        return response.data[0]["user_id"]
    
    async def update_password(self, user_id: str, hashed_password: str) -> bool:
        """Update a user's password by user ID"""
        response = supabase.table("users").update({"hashed_password": hashed_password}).eq("id", user_id).execute()
        
        # Delete all reset tokens for this user
        supabase.table("password_resets").delete().eq("user_id", user_id).execute()
        
        return bool(response.data)

# Create a database instance
db = SupabaseDB()
