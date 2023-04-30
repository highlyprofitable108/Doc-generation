import requests
import json
import time
import os
import base64

openai_api_key = os.environ["OPENAI_API_KEY"]
github_access_token = os.environ["MY_GITHUB_ACCESS_TOKEN"]

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {github_access_token}"
}

def send_message_to_chatgpt(prompt, conversation_history):
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {openai_api_key}"
    }

    data = {
        "model": "gpt-3.5-turbo",
        "messages": conversation_history + [{"role": "user", "content": prompt}],
        "temperature": 0.7
    }

    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        result = response.json()
        message = result["choices"][0]["message"]["content"].strip()
        return message
    else:
        print(f"Error {response.status_code}: {response.text}")
        return None

def upload_to_github(filename, content):
    url = f"https://api.github.com/repos/mikefusc/Doc-generation/contents/docs/{filename}"
    content_base64 = base64.b64encode(content.encode()).decode()

    data = {
        "message": f"Create/update {filename}",
        "content": content_base64
    }

    response = requests.put(url, headers=headers, json=data)
    if response.status_code in [201, 200]:
        print(f"Successfully uploaded {filename}")
    else:
        print(f"Error {response.status_code}: {response.text}")

initial_prompt = "Hi I just created a new github repo I would like your help with. The repo is a document generator that will call github api to create a new repo. Based on the user description of the repo, we will begin sending information to api asking for chatgpt to create specific files in .md format (Ex: test plan, high level design, tech specs, executive summary, readme)"

conversation_history = []
response_message = send_message_to_chatgpt(initial_prompt, conversation_history)
conversation_history.append({"role": "assistant", "content": response_message})

fixed_prompts = [
    "write me an executive summary for this in Md format.",
    "write me a high level design doc in Md format.",
    "write me technical specs in .Md format.",
    "write me an implementation guide in .Md format",
    "write me a test plan in .Md format",
    "write me user stories in Md format.",
    "write me test cases in .Md format",
    "write me a deployment guide",
    "write me a project flow in mermaid",
    "write me a things we still may need list in md format",
]

for prompt in fixed_prompts:
    time.sleep(20)  # Add rate limit (3 requests per minute)
    prompt += " written in Python."
    response_message = send_message_to_chatgpt(prompt, conversation_history)
    conversation_history.append({"role": "user", "content": prompt})
    conversation_history.append({"role": "assistant", "content": response_message})

    if "Md format" in prompt:
        filename = prompt.split(" in ")[0].replace(" ", "_") + ".md"
        upload_to_github(filename, response_message)

print("All documents have been generated and uploaded to the GitHub repo.")
