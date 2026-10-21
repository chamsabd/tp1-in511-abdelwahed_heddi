from utils import (
     
        call_llm,
        make_tools,
        make_registry,
        execute_tool,
        # Tools
        Database,
        make_sql_tools,
        Calculator,
        # Data
        init_demo_db,
    )
registry = make_registry([Calculator])
tools = make_tools([Calculator])
message=[{
    "role":"user",
    "content":"What is 15 times 8?"
}]

def extract_message(response):
    return response["choices"][0]["message"]
response=call_llm(message,tools=tools)
response_history=extract_message(response)
tool_call=response_history["tool_calls"][0]
tool_result=execute_tool(tool_call,registry)
message.append(response_history)
message.append({"role":"tool","tool_call_id":tool_call["id"], "content":tool_result})
response=call_llm(message,tools=tools)
print(extract_message(response))