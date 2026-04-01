import json
import os
from pydantic import ValidationError
from fastapi import HTTPException
from openai_handler import evaluate_resume_with_openai
from resumePreprocessing import ResumeReader
from data_validation import Candidate, JobDetails
import logging
import requests

logger = logging.getLogger(__name__)

async def process_files_from_sqs(message_body: dict):
    """
    Process a single message from SQS and evaluates candidates.
    """
    results = []

    try:
        logger.info(f"Processing message body: {message_body}")

        job_details = message_body.get("jobDetails", {})

        # Process each candidate in the message
        for candidate in message_body.get("candidateDetails", []):
            result = await process_candidate(candidate, job_details)
            results.append(result)

        # If results are found, send them to response queue
        if results:
            from sqs_handler import sqs
            sqs.send_message(
                QueueUrl=os.getenv("RESPONSE_QUEUE_URL"),
                MessageBody=json.dumps(results)  # Send results directly as JSON
            )
            logger.info(f"Results sent to response queue: {os.getenv('RESPONSE_QUEUE_URL')}")

    except Exception as e:
        logger.error(f"Error processing files from SQS: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to process files from SQS.")

    return results

async def process_candidate(candidate_data: dict, job_details_data: dict):
    try:
        # Extract candidate information
        user_id = candidate_data.get('userId', 'unknown')
        job_id = candidate_data.get('jobId', 'unknown')
        email = candidate_data.get('email', 'unknown')
        resume_url = candidate_data.get('resumeUrl', '')

        # Validate input data
        try:
            Candidate(**candidate_data)
            JobDetails(**job_details_data)
        except ValidationError as e:
            logger.error(f"Validation error: {e.json()}")
            return generate_error_response(user_id, job_id, email, "Validation error.")

        # Fetch and process resume
        try:
            resume_reader = ResumeReader()
            response = requests.get(resume_url)
            response.raise_for_status()
            resume_content = resume_reader.read_file(response.content, url_path=resume_url)
        except requests.RequestException as e:
            logger.error(f"Failed to fetch resume: {e}")
            return generate_error_response(user_id, job_id, email, "Failed to fetch resume.")

        # Call OpenAI for evaluation
        evaluation_response = evaluate_resume_with_openai(
            resume_content, job_details_data, candidate_data
        )

        if not isinstance(evaluation_response, dict):
            raise ValueError("OpenAI response is not a valid dictionary.")

        # Extract and directly use OpenAI's evaluation
        application_evaluation = evaluation_response.get("applicationEvaluation", {})
        overall_score = evaluation_response.get("overallScore", 0)

        return {
            "userId": user_id,
            "jobId": job_id,
            "email": email,
            "overallScore": overall_score,
            "applicationEvaluation": application_evaluation,
            "justification": evaluation_response.get("justification", "No justification provided"),
        }

    except Exception as e:
        logger.error(f"Error during candidate processing: {e}")
        return generate_error_response("unknown", "unknown", "unknown", str(e))

def generate_error_response(user_id, job_id, email, message):
    return {
        "userId": user_id,
        "jobId": job_id,
        "email": email,
        "overallScore": 0,
        "applicationEvaluation": {
            "coreCompetencyAlignment": 0,
            "relevantProfessionalExperience": 0,
            "complementaryQualifications": 0,
            "additionalDesiredSkills": 0,
        },
        "justification": message,
    }









# import json
# import os
# from pydantic import ValidationError
# from fastapi import HTTPException
# from openai_handler import evaluate_resume_with_openai
# from resumePreprocessing import ResumeReader
# from data_validation import Candidate, JobDetails
# import logging
# import requests

# logger = logging.getLogger(__name__)


# async def process_files_from_sqs(message_body: dict):
#     """
#     Process a single message from SQS and evaluates candidates.
#     """
#     results = []
    
#     try:
#         logger.info(f"Processing message body: {message_body}")
        
#         job_details = message_body.get("jobDetails", {})
        
#         # Process each candidate in the message
#         for candidate in message_body.get("candidateDetails", []):
#             result = await process_candidate(candidate, job_details)
#             results.append(result)
        
#         # If results are found, send them to response queue
#         if results:
#             from sqs_handler import sqs
#             sqs.send_message(
#                 QueueUrl=os.getenv("RESPONSE_QUEUE_URL"),
#                 MessageBody=json.dumps(results)  # Send results directly as JSON
#             )
#             logger.info(f"Results sent to response queue: {os.getenv('RESPONSE_QUEUE_URL')}")

#     except Exception as e:
#         logger.error(f"Error processing files from SQS: {str(e)}")
#         raise HTTPException(status_code=500, detail="Failed to process files from SQS.")
    
#     return results


# async def process_candidate(candidate_data: dict, job_details_data: dict):
#     try:
#         # Ensure required fields are present or set default values
#         user_id = candidate_data.get('userId', 'unknown')
#         job_id = candidate_data.get('jobId', 'unknown')
#         email = candidate_data.get('email', 'unknown')
#         resume_url = candidate_data.get('resumeUrl', '')  # URL for the resume file

#         # Validate candidate and job details using Pydantic
#         try:
#             Candidate(**candidate_data)
#             JobDetails(**job_details_data)
#         except ValidationError as e:
#             logger.error(f"Validation error for input data: {e.json()}")
#             return {
#                 "userId": user_id,
#                 "jobId": job_id,
#                 "email": email,
#                 "overallScore": 0,
#                 "applicationEvaluation": {
#                     "coreCompetencyAlignment": 0,
#                     "relevantProfessionalExperience": 0,
#                     "complementaryQualifications": 0,
#                     "additionalDesiredSkills": 0,
#                 },
#                 "justification": f"Validation error: {e.errors()}",
#             }

#         # Step 2: Apply validation by capping values to match model constraints
#         application_evaluation = {
#             "coreCompetencyAlignment": min(candidate_data.get('coreCompetencyAlignment', 0), 40),
#             "relevantProfessionalExperience": min(candidate_data.get('relevantProfessionalExperience', 0), 40),
#             "complementaryQualifications": min(candidate_data.get('complementaryQualifications', 0), 15),
#             "additionalDesiredSkills": min(candidate_data.get('additionalDesiredSkills', 0), 5),
#         }

#         # Step 3: Read resume from the URL and extract text
#         # Fetch resume content
#         try:
#             resume_reader = ResumeReader()
#             response = requests.get(resume_url)
#             response.raise_for_status()
#             resume_content = resume_reader.read_file(file_content=response.content, url_path=resume_url)
#         except requests.exceptions.RequestException as e:
#             logger.error(f"Failed to fetch resume for candidate {user_id}: {str(e)}")
#             return {
#                 "userId": user_id,
#                 "jobId": job_id,
#                 "email": email,
#                 "overallScore": 0,
#                 "applicationEvaluation": {
#                     "coreCompetencyAlignment": 0,
#                     "relevantProfessionalExperience": 0,
#                     "complementaryQualifications": 0,
#                     "additionalDesiredSkills": 0
#                 },
#                 "justification": f"Failed to fetch resume: {str(e)}"
#             }
        
#         # Step 4: Call OpenAI API for resume evaluation
#         evaluation_response = await evaluate_resume_with_openai(
#             resume_content=resume_content,
#             job_details=job_details_data,
#             candidate=candidate_data
#         )

#         # Extract the evaluation results from OpenAI's response
#         openai_evaluation = evaluation_response.get('applicationEvaluation', {})

#         # Ensure application evaluation is populated
#         application_evaluation.update({
#             "coreCompetencyAlignment": openai_evaluation.get("coreCompetencyAlignment", application_evaluation["coreCompetencyAlignment"]),
#             "relevantProfessionalExperience": openai_evaluation.get("relevantProfessionalExperience", application_evaluation["relevantProfessionalExperience"]),
#             "complementaryQualifications": openai_evaluation.get("complementaryQualifications", application_evaluation["complementaryQualifications"]),
#             "additionalDesiredSkills": openai_evaluation.get("additionalDesiredSkills", application_evaluation["additionalDesiredSkills"]),
#         })

#         # Calculate overall score from the application evaluation
#         overall_score = (application_evaluation["coreCompetencyAlignment"] +
#                          application_evaluation["relevantProfessionalExperience"] +
#                          application_evaluation["complementaryQualifications"] +
#                          application_evaluation["additionalDesiredSkills"]) / 100 * 100

#         return {
#             "userId": user_id,
#             "jobId": job_id,
#             "email": email,
#             "overallScore": overall_score,
#             "applicationEvaluation": application_evaluation,
#             "justification": evaluation_response.get("justification", "No justification provided"),
#         }

#     except Exception as e:
#         logger.error(f"Error during candidate processing: {e}")
#         return {
#             "userId": "unknown",
#             "jobId": "unknown",
#             "email": "unknown",
#             "overallScore": 0,
#             "applicationEvaluation": {
#                 "coreCompetencyAlignment": 0,
#                 "relevantProfessionalExperience": 0,
#                 "complementaryQualifications": 0,
#                 "additionalDesiredSkills": 0,
#             },
#             "justification": f"Error: {str(e)}",
#         }
