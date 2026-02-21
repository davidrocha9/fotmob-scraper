import os
from dotenv import load_dotenv

load_dotenv()

TEAM_ID = os.getenv("TEAM_ID")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
SUPABASE_SCHEMA = os.getenv("SUPABASE_SCHEMA", "public")
