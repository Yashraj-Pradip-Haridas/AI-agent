from fastapi import FastAPI, HTTPException, Query
import os
import subprocess
import re
import requests
import json
import heapq
import openai
from PIL import Image
import base64
import numpy as np
import sqlite3

app = FastAPI()

def ensure_folder_exists(folder_path):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        print(f"✅ Folder created: {folder_path}")
    else:
        print(f"✅ Folder already exists: {folder_path}")

data_dir = os.path.abspath("data")  # Use absolute path
ensure_folder_exists(data_dir)

@app.post("/run")
def run_task(task: str = Query(..., description="Task description")):
    try:
        parsed_task = task.lower()

        if "install uv" in parsed_task and "datagen.py" in parsed_task:
            # Extract email from task
            email_match = re.search(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", task)
            if not email_match:
                raise HTTPException(status_code=400, detail="Email not found in task description.")
            
            email = email_match.group(0)
            print(f"✅ Extracted email: {email}")

            # Install uv
            subprocess.run(["pip", "install", "--user", "uv"], check=True)

            # Download the script
            script_url = "https://raw.githubusercontent.com/sanand0/tools-in-data-science-public/tds-2025-01/project-1/datagen.py"
            script_path = os.path.join(data_dir, "datagen.py")

            response = requests.get(script_url)
            if response.status_code == 200:
                with open(script_path, "w") as file:
                    file.write(response.text)
                print(f"✅ Script downloaded: {script_path}")
            else:
                raise HTTPException(status_code=500, detail="Failed to download datagen.py")

            # Ensure the script exists
            if not os.path.exists(script_path):
                raise HTTPException(status_code=500, detail=f"Script file not found at {script_path}")

            # Use absolute path and correct format for uv
            script_path = os.path.abspath(script_path)

            # Run the script with uv
            print(f"✅ Running script: {script_path} with argument {email}")
            subprocess.run(["uv", "run", script_path, email], check=True, cwd=data_dir, shell=True)

            return {"status": "success", "task": "A1 completed"}
        

        elif "format" in parsed_task and "prettier" in parsed_task:
            file_path = os.path.join(r"D:\data", "format.md")
            if os.path.exists(file_path):
                print(file_path)
                try:
                    subprocess.run(["npx", "--version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
                    print("✅ Prettier installed")
                except subprocess.CalledProcessError:
                    raise HTTPException(status_code=500, detail="Prettier is not installed. Run 'npm install -g prettier'")

                print(f"✅ Running Prettier on file: {file_path}")
                subprocess.run(["npx", "prettier", "--write", file_path], check=True,shell=True)

                return {"status": "success", "task": "A2 completed"}
            else:
                print("Error finding path")

        elif "count" in parsed_task and "wednesdays" in parsed_task:
            file_path = os.path.join(r"D:\data", "dates.txt")
            ensure_folder_exists(file_path)
            with open(file_path, "r") as f:
                dates = f.readlines()
            count = sum(1 for date in dates if "Wed" in date)
            with open(os.path.join(r"D:\data", "dates-wednesdays.txt"), "w") as f:
                f.write(str(count))
            return {"status": "success", "task": "A3 completed"}
            
        elif "sort" in parsed_task and "contact" in parsed_task:
            file_path = os.path.join(r"D:\data", "contacts.json")
            # ensure_folder_exists(file_path)
            # Load JSON file
            if os.path.exists(file_path):
                print("Path exists")
            with open(file_path, "r", encoding="utf-8") as file:
                contacts = json.load(file)

            # Sort contacts by first name
            sorted_contacts = sorted(contacts, key=lambda x: x["last_name"])
            sorted_contacts = sorted(sorted_contacts, key=lambda x: x["first_name"])

            # Save back to JSON file
            with open(file_path, "w", encoding="utf-8") as file:
                json.dump(sorted_contacts, file, indent=4)

            # Print sorted contacts
            print(json.dumps(sorted_contacts, indent=4))
            return {"status": "success", "task": "A3 completed"}
        
        elif "logs" in parsed_task:
            log_dir = r"D:/data/logs"
            output_file = r"D:/data/logs-recent.txt"

            # Get all .log files with their modified times
            log_files = [(os.path.getmtime(os.path.join(log_dir, f)), f) for f in os.listdir(log_dir) if f.endswith(".log")]

            # Get 10 most recent logs, sorted by modified time (most recent first)
            recent_logs = heapq.nlargest(10, log_files, key=lambda x: x[0])

            # Read the first line from each log file
            first_lines = []
            for _, filename in recent_logs:
                file_path = os.path.join(log_dir, filename)
                with open(file_path, "r", encoding="utf-8") as f:
                    first_line = f.readline().strip()  # Read first line and remove leading/trailing spaces
                    first_lines.append(first_line)

            # Write to logs-recent.txt
            with open(output_file, "w", encoding="utf-8") as f:
                f.write("\n".join(first_lines) + "\n")

            print(f"Written first lines of 10 most recent log files to {output_file}")  

        
        elif "markdown" in parsed_task and "extract" in parsed_task:
            # Define the directory and output file
            docs_dir = r"D:/data/docs"
            index_file = r"D:/data/docs/index.json"

            # Dictionary to store filename-to-title mapping
            index = {}

            # Iterate through all .md files in the docs directory
            for root, _, files in os.walk(docs_dir):
                for file in files:
                    if file.endswith(".md"):
                        file_path = os.path.join(root, file)
                        relative_path = os.path.relpath(file_path, docs_dir)  # Get relative path

                        # Read file and extract the first H1 title
                        with open(file_path, "r", encoding="utf-8") as f:
                            for line in f:
                                if line.strip().startswith("# "):  # H1 title
                                    title = line.strip("# ").strip()
                                    index[relative_path] = title
                                    break  # Stop after the first H1

            # Write the index to a JSON file
            with open(index_file, "w", encoding="utf-8") as f:
                json.dump(index, f, indent=4)

            print(f"✅ Index file created at {index_file}")


        elif "email" in parsed_task and "extract" in parsed_task:
            print("Entered body")
            # File paths
            email_file = r"D:/data/email.txt"
            output_file = r"D:/data/email-sender.txt"

            # Read the email content
            with open(email_file, "r", encoding="utf-8") as f:
                content = f.read()

            # Extract sender's email using regex
            match = re.search(r"From: .*?<(.*?)>", content)
            if match:
                sender_email = match.group(1)
                
                # Write the extracted email to output file
                with open(output_file, "w", encoding="utf-8") as f:
                    f.write(sender_email)

                print(f"✅ Sender's email extracted: {sender_email}")
            else:
                print("❌ Could not find sender's email.")


        elif "extract" in parsed_task and "card" in parsed_task:
            # OpenAI API Key (ensure this is set up correctly)
            OPENAI_API_KEY = "your_openai_api_key"

            # File paths
            image_path = r"D:/data/credit-card.png"
            output_path = r"D:/data/credit-card.txt"

            # Convert image to base64
            with open(image_path, "rb") as image_file:
                image_base64 = base64.b64encode(image_file.read()).decode("utf-8")

            # Call OpenAI Vision Model
            response = openai.ChatCompletion.create(
                model="gpt-4-vision-preview",
                messages=[
                    {"role": "system", "content": "Extract the 16-digit credit card number from the image and return only the number with no spaces or dashes."},
                    {"role": "user", "content": [{"type": "image_url", "image_url": f"data:image/png;base64,{image_base64}"}]}
                ],
                max_tokens=20,
                api_key=OPENAI_API_KEY
            )

            # Extract number from response
            credit_card_number = response["choices"][0]["message"]["content"].strip()

            # Write to file
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(credit_card_number)

            print(f"✅ Extracted Credit Card Number: {credit_card_number}")

        elif "similar" in parsed_task and "comment" in parsed_task:
            # OpenAI API Key
            OPENAI_API_KEY = "your_openai_api_key"

            # File paths
            input_path = r"D:/data/comments.txt"
            output_path = r"D:/data/comments-similar.txt"

            # Load comments
            with open(input_path, "r", encoding="utf-8") as f:
                comments = [line.strip() for line in f.readlines() if line.strip()]

            # Generate embeddings
            def get_embedding(text):
                response = openai.Embedding.create(
                    model="text-embedding-ada-002",
                    input=text,
                    api_key=OPENAI_API_KEY
                )
                return np.array(response["data"][0]["embedding"])

            embeddings = np.array([get_embedding(comment) for comment in comments])

            # Compute cosine similarity
            def cosine_similarity(vec1, vec2):
                return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

            max_sim = -1
            most_similar_pair = ("", "")

            for i in range(len(comments)):
                for j in range(i + 1, len(comments)):
                    sim = cosine_similarity(embeddings[i], embeddings[j])
                    if sim > max_sim:
                        max_sim = sim
                        most_similar_pair = (comments[i], comments[j])

            # Write the most similar pair to file
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(most_similar_pair[0] + "\n")
                f.write(most_similar_pair[1] + "\n")

            print("✅ Most similar comments saved to:", output_path)

        elif "total Sales" in parsed_task and "gold" in parsed_task:
            # File paths
            db_path = "/data/ticket-sales.db"
            output_path = "/data/ticket-sales-gold.txt"

            # Connect to the database
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            # Query to calculate total sales for "Gold" tickets
            cursor.execute("SELECT SUM(units * price) FROM tickets WHERE type = 'Gold'")
            total_sales = cursor.fetchone()[0]  # Fetch result

            # Close connection
            conn.close()

            # Save result to file
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(str(total_sales) + "\n")

            print(f"✅ Total sales for 'Gold' tickets saved to {output_path}")

        # elif "fetch" in parsed_task and "data" in parsed_task:
        # elif "clone" in parsed_task and "git" in parsed_task:
        # elif "sql" in parsed_task and "query" in parsed_task:
        # elif "scrap" in parsed_task and "website" in parsed_task:
        # elif "compress" in parsed_task and "resize" in parsed_task:
        # elif "transcribe" in parsed_task and "audio" in parsed_task:
        # elif "markdown" in parsed_task and "html" in parsed_task:
        # elif "filter" in parsed_task and "csv" in parsed_task:
        else:
            raise HTTPException(status_code=400, detail="Unknown or unsupported task format.")
        
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"Error executing command: {e}")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
