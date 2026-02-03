'''
Copyright(c) Liang Yiyan, Pekin University, 2025. All rights reserved.

These programs are used to temporarily process some files.
The reason why we need to perform these processes may be because the output file format is not satisfactory, 
or there are some special situations that we have not considered.
Therefore, many programs here are likely to be used only once,
and I will not write them in a more general form.
If you are interested, you may take a look and find that they are really simple.
After all, they just need to be usable. No one will pay attention to how they are implemented.

DISCLAIMER:
Please note that this program is only for scientific research and learning purposes.
The author shall not be held legally responsible for any consequences resulting from improper use of the program.

Function Table:
ExtractQuestionIDs(InputJSONLPath: str, SaveFolder: str, OutputJson: list) -> list 
-- Extract question IDs for each subject from a processed question set and return the counts
ExtractMissingQuestionIDs(FirstJSONPath: str, SecondJSONPath: str) -> list 
-- Extract questionIDs that appear in the first file but not in the second file
FileFormatStandardization(ProcessedJSONPath: str) -> None
-- Standardize file formats for later processing
ExtractQuestionAndBankIDs(InputJSONPath: str, RecordJSONPath: str) -> int
-- Extract question IDs and bank IDs for all questions in a given question set
'''

import os
import json

from FileProcess import LogMessage

DEFAULT_OUTPUT_ID_PATH = [
    # The output path for questionIDs of subject "Math"
    "Math.json",
    # The output path for questionIDs of subject "Physics"
    "Physics.json",
    # The output path for questionIDs of subject "Biology"
    "Biology.json"
]

# Extract question IDs for each subject from a processed question set
# The format of the input JSONL file is as follows:
# {
#     "taskId": 1/"1", 
#     "subject": "Math"/"Physics"/"Biology", 
#     ...
# }
# The function will save the extracted question IDs into separate JSON files for each subject.
# The output files will be named according to the OutputJSON parameter. The format is as follows:
# [ "1", "2", "3", ... ]
def ExtractQuestionIDs(InputJSONLPath: str = None, SaveFolder: str = None, OutputJSON: list = DEFAULT_OUTPUT_ID_PATH) -> list: 
    if not os.path.exists(SaveFolder):
        os.makedirs(SaveFolder)

    if not os.path.exists(InputJSONLPath):
        LogMessage(f"Input JSONL file does not exist: {InputJSONLPath}", Type="Error")
        return []

    # Load the input JSONL file
    with open(InputJSONLPath, "r", encoding="utf-8") as infile:
        Lines = infile.readlines()

    # Parse each line as a JSON object
    Data = [json.loads(line) for line in Lines]

    # Prepare lists to store question IDs for each subject
    MathQuestionIDs = []
    PhysicsQuestionIDs = []
    BiologyQuestionIDs = []

    # Iterate through each question entry
    for entry in Data:
        QuestionID = entry.get("taskId", "")
        Subject = entry.get("subject", "")

        # Convert QuestionID to string for consistency
        QuestionID = str(QuestionID)
        
        if Subject == "Math":
            MathQuestionIDs.append(QuestionID)
        elif Subject == "Physics":
            PhysicsQuestionIDs.append(QuestionID)
        elif Subject == "Biology":
            BiologyQuestionIDs.append(QuestionID)

    # Prepare output paths
    MathOutputPath = os.path.join(SaveFolder, OutputJSON[0])
    PhysicsOutputPath = os.path.join(SaveFolder, OutputJSON[1])
    BiologyOutputPath = os.path.join(SaveFolder, OutputJSON[2])

    # Save question IDs to respective JSON files
    with open(MathOutputPath, "w", encoding="utf-8") as mathfile:
        json.dump(MathQuestionIDs, mathfile, ensure_ascii=False, indent=4)

    with open(PhysicsOutputPath, "w", encoding="utf-8") as physicsfile:
        json.dump(PhysicsQuestionIDs, physicsfile, ensure_ascii=False, indent=4)

    with open(BiologyOutputPath, "w", encoding="utf-8") as biologyfile:
        json.dump(BiologyQuestionIDs, biologyfile, ensure_ascii=False, indent=4)

    LogMessage(f"Extracted question IDs saved to {SaveFolder}", Type="INFO")
    return [len(MathQuestionIDs), len(PhysicsQuestionIDs), len(BiologyQuestionIDs)]

# Extract questionIDs that appear in the first file but not in the second file
# The input files should just contain a list of questionIDs
def ExtractMissingQuestionIDs(FirstJSONPath: str = None, SecondJSONPath: str = None) -> list:
    if not os.path.exists(FirstJSONPath):
        LogMessage(f"First JSON file does not exist: {FirstJSONPath}", Type="Error")
        return []

    if not os.path.exists(SecondJSONPath):
        LogMessage(f"Second JSON file does not exist: {SecondJSONPath}", Type="Error")
        return []

    # Load the first JSON file
    with open(FirstJSONPath, "r", encoding="utf-8") as firstfile:
        FirstQuestionIDs = set(json.load(firstfile))

    # Load the second JSON file
    with open(SecondJSONPath, "r", encoding="utf-8") as secondfile:
        SecondQuestionIDs = set(json.load(secondfile))

    # Find question IDs that are in the first set but not in the second
    MissingQuestionIDs = list(FirstQuestionIDs - SecondQuestionIDs)

    LogMessage(f"Found {len(MissingQuestionIDs)} missing question IDs.", Type="INFO")
    return MissingQuestionIDs

# Standardize file formats for later processing 
# NOTE: This function will overwrite the original file, please be cautious when using it.
# Please confirm that you have backed up the original file.
# The format of the original file is as follows:
# { "GoodQuestionIDs": [ ["1", ...], ["2", ...], ... ] }
def FileFormatStandardization(ProcessedJSONPath: str = None) -> None:
    if not os.path.exists(ProcessedJSONPath):
        LogMessage(f"Processed JSON file does not exist: {ProcessedJSONPath}", Type="Error")
        return
    
    # Load the processed JSON file
    with open(ProcessedJSONPath, "r", encoding="utf-8") as infile:
        Data = json.load(infile)

    GoodQuestionIDs = Data.get("GoodQuestionIDs", [])
    StandardQuestionIDs = [item[0] for item in GoodQuestionIDs]

    # Overwrite the original file with standardized format
    with open(ProcessedJSONPath, "w", encoding="utf-8") as outfile:
        json.dump(StandardQuestionIDs, outfile, ensure_ascii=False, indent=4)
        
    LogMessage(f"File format standardized and saved to {ProcessedJSONPath}", Type="INFO")

# Extract question IDs and bank IDs for all questions in a given question set
# The output is a list of tuples like: 
# [ (QuestionID1, BankID1), (QuestionID2, BankID2), ... ]
# We will add all unique question IDs into the output file.
# That means, there will be no duplicate (QuestionID, BankID) pairs in the output file.
# NOTE: This function will overwrite the original file, please be cautious when using it.
# The function will return the total number of unique question IDs in the list.
def ExtractQuestionAndBankIDs(InputJSONPath: str = None, RecordJSONPath: str = None) -> int:
    if not os.path.exists(InputJSONPath):
        LogMessage(f"Input JSON file does not exist: {InputJSONPath}", Type="Error")
        return 0
    
    # Load the input JSON file
    with open(InputJSONPath, "r", encoding="utf-8") as infile:
        Data = json.load(infile)

    AllQuestionBankIDs = []
    QuestionBankIDSet = set()
    # If the record file already exists, we need to load the existing records first
    if os.path.exists(RecordJSONPath):
        with open(RecordJSONPath, "r", encoding="utf-8") as recordfile:
            ExistingRecords = json.load(recordfile)
            for item in ExistingRecords:
                QuestionID = item[0]
                BankID = item[1]
                
                if (QuestionID, BankID) in QuestionBankIDSet:
                    continue
                
                QuestionBankIDSet.add((QuestionID, BankID))
                AllQuestionBankIDs.append((QuestionID, BankID))

    # Iterate each question in the data
    for Question in Data:
        QuestionID = Question.get("QuestionID", "")
        BankID = Question.get("BankID", "")

        if (QuestionID, BankID) in QuestionBankIDSet:
            continue

        QuestionBankIDSet.add((QuestionID, BankID))
        AllQuestionBankIDs.append((QuestionID, BankID))

    # Overwrite the record file with all unique question IDs
    with open(RecordJSONPath, "w", encoding="utf-8") as recordfile:
        json.dump(AllQuestionBankIDs, recordfile, ensure_ascii=False, indent=4)

    LogMessage(f"Extracted {len(AllQuestionBankIDs)} unique question and bank ID pairs.", Type="INFO")
    return len(AllQuestionBankIDs)
