# 🤖 AI Resume Processor

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115.6-009688.svg)](https://fastapi.tiangolo.com)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4-412991.svg)](https://openai.com)
[![AWS](https://img.shields.io/badge/AWS-SQS%20%7C%20Textract-FF9900.svg)](https://aws.amazon.com)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

> An intelligent, AI-powered resume evaluation system that leverages OpenAI GPT-4 to objectively assess candidates against job descriptions with automated scoring and categorization.

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Architecture](#-architecture)
- [Features](#-features)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Usage](#-usage)
- [API Endpoints](#-api-endpoints)
- [Evaluation Criteria](#-evaluation-criteria)
- [File Structure](#-file-structure)
- [Dependencies](#-dependencies)

---

## 🌟 Overview

This project automates the candidate screening process by using OpenAI's GPT-4 model to analyze resumes against job descriptions. It extracts text from various document formats (PDF, DOCX, TXT), processes them using AWS services, and generates objective evaluations with scoring breakdowns.

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         AI RESUME PROCESSOR                             │
├─────────────────────────────────────────────────────────────────────────┤
│  Input Documents        Processing Pipeline         Evaluation Output    │
│                                                                         │
│  ┌───────────┐    ┌──────────────┐   ┌──────────┐    ┌───────────────┐  │
│  │   PDF     │───▶│   AWS        │──▶│  OpenAI  │───▶│   Scored      │  │
│  │   DOCX    │    │   Textract   │   │  GPT-4   │    │   Candidate   │  │
│  │   TXT     │    │   (OCR)      │   │  API     │    │   Evaluation  │  │
│  └───────────┘    └──────────────┘   └──────────┘    └───────────────┘  │
│        │                 │                  │               │          │
│        ▼                 ▼                  ▼               ▼          │
│  ┌────────────────────────────────────────────────────────────────┐  │
│  │                     SQS Message Queue                          │  │
│  └────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                              CLIENT/SQS QUEUE                                │
│                              (Resume Upload)                                   │
└────────────────────────┬─────────────────────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                           FASTAPI APPLICATION                                  │
│  ┌────────────────────────────────────────────────────────────────────────┐   │
│  │  @repeat_every(seconds=10)                                             │   │
│  │  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐                │   │
│  │  │   Check     │───▶│  Process    │───▶│   Send      │                │   │
│  │  │   SQS Queue │    │  Messages   │    │   Results   │                │   │
│  │  └─────────────┘    └─────────────┘    └─────────────┘                │   │
│  └────────────────────────────────────────────────────────────────────────┘   │
└────────────────────────┬─────────────────────────────────────────────────────┘
                         │
         ┌───────────────┼───────────────┐
         ▼               ▼               ▼
┌─────────────┐   ┌─────────────┐   ┌─────────────┐
│  AWS SQS    │   │  AWS        │   │  OpenAI     │
│  (Input/    │   │  Textract   │   │  GPT-4 API  │
│  Output)    │   │  (OCR)      │   │             │
└─────────────┘   └─────────────┘   └─────────────┘
```

---

## ✨ Features

### 📄 Document Processing
- **Multi-format Support**: PDF, DOCX, TXT files
- **OCR Capability**: AWS Textract for scanned/image-based PDFs
- **Intelligent Extraction**: pdfplumber for native PDFs, python-docx for Word documents

### 🤖 AI-Powered Evaluation
- **OpenAI GPT-4 Integration**: Advanced natural language processing
- **Objective Scoring**: Four-dimensional evaluation criteria
- **Categorization**: Automatic candidate classification (Recommended/Potential/Less Likely)

### ☁️ AWS Integration
- **SQS Queues**: Asynchronous message processing
- **Textract OCR**: Scanned document text extraction
- **S3 Storage**: Resume file storage and retrieval

### 🔒 Data Validation
- **Pydantic Models**: Strict input/output validation
- **Error Handling**: Graceful failure management with detailed logging

---

## 📦 Installation

### Prerequisites
- Python 3.11+
- AWS Account with SQS and Textract access
- OpenAI API Key

### Step 1: Clone the Repository
```bash
git clone https://github.com/yourusername/ai-resume-processor.git
cd ai-resume-processor
```

### Step 2: Create Virtual Environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

---

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the project root (see `.env.example` for template):

```bash
cp .env.example .env
```

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `OPENAI_API_KEY` | Your OpenAI API key | `sk-abc123...` |
| `AWS_ACCESS_KEY_ID` | AWS IAM access key | `AKIAIOSFODNN7EXAMPLE` |
| `AWS_SECRET_ACCESS_KEY` | AWS IAM secret key | `wJalrXUtnFEMI...` |
| `AWS_REGION` | AWS region | `ap-south-1` |
| `QUEUE_URL` | SQS input queue URL | `https://sqs...` |
| `RESPONSE_QUEUE_URL` | SQS output queue URL | `https://sqs...` |
| `APP_TITLE` | FastAPI app title | `AI Resume Processor` |
| `APP_VERSION` | App version | `1.0.0` |
| `DESCRIPTION` | App description | `AI-powered resume evaluation` |
| `IS_DEBUG` | Debug mode | `True` |

---

## 🚀 Usage

### Start the Application
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Access the API
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/

### Message Format (SQS Input)

```json
{
  "jobDetails": {
    "jobTitle": "Senior Python Developer",
    "jobLocation": "Bangalore",
    "country": "India",
    "workExperienceMin": 5,
    "workExperienceMax": 10,
    "mustHaveSkills": ["Python", "FastAPI", "AWS"],
    "goodToHaveSkills": ["Docker", "Kubernetes", "CI/CD"],
    "jobRole": "Backend Developer",
    "department": "Engineering",
    "jobDescription": "We are looking for an experienced Python developer...",
    "availability": "Immediate"
  },
  "candidateDetails": [
    {
      "userId": "user-123",
      "jobId": "job-456",
      "email": "candidate@example.com",
      "resumeUrl": "https://s3.amazonaws.com/bucket/resume.pdf"
    }
  ]
}
```

### Evaluation Response Format

```json
{
  "userId": "user-123",
  "jobId": "job-456",
  "email": "candidate@example.com",
  "overallScore": 85,
  "applicationEvaluation": {
    "coreCompetencyAlignment": 35,
    "relevantProfessionalExperience": 32,
    "complementaryQualifications": 12,
    "additionalDesiredSkills": 4
  },
  "justification": "Candidate has strong Python experience and AWS certification. Recommended for interview."
}
```

---

## 🔌 API Endpoints

```
┌─────────────────────────────────────────────────────────────┐
│                      API ENDPOINTS                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  GET  /                                                     │
│  ├── Description: Health check / Welcome message           │
│  └── Response: {"message": "Welcome to AIDIPH AI API"}      │
│                                                             │
│  GET  /docs                                                 │
│  ├── Description: Interactive API documentation (Swagger)    │
│  └── Auto-generated by FastAPI                             │
│                                                             │
│  GET  /redoc                                              │
│  ├── Description: Alternative API documentation (ReDoc)      │
│  └── Auto-generated by FastAPI                             │
│                                                             │
│  (Background Task: SQS Polling)                             │
│  ├── Trigger: Every 10 seconds (@repeat_every)             │
│  └── Action: Process pending messages from SQS queue       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 📊 Evaluation Criteria

The AI evaluates candidates across four dimensions with a total score of 100 points:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      EVALUATION SCORING MATRIX                           │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  1. Core Competency Alignment        [0 - 40 points]           │   │
│  │     └─▶ Match with must-have skills from job description       │   │
│  ├─────────────────────────────────────────────────────────────────┤   │
│  │  2. Relevant Professional Experience [0 - 40 points]           │   │
│  │     └─▶ Years of experience alignment with requirements        │   │
│  ├─────────────────────────────────────────────────────────────────┤   │
│  │  3. Complementary Qualifications     [0 - 15 points]           │   │
│  │     └─▶ Good-to-have skills and additional certifications      │   │
│  ├─────────────────────────────────────────────────────────────────┤   │
│  │  4. Additional Desirable Skills        [0 - 5 points]            │   │
│  │     └─▶ Location, availability, language fluency               │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  ╔═══════════════════════════════════════════════════════════════════╗  │
│  ║                    CANDIDATE CATEGORIZATION                        ║  │
│  ╠═══════════════════════════════════════════════════════════════════╣  │
│  ║  ⭐ RECOMMENDED (85% - 100%)  →  Strong match, proceed to interview║  │
│  ║  🟡 POTENTIAL    (50% - 84%)  →  Moderate match, consider for review║  │
│  ║  🔴 LESS LIKELY  (0%  - 49%)  →  Weak match, likely not a fit     ║  │
│  ╚═══════════════════════════════════════════════════════════════════╝  │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 📁 File Structure

```
ai-resume-processor/
│
├── 📄 main.py                  # FastAPI application entry point
│                                # - Initializes app with config
│                                # - Sets up SQS polling (10s interval)
│                                # - Configures OpenAI API
│
├── 📄 candidate_processor.py  # Core processing logic
│                                # - Fetches resumes from URLs
│                                # - Validates data with Pydantic
│                                # - Orchestrates OpenAI evaluation
│                                # - Sends results to response queue
│
├── 📄 openai_handler.py         # OpenAI GPT-4 integration
│                                # - Constructs evaluation prompts
│                                # - Parses AI responses
│                                # - Handles JSON extraction
│
├── 📄 resumePreprocessing.py    # Document processing module
│                                # - PDF extraction (pdfplumber)
│                                # - DOCX extraction (python-docx)
│                                # - OCR for scanned docs (AWS Textract)
│                                # - Text cleaning and normalization
│
├── 📄 sqs_handler.py           # AWS SQS message handling
│                                # - Polls messages from input queue
│                                # - Triggers candidate processing
│                                # - Deletes processed messages
│
├── 📄 data_validation.py       # Pydantic data models
│                                # - Candidate schema
│                                # - JobDetails schema
│                                # - EvaluationResponse schema
│
├── 📄 requirements.txt         # Python dependencies
├── 📄 package.json             # Node.js dependencies (AWS SDK)
├── 📄 .env.example             # Environment variables template
└── 📄 README.md                # This documentation file
```

---

## 📦 Dependencies

### Core Framework
- **FastAPI** (0.115.6) - Modern, fast web framework
- **uvicorn** (0.34.0) - ASGI server
- **fastapi-utils** (0.8.0) - Background task utilities

### AI & Cloud
- **openai** (1.58.1) - OpenAI Python client
- **boto3** (1.35.87) - AWS SDK for Python

### Document Processing
- **pdfplumber** (0.11.4) - PDF text extraction
- **python-docx** (1.1.2) - Word document processing
- **Pillow** (11.0.0) - Image processing

### Data & Validation
- **pydantic** (2.10.4) - Data validation
- **requests** (2.32.3) - HTTP requests

### Configuration
- **python-dotenv** (1.0.1) - Environment variable management

---

## 🔐 Security Notes

- Never commit your `.env` file to version control
- Use AWS IAM roles with minimal required permissions
- Rotate OpenAI API keys regularly
- Enable CloudWatch logging for production monitoring

---

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 🙏 Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) - For the amazing web framework
- [OpenAI](https://openai.com/) - For the GPT-4 API
- [AWS](https://aws.amazon.com/) - For SQS and Textract services

---

<div align="center">

**Built with ❤️ using Python, FastAPI, and OpenAI GPT-4**

[⬆ Back to Top](#-ai-resume-processor)

</div>
