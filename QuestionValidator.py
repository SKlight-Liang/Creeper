'''
Copyright(c) Liang Yiyan, Pekin University, 2026. All rights reserved.

The program in this file is used to verify whether the obtained questions are difficult enough 
for a large language model. We will choose a baseline model to answer these questions, 
then another model with stronger reasoning ability will check whether the baseline model's answer is correct.
If the answer is correct, it indicates that the question is not difficult enough, so we need to throw it away.
You can refer to the BatchProcessor.py for the subsequent processing procedures. 

Function Table:
BaselineModelAnswer(Question: dict, BaselineModel: ModelInterface) -> dict
-- Submit a question to the baseline model and extract the answer from the response.
JudgingModelResponse(Question: str, BaselineAnswer: str, GroundTruthAnswer: str, JudgingModel: ModelInterface) -> dict
-- Check whether the baseline model's answer is correct.
MultipleJudging(Question: dict, BaselineModel: ModelInterface, JudgingModel: ModelInterface, Rounds: int = 5) -> dict
-- Conduct multiple rounds of judging and take the majority vote as the final result.
'''

import re

from ModelInterface import ModelInterface

from FileProcess import LogMessage
from FileProcess import EncodeImageToBase64

from PromptTemplate import ANSWER_JUDGE_PROMPT_TEMPLATE

# Submit a question to the baseline model and extract the answer from the response.
# Your question should at least include the following two parts:
# { "Question": ..., "ImagePath": ... }
# NOTE: The model will take a long time to thik deeply. To avoid timeouts or other issues like 
# network fluctuations, you can set a timeout value in the ModelInterface class(We will add this feature in the future).
# We suggest setting a timeout value of at least 1800 seconds (30 minutes) for the baseline model.
def BaselineModelAnswer(Question: dict = None, BaselineModel: ModelInterface = None) -> dict:
    # Check if the question and baseline model are provided
    if not Question or not BaselineModel:
        LogMessage("Question and BaselineModel must be provided.", Type = "ERROR")
        return None

    # Obtain the question text and image path from the input question
    QuestionText = Question.get("Question"  , "")
    ImagePaths   = Question.get("ImagePaths", "")

    # Convert the image to Base64 format for model input
    # Here we assume that the image is stored locally, so we need to read it and convert it to Base64 format.
    # If your image is already in Base64 format or accessible via a public URL, 
    # you can directly use it as input without conversion.
    ImageURLs = []
    for ImagePath in ImagePaths:
        ImageBase64 = EncodeImageToBase64(ImagePath)
        if ImageBase64:
            ImageURLs.append(ImageBase64)

    # Prompt template for the baseline model to answer the question
    # The reason why we use this prompt template is to ensure that we can easily extract the answer 
    # from the model's response, which is crucial for subsequent verification.
    ANSWER_PROMPT_TEMPLATE = "\n Please put all the final answers inside one \\boxed{} ."

    # Submit the question to the baseline model and get the response
    Prompt   = QuestionText + ANSWER_PROMPT_TEMPLATE
    Response = BaselineModel.ModelResponse(Prompt = Prompt, ImageURLs = ImageURLs, MaxTokens = 65536)

    ModelResponseText  = Response.get("Response", None)
    ModelReasoningText = Response.get("Reasoning", None)

    if ModelResponseText is None:
        LogMessage("Baseline model did not return a response.", Type = "ERROR")
        return None
    
    # Find all positions where the pattern "\boxed{...}" appears in the model's response.
    # Here we require that there must be no characters between "\boxed" and "{", except for spaces.
    # This can prevent "{...}" from being mistakenly recognized as the answer elsewhere in the response.
    AnswerPattern = r'\\boxed\s*{'
    AnswerMatches = list(re.finditer(AnswerPattern, ModelResponseText))
    if not AnswerMatches:
        LogMessage("No answer found in the baseline model's response.", Type = "WARNING")
        return None

    # Check each matching item from back to front.
    # And select the last one that can be successfully extracted as the final answer.
    # This means its "{" and "}" pairs are complete and correctly nested, 
    # which can ensure the reliability of the extracted answer.
    for Match in reversed(AnswerMatches):
        # Start from the position of the current match and move forward to find the corresponding "{" and "}" pairs.
        Pointer = Match.end()
        OpenBraces = 1

        while Pointer < len(ModelResponseText) and OpenBraces > 0:
            if ModelResponseText[Pointer] == '{':
                OpenBraces += 1
            elif ModelResponseText[Pointer] == '}':
                OpenBraces -= 1
            Pointer += 1

        if OpenBraces == 0:
            # Successfully found a complete answer, extract it and return
            Answer = ModelResponseText[Match.end():Pointer-1].strip()
            return {
                "Answer": Answer,
                "ModelResponse": ModelResponseText,
                "ModelReasoning": ModelReasoningText
            }
        
    # If we cannot find a complete answer, just return model response for reference.
    LogMessage("No complete answer found in the baseline model's response.", Type = "WARNING")
    return {
        "Answer": None,
        "ModelResponse": ModelResponseText,
        "ModelReasoning": ModelReasoningText
    }

# NOTE: The code for extracting answers refers to the following function.
# If the code could not work properly, you can consider using the following one.
def ExtractBoxedAnswer(ModelResponseText: str = None) -> str:
    # Find the starting position of all occurrences of the pattern "\\boxed{...}" in the model's response.
    # Here we allow spaces between "\\boxed" and "{", that means the pattern can be "\\boxed{", "\\boxed {" and so on.
    BoxPattern = r'\\boxed\s*{'
    BoxMatches = list(re.finditer(BoxPattern, ModelResponseText))
    if not BoxMatches:
        return None

    # Take the last occurrence of the pattern
    StartIndex = BoxMatches[-1].start()
    # Find the position of the first "{" after this "\\boxed", 
    # which will be considered as the starting position of the answer. 
    OpenBraceIndex = ModelResponseText.find("{", StartIndex)
    if OpenBraceIndex == -1:
        return None

    # The answer starts after the first "{", so we set the pointer to the next position.
    Pointer = OpenBraceIndex + 1
    BraceCount = 1
    # Scan forward to find the corresponding "}" that matches the first "{".
    while Pointer < len(ModelResponseText) and BraceCount > 0:
        if ModelResponseText[Pointer] == '{':
            BraceCount += 1
        elif ModelResponseText[Pointer] == '}':
            BraceCount -= 1
        Pointer += 1

    # If the BraceCount is not zero, it indicates that the braces are not properly matched, 
    # and we cannot extract a valid answer.
    if BraceCount != 0:
        return None

    # Extract the answer from the model's response.
    Answer = ModelResponseText[OpenBraceIndex+1:Pointer-1].strip()
    return Answer

# According to the question, the answer provided by the baseline model and the ground-truth answer,
# a stronger model will check whether the baseline model's answer is correct.
# Here we recommend using "Google: Gemini 3.1 Flash Lite Preview" as the judging model.
def JudgingModelResponse(
        Question: str = "", BaselineAnswer: str = "", 
        GroundTruthAnswer: str = "", JudgingModel: ModelInterface = None) -> dict:
    
    if not Question or not BaselineAnswer or not GroundTruthAnswer or not JudgingModel:
        LogMessage("Question, BaselineAnswer, GroundTruthAnswer and JudgingModel must be provided.", Type = "ERROR")
        return None
    
    # Construct the prompt for the judging model
    Prompt = ANSWER_JUDGE_PROMPT_TEMPLATE.format(
        Question = Question,
        GroundTruthAnswer = GroundTruthAnswer,
        ModelOutput = BaselineAnswer
    )

    # Get the judging model's response
    Response = JudgingModel.ModelResponse(Prompt = Prompt, MaxTokens = 2048)
    JudgeResult = Response.get("Response", None)

    if JudgeResult is not None and "TRUE" in JudgeResult.strip().upper():
        return {
            "LLMJudgeResult": True,
            "LLMJudgeResponse": JudgeResult,
            "LLMJudgeReasoning": Response.get("Reasoning", None)
        }
    elif JudgeResult is not None and "FALSE" in JudgeResult.strip().upper():
        return {
            "LLMJudgeResult": False,
            "LLMJudgeResponse": JudgeResult,
            "LLMJudgeReasoning": Response.get("Reasoning", None)
        }
    else:
        LogMessage("Judging model did not return a clear TRUE or FALSE response.", Type = "WARNING")
        return {
            "LLMJudgeResult": False,
            "LLMJudgeResponse": JudgeResult,
            "LLMJudgeReasoning": Response.get("Reasoning", None)
        }
    
# To enhance the credibility and robustness of the judging result, 
# we need to conduct multiple rounds of judging and take the majority vote as the final result.
# We will use pass@k as an indicator for verifying whether the model can answer the question correctly.
# Here your question should at least include the following three parts:
# { "Question": ..., "ImagePath": ..., "GroundTruthAnswer": ... }
def MultipleJudging(
        Question: dict = None, BaselineModel: ModelInterface = None, 
        JudgingModel: ModelInterface = None, Rounds: int = 5
    ) -> dict:

    AllResults = []
    PassCount  = 0
    
    for Round in range(Rounds):
        # Get the baseline model's answer for the question
        BaselineResult = BaselineModelAnswer(Question = Question, BaselineModel = BaselineModel)
        BaselineAnswer = BaselineResult.get("Answer", None)

        # Use the judging model to check whether the baseline model's answer is correct
        if BaselineAnswer is not None:    
            JudgeResult = JudgingModelResponse(
                Question = Question.get("Question", ""),
                BaselineAnswer = BaselineAnswer,
                GroundTruthAnswer = Question.get("GroundTruthAnswer", ""),
                JudgingModel = JudgingModel
            )

            # Collect the results of each round for later analysis
            AllResults.append({
                "TestRound": Round + 1,
                "Baseline": BaselineAnswer,
                "Judger": JudgeResult
            })

            # Calculate the pass@k value based on the judging results
            if JudgeResult.get("LLMJudgeResult", False):
                PassCount += 1

    # Calculate the final pass@k value
    PassRate = PassCount / Rounds if Rounds > 0 else 0

    return {
        "Question": Question,
        "Results": AllResults,
        "TotalRounds": Rounds,
        "PassRate": PassRate
    }