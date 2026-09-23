import asyncio
import json
import logging
import os
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

# from src.multimodal.image_analyzer import imageAnalyzer
from src.agents.agriculture_agent import stream_response, invoke_response

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ── App setup ─────────────────────────────────────────────────────────────────

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
    thread_id: str = "default"

# ── Helpers ───────────────────────────────────────────────────────────────────

def build_prompt(disease: str, confidence: float) -> str:
    return f"""
The plant disease detection model identified: "{disease}" with {confidence * 100:.1f}% confidence.

Please provide:
1. Definition: What is this disease?
2. Recommended Treatment: What should the farmer do?

Be concise and practical.
"""

# ── Routes ────────────────────────────────────────────────────────────────────
# @app.post("/diagnose")
# async def diagnose(file: UploadFile = File(...)):
#     """Upload a leaf image → diagnosis + AI treatment recommendation."""


#     temp_path = f"temp_{file.filename}"
#     with open(temp_path, "wb") as f:
#         f.write(await file.read())

#     try:
#         diagnosis  = imageAnalyzer(temp_path)
#         disease    = diagnosis["disease"]
#         confidence = diagnosis["confidence"]

#         # prompt      = build_prompt(disease, confidence)
#         # ai_response = await asyncio.wait_for(
#         #     invoke_response(prompt),
#         #     timeout=20.0
#         # )

#         return {
#             "diagnosis": {
#                 "disease":    disease,
#                 "confidence": f"{confidence * 100:.1f}%",
#             },
#             # "ai_response": ai_response
#         }
 
#     except asyncio.TimeoutError:
#         logger.error("Diagnose timed out after 20 seconds")
#         return {"status": "error", "detail": "Request timed out after 20 seconds"}

#     except Exception as e:
#         logger.log(e)
#         logger.error(f"Diagnose error: {e}", exc_info=True)
#         return {"status": "error", "detail": str(e)}

#     finally:
#         if os.path.exists(temp_path):
#             os.remove(temp_path)

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


