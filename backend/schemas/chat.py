from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class ChatCreateSchema(BaseModel):
    title: str
    model: str

class RenameSchema(BaseModel):
    title: str

class ChatRequest(BaseModel):
    """
    Request sent by the frontend to the AI Agent.
    """
    text: str = Field(..., description="User question or prompt")
    attachments: Optional[List[Dict[str, Any]]] = Field(default_factory=list, description="List of attachment files/images")
    model: str = Field(..., description="Model name selected in UI")
    settings: Optional[Dict[str, Any]] = Field(
        default_factory=lambda: {
            'topK': 4,
            'similarity': 0.70,
            'temperature': 0.2
        },
        description="Retrieval and generation settings"
    )
    system_prompt: Optional[str] = Field(None, description="System instructions prompt")


class ChatResponse(BaseModel):
    """
    Response returned by the AI Agent.
    """
    id: str = Field(..., description="Message ID")
    conversation_id: str = Field(..., description="Conversation ID")
    sender: str = Field(..., description="Sender type (assistant)")
    text: str = Field(..., description="AI generated response")
    attachments: Optional[List[Dict[str, Any]]] = Field(default_factory=list)
    citations: Optional[List[Dict[str, Any]]] = Field(default_factory=list)
