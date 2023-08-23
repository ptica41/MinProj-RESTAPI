import os
from dotenv import load_dotenv

# load_dotenv()

dotenv_path = os.path.join(os.path.split(os.path.split(os.getcwd())[0])[0], '.env')
print(dotenv_path)
print(os.getcwd())
print(os.path.split(os.path.split(os.getcwd())[0])[0])
print(os.environ.get("USERNAME"))
