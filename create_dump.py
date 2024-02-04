import subprocess
from datetime import datetime
from dotenv import load_dotenv
import os

# Specify the path to your .env file
env_path = "./app/.env"

# Load the .env file
load_dotenv(dotenv_path=env_path)


# Database credentials and connection details
db_connection_string = "postgresql://admin:5tgb%25TGB@localhost:5432/famaga"
container_name = "famaga-pg"

# Generating the filename with the current timestamp
timestamp = datetime.now().strftime("%Y-%m-%d-%M%S")
filename = f"famaga_db_{timestamp}.sql"

# Command to create a SQL dump inside the Docker container
dump_command = f"docker exec {container_name} pg_dump {db_connection_string} -F p -f /tmp/{filename}"

# Execute the dump command
subprocess.run(dump_command, shell=True)

# Copy the dump file from the Docker container to the local machine
copy_command = f"docker cp {container_name}:/tmp/{filename} ./"
subprocess.run(copy_command, shell=True)

print(f"SQL dump file copied to the current directory as {filename}")
