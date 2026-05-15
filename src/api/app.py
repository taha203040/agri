# # src/api/app.py
# from fastapi import FastAPI
# from fastapi.responses import StreamingResponse
# from pydantic import BaseModel
# from src.agents.agriculture_agent import agriculture_agent
# import json
# import logging
# import re
# from fastapi.middleware.cors import CORSMiddleware
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# app = FastAPI(
#     title="Agriculture API",
#     description="API for agriculture-related queries including soil and disease information",
#     version="1.0.0"
# )
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=[
#         "http://localhost:8080",
#         "http://127.0.0.1:8080",
#         "http://localhost:3000",  # React default
#         "http://127.0.0.1:3000",
#         "http://localhost:5173",  # Vite default
#         "http://127.0.0.1:5173",
#         # Add your production domains here
#     ],
#     allow_credentials=True,
#     allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
#     allow_headers=["*"],  # Allow all headers
#     expose_headers=["*"],  # Expose all headers to client
#     max_age=3600,  # Cache preflight requests for 1 hour
# )

# class QuestionRequest(BaseModel):
#     question: str

# def extract_content_from_chunk(chunk):
#     """
#     Extract clean text content from various chunk formats
#     """
#     if isinstance(chunk, dict):
#         # Check for AIMessage in the chunk
#         if 'model' in chunk and 'messages' in chunk['model']:
#             messages = chunk['model']['messages']
#             if messages and len(messages) > 0:
#                 last_msg = messages[-1]
#                 if hasattr(last_msg, 'content'):
#                     return last_msg.content
#                 elif isinstance(last_msg, dict) and 'content' in last_msg:
#                     return last_msg['content']
        
#         # Check for ToolMessage
#         if 'tools' in chunk and 'messages' in chunk['tools']:
#             messages = chunk['tools']['messages']
#             if messages and len(messages) > 0:
#                 tool_msg = messages[0]
#                 if hasattr(tool_msg, 'content'):
#                     return tool_msg.content
#                 elif isinstance(tool_msg, dict) and 'content' in tool_msg:
#                     return tool_msg['content']
        
#         # Direct content field
#         if 'content' in chunk:
#             return chunk['content']
        
#         # Check for AIMessage directly
#         if 'AIMessage' in str(chunk):
#             match = re.search(r"content='(.*?)'(?:,|$)", str(chunk))
#             if match:
#                 return match.group(1)
    
#     elif hasattr(chunk, 'content'):
#         return chunk.content
    
#     return None

# def is_tool_call(chunk):
#     """Check if chunk contains a tool call"""
#     chunk_str = str(chunk)
#     return 'tool_calls' in chunk_str and 'tool_call' in chunk_str

# def is_tool_response(chunk):
#     """Check if chunk contains a tool response"""
#     chunk_str = str(chunk)
#     return 'ToolMessage' in chunk_str or 'tool_response' in chunk_str

# @app.get("/")
# async def root():
#     return {
#         "status": "healthy",
#         "service": "Agriculture API",
#         "version": "1.0.0"
#     }

# @app.get("/health")
# async def health_check():
#     return {
#         "status": "ok",
#         "agent_loaded": agriculture_agent is not None
#     }

# @app.post("/chat/stream/simple")
# async def chat_stream(request: QuestionRequest):
#     """
#     Stream chat responses - now properly extracts clean content
#     """
#     async def generate():
#         question_input = {'messages': [{'role': 'user', 'content': request.question}]}
        
#         try:
#             # Send initial status
#             yield f"data: {json.dumps({'type': 'status', 'content': 'Processing your question...'})}\n\n"
            
#             for chunk in agriculture_agent.stream(question_input):
#                 logger.info(f"Processing chunk")
                
#                 # Extract clean content
#                 content = extract_content_from_chunk(chunk)
                
#                 if content:
#                     # Send the content as a token
#                     data = {
#                         "type": "token", 
#                         "content": content
#                     }
#                     yield f"data: {json.dumps(data)}\n\n"
                    
#                     # Small delay between chunks for better UX
#                     import asyncio
#                     await asyncio.sleep(0.1)
                
#                 # Optional: Send tool call/response indicators
#                 elif is_tool_call(chunk):
#                     yield f"data: {json.dumps({'type': 'info', 'content': '🔍 Searching database...'})}\n\n"
                
#                 elif is_tool_response(chunk):
#                     yield f"data: {json.dumps({'type': 'info', 'content': '📊 Analyzing results...'})}\n\n"
            
#             # Send completion
#             yield f"data: {json.dumps({'type': 'done', 'status': 'complete'})}\n\n"
            
#         except Exception as e:
#             logger.error(f"Error: {e}", exc_info=True)
#             yield f"data: {json.dumps({'type': 'error', 'error': str(e)})}\n\n"
    
#     return StreamingResponse(
#         generate(),
#         media_type="text/event-stream",
#         headers={
#             "Cache-Control": "no-cache",
#             "X-Accel-Buffering": "no",
#             "Connection": "keep-alive",
#         }
#     )


# @app.post("/chat")
# async def chat(request: QuestionRequest):
#     """Non-streaming endpoint - returns clean response"""
#     try:
#         logger.info(f"Processing: {request.question}")
#         messages = agriculture_agent.run(request.question)
        
#         # Get the final response
#         final_response = messages[-1] if messages else "No response generated"
        
#         return {
#             "status": "success",
#             "response": final_response,
#             "all_messages": messages
#         }
#     except Exception as e:
#         logger.error(f"Error: {e}", exc_info=True)
#         return {
#             "status": "error",
#             "error": str(e)
#         }

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(
#         app, 
#         host="0.0.0.0", 
#         port=8000,
#         reload=True
#     )
import json
import logging
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from src.agents.agriculture_agent import stream_response, invoke_response

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ── App setup ────────────────────────────────────────────────────────────────

app = FastAPI(
    title="Agriculture API",
    description="Soil and plant disease queries with persistent memory.",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Schemas ───────────────────────────────────────────────────────────────────

class ChatRequest(BaseModel):
    question: str
    thread_id: str = "default"   # one thread_id = one conversation history


# ── Routes ───────────────────────────────────────────────────────────────────

@app.get("/")
async def root():
    return {"status": "healthy", "version": "2.0.0"}


@app.post("/chat")
async def chat(req: ChatRequest):
    """Non-streaming — returns the final answer."""
    response = await invoke_response(req.question, req.thread_id)
    return {"status": "success", "response": response}


@app.post("/chat/stream/simple")
async def chat_stream(req: ChatRequest):
    """Streaming — yields SSE tokens with memory per thread_id."""

    async def generate():
        try:
            yield f"data: {json.dumps({'type': 'status', 'content': 'Thinking...'})}\n\n"

            async for text in stream_response(req.question, req.thread_id):
                yield f"data: {json.dumps({'type': 'token', 'content': text})}\n\n"

            yield f"data: {json.dumps({'type': 'done'})}\n\n"

        except Exception as e:
            logger.error(f"Stream error: {e}", exc_info=True)
            yield f"data: {json.dumps({'type': 'error', 'error': str(e)})}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )