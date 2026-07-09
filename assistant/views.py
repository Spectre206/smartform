import json
import urllib.request
import urllib.error
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from applications.models import Application

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "qwen3:1.7b"

def load_system_prompt():
    with open("system_prompt.txt", "r") as f:
        return f.read()

def call_ollama(prompt):
    """Send prompt to Ollama and return the response text."""
    payload = json.dumps({
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False,
        "options": {
            "num_predict": 120
        }
    }).encode("utf-8")

    req = urllib.request.Request(OLLAMA_URL, data=payload, headers={
        "Content-Type": "application/json"
    })
    try:
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            return data.get("response", "Sorry, I couldn't process that.")
    except urllib.error.URLError:
        return "Error: Could not reach the assistant."

@login_required
@require_POST
def ask_assistant(request):
    application_id = request.POST.get("application_id")
    user_message = request.POST.get("message", "")
    application = get_object_or_404(Application, pk=application_id, user=request.user)

    form_data = {
        "full_name": application.full_name,
        "father_name": application.father_name,
        "cnic_number": application.cnic_number,
        "date_of_birth": str(application.date_of_birth) if application.date_of_birth else "",
        "address": application.address,
        "city": application.city,
        "reason": application.reason,
    }
    system_prompt = load_system_prompt().replace("{form_data}", json.dumps(form_data))
    full_prompt = f"{system_prompt}\n\nUser: {user_message}\nAssistant:"
    reply = call_ollama(full_prompt)

    # Extract ALL error fields
    errors = []
    clean_lines = []
    for line in reply.splitlines():
        if line.startswith("ERROR_FIELD:"):
            parts = line.split(":", 2)
            if len(parts) >= 3:
                errors.append({
                    "field": parts[1],
                    "message": parts[2].strip()
                })
        else:
            clean_lines.append(line)

    clean_reply = "\n".join(clean_lines).strip()
    # If reply is empty after removing errors, provide a default message
    if not clean_reply:
        if errors:
            clean_reply = f"I found {len(errors)} issue(s) with your form."
        else:
            clean_reply = "I've checked your form. Everything looks good."

    context = {
        "user_message": user_message,
        "assistant_reply": clean_reply,
        "errors": errors,          # list of dicts
    }
    return render(request, "partials/chat_message.html", context)