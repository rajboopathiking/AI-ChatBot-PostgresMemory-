import httpx
from pydataui import App, state, Container
from pydataui.components import Chat
  
ui = App(title="AI Chat Support")
  
    # 1. Zero-Class Procedural State
s = state(
        messages=[
            {"role": "assistant", "content": "Hello! How can I help you today?"}
        ],
        session_id="sess_001",                                                                             
        loading=False
    )

    # 2. Async Message Handler with Loading Indicator
@s.action
async def handle_message(message: str = "", **kwargs):
        user_msg = (message or kwargs.get("message", "")).strip()
        if not user_msg:
            return
  
        s.messages.append({"role": "user", "content": user_msg})
        s.loading = True 

        try:                                                                                               
            async with httpx.AsyncClient(base_url="http://127.0.0.1:8000", timeout=120.0) as client:
                resp = await client.post("/chat/invoke", json={"id": s.session_id, "message": user_msg})   
                resp.raise_for_status()
                reply = resp.json().get("response", "No response received.")                               
        except Exception as e:
            reply = f"Error: {e}"
        finally:
            s.loading = False

        s.messages.append({"role": "assistant", "content": reply})                                         

@s.action
def clear_chat():
        s.messages = [{"role": "assistant", "content": "Chat history cleared."}]                           

    # 3. Declarative Chat View
@ui.page("/")
def home():                                                                                            
        return Container(                                                                                  
            Chat(                                                                                          
                messages=s.messages,                                                                       
                title="Support AI",                                                               
                subtitle="Postgre - Memory - Agent",
                placeholder="Type your message... (Shift+Enter for new line)",                             
                on_send=handle_message,                                                                    
                on_clear=clear_chat,
                loading=s.loading,                                                                         
                height="650px",                                                                            
                show_clear=True
            ),
            max_width="lg",
            padding="lg"
        )

if __name__ == "__main__":
        ui.run(port=8000)