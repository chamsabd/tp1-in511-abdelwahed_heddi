from utils import (
     
        call_llm,
        make_tools,
        make_registry,
        execute_tool,
        # Tools
        Database,
        make_sql_tools,
        WordCounter,
        # Data
        init_demo_db,
    )
registry = make_registry([WordCounter])
tools = make_tools([WordCounter])
message=[{
    "role":"user",
    "content":"How many words are in 'Hola mundo, esto es una prueba'?"
}]

def extract_message(response):
    return response["choices"][0]["message"]
response=call_llm(message,tools=tools)
response_history=extract_message(response)
tool_call=response_history["tool_calls"][0]
tool_result=execute_tool(tool_call,registry)
message.append(response_history)
message.append({"role":"tool","tool_call_id":tool_call["id"], "content":tool_result})
print(message)
response=call_llm(message,tools=tools)
print(extract_message(response))