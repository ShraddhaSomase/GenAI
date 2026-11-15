# MudraMitra - Prompt Comparison

## Objective

Compare two prompt versions using the same MUDRA loan-category question.

## Test Question

What are all four MUDRA loan categories and their loan limits?

## Version 1 Results

- Response: The chatbot said it did not have the specific loan limits.
- Confidence: Low
- Observation: It avoided guessing, but failed to provide the available information.

## Version 2 Results

- Response: The chatbot listed all four categories.
- Confidence: High
- Observation: It provided a more complete answer but gave incorrect lower limits for Tarun and Tarun Plus.

## Correct Reference Information

| Category | Correct loan limit |
|---|---|
| Shishu | Up to Rs. 50,000 |
| Kishor | Above Rs. 50,000 to Rs. 5 lakh |
| Tarun | Above Rs. 5 lakh to Rs. 10 lakh |
| Tarun Plus | Above Rs. 10 lakh to Rs. 20 lakh |

## Comparison

| Evaluation criteria | Version 1 | Version 2 |
|---|---|---|
| Completeness | Low | High |
| Accuracy | Does not provide an incorrect range | Incorrect ranges |
| Hallucination control | Better abstention | Needs improvement |
| Confidence | Low | High, but not justified |

## Conclusion

Version 1 is safer when information is unavailable, while Version 2 provides more complete answers.

However, neither version is fully satisfactory.

Version 2 should not be considered the winner because it returned incorrect loan limits with high confidence.

## Improvement Plan

1. Provide retrieved MUDRA records as context to the LLM.
2. Instruct the chatbot to answer only from retrieved information.
3. Improve confidence handling.
4. Test both prompts against all evaluation questions.
5. Verify answers against the correct MUDRA records.

## Results After RAG Integration

After connecting the LLM with the MUDRA records using smart search, both test questions were tested again.

### Test 1: MUDRA Categories

Question: What are all four MUDRA categories and their loan limits?

- Result: All four categories were returned correctly.
- Confidence: High
- Observation: The answer matched the retrieved records.

### Test 2: Current SBI Interest Rate

Question: What is the exact current SBI interest rate for a Rs. 3 lakh MUDRA loan?

- Result: The chatbot explained that the retrieved records do not contain SBI interest-rate information.
- Confidence: Low
- Observation: The chatbot avoided inventing a current interest rate.

### Final Conclusion

RAG integration improved the chatbot's factual accuracy by providing relevant project records as context.

Version 2 with retrieved context is the preferred configuration based on these tests. More evaluation questions are still needed before considering the chatbot fully reliable.
