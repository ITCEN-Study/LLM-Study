from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from openai import OpenAI
import os
import uuid

app = FastAPI()

openai_client = OpenAI()  # 환경 변수의 OPENAI_API_KEY 반영

gemini_client = OpenAI(
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    api_key=os.environ.get("GEMINI_API_KEY"),
)

ollama_client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")

# 서버 메모리에 세션별 대화 기록 리스트 관리
# 구조: { session_id: [ {"role": "user"/"assistant", "content": "..."} ] }
conversations = {}


@app.get("/")
def get_chat_page():
    html_path = "chatmulti.html"
    if not os.path.exists(html_path):
        return HTMLResponse(
            content="<h1>chatmulti.html 파일을 찾을 수 없습니다.</h1>", status_code=404
        )
    with open(html_path, "r", encoding="utf-8") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content)


@app.get("/chat")
def chat(message: str, model_type: str, session_id: str = None):
    # 세션 ID가 전달되지 않거나 유효하지 않으면 새로운 세션 생성
    if not session_id or session_id not in conversations:
        session_id = str(uuid.uuid4())
        conversations[session_id] = []

    # 사용자 질문을 해당 세션 대화 리스트에 누적
    conversations[session_id].append({"role": "user", "content": message})

    try:
        # 선택된 모델 타입에 따라 알맞은 클라이언트로 API 요청 수행
        if model_type == "gpt":
            response = openai_client.chat.completions.create(
                model="gpt-4o-mini", messages=conversations[session_id]
            )
            answer = response.choices[0].message.content

        elif model_type == "gemini":
            response = gemini_client.chat.completions.create(
                model="gemini-2.5-flash", messages=conversations[session_id]
            )
            answer = response.choices[0].message.content

        elif model_type == "ollama":
            response = ollama_client.chat.completions.create(
                model="exaone3.5", messages=conversations[session_id]
            )
            answer = response.choices[0].message.content

        else:
            raise HTTPException(
                status_code=400, detail="유효하지 않은 모델 타입입니다."
            )

        # AI 응답 내용을 해당 세션 대화 리스트에 누적
        conversations[session_id].append({"role": "assistant", "content": answer})

        return {"answer": answer, "session_id": session_id}

    except Exception as e:
        conversations[session_id].pop()
        raise HTTPException(status_code=500, detail=f"API 호출 중 오류 발생: {str(e)}")
