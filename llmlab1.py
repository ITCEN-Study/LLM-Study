from fastapi import FastAPI
from openai import OpenAI

app = FastAPI()
client = OpenAI()

@app.get("/chat")
def chat(message: str):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": message}]
    )

    return {
        "모델명": response.model,
        "입력 토큰수": response.usage.prompt_tokens,
        "출력 토큰수": response.usage.completion_tokens,
        "총합 토큰수": response.usage.total_tokens,
        "응답 내용": response.choices[0].message.content
    }