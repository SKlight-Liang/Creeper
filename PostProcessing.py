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
OptionsOrderCheck(Question: str = None, Model: ModelInterface = None) -> dict
-- Check whether the above function works correctly, which means the order of options should be correct.
ExtractAnswer(AnswerMDText: str = None) -> str
-- Extract answer from the question Markdown text. 
'''

import re

from ModelInterface import ModelInterface
from PromptTemplate import CHOICE_ORDER_JUDGE_PROMPT_TEMPLATE

from MarkdownProcess import ClearMDFormatting

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

# Check whether the above function works correctly, which means the order of options should be correct.
# We will use LLM to help us judge this fact.
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
    
# The following function could extract answer from the question Markdown text.
# However, it is really headache that the format of the answer is not always the same,
# thus I have to add a lot of matching logic to try to cover as many cases as possible, but it is still not perfect.
# A better way is to use LLM to help us extract the answer. Maybe you can try to complete this by yourself.
def ExtractAnswer(AnswerMDText: str = None, IsMultiChoice: bool = False) -> str:

    AnswerMDText = ClearMDFormatting(AnswerMDText)

    # The AnswerMDText usually could be split by brackets, like "【答案】""【详解】" and so on.
    # So we can try to split the text by these brackets and then find the part that contains the answer.
    SIDENT1 = "【"
    SIDENT2 = "】"

    # Split the text by the brackets
    Matches = []
    Details = []

    Pattern = rf"{SIDENT1}(.*?){SIDENT2}"
    Matches = re.findall(Pattern, AnswerMDText)
    Length  = len(Matches)

    for i in range(1, Length):
        DetailsPattern = rf"{SIDENT1}{Matches[i-1]}{SIDENT2}([\s\S]*?){SIDENT1}{Matches[i]}{SIDENT2}"
        DetailMatch = re.findall(DetailsPattern, AnswerMDText)
        if DetailMatch:
            Details.append(DetailMatch[0].strip())

    # Note that the last part of the text after the last bracket may also contain the answer, so we need to check it as well.
    DetailsPattern = rf"{SIDENT1}{Matches[-1]}{SIDENT2}([\s\S]*)"
    DetailMatch = re.findall(DetailsPattern, AnswerMDText)
    if DetailMatch:
        Details.append(DetailMatch[0].strip())

    # Usually, the answer will appear in the part that contains the keyword "答案".
    # If we could not find such part, we need to extract the answer from the parts that contain the keyword "详解".
    ANSWER_KEYWORD    = "答案"
    REASONING_KEYWORD = "详解"
    
    # First, we try to find the part that contains the answer keyword.
    AnswerIndex    = Matches.index(ANSWER_KEYWORD) if ANSWER_KEYWORD in Matches else -1
    ReasoningIndex = Matches.index(REASONING_KEYWORD) if REASONING_KEYWORD in Matches else -1

    if AnswerIndex != -1 and Details[AnswerIndex].strip() != "":
        Answer = Details[AnswerIndex]
        # The rest of the parts are considered as the analysis of the question.
        del Details[AnswerIndex]
        Analysis = "\n".join(Details)

        return Answer, Analysis

    # If we cannot find the part that contains the answer keyword, we try to find the part that contains the reasoning keyword.
    if not IsMultiChoice or ReasoningIndex == -1 or Details[ReasoningIndex].strip() == "":
        # If we cannot find the part that contains the reasoning keyword, give up.
        Answer   = ""
        Analysis = "\n".join(Details)

        return Answer, Analysis
    
    
    # --------------- Answer Extraction Logic for Multiple-Choice Questions ---------------
    # NOTE: The following content is only applicable to multiple-choice questions.
    # We cannot guarantee that it is also valid for other types of questions.

    # The answer usually appears after the symbol word "答案为/是" or "故选" in the reasoning part.
    # We can try to extract the answer by matching these symbols. 
    # But I have to point out that the answer will not appear after the symbol word "故选项".
    # So we need to make sure that our regular expression does not match this condition.
    SYMBOLPATTERN1 = r"答案[为是][:：]\s*(.*)"
    SYMBOLPATTERN2 = r"故选[^a-zA-Z0-9项]*([a-zA-Z0-9]+)[^a-zA-Z0-9]*"

    ReasoningText = Details[ReasoningIndex]
    SymbolMatch   = re.search(SYMBOLPATTERN1, ReasoningText)
    if not SymbolMatch:
        SymbolMatch = re.search(SYMBOLPATTERN2, ReasoningText)

    if SymbolMatch:
        Answer   = SymbolMatch[1].strip()
        # Since the answer is extracted from the reasoning part, there is no need to delete the answer part
        Analysis = "\n".join(Details)

        return Answer, Analysis
    
    # If none of the above methods are feasible, that means we should combine the answer by outselves.
    # We can try to find all the pattern "故...正确", and extract the options in these patterns to form the answer.
    COMBINEPATTERN = r"故(.*?)正确"
    CombineMatches = re.findall(COMBINEPATTERN, ReasoningText)

    if CombineMatches:
        Answer   = "".join([re.search(r"[A-Z]+", Match).group(0) for Match in CombineMatches])
        Analysis = "\n".join(Details)

        return Answer, Analysis
    # --------------- End of Answer Extraction Logic ---------------
    
    # If we cannot find any answer-related information in the reasoning part, we have to give up.
    Answer   = ""
    Analysis = "\n".join(Details)

    return Answer, Analysis