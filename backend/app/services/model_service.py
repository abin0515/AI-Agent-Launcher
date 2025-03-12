from typing import List, Optional, Dict, Union
import logging
import traceback
from openai import OpenAI
from pydantic import BaseModel
import json

logger = logging.getLogger(__name__)


class ChatMessage(BaseModel):
    role: str
    content: str


class ModelService:
    def __init__(self):
        self.client = OpenAI()
        self.model = "gpt-3.5-turbo"

        self.tools = [
            {
                "type": "function",
                "function": {
                    "name": "get_weather",
                    "description": "Retrieve current weather details for specified coordinates. ",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "latitude": {"type": "number"},
                            "longitude": {"type": "number"},
                        },
                        "required": ["latitude", "longitude"],
                        "additionalProperties": False,
                    },
                    "strict": True,
                },
            }
        ]

    def generate_response(
        self,
        messages: List[ChatMessage],
        function_result: Optional[Union[str, Dict]] = None,
        current_function: Optional[str] = None,
    ) -> Union[str, dict]:
        """
        Generate a response using the OpenAI API with function calling and structured responses.

        :param messages: Chat history messages.
        :param function_result: The result returned by an external function (optional).
        :param current_function: The name of the function that was just called (optional).
        :return: If the model decides to call a function, returns {"function": ..., "arguments": ...}; otherwise returns a text reply.
        """
        try:
            # 1. Format the chat messages as expected by the API
            formatted_messages = [
                {"role": msg.role, "content": msg.content} for msg in messages
            ]

            # 2. If there is function_result, add a system message with context.
            if function_result:
                formatted_context = (
                    json.dumps(function_result, indent=2)
                    if isinstance(function_result, dict)
                    else function_result
                )
                readable_context = (
                    "You are a helpful assistant aiding students in building AI Agents. "
                    "Use the following context to answer the question naturally and conversationally. "
                    f"\n\nContext: {formatted_context}\n\n"
                    "Please summarize it for the user in a user friendly manner, incorporating emojis to enhance engagement. "
                )
                # Append additional details based on which function was called
                if current_function:

                    if current_function == "get_weather":
                        readable_context += f"please add this content:{current_function} to the response."
                    # elif current_function == "get_course_assignments":

                formatted_messages.append(
                    {"role": "system", "content": readable_context}
                )

            # 3. If current_function is provided, add a system message indicating which function was just called.
            if current_function:
                system_message = f"(Function Called: {current_function})"
                formatted_messages.append({"role": "system", "content": system_message})
                logger.info(f"(Function Called: {current_function})")

            # 4. Call the OpenAI API to generate a response.
            response = self.client.chat.completions.create(
                model=self.model,
                messages=formatted_messages,
                tools=self.tools,
                tool_choice="auto",
                temperature=0.7,
                max_tokens=500,
            )

            response_message = response.choices[0].message
            if hasattr(response_message, "tool_calls") and response_message.tool_calls:
                return {
                    "function": response_message.tool_calls[0].function.name,
                    "arguments": response_message.tool_calls[0].function.arguments,
                }

            return response_message.content

        except Exception as e:
            logger.error(
                f"Error generating response: {str(e)}\n{traceback.format_exc()}"
            )
            return "I apologize, but I encountered an error generating a response."
