# Use dotenv to set the below environment variables in the .env file
# This will update or add the variables directly in the .env file inplace
from dotenv import set_key
from pathlib import Path

env_path = Path(__file__).resolve().parent.parent.parent.parent / '.env'
set_key(str(env_path), 'DS_RUNNER_COSTEER_DUMP_STDOUT_TYPE', 'full')
