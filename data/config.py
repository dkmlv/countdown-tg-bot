from environs import Env

env = Env()
env.read_env()

BOT_TOKEN = env.str("BOT_TOKEN")
ADMIN = env.str("ADMIN")

# redis stuff
REDIS_HOST = env.str("REDIS_HOST")
REDIS_PORT = env.str("REDIS_PORT")
REDIS_DB = env.str("REDIS_DB")
REDIS_PASSWORD = env.str("REDIS_PASSWORD")

# supabase stuff
SUPABASE_URL = env.str("SUPABASE_URL")
SUPABASE_KEY = env.str("SUPABASE_KEY")
