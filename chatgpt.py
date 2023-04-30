import requests
import json
import time
import os
from github import Github

openai_api_key = os.environ["OPENAI_API_KEY"]
github_access_token = os.environ["MY_GITHUB_ACCESS_TOKEN"]

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
    g = Github(github_access_token)
    user = g.get_user()
    repo = user.get_repo("YOUR_GITHUB_REPO_NAME")

    try:
        file = repo.get_contents(f"/docs/{filename}", ref="main")
        repo.update_file(file.path, f"Update {filename}", content, file.sha, branch="main")
    except:
        repo.create_file(f"/docs/{filename}", f"Create {filename}", content, branch="main")

if __name__ == "__main__":
    conversation_history = []
    prompts = [
        "Write me an executive summary in MD format.",
        "Write me a high-level design doc in MD format.",
        "Write me technical specs in MD format.",
        "Write me an implementation guide in MD format.",
        "Write me a test plan in MD format.",
        "Write me user stories in MD format.",
        "Write me test cases in MD format.",
        "Write me a deployment guide.",
        "Write me a project flow in mermaid.",
        "Write me a 'things we still may need' list in MD format.",
    ]

    initial_prompt = input("Enter a prompt: ") + " written in Python."
    conversation_history.append({"role": "user", "content": initial_prompt})
    response_message = send_message_to_chatgpt(initial_prompt, conversation_history)
    if response_message:
        conversation_history.append({"role": "assistant", "content": response_message})
        print(f"ChatGPT: {response_message}")

    for index, prompt in enumerate(prompts):
        prompt += " written in Python."
        response_message = send_message_to_chatgpt(prompt, conversation_history)
        if response_message:
            conversation_history.append({"role": "user", "content": prompt})
            conversation_history.append({"role": "assistant", "content": response_message})
            print(f"ChatGPT: {response_message}")

            if "MD format" in prompt:
                filename = f"generated_file_{index}.md"
                upload_to_github(filename, response_message, "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")

        time.sleep(20)  # Wait for 20 seconds between requests to maintain a rate limit of 
