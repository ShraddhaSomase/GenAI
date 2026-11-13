# Loan Chatbot – Evaluation Questions

These are 10 realistic questions that users may ask our loan chatbot.

## Questions

1. How many loan applications are available in the dataset?
2. How many loans were approved and how many were denied?
3. What is the average annual income of applicants?
4. What is the average credit score of applicants?
5. Which loan purpose appears most frequently in the dataset?
6. What is the loan amount for application LN-000001?
7. What is the monthly payment for application LN-000010?
8. What is the interest rate for application LN-000020?
9. How many applicants have an approved loan decision?

## Question that our data cannot answer

10. What was the exact reason why application LN-000001 was rejected?

**Expected chatbot behavior:** The chatbot should explain that the dataset contains the loan decision but does not contain a specific rejection reason. It should not guess or generate a false reason.

## Evaluation Rules

We will evaluate our chatbot using the following points:

1. Does it understand the user's question?
2. Does it retrieve the correct loan information?
3. Does it provide accurate answers?
4. Does it respond in simple language?
5. Does it clearly say when the required information is unavailable?

**Goal:** The chatbot should answer questions using available loan records and should not make up information when the dataset does not contain the answer.