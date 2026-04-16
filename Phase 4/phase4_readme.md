## RAG
- We used the production grade Qdrant vector database. It's a Rust-based engine for "low-latency retrieval". Qdrant makes this "metadata filtering" faster than almost any other DB.
- We used the chunk size of 500 and overlap of 10% considering the size of input data.
- We used OpenAI text-embedding-3-small model with 512 dimensions to speed up the retrieval process.
- Metadata filtering based on the user intent\category.
- Data ingestion must be done once by running the below command:
    - `python ingest.py`

## Response comparision
| Retriever     | Query                                              | Response                                                                                        |
| -------------   | ---------------------------------------------------| ----------------------------------------------------------------------------------------------- |
 No             | what is the current interest rate on home loans?   | The current interest rate on home loans can vary based on several factors such as loan amount, tenure, and the applicant's credit history. Typically, home loan interest rates range from 7% to 9% per annum. It's advisable to check the latest rates on the XYZ Bank website or use the 'Loan Calculator' available there for a more tailored estimation. Additionally, don't forget to consider any processing fees or charges that may apply. |
| Yes           |  what is the current interest rate on home loans?  | The indicative interest rates for home loans currently range from 8.40% to 9.25% per annum, which are linked to the EBLR/Repo rate. For detailed inquiries, I encourage you to utilize the Loan Calculator available on our website to better understand your potential loan repayments based on these rates. |

## Handle case where relevant information is missing
| Query                                                         | Response                                                                          |
| --------------------------------------------------------------| ----------------------------------------------------------------------------------|
| car                                                           | It seems like you may be interested in financing a car. For detailed loan products, including interest rates and required documents, I recommend checking the 'Loan' section on our website or using the 'Loan Calculator' for a clearer perspective on your financial needs. |
| what type of car is suited for family of 5?                   | I can only provide information related to banking. For vehicle recommendations, you might want to consult an automotive expert or research online based on your family's specific needs and preferences. |