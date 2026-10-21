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
messages=[{
    "role":"user",
    "content":"What is 15 times 8?"
},
{
    "role":"user",
    "content":"What is 5 times 8?"
},
{
    "role":"user",
    "content":"What is 15 plus 8?"
}]

registry = make_registry([Calculator])
tools = make_tools([Calculator])
response_history=[]

def extract_message(response):
    return response["choices"][0]["message"]

for i in range(10):
    response=call_llm(messages,tools=tools)
    response_history=extract_message(response)
    messages.append(response_history)
    tool_call=response_history[-1]["tool_calls"][0]
    if tool_call !=[] :
        tool_result=execute_tool(tool_call,registry)
        messages.append({"role":"tool","tool_call_id":tool_call["id"], "content":tool_result})
        
    else:
        break
print(extract_message(response)) 
print("max iteration reached",i)