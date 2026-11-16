# MudraMitra - Prompt Comparison

## Objective

Compare task_prompt_v1 and task_prompt_v2 using the same 10 questions.
Both versions use the same RAG retrieval configuration.

## Results

| No. | Question | V1 Answer | V1 Confidence | V1 Correct? | V2 Answer | V2 Confidence | V2 Correct? |
|---|---|---|---|---|---|---|---|
| 1 | What are the different categories available under the Pradhan Mantri Mudra Yojana (PMMY)? | The Pradhan Mantri Mudra Yojana (PMMY) has four loan categories: Shishu, Kishor, Tarun, and Tarun Plus. | high | Yes | The Pradhan Mantri Mudra Yojana (PMMY) has four loan categories: Shishu, Kishor, Tarun, and Tarun Plus. | high | Yes |
| 2 | Which Mudra category is suitable for a loan amount of Rs. 3 lakh? | The loan amount of Rs. 3 lakh falls under the Kishor category of the PMMY MUDRA scheme. | high | Yes | The Rs. 3 lakh loan falls under the Kishor category, which covers loans above Rs. 50,000 and up to Rs. 5 lakh. | high | Yes |
| 3 | What is the maximum loan amount available under the Shishu category? | The maximum loan amount available under the Shishu category is up to Rs. 50,000/-. | high | Yes | The maximum loan amount available under the Shishu category is up to Rs.â€¯50,000. | high | Yes |
| 4 | What is the loan amount range under the Kishor category? | The Kishor category covers loans above Rs.â€¯50,000 and up to Rs.â€¯5.00â€¯lakh. | high | Yes | The Kishor category covers loans above Rs.â€¯50,000 and up to Rs.â€¯5.00â€¯lakh. | high | Yes |
| 5 | What is the loan amount range under the Tarun category? | The Tarun category covers loans above Rs.â€¯5.00 lakh and up to Rs.â€¯10.00 lakh. | high | Yes | The Tarun category covers loans above Rs.â€¯5.00 lakh and up to Rs.â€¯10.00 lakh. | high | Yes |
| 6 | What is the exact current interest rate offered by SBI for a Rs. 3 lakh Mudra loan? | The retrieved records do not contain any information about the current interest rate offered by SBI for a Rs. 3 lakh Mudra loan. | low | Yes | The retrieved records do not contain any information about the interest rate offered by SBI for a Rs. 3 lakh Mudra loan. | low | Yes |
| 7 | What is the maximum loan amount available under the Tarun Plus category? | The maximum loan amount available under the Tarun Plus category is Rs. 20.00 lakh. | high | Yes | The maximum loan amount available under the Tarun Plus category is Rs. 20.00 lakh. | high | Yes |
| 8 | What is the eligibility condition for applying under the Tarun Plus category? | To be eligible for a Tarun Plus MUDRA loan you must be an Indian citizen with a business plan for a nonâ€‘farm incomeâ€‘generating activity (manufacturing, processing, trading or services). Your credit need should be up to â‚¹20 lakh, and you must have successfully repaid a previous Tarunâ€‘category loan. | high | Yes | To be eligible for a Tarun Plus MUDRA loan, you must be an Indian citizen with a business plan for a nonâ€‘farm incomeâ€‘generating activity (such as manufacturing, processing, trading or services), need credit up to â‚¹20â€¯lakh, and you must have successfully repaid a previous Tarunâ€‘category loan. | high | Yes |
| 9 | What types of businesses are represented in the MudraMitra records? | The records indicate that the businesses represented are nonâ€‘farm incomeâ€‘generating activities, specifically manufacturing, processing, trading, and service sector enterprises. | high | Yes | The records indicate that eligible businesses are nonâ€‘farm, incomeâ€‘generating activities in the manufacturing, processing, trading, or service sectors. | high | Yes |
| 10 | According to the records, who decides the repayment period and terms? | The retrieved records do not specify who decides the repayment period and terms for MUDRA loans. | low | Yes | The retrieved records do not specify who decides the repayment period and terms for MUDRA loans. | low | Yes |

## Evaluation Notes

- Correctness must be checked against the actual MUDRA and Stand-Up India source records.
- Question 6 is intentionally unanswerable. The chatbot must not invent an SBI interest rate.
- Question 10 must not claim who decides repayment terms unless the records support that claim.
- All 20 responses were reviewed against the project records. Both prompts passed all 10 questions, including the two questions requiring the chatbot to state that information was unavailable.

## Final Comparison

Prompt V2 is selected as the winner. Both versions answered all 10 questions correctly, but V2 has clearer instructions for evidence-based answers, confidence levels and avoiding unsupported information. The improved query expansion in smart_search.py also helped both prompts answer Question 9 correctly.

