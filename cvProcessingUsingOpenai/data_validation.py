import logging
from pydantic import BaseModel, Field
from typing import Optional, List

# Initialize logger
logger = logging.getLogger(__name__)

# Define your Pydantic models
class ApplicationEvaluation(BaseModel):
    coreCompetencyAlignment: int = Field(ge=0, le=40, alias="coreCompetencyAlignment", description="Score out of 40")
    relevantProfessionalExperience: int = Field(ge=0, le=40, alias="relevantProfessionalExperience", description="Score out of 40")
    complementaryQualifications: int = Field(ge=0, le=15, alias="complementaryQualifications", description="Score out of 15")
    additionalDesiredSkills: int = Field(ge=0, le=5, alias="additionalDesiredSkills", description="Score out of 5")

    class Config:
        populate_by_name = True

class EvaluationResponse(BaseModel):
    userId: str
    jobId: str
    email: str
    overallScore: int = Field(ge=0, le=100, description="Overall score as a percentage")
    applicationEvaluation: ApplicationEvaluation
    justification: str

    class Config:
        populate_by_name = True

class Candidate(BaseModel):
    userId: str
    jobId: str
    email: str
    resumeUrl: str

class JobDetails(BaseModel):
    jobTitle: str = Field(..., min_length=1, description="Job title must be at least 1 character long")
    jobLocation: str = Field(..., min_length=1, description="Job location must be valid")
    country: str = Field(..., min_length=1, description="Country must be valid")
    workExperienceMin: int = Field(..., ge=0, description="Minimum work experience, must be non-negative")
    workExperienceMax: int = Field(..., ge=0, description="Maximum work experience, must be non-negative")
    mustHaveSkills: List[str] = Field(..., description="List of required skills (non-empty strings)")
    goodToHaveSkills: List[str] = Field(..., description="List of good-to-have skills (non-empty strings)")
    jobRole: str = Field(..., min_length=1, description="Job role must be non-empty")
    department: str = Field(..., min_length=1, description="Department name must be non-empty")
    jobDescription: str = Field(..., min_length=1, description="Job description must be non-empty")
    availability: Optional[str] = Field(None, min_length=1, description="Availability is optional, but must be non-empty if present")

    class Config:
        populate_by_name = True