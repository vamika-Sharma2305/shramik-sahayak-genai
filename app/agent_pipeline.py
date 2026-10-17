import os
from functools import lru_cache
from typing import Dict, Any
from pydantic import BaseModel, Field
from fastapi import FastAPI, Form, HTTPException
from langgraph.graph import StateGraph, END
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI
import httpx

app = FastAPI(title="Shramik Sahayak Core Engine")


@lru_cache(maxsize=1)
def get_llm() -> ChatOpenAI:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not configured")
    return ChatOpenAI(model="gpt-4o", temperature=0.1, api_key=api_key)


@app.get("/health")
async def health_check():
    return {"status": "ok"}


class WorkerSessionState(BaseModel):
    user_phone: str
    preferred_language: str = "hi"
    raw_input_type: str  # "voice", "image", "text"
    transcript: str = ""
    intent: str = ""
    extracted_data: Dict[str, Any] = Field(default_factory=dict)
    response_text: str = ""
    draft_document_url: str = ""


# 1. Voice transcription via Indic ASR (Bhashini API wrapper)
async def transcribe_indic_audio(audio_bytes: bytes, source_lang: str) -> str:
    # Integration with Bhashini ULCA / Whisper Indic Endpoint
    async with httpx.AsyncClient() as client:
        # Mock payload structure representing Bhashini ASR Pipeline
        response = await client.post(
            "https://dhruva-api.bhashini.gov.in/services/inference/asr",
            headers={"Authorization": os.getenv("BHASHINI_API_KEY", "")},
            json={"language": source_lang, "audio_content": audio_bytes.hex()},
            timeout=10.0,
        )
        if response.status_code == 200:
            return response.json().get("pipelineResponse", [{}])[0].get("output", [{}])[0].get("source", "")
    return "Aapki aawaz theek se sunai nahi di. Kripya dobara bolein."


# 2. Intent Classifier Node
def intent_routing_node(state: WorkerSessionState) -> WorkerSessionState:
    prompt = f"""
    You are an intent router for an Indian gig/informal worker assistant.
    Input transcript: "{state.transcript}"

    Classify the transcript into strictly ONE category:
    - 'EARNINGS_AUDIT': issues with pay slips, fuel deductions, trip pay, incentive targets.
    - 'WELFARE_SCHEME': questions on e-Shram, medical insurance, pension, government cards, maternity benefits.
    - 'GRIEVANCE_DISPUTE': ID deactivation/blocked, unfair customer strike, police harassment, COD mismatch.
    - 'SAFETY_SOS': road accident, physical assault, medical emergency, vehicle breakdown.
    - 'GENERAL_HELP': basic greetings or app navigation.

    Return only the category name.
    """
    res = get_llm().invoke([HumanMessage(content=prompt)]).content.strip()
    state.intent = res
    return state


# 3. Grievance Draft Generation Node
def grievance_generator_node(state: WorkerSessionState) -> WorkerSessionState:
    worker_lang = state.preferred_language
    prompt = f"""
    You are an expert advocate for platform gig workers in India.
    Worker grievance statement: "{state.transcript}"
    Worker State/Context: {state.extracted_data.get('location', 'India')}

    Tasks:
    1. Draft a formal, legally grounded appeal letter to the Aggregator Grievance Officer & State Welfare Board.
       Reference the Karnataka Platform-Based Gig Workers Act (2025) or Rajasthan Gig Workers Act (2023) if applicable.
       Emphasize principles of Natural Justice and arbitrary algorithmic blocking without written show-cause.
    2. Provide a 2-sentence simplified summary in {worker_lang} that the worker can send on WhatsApp or say directly to their team lead.

    Return output formatted as:
    [SUMMARY_VOICE]
    <Worker colloquial summary>
    [FORMAL_LETTER]
    <Official grievance letter>
    """
    response = get_llm().invoke([SystemMessage(content=prompt)]).content
    state.response_text = response
    return state


# Build Graph Workflow
builder = StateGraph(WorkerSessionState)
builder.add_node("classify_intent", intent_routing_node)
builder.add_node("draft_grievance", grievance_generator_node)

builder.set_entry_point("classify_intent")
builder.add_conditional_edges(
    "classify_intent",
    lambda state: "draft_grievance" if state.intent == "GRIEVANCE_DISPUTE" else END,
)
builder.add_edge("draft_grievance", END)
graph_executor = builder.compile()


@app.post("/api/v1/webhook")
async def handle_whatsapp_message(
    From: str = Form(...),
    Body: str = Form(None),
    MediaUrl0: str = Form(None),
    language: str = Form("hi"),
):
    if not os.getenv("OPENAI_API_KEY"):
        raise HTTPException(status_code=503, detail="OPENAI_API_KEY is not configured")

    session = WorkerSessionState(
        user_phone=From,
        preferred_language=language,
        raw_input_type="text" if Body else "voice",
        transcript=Body or "Mera Swiggy account bina bataye deactivate kar diya customer jhooth bol raha tha",
    )
    result = graph_executor.invoke(session)
    return {"status": "success", "data": result}