from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
import os
import subprocess
import json
from typing import Optional
import re

app = FastAPI()

data_dir = "/data"  # Restrict operations within /data
os.makedirs("/data")
def validate_path(file_path: str):
    """Ensures the file path is within the /data directory."""
    abs_path = os.path.abspath(file_path)
    if not abs_path.startswith(data_dir):
        raise HTTPException(status_code=400, detail="Access outside /data is not allowed.")
    return abs_path

@app.post("/run")
def run_task(task: str = Query(..., description="Task description")):
    try:
        parsed_task = task.lower()

        if "install uv" in parsed_task and "datagen.py" in parsed_task:
            # Extract the email using regex
            email_match = re.search(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", task)
            if not email_match:
                raise HTTPException(status_code=400, detail="Email not found in task description.")
            
            email = email_match.group(0)

            # Install uv if not installed
            subprocess.run(["pip", "install","uv"], check=True)
            data_dir = "/data"

            # Download the script first
            script_path = os.path.join(data_dir, "datagen.py")
            subprocess.run(["curl", "-o", script_path, 
                            "https://raw.githubusercontent.com/sanand0/tools-in-data-science-public/tds-2025-01/project-1/datagen.py"], check=True)

            # Run the script with the email as an argument
            subprocess.run(["uv", "run", script_path, email], check=True, cwd=data_dir)

            return {"status": "success", "task": "A1 completed"}

    #     else:
    #         raise HTTPException(status_code=400, detail="Unknown or unsupported task format.")

    # except subprocess.CalledProcessError as e:
    #     raise HTTPException(status_code=500, detail=f"Error executing command: {e}")

    # except Exception as e:
    #     raise HTTPException(status_code=500, detail=str(e))

        elif "format" in parsed_task and "prettier" in parsed_task:
            file_path = os.path.join(data_dir, "format.md")
            validate_path(file_path)
            subprocess.run(["npx", "prettier", "--write", file_path], check=True)
            return {"status": "success", "task": "A2 completed"}
        
        elif "count wednesdays" in parsed_task:
            file_path = os.path.join(data_dir, "dates.txt")
            validate_path(file_path)
            with open(file_path, "r") as f:
                dates = f.readlines()
            count = sum(1 for date in dates if "Wed" in date)
            with open(os.path.join(data_dir, "dates-wednesdays.txt"), "w") as f:
                f.write(str(count))
            return {"status": "success", "task": "A3 completed"}
        
        else:
            raise HTTPException(status_code=400, detail="Unknown task format.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/read")
def read_file(path: str):
    try:
        abs_path = validate_path(os.path.join(data_dir, path))
        if not os.path.exists(abs_path):
            raise HTTPException(status_code=404, detail="File not found.")
        with open(abs_path, "r") as f:
            content = f.read()
        return {"content": content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
