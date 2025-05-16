def get_chatbot_response(client,model_name,messages,temperature=0):
    input_messages = []
    for message in messages:
        input_messages.append({"role": message["role"], "content": message["content"]})

    response = client.chat.completions.create(
        model=model_name,
        messages=input_messages,
        temperature=temperature,
        top_p=0.8,
        max_tokens=2000,
    ).choices[0].message.content
    
    return response

def get_embedding(embedding_client,model_name,text_input):
    output = embedding_client.embeddings.create(input = text_input,model=model_name)
    
    embedings = []
    for embedding_object in output.data:
        embedings.append(embedding_object.embedding)

    return embedings

def double_check_json_output(client, model_name, chatbot_output):
    import json
    import re

    try:
        # ✅ Quitar prefacios: cortar desde el primer `{`
        if not chatbot_output.strip().startswith('{'):
            chatbot_output = chatbot_output[chatbot_output.find('{'):]
        
        return json.dumps(json.loads(chatbot_output))  # para asegurarnos de que es JSON válido
    except json.JSONDecodeError:
        # En caso de error, pedirle al modelo que devuelva solo el JSON limpio
        fallback_prompt = f"""
You returned an invalid JSON response. Please return ONLY the fixed JSON structure, starting directly with '{{' and following this format exactly:

{{
  "chain of thought": "...",
  "step number": "...",
  "order": [...],
  "response": "..."
}}

Here is what you gave me before:
{chatbot_output}
"""
        response = get_chatbot_response(client, model_name, [{"role": "user", "content": fallback_prompt}])

        # Intentar de nuevo con el JSON limpio del modelo
        cleaned_response = response[response.find('{'):]
        return json.dumps(json.loads(cleaned_response))