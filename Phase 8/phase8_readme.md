## Deploy locally or on the cloud 
```bash
pip install -r requirements.txt
```

## Capture latency and error logs 

### Latency
- Latency based on the short and concise response feedback
```
2026-04-26 07:29:10,738 UTC - INFO - Async function 'categorize_intent' executed in 2.449931 seconds
2026-04-26 07:29:13,216 UTC - INFO - Async function 'process_query' executed in 5.022604 seconds
```

- Latency based on the detailed response fedback
```
2026-04-25 17:46:12,247 UTC - INFO - Async function 'categorize_intent' executed in 1.800180 seconds
2026-04-25 17:46:25,769 UTC - INFO - Async function 'process_query' executed in 15.382759 seconds
```
### Error logs
```
2026-04-26 07:46:36,010 UTC - INFO - Agent Action: Using tool 'advisory_engine' with input '{'query': 'lost my card', 'intent': 'human_handoff'}'
2026-04-26 07:46:36,015 UTC - ERROR - Error: Advisory engine exception: module 'qdrant_client.http.models.models' has no attribute 'Filte'
Traceback (most recent call last):
  File "C:\iitm_pravartak\Capstone\Phase 8\advisory_engine.py", line 44, in advisory_engine
    "filter": rest.Filte(
              ^^^^^^^^^^
AttributeError: module 'qdrant_client.http.models.models' has no attribute 'Filte'. Did you mean: 'Filter'?

2026-04-26 07:46:36,020 UTC - ERROR - Error: Error during agent execution: module 'qdrant_client.http.models.models' has no attribute 'Filte'
Traceback (most recent call last):
  File "C:\iitm_pravartak\Capstone\Phase 8\main.py", line 74, in process_query
    response = await agent_executor.ainvoke(args)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "c:\iitm_pravartak\Capstone\capstone\Lib\site-packages\langchain_classic\chains\base.py", line 222, in ainvoke
    await self._acall(inputs, run_manager=run_manager)
  File "c:\iitm_pravartak\Capstone\capstone\Lib\site-packages\langchain_classic\agents\agent.py", line 1646, in _acall
    next_step_output = await self._atake_next_step(
                       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    ...<5 lines>...
    )
    ^
  File "c:\iitm_pravartak\Capstone\capstone\Lib\site-packages\langchain_classic\agents\agent.py", line 1428, in _atake_next_step
    [
    ^
    ...<8 lines>...
    ],
    ^
  File "c:\iitm_pravartak\Capstone\capstone\Lib\site-packages\langchain_classic\agents\agent.py", line 1511, in _aiter_next_step
    result = await asyncio.gather(
             ^^^^^^^^^^^^^^^^^^^^^
    ...<9 lines>...
    )
    ^
  File "c:\iitm_pravartak\Capstone\capstone\Lib\site-packages\langchain_classic\agents\agent.py", line 1549, in _aperform_agent_action
    observation = await tool.arun(
                  ^^^^^^^^^^^^^^^^
    ...<5 lines>...
    )
    ^
  File "c:\iitm_pravartak\Capstone\capstone\Lib\site-packages\langchain_core\tools\base.py", line 1131, in arun
    raise error_to_raise
  File "c:\iitm_pravartak\Capstone\capstone\Lib\site-packages\langchain_core\tools\base.py", line 1097, in arun
    response = await coro_with_context(coro, context)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "c:\iitm_pravartak\Capstone\capstone\Lib\site-packages\langchain_core\tools\structured.py", line 124, in _arun
    return await self.coroutine(*args, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "c:\iitm_pravartak\Capstone\capstone\Lib\site-packages\langsmith\run_helpers.py", line 631, in async_wrapper
    function_result = await asyncio.create_task(  # type: ignore[call-arg]
                      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
        fr_coro, context=run_container["context"]
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    )
    ^
  File "C:\iitm_pravartak\Capstone\Phase 8\advisory_engine.py", line 44, in advisory_engine
    "filter": rest.Filte(
              ^^^^^^^^^^
AttributeError: module 'qdrant_client.http.models.models' has no attribute 'Filte'. Did you mean: 'Filter'?
```
![alt text](error_agent_response.jpg)

## Demonstrate graceful failure handling 
- Introduced one error to showcase graceful handling
```
2026-04-26 06:53:12,749 UTC - INFO - User query: home loan interest rates
2026-04-26 06:53:14,423 UTC - INFO - HTTP Request: POST https://openai.vocareum.com/v1/chat/completions "HTTP/1.1 200 OK"
2026-04-26 06:53:14,444 UTC - ERROR - Error: Error during intent classification: 'dict' object has no attribute 'dict'
2026-04-26 06:53:14,444 UTC - INFO - Async function 'categorize_intent' executed in 1.529421 seconds
2026-04-26 06:53:14,444 UTC - INFO - Intent classification result: {'intent': 'unknown', 'confidence_score': 0.0, 'feedback': None}
2026-04-26 06:53:14,445 UTC - WARNING - Warning: Low confidence in intent classification: {'intent': 'unknown', 'confidence_score': 0.0, 'feedback': None}
2026-04-26 06:53:14,445 UTC - INFO - Async function 'process_query' executed in 1.675263 seconds
```
![alt text](graceful_error_handling.jpg)

- Added additional pre-check guardrail for the user queries
```
2026-04-26 07:22:41,576 UTC - INFO - HTTP Request: POST https://openai.vocareum.com/v1/embeddings "HTTP/1.1 200 OK"
2026-04-26 07:22:42,488 UTC - INFO - XYZ Bank Chatbot initialized and ready to receive queries.
2026-04-26 07:22:42,488 UTC - INFO - Session ID: ba7dfd65510643c3
2026-04-26 07:23:20,125 UTC - INFO - User query: guaranteed return investment options
2026-04-26 07:23:20,163 UTC - WARNING - Warning: Guardrail pre-check failed: Request appears out of scope: avoid topics related to guaranteed return.
2026-04-26 07:23:36,181 UTC - INFO - User query: exit
2026-04-26 07:23:36,183 UTC - INFO - User requested to exit.
```

## Document deployment assumptions and limitations 

### Deplyment assumptions
- Python 3.11+ should be installed
- Virtual environment should be set using `venv`
- Required python packages should be installed using `pip install -r requirements.txt`

### Deployment limitations
- Missing docker deployment
