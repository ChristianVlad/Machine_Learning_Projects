from dotenv import load_dotenv
import os
import json
from copy import deepcopy
from .utils import get_chatbot_response, double_check_json_output
from openai import OpenAI
load_dotenv()


class ClassificationAgent():
    def __init__(self):
        self.client = OpenAI(
            api_key=os.getenv("RUNPOD_TOKEN"),
            base_url=os.getenv("RUNPOD_CHATBOT_URL"),
        )
        self.model_name = os.getenv("MODEL_NAME")

    def fallback_intent_detection(self, user_message):
        msg = user_message.lower()
        if any(word in msg for word in ["recommend", "suggest", "what should i get", "something good", "what do you recommend"]):
            return "recommendation_agent"
        if any(word in msg for word in ["order", "i want", "i’d like", "can i get", "i'll take", "give me", "get me", "latte", "tea", "coffee", "croissant"]):
            return "order_taking_agent"
        return None

    def get_response(self, messages):
        messages = deepcopy(messages)

        system_prompt = """
            You are a helpful AI assistant for a coffee shop application.
            Your task is to determine what agent should handle the user input. You have 3 agents to choose from:
            1. details_agent: This agent is responsible for answering questions about the coffee shop, like location, delivery places, working hours, details about menu items. Or listing items in the menu. Or asking what we have.
            2. order_taking_agent: This agent is responsible for taking orders from the user. It's responsible to have a conversation with the user about the order until it's complete.
            3. recommendation_agent: This agent is responsible for giving recommendations to the user about what to buy. If the user asks for a recommendation, this agent should be used.

            Your output should be in a structured json format like so. Each key is a string and each value is a string. Make sure to follow the format exactly:
            {
            "chain of thought": "...",
            "decision": "details_agent" or "order_taking_agent" or "recommendation_agent",
            "message": ""
            }
        """

        input_messages = [{"role": "system", "content": system_prompt}] + messages[-3:]
        chatbot_output = get_chatbot_response(self.client, self.model_name, input_messages)

        # Postproceso normal
        try:
            payload = json.loads(chatbot_output)
        except json.JSONDecodeError:
            corrected = double_check_json_output(self.client, self.model_name, chatbot_output)
            try:
                payload = json.loads(corrected)
            except json.JSONDecodeError as e:
                print("JSON sigue inválido tras fallback:", e)
                payload = {"decision": "details_agent", "message": ""}

        decision = payload.get("decision", "").strip()
        user_message = messages[-1]['content']

        # Fallback manual si no hay decisión o es dudosa
        if not decision or decision not in ["details_agent", "order_taking_agent", "recommendation_agent"]:
            print("⚠️ Usando fallback manual para clasificar...")
            decision = self.fallback_intent_detection(user_message) or "details_agent"

        return {
            "role": "assistant",
            "content": payload.get("message", ""),
            "memory": {
                "agent": "classification_agent",
                "classification_decision": decision
            }
        }