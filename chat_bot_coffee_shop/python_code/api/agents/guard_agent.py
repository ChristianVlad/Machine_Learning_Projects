from dotenv import load_dotenv
import os
import json
from copy import deepcopy
from .utils import double_check_json_output, get_chatbot_response
from openai import OpenAI
from .classification_agent import ClassificationAgent

load_dotenv()

class GuardAgent():
    def __init__(self):
        self.client = OpenAI(
            api_key=os.getenv("RUNPOD_TOKEN"),
            base_url=os.getenv("RUNPOD_CHATBOT_URL"),
        )
        self.model_name = os.getenv("MODEL_NAME")
        self.classifier = ClassificationAgent()

    def fallback_guard_decision(self, message: str):
        message = message.lower()
        if any(word in message for word in ["order", "coffee", "tea", "croissant", "latte", "recommend", "i want", "i'd like", "give me"]):
            return "allowed"
        return "not allowed"

    def get_response(self, messages):
        messages = deepcopy(messages)

        system_prompt = """
            You are a helpful AI assistant for a coffee shop application which serves drinks and pastries.
            Your task is to determine whether the user is asking something relevant to the coffee shop or not.
            The user is allowed to:
            1. Ask questions about the coffee shop, like location, working hours, menu items, and coffee shop related questions.
            2. Ask questions about menu items, they can ask for ingredients in an item and more details about the item.
            3. Make an order.
            4. Ask about recommendations of what to buy.

            The user is NOT allowed to:
            1. Ask questions about anything else other than our coffee shop.
            2. Ask questions about the staff or how to make a certain menu item.

            Make sure to follow this exact JSON format:
            {
            "chain of thought": "...",
            "decision": "allowed" or "not allowed",
            "message": ""
            }

            Only reply with this JSON structure. If the message is allowed, the classification agent will decide the next step.
        """

        input_messages = [{"role": "system", "content": system_prompt}] + messages[-3:]

        try:
            chatbot_output = get_chatbot_response(self.client, self.model_name, input_messages)
            print("🛡️ Guard Output:", chatbot_output)
        except Exception as e:
            print("Error calling LLM:", str(e))
            chatbot_output = '{"decision": "not allowed", "message": "Sorry, I can\'t help with that. Can I help you with your order?"}'

        # Procesar decisión
        try:
            output = json.loads(chatbot_output)
        except:
            output = {"decision": "not allowed", "message": "Sorry, I can’t help with that. Can I help you with your order?"}

        # Fallback manual si el modelo falla o responde con decisión vacía
        decision = output.get("decision", "").strip().lower()
        if decision not in ["allowed", "not allowed"]:
            decision = self.fallback_guard_decision(messages[-1]["content"])
            output["decision"] = decision

        # Si está permitido, pasar al classification_agent
        if decision == "allowed":
            classification_result = self.classifier.get_response(messages)
            classification_result["memory"]["guard_decision"] = "allowed"
            return classification_result
        else:
            return {
                "role": "assistant",
                "content": output.get("message", "Sorry, I can’t help with that."),
                "memory": {
                    "agent": "guard_agent",
                    "guard_decision": "not allowed"
                }
            }