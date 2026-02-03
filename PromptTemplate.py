'''
Copyright(c) Liang Yiyan, Pekin University, 2026. All rights reserved.

This file includes a series of prompt templates required in the project,
including prompts for extracting answers from the provided context,
adjusting the order of multiple-choice options, etc.
Although these prompts may not be very perfect, 
they are more than sufficient for current use cases.

Prompt Table:
CHOICE_ORDER_JUDGE_PROMPT_TEMPLATE(Question: str) 
-- Prompt template for judging the order of multiple-choice options
'''

# Prompt template for judging the order of multiple-choice options
CHOICE_ORDER_JUDGE_PROMPT_TEMPLATE = """
You are a professional question format checker. Please strictly determine whether the options in the following multiple-choice question are arranged in the correct order.

Task Description:
Input: A text that may contain a multiple-choice question
Output: "true", "false", or "unknown"

Requirements:
1. Identify the option section in the question
2. Options typically start with letters (e.g., A, B, C, D or A., B., C., D. or A、B、C、D, etc.)
3. Determine whether these options are arranged in standard alphabetical order (A, B, C, D...)
4. Note: Options may contain formulas or special symbols, which do not affect the order judgment
5. If the same letter appears multiple times, use the first occurrence
6. Options may be distributed across multiple lines or on the same line - both need to be recognized
7. Note: Questions may contain more than 4 options - judge whether ALL options are in sequential order

Important Cases:
- If options are in INCORRECT order like A, C, B, D, return "false"
- If options are in CORRECT alphabetical order like A, B, C, D, return "true"
- If there are no identifiable options, return "unknown"

Examples:
Input 1: "Question content... A. Option 1 B. Option 2 C. Option 3 D. Option 4 E. Option 5" → Output: "true"
Input 2: "Question content... A. Option 1 C. Option 3 B. Option 2 D. Option 4" → Output: "false"
Input 3: "Question content... no clear options" → Output: "unknown"

Critical Instructions:
- Respond with ONLY one word: "true", "false", or "unknown"
- Do NOT provide explanations or additional text
- Be case-insensitive in your response

Now judge the following question:
{Question}
"""