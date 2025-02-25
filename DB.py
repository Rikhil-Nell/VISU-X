from typing import Any, List
from pydantic_ai.messages import (
    ModelMessage,
    ModelRequest,
    ModelResponse,
    UserPromptPart,
    TextPart,
)


class DatabaseHandler:
    def __init__(self, deps):
        self.deps = deps

    async def message_handler(self, response: List[Any]) -> List[ModelMessage]:
        messages: List[ModelMessage] = []

        for item in response:
            role = item["role"]
            content = item["content"]

            if role == "user":
                messages.append(ModelRequest(parts=[UserPromptPart(content=content)]))
            elif role == "bot":
                messages.append(ModelResponse(parts=[TextPart(content=content)]))
        return messages

    async def get_memory(self, user_id: str, limit: int) -> List[ModelMessage]:
        supabase = self.deps.supabase_client

        # Fetch the latest messages from Supabase
        response = (
            supabase.table("memory")
            .select("role, content")
            .eq("user_id", user_id)
            .order("timestamp", desc=True)
            .limit(limit)
            .execute()
        )
        response = list(reversed(response.data))  # Reverse for chronological order

        messages = await self.message_handler(response)

        return messages

    async def append_message(self, user_id: str, role: str, content: str) -> None:
        supabase_client = self.deps.supabase_client

        supabase_client.table("memory").insert(
            {
                "user_id": user_id,
                "role": role,
                "content": content,
            }
        ).execute()
