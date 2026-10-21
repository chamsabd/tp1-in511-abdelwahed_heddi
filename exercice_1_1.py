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

tools = make_tools([Calculator])
message=[{
    "role":"user",
    "content":"What is 15 times 8?"
}]
#print(tools)
response=call_llm(message,tools=tools)
print(response)