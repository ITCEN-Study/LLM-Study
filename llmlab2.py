from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from openai import OpenAI

app = FastAPI()
client = OpenAI()


@app.get("/")
def get_chat_page():
    html_content = """
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <title>이재혁의 챗봇</title>
        <style>
            body {
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
                background-color: #f4f6f9;
                margin: 0;
                padding: 0;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
            }
            .chat-container {
                width: 450px;
                height: 650px;
                background-color: #ffffff;
                border-radius: 20px;
                box-shadow: 0 10px 30px rgba(0, 0, 0, 0.08);
                display: flex;
                flex-direction: column;
                overflow: hidden;
                border: 1px solid #eaeaea;
            }
            .chat-header {
                background-color: #ffffff;
                color: #1e293b;
                padding: 20px;
                font-size: 18px;
                font-weight: bold;
                border-bottom: 1px solid #f1f5f9;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            .reset-btn {
                background-color: #f1f5f9;
                border: none;
                color: #64748b;
                padding: 6px 12px;
                border-radius: 8px;
                cursor: pointer;
                font-size: 12px;
                font-weight: 500;
                transition: background 0.2s;
            }
            .reset-btn:hover {
                background-color: #e2e8f0;
                color: #334155;
            }
            .chat-messages {
                flex: 1;
                padding: 20px;
                overflow-y: auto;
                background-color: #f8fafc;
                display: flex;
                flex-direction: column;
                gap: 12px;
            }
            .message {
                max-width: 75%;
                padding: 12px 16px;
                font-size: 14px;
                line-height: 1.6;
                word-wrap: break-word;
                box-shadow: 0 2px 4px rgba(0,0,0,0.02);
            }
            /* 유저 메시지: 진한 보라색 바탕에 흰색 글씨 */
            .user-msg {
                background-color: #5842e3;
                color: #ffffff;
                border-radius: 18px 18px 4px 18px;
                align-self: flex-end;
                margin-left: auto;
            }
            /* AI 메시지: 흰색 바탕에 회색 테두리 */
            .ai-msg {
                background-color: #ffffff;
                color: #334155;
                border-radius: 18px 18px 18px 4px;
                border: 1px solid #f1f5f9;
                align-self: flex-start;
            }
            .system-msg {
                align-self: center;
                color: #94a3b8;
                font-size: 13px;
                margin: 10px 0;
                text-align: center;
            }
            .chat-input-area {
                display: flex;
                padding: 15px;
                background-color: #ffffff;
                gap: 10px;
                align-items: center;
            }
            /* 둥근 형태의 인풋창 */
            .chat-input {
                flex: 1;
                padding: 12px 18px;
                border: 2px solid #5842e3;
                border-radius: 14px;
                font-size: 14px;
                outline: none;
            }
            /* 보라색 전송 버튼 */
            .send-btn {
                background-color: #5842e3;
                border: none;
                color: white;
                padding: 12px 20px;
                border-radius: 14px;
                cursor: pointer;
                font-size: 14px;
                font-weight: bold;
                transition: background 0.2s;
            }
            .send-btn:hover {
                background-color: #4330c4;
            }
        </style>
    </head>
    <body>
        <div class="chat-container">
            <div class="chat-header">
                <span>이재혁의 챗봇</span>
                <button class="reset-btn" onclick="resetChat()">대화 리셋</button>
            </div>
            <div class="chat-messages" id="chatMessages">
                <div class="system-msg" id="introMsg">대화를 시작해보세요!</div>
            </div>
            <div class="chat-input-area">
                <input type="text" class="chat-input" id="chatInput" placeholder="메시지를 입력하세요..." onkeydown="handleKey(event)">
                <button class="send-btn" onclick="sendMessage()">전송</button>
            </div>
        </div>

        <script>
            let convId = null;

            function handleKey(event) {
                if (event.key === 'Enter') {
                    sendMessage();
                }
            }

            async function sendMessage() {
                const input = document.getElementById('chatInput');
                const text = input.value.trim();
                if (!text) return;

                // 최초 메시지 전송 시 "대화를 시작해보세요!" 안내 문구 제거
                const intro = document.getElementById('introMsg');
                if (intro) intro.remove();

                // 1) 유저 메시지 화면 표시
                appendMessage(text, 'user-msg');
                input.value = '';

                // 2) 로딩 상태 표시
                const loadingDiv = appendMessage('AI가 생각하는 중...', 'ai-msg');

                try {
                    let url = `/chat?message=${encodeURIComponent(text)}`;
                    if (convId) {
                        url += `&conv_id=${convId}`;
                    }

                    const response = await fetch(url);
                    const data = await response.json();

                    loadingDiv.remove();

                    if (data.answer) {
                        appendMessage(data.answer, 'ai-msg');
                        convId = data.conv_id;
                    } else {
                        appendMessage('답변 호출 오류가 발생했습니다.', 'ai-msg');
                    }
                } catch (e) {
                    loadingDiv.remove();
                    appendMessage('네트워크 연결 에러가 발생했습니다.', 'ai-msg');
                }
            }

            function appendMessage(text, className) {
                const messagesContainer = document.getElementById('chatMessages');
                const msgDiv = document.createElement('div');
                msgDiv.className = `message ${className}`;
                msgDiv.innerText = text;
                messagesContainer.appendChild(msgDiv);
                messagesContainer.scrollTop = messagesContainer.scrollHeight;
                return msgDiv;
            }

            function resetChat() {
                convId = null;
                const messagesContainer = document.getElementById('chatMessages');
                messagesContainer.innerHTML = '<div class="system-msg" id="introMsg">대화를 시작해보세요!</div>';
            }
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


@app.get("/chat")
def chat(message: str, conv_id: str = None):
    # 대화방 생성 없는경우
    if not conv_id:
        conversation = client.conversations.create()
        conv_id = conversation.id

    response = client.responses.create(
        model="gpt-4o-mini", conversation=conv_id, input=message
    )

    return {"answer": response.output_text, "conv_id": conv_id}
