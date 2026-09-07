from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Generic, TypeVar
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field

T = TypeVar('T')


class APIResponse(BaseModel, Generic[T]):
    message: str
    data: T | None = None
    success: bool = True


class ChatMessageType(str, Enum):
    USER = 'user'
    ASSISTANT = 'assistant'
    SYSTEM = 'system'
    TOOL = 'tool'


class ChatMessageBase(BaseModel):
    content: str
    message_type: ChatMessageType = ChatMessageType.USER
    metadata: dict[str, Any] = Field(default_factory=dict)


class ChatMessageCreate(ChatMessageBase):
    session_id: str | None = None


class ChatMessage(ChatMessageBase):
    id: str = Field(default_factory=lambda: str(uuid4()))
    session_id: str
    user_id: str | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ChatSessionCreate(BaseModel):
    user_id: str | None = None
    session_name: str | None = None
    context: dict[str, Any] = Field(default_factory=dict)


class ChatSessionUpdate(BaseModel):
    session_name: str | None = None
    is_active: bool | None = None
    context: dict[str, Any] | None = None


class ChatSession(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str = Field(default_factory=lambda: str(uuid4()))
    user_id: str | None = None
    session_name: str
    message_count: int = 0
    last_message_at: datetime | None = None
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    context: dict[str, Any] = Field(default_factory=dict)
    messages: list[ChatMessage] = Field(default_factory=list)


class CatalogItem(BaseModel):
    id: str
    title: str
    category: str
    description: str | None = None
    image: str
    highlights: list[str] = Field(default_factory=list)
    price: float | None = None
    rating: float | None = None


class OrderStatus(str, Enum):
    PENDING = 'pending'
    PROCESSING = 'processing'
    SHIPPED = 'shipped'
    DELIVERED = 'delivered'
    CANCELLED = 'cancelled'
    REFUNDED = 'refunded'


class TransactionItem(BaseModel):
    product_id: str
    product_title: str
    quantity: int
    unit_price: float
    total_price: float


class Transaction(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    user_id: str
    order_number: str
    status: OrderStatus = OrderStatus.PENDING
    items: list[TransactionItem] = Field(default_factory=list)
    subtotal: float = 0.0
    tax: float = 0.0
    shipping: float = 0.0
    total: float = 0.0
    shipping_address: dict[str, Any] = Field(default_factory=dict)
    payment_method: str = ''
    payment_reference: str | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
