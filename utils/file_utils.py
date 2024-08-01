from supabase import create_client, Client
from supabase import StorageException
import os
from dotenv import load_dotenv

load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)

# Function to read a file
def read_file(file_name: str, bucket_name: str, destination: str):
    with open(destination, 'wb+') as f:
        res = supabase.storage.from_(bucket_name).download(file_name)
        f.write(res)
    return destination