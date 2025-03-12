from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Dict
from app.services.model_service import ModelService
from app.context import get_service_context
import re
import logging
import json

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter()
model_service = ModelService()


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: List[ChatMessage]


class ChatResponse(BaseModel):
    response: str
    sources: List[dict] = []




@router.post("/")
async def chat(request: ChatRequest, services: dict = Depends(get_service_context)):
    """Chat endpoint that allows the model to invoke services functions"""
    try:
        user_message = request.messages[-1].content
        logger.info(f"\n=== New Chat Request ===\nReceived message: {user_message}")

        any_service = services["any_service"]
        

        conversation_history = request.messages.copy()
        # Initial call: no current_function provided
        model_response = model_service.generate_response(request.messages)

        if not isinstance(model_response, dict):
            logger.error(f"Unexpected model response type: {type(model_response)}. Response: {model_response}")
            # return ChatResponse(response="Unexpected response from model.")
            return ChatResponse(response=f"{model_response}")

        logger.info(f"\nInitial LLM response: {json.dumps(model_response, indent=2)}")

        attempts = 0
        max_attempts = 5
        while isinstance(model_response, dict) and "function" in model_response and attempts < max_attempts:
            attempts += 1
            logger.info(f"Processing function call attempt {attempts}")

            function_name = model_response["function"]
            try:
                arguments = model_response["arguments"]
                if isinstance(arguments, str):
                    arguments = json.loads(arguments)
            except json.JSONDecodeError as e:
                logger.error(f"Error parsing arguments: {str(e)}. Arguments: {model_response['arguments']}")
                return ChatResponse(response="Invalid arguments.")

            logger.info(f"Function call: {function_name} with arguments: {arguments}")

            function_result = None

            if function_name == "get_weather":
                return any_service.get_weather(**arguments)
            # you can add more functions here
            # elif function_name == "get_course_assignments":
            #     return any_service.get_course_assignments(**arguments)
                


            # Add function result to conversation history
            function_result_str = json.dumps(function_result) if isinstance(function_result, (dict, list)) else function_result

            conversation_history.append(ChatMessage(role="assistant", content=function_result_str))

            # Pass the current function name along with function_result to generate_response
            model_response = model_service.generate_response(conversation_history, function_result_str, current_function=function_name)
            logger.info(f"Next LLM response: {model_response}")

        if isinstance(model_response, dict):
            return ChatResponse(response=f"Error: Unable to process request after {max_attempts} attempts")
        return ChatResponse(response=model_response)

    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
