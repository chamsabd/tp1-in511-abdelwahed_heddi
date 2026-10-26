import json
from utils import SafeReadOnlyDatabase, make_sql_tools, make_tools, make_registry, call_llm, execute_tool

# Prompt système de base de l'énoncé
SYSTEM_PROMPT = """You are a SQL assistant with access to a SQLite database.

Tools:
- ListTables: list all tables
- DescribeTable: get table structure
- SQLQuery: execute any SQL query

Think step by step. Explore the schema first, then query.

Always use JOINs instead of multiple queries when possible."""


def _short(text, max_len=100):
    """Raccourcit un texte pour garder des logs simples et lisibles."""
    text = str(text).replace("\n", " ").strip()
    return text if len(text) <= max_len else text[: max_len - 3] + "..."


def _summarize_result(result):
    """Résume le résultat d'un outil en une ligne."""
    try:
        data = json.loads(result)
    except Exception:
        return _short(result, 140)

    if isinstance(data, dict) and "error" in data:
        return f"ERROR: {_short(data['error'], 120)}"
    if isinstance(data, list):
        return f"{len(data)} rows"
    return _short(data, 140)


def extract_message(response):
    """Extrait le message du LLM de la réponse brute de l'API"""
    return response["choices"][0]["message"]


def run_agent(question, tool_classes, system_prompt=SYSTEM_PROMPT,
              max_iterations=5, verbose=True):
    """Boucle agent : LLM -> outils -> LLM -> ... -> réponse finale."""
    # Schémas JSON des outils (vus par le LLM) et registre nom -> classe
    tools = make_tools(tool_classes)
    registry = make_registry(tool_classes)

    # Historique initial : consigne système + question
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": question},
    ]

    for i in range(max_iterations):  # limite anti-boucle infinie
        # Appel du LLM, puis ajout de sa réponse à l'historique
        message = extract_message(call_llm(messages, tools=tools))
        messages.append(message)

        # Pas de tool_calls : réponse finale
        tool_calls = message.get("tool_calls")
        if not tool_calls:
            return message["content"]

        # Sinon : exécution de chaque outil demandé
        for tool_call in tool_calls:
            try:
                result = execute_tool(tool_call, registry)
            except Exception as e:
                # L'erreur est renvoyée au LLM au lieu d'arrêter l'agent
                result = json.dumps({"error": str(e)})
            if verbose:
                function = tool_call.get("function", {})
                tool_name = function.get("name", "UnknownTool")
                args_text = ""
                try:
                    args = json.loads(function.get("arguments", "{}"))
                    if tool_name == "DescribeTable":
                        args_text = f"table={args.get('table_name', '?')}"
                    elif tool_name == "SQLQuery":
                        args_text = f"query={_short(args.get('query', ''), 80)}"
                    elif args:
                        args_text = f"args={_short(args, 80)}"
                except Exception:
                    args_text = f"raw_args={_short(function.get('arguments', ''), 80)}"

                print(f"  [iter {i + 1}] {tool_name} {args_text}".rstrip())
                print(f"             -> {_summarize_result(result)}")
            # Résultat lié à l'appel d'origine par tool_call_id
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call["id"],
                "content": result,
            })

    return "Max iterations reached"


if __name__ == "__main__":
    db = SafeReadOnlyDatabase("library.db")  # read-only + guardrails SQL
    sql_tools = make_sql_tools(db)       # SQLQuery, ListTables, DescribeTable

    questions = [
        "What are the books written after 1970?",
        "Who is the author of 'Dune' and when were they born?",
        "How many books are there per genre?",
        "What is the average rating per publisher?",
        "Which author has written the most books?",
    ]
    for q in questions:
        print(f"\nQ: {q}")
        print("A:", run_agent(q, sql_tools))