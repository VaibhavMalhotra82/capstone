## Prompt comparision
| Prompt file     | Query                                              | Response                                                                                        |
| -------------   | ---------------------------------------------------| ----------------------------------------------------------------------------------------------- |
| *prompts_v0.py* | what is the current interest rate on home loans?   | Advisory engine response: advice='Thank you for reaching out to XYZ Bank! How can I assist you with your loan inquiry today? Please let me know if you need information on specific loan products, interest rates, or required documents.                                    |
| *prompts_v1.py* | what is the current interest rate on home loans?   | Advisory engine response: advice='Welcome to XYZ Bank! How may I assist you with your loan inquiry today? I can provide general information about our loan products, including interest rates and required documents. You might also find our Loan Calculator on the website helpful for estimating your loan terms.                                                                                                                                  |
| *prompts.py* | what is the current interest rate on home loans?      | Advisory engine response: advice="Thank you for reaching out to XYZ Bank! If you're interested in a loan, I can provide some general information. We offer various loan products including personal loans, home loans, and auto loans. The interest rates vary based on the loan type, typically ranging from 8% to 15% per annum. For applications, you'll generally need to submit documents like proof of identity, income statements, and property details if applicable. I recommend checking out our 'Loan Calculator' on the website for an estimate tailored to your needs. If you have more questions or need assistance with the application process, feel free to reach out!                                                                                                                             |

## Improvements
- Ground the information that agent uses for answering queries using RAG.
- Add tools for calculating loan interest rates.
- Add persistent memory to save the conversational history.
- Add observability to document details like token consumption.
- Limit the query to a certian size to avoid context poisioning.

## Failures
- Hallucination due to old\outdated data based on the LLM training set.
- No checks on the query length.
- No guardrails for PII data and sensitive keywords.

## Prompt strategy justification
- Intent classification is the first step in the complete chain. In order to make sure that it's accurate we went ahead of few-shot prompting technique. We have included three specific examples of inputs and their desired outputs.
- Advisory prompt is a Zero-Shot approach because we are asking the model to perform a task (responding to banking intents) without providing any completed examples of the input and desired output.