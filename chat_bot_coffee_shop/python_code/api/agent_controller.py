from agents import (
    GuardAgent,
    ClassificationAgent,
    DetailsAgent,
    OrderTakingAgent,
    RecommendationAgent,
    AgentProtocol
)

class AgentController():
    def __init__(self):
        self.guard_agent = GuardAgent()
        self.classification_agent = ClassificationAgent()  # Ya no se usa directamente pero lo mantengo por compatibilidad
        self.recommendation_agent = RecommendationAgent(
            'recommendation_objects/apriori_recommendations.json',
            'recommendation_objects/popularity_recommendation.csv'
        )

        self.agent_dict: dict[str, AgentProtocol] = {
            "details_agent": DetailsAgent(),
            "order_taking_agent": OrderTakingAgent(self.recommendation_agent),
            "recommendation_agent": self.recommendation_agent
        }

    def get_response(self, input):
        # 1. Extraer mensaje del usuario
        job_input = input["input"]
        messages = job_input["messages"]

        # 2. Evaluar si el mensaje es permitido (guard_agent)
        guard_agent_response = self.guard_agent.get_response(messages)

        # Validación mínima
        if "memory" not in guard_agent_response:
            return {
                "error": "Guard agent response missing 'memory' key",
                "response": guard_agent_response
            }

        # 3. Si el mensaje no está permitido, devolver respuesta
        if guard_agent_response["memory"].get("guard_decision") == "not allowed":
            return guard_agent_response

        # 4. Si está permitido, tomar la decisión del agente desde el memory
        chosen_agent = guard_agent_response["memory"].get("classification_decision")

        # 5. Buscar y ejecutar el agente correspondiente
        agent = self.agent_dict.get(chosen_agent)
        if agent:
            return agent.get_response(messages)
        else:
            return {
                "error": f"Chosen agent '{chosen_agent}' not found in agent_dict"
            }

