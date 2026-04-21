## Multi-step reasoning
```
2026-04-20 02:15:53,531 UTC - INFO - XYZ Bank Chatbot initialized and ready to receive queries.
2026-04-20 02:15:53,531 UTC - INFO - Session ID: ba7dfd65510643c3
2026-04-20 02:15:56,508 UTC - INFO - User query: I want to save 10k a month for 5 years; if that reaches 8 Lakhs, can I use it as a down payment for a 40 Lakh home loan?
2026-04-20 02:15:57,915 UTC - INFO - HTTP Request: POST https://openai.vocareum.com/v1/chat/completions "HTTP/1.1 200 OK"
2026-04-20 02:15:57,928 UTC - INFO - Intent classification result: {'intent': 'loan_inquiry', 'confidence_score': 0.92}
2026-04-20 02:15:58,952 UTC - INFO - HTTP Request: POST https://openai.vocareum.com/v1/chat/completions "HTTP/1.1 200 OK"
2026-04-20 02:16:03,054 UTC - INFO - Agent Action: Using tool 'advisory_engine' with input '{'query': 'down payment requirements for a home loan of 40 Lakhs', 'intent': 'advisory'}'
2026-04-20 02:16:03,054 UTC - INFO - Agent Action: Using tool 'calculate_sip' with input '{'monthly_investment': 10000, 'expected_return_rate': 10, 'years': 5}'
2026-04-20 02:16:04,934 UTC - INFO - HTTP Request: POST https://openai.vocareum.com/v1/embeddings "HTTP/1.1 200 OK"
2026-04-20 02:16:07,995 UTC - INFO - HTTP Request: POST https://openai.vocareum.com/v1/chat/completions "HTTP/1.1 200 OK"
2026-04-20 02:16:08,003 UTC - INFO - Advisory engine result: advice="For a home loan of ₹40 Lakhs, the general down payment requirement is typically around 10% to 20% of the property value. This means you would need to prepare a down payment of approximately ₹4 Lakhs to ₹8 Lakhs, depending on the bank's policies and your financial profile. I recommend using the 'Loan Calculator' on our website to get more detailed insights tailored to your situation."
2026-04-20 02:16:09,402 UTC - INFO - HTTP Request: POST https://openai.vocareum.com/v1/chat/completions "HTTP/1.1 200 OK"
2026-04-20 02:16:11,571 UTC - INFO - Agent Final Answer: After saving ₹10,000 per month for 5 years at an assumed annual return of 10%, your total savings will grow to approximately ₹780,823.81.

Regarding the down payment for a home loan of ₹40 Lakhs, lenders typically require a down payment of about 10% to 20% of the property's value. This means you would generally need around ₹4 Lakhs to ₹8 Lakhs as a down payment, which indicates that your savings of approximately ₹780,823.81 can indeed be used for the down payment.

I recommend using the "Loan Calculator" on our website for more detailed insights tailored to your situation.

_Disclaimer: Educational purposes only._
2026-04-20 02:17:34,675 UTC - INFO - User query: exit
2026-04-20 02:17:34,675 UTC - INFO - User requested to exit.
```
## Add memory handling 
- JSON file backed memory. File naming convention is `history_<session_id>.json`
- Session ID is based on the host node name and the MAC address to uniquely identify the per-host session.

## Improve multi-turn conversations
```
2026-04-19 11:46:23,077 UTC - INFO - HTTP Request: POST https://openai.vocareum.com/v1/embeddings "HTTP/1.1 200 OK"
2026-04-19 11:46:23,610 UTC - INFO - XYZ Bank Chatbot initialized and ready to receive queries.
2026-04-19 11:46:23,611 UTC - INFO - Session ID: ba7dfd65510643c3
2026-04-19 11:46:33,728 UTC - INFO - User query: How much will 5,000/month grow to in 10 years at 12%?
2026-04-19 11:46:36,658 UTC - INFO - HTTP Request: POST https://openai.vocareum.com/v1/chat/completions "HTTP/1.1 200 OK"
2026-04-19 11:46:36,691 UTC - INFO - Intent classification result: {'intent': 'investment_advice', 'confidence_score': 0.97}
2026-04-19 11:46:38,414 UTC - INFO - HTTP Request: POST https://openai.vocareum.com/v1/chat/completions "HTTP/1.1 200 OK"
2026-04-19 11:46:38,613 UTC - INFO - Agent Action: Using tool 'calculate_sip' with input '{'monthly_investment': 5000, 'expected_return_rate': 12, 'years': 10}'
2026-04-19 11:46:39,789 UTC - INFO - HTTP Request: POST https://openai.vocareum.com/v1/chat/completions "HTTP/1.1 200 OK"
2026-04-19 11:46:40,520 UTC - INFO - Agent Final Answer: If you invest ₹5,000 every month for 10 years at an annual return rate of 12%, your investment will grow to approximately ₹1,161,695.38.

_Disclaimer: Educational purposes only._
2026-04-19 11:46:45,761 UTC - INFO - User query: What if the interest rate was 15% instead?
2026-04-19 11:46:47,812 UTC - INFO - HTTP Request: POST https://openai.vocareum.com/v1/chat/completions "HTTP/1.1 200 OK"
2026-04-19 11:46:47,816 UTC - INFO - Intent classification result: {'intent': 'loan_inquiry', 'confidence_score': 0.85}
2026-04-19 11:46:49,049 UTC - INFO - HTTP Request: POST https://openai.vocareum.com/v1/chat/completions "HTTP/1.1 200 OK"
2026-04-19 11:46:49,261 UTC - INFO - Agent Action: Using tool 'calculate_sip' with input '{'monthly_investment': 5000, 'expected_return_rate': 15, 'years': 10}'
2026-04-19 11:46:50,413 UTC - INFO - HTTP Request: POST https://openai.vocareum.com/v1/chat/completions "HTTP/1.1 200 OK"
2026-04-19 11:46:51,137 UTC - INFO - Agent Final Answer: If you invest ₹5,000 every month for 10 years at an annual return rate of 15%, your investment will grow to approximately ₹1,393,286.36.

_Disclaimer: Educational purposes only._
2026-04-19 11:47:40,776 UTC - INFO - User query: exit
2026-04-19 11:47:40,777 UTC - INFO - User requested to exit.
```

## Memory retention and reset behaviour 
- Memory retention is based on the size of the `history_<session_id>.json` file. If the size increases beyond 100 KB then the previous 50% chat is summarized followed by pruning the previous chat.
- Tested the behaviour by reducing the file size limit to 10 KB

```2026-04-20 18:40:27,082 UTC - INFO - Memory bloat detected for ba7dfd65510643c3. Triggering reduction.```
