'''
Copyright(c) Liang Yiyan, Pekin University, 2025. All rights reserved.

This file is used for the final processing of generated questions.
Common problems include OCR errors, incorrect order of options, and so on.
Therefore, it is necessary to use some regular matching techniques to identify and correct them.
However, I must point out that these functions may not be applicable to other scenarios, 
so please use them with caution.

Function Table:
OptionsOrderCorrection(QuestionMDText: str = None) -> str
-- Correct the order of options in the question Markdown text
'''

import re

from ModelInterface import ModelInterface
from PromptTemplate import CHOICE_ORDER_JUDGE_PROMPT_TEMPLATE

# Correct the order of options in the question Markdown text
def OptionsOrderCorrection(QuestionMDText: str = None) -> str:
    # In some cases, the four options in the original question's image may be distributed across two lines.
    # At this point, the model may mistakenly change the order of options to ACBD.
    # Therefore, we need to correct the order of options back to ABCD.

    # The pattern for the options is: 
    # A ... \n ... C ... \n ... B ... \n ... D ... \n
    # Among them, ... represents any content.
    OptionsPattern = r'(A.*?\n)(C.*?\n)(B.*?\n)(D.*?\n)'
    MatchResult = re.search(OptionsPattern, QuestionMDText, re.DOTALL)

    if MatchResult:
        # If a match is found, it indicates that the order of options is incorrect.
        # We need to rearrange the options back to ABCD order.
        OptionA = MatchResult.group(1)
        OptionC = MatchResult.group(2)
        OptionB = MatchResult.group(3)
        OptionD = MatchResult.group(4)

        # Ensure that there is only one line break between options after correction
        # Keep possible double line breaks in other parts
        OptionA = re.sub(r'\n+', '\n', OptionA)
        OptionB = re.sub(r'\n+', '\n', OptionB)
        OptionC = re.sub(r'\n+', '\n', OptionC)
        OptionD = re.sub(r'\n+', '\n', OptionD)

        # Joint the corrected and ordered options back to the original text
        CorrectedQuestionMDText =  (
            QuestionMDText[:MatchResult.start()] +
            OptionA + OptionB + OptionC + OptionD +
            QuestionMDText[MatchResult.end():])
        
    else:
        # If no match is found, it indicates that the order of options is correct.
        CorrectedQuestionMDText = QuestionMDText
        
    return CorrectedQuestionMDText

# Check whether the above function works correctly. 
# That means the order of options should be correct.
# We will use LLM to help us judge this fact.
# 
def OptionsOrderCheck(Question: str = None, Model: ModelInterface = None) -> dict:
    if not Question or not Model:
        raise ValueError("Question and Model must be provided.")
    
    # Construct the prompt
    Prompt = CHOICE_ORDER_JUDGE_PROMPT_TEMPLATE.format(Question = Question)
    # Get the model response
    Response = Model.ModelResponse(Prompt = Prompt, MaxTokens = 50)
    # Standardize the model's reply
    Reply = str(Response["Response"]).strip().lower()

    if "true" in Reply:
        return {
            "JudgeResponse": Reply,
            "JudgeResult": True,
        }
    else:
        return {
            "JudgeResponse": Reply,
            "JudgeResult": False,
        }