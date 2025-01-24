from groq import Groq
from fastapi import FastAPI, Form, Request, WebSocket
from typing import Annotated
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

app = FastAPI()

templates = Jinja2Templates(directory="templates")

chat_responses = []
chat_log = []

@app.get("/", response_class=HTMLResponse)
async def chat_page(request: Request):
    return templates.TemplateResponse("home.html", {"request": request, "chat_responses": chat_responses})

@app.get("/ws")
async def chat(websocket: WebSocket):
    await websocket.accept()
    while True:
        user_input = await websocket.receive_text()
        await websocket.send_text(user_input)
#ws
@app.post("/", response_class=HTMLResponse)
async def chat_home(request: Request, user_input: Annotated[str, Form()]):

    chat_log.append({'role': 'user', 'content': user_input})
    chat_responses.append(user_input)

    client = Groq(api_key="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")
    messages = [
        {
            "role": "system",
            "content": "You are an Honest Man, a persona dedicated to speaking the truth with clarity, kindness, and integrity. You avoid deception, half-truths, or manipulation, even if the truth is difficult to hear. You provide thoughtful, honest responses and value transparency above all. If you don’t know something or are unsure, you admit it openly rather than guessing."
        }
    ] + chat_log + [
        {
            "role": "user",
            "content": user_input
        }
    ]

    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages,
        temperature=1,
        max_completion_tokens=1024,
        top_p=1,
        stream=True,
        stop=None,
    )

    response = ""
    for chunk in completion:
        response += chunk.choices[0].delta.content or ""
      
    
    bot_response = response
    chat_log.append({'role': 'assistant', 'content': bot_response})
    chat_responses.append(bot_response)

    return templates.TemplateResponse("home.html", {"request": request, "chat_responses": chat_responses})

