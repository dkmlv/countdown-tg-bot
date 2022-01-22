from environs import Env

env = Env()
env.read_env()

BOT_TOKEN: str = env.str("BOT_TOKEN")
ADMIN: str = env.str("ADMIN")

# supabase stuff
SUPABASE_URL: str = env.str("SUPABASE_URL")
SUPABASE_KEY: str = env.str("SUPABASE_KEY")
