## Tools
- advisory_engine is a tool for performing the similarity search on Qdrant vector database to retrieve known facts from internal knowledge base.
- calculate_emi is a tool for calculating the monthly installment for a loan.
- calculate_sip is a tool for calculating the future value of a Mutual Fund SIP.

## Demonstrate correct tool selection
```
2026-04-19 06:05:23,213 UTC - INFO - XYZ Bank Chatbot initialized and ready to receive queries.
2026-04-19 06:05:58,143 UTC - INFO - User query: What's the EMI for a 20L loan at 9%?
2026-04-19 06:06:00,235 UTC - INFO - HTTP Request: POST https://openai.vocareum.com/v1/chat/completions "HTTP/1.1 200 OK"
2026-04-19 06:06:00,249 UTC - INFO - Intent classification result: {'intent': 'loan_inquiry', 'confidence_score': 0.95}
2026-04-19 06:06:01,734 UTC - INFO - HTTP Request: POST https://openai.vocareum.com/v1/chat/completions "HTTP/1.1 200 OK"
2026-04-19 06:06:02,403 UTC - INFO - Agent Action: Using tool 'calculate_emi' with input '{'principal': 2000000, 'annual_rate': 9, 'tenure_years': 20}'
2026-04-19 06:06:04,438 UTC - INFO - HTTP Request: POST https://openai.vocareum.com/v1/chat/completions "HTTP/1.1 200 OK"
2026-04-19 06:06:05,150 UTC - INFO - Agent Final Answer: The monthly EMI for a loan of ₹20,00,000 at an interest rate of 9% for a tenure of 20 years is approximately ₹17,994.52.

_Disclaimer: Educational purposes only._
2026-04-19 06:07:53,355 UTC - INFO - User query: How much will 15,000/month grow to in 10 years at 12%?
2026-04-19 06:07:55,532 UTC - INFO - HTTP Request: POST https://openai.vocareum.com/v1/chat/completions "HTTP/1.1 200 OK"
2026-04-19 06:07:55,536 UTC - INFO - Intent classification result: {'intent': 'investment_advice', 'confidence_score': 0.97}
2026-04-19 06:07:56,920 UTC - INFO - HTTP Request: POST https://openai.vocareum.com/v1/chat/completions "HTTP/1.1 200 OK"
2026-04-19 06:07:57,119 UTC - INFO - Agent Action: Using tool 'calculate_sip' with input '{'monthly_investment': 15000, 'expected_return_rate': 12, 'years': 10}'
2026-04-19 06:07:59,017 UTC - INFO - HTTP Request: POST https://openai.vocareum.com/v1/chat/completions "HTTP/1.1 200 OK"
2026-04-19 06:07:59,762 UTC - INFO - Agent Final Answer: If you invest ₹15,000 each month for 10 years at an annual return rate of 12%, your investment will grow to approximately ₹34,85,086.15.

_Disclaimer: Educational purposes only._
2026-04-19 06:08:04,734 UTC - INFO - User query: exit
2026-04-19 06:08:04,734 UTC - INFO - User requested to exit.
2026-04-19 06:08:57,349 UTC - INFO - HTTP Request: POST https://openai.vocareum.com/v1/embeddings "HTTP/1.1 200 OK"
2026-04-19 06:08:57,570 UTC - INFO - XYZ Bank Chatbot initialized and ready to receive queries.
2026-04-19 06:09:01,133 UTC - INFO - User query: home loan interest rate
2026-04-19 06:09:02,758 UTC - INFO - HTTP Request: POST https://openai.vocareum.com/v1/chat/completions "HTTP/1.1 200 OK"
2026-04-19 06:09:02,770 UTC - INFO - Intent classification result: {'intent': 'loan_inquiry', 'confidence_score': 0.95}
2026-04-19 06:09:04,394 UTC - INFO - HTTP Request: POST https://openai.vocareum.com/v1/chat/completions "HTTP/1.1 200 OK"
2026-04-19 06:09:04,685 UTC - INFO - Agent Action: Using tool 'advisory_engine' with input '{'query': 'home loan interest rate', 'intent': 'loan_inquiry'}'
2026-04-19 06:09:05,583 UTC - INFO - HTTP Request: POST https://openai.vocareum.com/v1/embeddings "HTTP/1.1 200 OK"
2026-04-19 06:09:05,597 UTC - INFO - Retrieved chunk from rag_data/loan.pdf (page 0):
2026-04-19 06:09:05,597 UTC - INFO - Retrieved chunk from rag_data/loan.pdf (page 0):
2026-04-19 06:09:05,597 UTC - INFO - Retrieved chunk from rag_data/loan.pdf (page 0):
2026-04-19 06:09:05,597 UTC - INFO - Retrieved chunk from rag_data/loan.pdf (page 0):
2026-04-19 06:09:08,011 UTC - INFO - HTTP Request: POST https://openai.vocareum.com/v1/chat/completions "HTTP/1.1 200 OK"
2026-04-19 06:09:08,015 UTC - INFO - Advisory engine result: advice="The indicative interest rates for home loans as of April 2026 range from 8.40% to 9.25%, depending on whether they are linked to EBLR or Repo Rate. For the best options, it's also advisable to consider your credit score and eligibility. You can explore more about your eligibility and calculate potential EMIs using the 'Loan Calculator' on our website."
2026-04-19 06:09:09,614 UTC - INFO - HTTP Request: POST https://openai.vocareum.com/v1/chat/completions "HTTP/1.1 200 OK"
2026-04-19 06:09:10,789 UTC - INFO - Agent Final Answer: The indicative interest rates for home loans as of April 2026 range from 8.40% to 9.25%, depending on whether they are linked to EBLR or Repo Rate. For the best options, it's also advisable to consider your credit score and eligibility. You can explore more about your eligibility and calculate potential EMIs using the 'Loan Calculator' on our website.

_Disclaimer: Educational purposes only._
2026-04-19 06:09:14,355 UTC - INFO - User query: exit
2026-04-19 06:09:14,355 UTC - INFO - User requested to exit.
```
## Show at least one failed or incorrect tool call
```
2026-04-17 19:31:29,328 UTC - INFO - Intent classification result: {'intent': 'investment_advice', 'confidence_score': 0.9}
2026-04-17 19:31:30,981 UTC - INFO - HTTP Request: POST https://openai.vocareum.com/v1/chat/completions "HTTP/1.1 200 OK"
2026-04-17 19:31:31,155 UTC - ERROR - Error: Error during agent execution: object str can't be used in 'await' expression
Traceback (most recent call last):
  File "C:\iitm_pravartak\Capstone\Phase 5\main.py", line 55, in process_query
    response = await agent_executor.ainvoke({"input": user_query})
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
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
  File "C:\iitm_pravartak\Capstone\Phase 5\tools.py", line 17, in calculate_sip
    return await f"Future Value: \u20b9{round(fv, 2)}"
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
TypeError: object str can't be used in 'await' expression
```

## Add safeguards against misuse or loops
- Setting max_iterations=5 in the AgentExecutor ensures that if the agent gets confused between the SIP and EMI tools (e.g., trying one, failing, then trying the same one again), the system will force-stop the execution before it drains your API tokens.
- In the advisory_prompt we have clearly specified `Only answer the queries related to banking domain.` to ensure no non-banking queries are answered.
