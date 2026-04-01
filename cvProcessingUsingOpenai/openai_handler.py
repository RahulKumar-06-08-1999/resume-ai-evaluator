import openai
import json
import logging

logger = logging.getLogger("openai_handler")


def evaluate_resume_with_openai(resume_content, job_details, candidate):
    try:
        # Make the API call
        openai_response = openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an AI that evaluates candidates for job postings based on job descriptions and resumes. "
                        "Your goal is to provide an objective assessment strictly based on the provided details and evaluation criteria. "
                        "Ensure all calculations and categorizations are accurate and strictly formatted as JSON."
                    ),
                },
                {
                    "role": "user",
                    "content": f"""
                    The following job description is provided:
                    {job_details}

                    The following candidate details are provided:
                    {candidate}

                    The following is the resume content of the candidate:
                    {resume_content}

                    **Evaluation Criteria:**
                    1. **Core Competency Alignment**: Evaluate how well the candidate's skills match the must-have skills in the job description. Score out of 40.
                    2. **Relevant Professional Experience**: Evaluate how well the candidate's work experience aligns with the required experience range in the job description. Score out of 40.
                    3. **Complementary Qualification**: Evaluate how well the candidate's skills match the good-to-have skills in the job description. Score out of 15.
                    4. **Additional Desirable Skills**: Evaluate location preference, availability, and language fluency against the job description. Score out of 5.

                    Generate a final **overallScore** as the sum of these four scores (out of 100).

                    Based on the overallScore:
                    - Categorize the candidate as **Recommended** (85% and above), **Potential** (50% to 85%), or **Less Likely** (below 50%).

                    **Output Format:**
                    Provide your response in **strict JSON** format with no additional commentary:
                    {{
                        "userId": "{candidate['userId']}",
                        "jobId": "{candidate['jobId']}",
                        "email": "{candidate['email']}",
                        "overallScore": "<calculated percentage>",
                        "applicationEvaluation": {{
                            "coreCompetencyAlignment": "<score>",
                            "relevantProfessionalExperience": "<score>",
                            "complementaryQualifications": "<score>",
                            "additionalDesiredSkills": "<score>"
                        }},
                        "justification": "<reason for categorization>"
                    }}
                    """
                },
            ],
            temperature=0.6,
            max_tokens=1200,
        )

        # Log raw response
        logger.info(f"Raw OpenAI Response: {openai_response}")

        # Extract the response content
        response_content = openai_response.choices[0].message.content.strip()

        # Attempt to isolate JSON from the response
        json_start = response_content.find("{")
        json_end = response_content.rfind("}") + 1

        if json_start == -1 or json_end == -1:
            raise ValueError("No valid JSON found in the OpenAI response.")

        response_json_str = response_content[json_start:json_end]

        # Parse the JSON response
        evaluation_data = json.loads(response_json_str)

        return {
            "userId": evaluation_data.get("userId"),
            "jobId": evaluation_data.get("jobId"),
            "email": evaluation_data.get("email"),
            "overallScore": evaluation_data.get("overallScore"),
            "applicationEvaluation": evaluation_data.get("applicationEvaluation", {}),
            "justification": evaluation_data.get("justification", "No justification provided."),
        }

    except Exception as e:
        logger.error(f"Error during evaluation: {str(e)}")
        return {
            "userId": candidate.get("userId"),
            "jobId": candidate.get("jobId"),
            "email": candidate.get("email"),
            "overallScore": 0,
            "applicationEvaluation": {
                "coreCompetencyAlignment": 0,
                "relevantProfessionalExperience": 0,
                "complementaryQualifications": 0,
                "additionalDesiredSkills": 0,
            },
            "justification": "Error during OpenAI API call or response parsing.",
        }








# import openai
# import json
# import re
# import logging

# logger = logging.getLogger(__name__)

# # Helper function to clean and cap the score values
# def clean_score(score, max_value):
#     score_value = int(re.sub(r"\D", "", str(score)))  # Extract the numeric value
#     return min(max(score_value, 0), max_value)


# # Function to evaluate the resume with OpenAI
# async def evaluate_resume_with_openai(resume_content, job_details, candidate):
#     try:
#         openai_response = openai.chat.completions.create(
#             model="gpt-4",  # Use GPT-4 for high-quality results
#             messages=[
#                 {
#                     "role": "system",
#                     "content": (
#                         "You are an AI that evaluates candidates for job postings based on job descriptions and resumes. "
#                         "Your goal is to provide an objective assessment strictly based on the provided details and evaluation criteria. "
#                         "Ensure all calculations and categorizations are accurate and strictly formatted as JSON."
#                     ),
#                 },
#                 {
#                     "role": "user",
#                     "content": f"""
#                     The following job description is provided:
#                     {job_details}

#                     The following candidate details are provided:
#                     {candidate}

#                     The following is the resume content of the candidate:
#                     {resume_content}

#                     **Evaluation Criteria:**
#                     1. **Core Competency Alignment**: Evaluate how well the candidate's skills match the must-have skills in the job description. Score out of 40.
#                     2. **Relevant Professional Experience**: Evaluate how well the candidate's work experience aligns with the required experience range in the job description. Score out of 40.
#                     3. **Complementary Qualification**: Evaluate how well the candidate's skills match the good-to-have skills in the job description. Score out of 15.
#                     4. **Additional Desirable Skills**: Evaluate location preference, availability, and language fluency against the job description. Score out of 5.

#                     Generate a final **overallScore** as the sum of these four scores (out of 100).
        
#                     Based on the overallScore:
#                     - Categorize the candidate as **Recommended** (85% and above), **Potential** (50% to 85%), or **Less Likely** (below 50%).
        
#                     **Output Format:**
#                     Provide your response in **strict JSON** format with no additional commentary:
#                     {{
#                         "userId": "{candidate['userId']}",
#                         "jobId": "{candidate['jobId']}",
#                         "email": "{candidate['email']}",
#                         "overallScore": "<calculated percentage>",
#                         "applicationEvaluation": {{
#                             "coreCompetencyAlignment": "<score>",
#                             "relevantProfessionalExperience": "<score>",
#                             "complementaryQualifications": "<score>",
#                             "additionalDesiredSkills": "<score>"
#                         }},
#                         "justification": "<reason for categorization>"
#                     }}
#                     """
#                 },
#             ],
#             temperature=0.6,
#             max_tokens=1200,
#         )

#         # Log raw response
#         logger.info(f"Raw OpenAI Response: {openai_response}")

#         # Extract content from the response
#         response_content = openai_response.choices[0].message.content.strip()

#         # Extract JSON part of the response
#         json_start = response_content.find("{")
#         json_end = response_content.rfind("}") + 1

#         if json_start == -1 or json_end == -1:
#             raise ValueError("No valid JSON found in the OpenAI response.")

#         response_json = response_content[json_start:json_end]

#         # Parse JSON response
#         evaluation_data = json.loads(response_json)

#         # Clean scores
#         application_evaluation = evaluation_data.get("applicationEvaluation", {})
#         cleaned_scores = {
#             "coreCompetencyAlignment": clean_score(application_evaluation.get("coreCompetencyAlignment", 0), 40),
#             "relevantProfessionalExperience": clean_score(application_evaluation.get("relevantProfessionalExperience", 0), 40),
#             "complementaryQualifications": clean_score(application_evaluation.get("complementaryQualifications", 0), 15),
#             "additionalDesiredSkills": clean_score(application_evaluation.get("additionalDesiredSkills", 0), 5),
#         }

#         overall_score = clean_score(evaluation_data.get("overallScore", "0%"), 100)

#         return {
#             "userId": evaluation_data["userId"],
#             "jobId": evaluation_data["jobId"],
#             "email": evaluation_data["email"],
#             "overallScore": overall_score,
#             "applicationEvaluation": cleaned_scores,
#             "justification": evaluation_data.get("justification", "No justification provided."),
#         }

#     except Exception as e:
#         logger.error(f"Error during evaluation: {str(e)}")
#         return {
#             "userId": candidate.get("userId"),
#             "jobId": candidate.get("jobId"),
#             "email": candidate.get("email"),
#             "overallScore": 0,
#             "applicationEvaluation": {
#                 "coreCompetencyAlignment": 0,
#                 "relevantProfessionalExperience": 0,
#                 "complementaryQualifications": 0,
#                 "additionalDesiredSkills": 0,
#             },
#             "justification": "Error during OpenAI API call or response parsing.",
#         }
    

    