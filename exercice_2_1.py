from utils import (
    call_llm,
    make_tools,
    make_registry,
    execute_tool,
    Calculator,
)

SYSTEM_PROMPT = """You are a calculator assistant.
Use the Calculator tool when the user asks for arithmetic operations.

"""

registry = make_registry([Calculator])
tools = make_tools([Calculator])


def extract_message(response):
    return response["choices"][0]["message"]


def run_question(question: str, max_iterations: int = 10):
    """Respecte le schéma de la boucle agent du TP."""
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": question},
    ]

    for i in range(max_iterations):
        response = call_llm(messages, tools=tools)
        assistant_msg = extract_message(response)
        messages.append(assistant_msg)

        tool_calls = assistant_msg.get("tool_calls", [])
        if not tool_calls:
            return assistant_msg["content"], i + 1, messages

        for tool_call in tool_calls:
            tool_result = execute_tool(tool_call, registry)
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call["id"],
                "content": tool_result,
            })

    return "Max iterations reached", max_iterations, messages


questions = [
    "What is 15 times 8?",
    "What is 5 times 8?",
    "What is 15 plus 8?",
]

for q in questions:
    result, iterations, history = run_question(q, max_iterations=5)
    print("Question:", q)
    print("Nombre d'itérations:", iterations)
    print("Résultat:", result)
    print("Historique:", history)
    print("---")