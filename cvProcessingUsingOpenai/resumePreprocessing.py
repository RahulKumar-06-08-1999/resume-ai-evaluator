import io
import logging
import pdfplumber
import boto3
import re
import time
import urllib.parse
import os
import time


# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)  


class ResumeReader:

    def __init__(self):
        self.textract_client = boto3.client('textract', region_name='ap-south-1')

    def get_s3_bucket_and_document_path(self, file_url):
        try:
            parsed_url = urllib.parse.urlparse(file_url)
            bucket_name = parsed_url.netloc.split('.')[0]
            document_path = parsed_url.path.lstrip('/')
            return bucket_name, document_path
        except Exception as e:
            logger.error(f"Error parsing file URL: {e}")
            raise


    def extract_text_or_check_scanned(self, pdf_stream: io.BytesIO) -> bool:
        try:
            with pdfplumber.open(pdf_stream) as pdf:
                for page in pdf.pages:
                    text = page.extract_text()
                    if text and text.strip():
                        continue
                    for image in page.images:
                        return True  # Scanned image detected
                return False
        except Exception as e:
            logger.error(f"Error while checking if PDF is scanned: {e}")
            raise


    def aws_textract(self, file_url: str, timeout: int = 300, interval: int = 5) -> list:
        try:
            bucket_name, document_path = self.get_s3_bucket_and_document_path(file_url)
            response = self.textract_client.start_document_text_detection(
                DocumentLocation={'S3Object': {'Bucket': bucket_name, 'Name': document_path}}
            )
            job_id = response['JobId']
            elapsed_time = 0

            while elapsed_time < timeout:
                job_status = self.textract_client.get_document_text_detection(JobId=job_id)
                status = job_status['JobStatus']
                logger.info(f"Textract job status: {status}")
                if status in ['SUCCEEDED', 'FAILED']:
                    break
                time.sleep(interval)
                elapsed_time += interval

            if status == 'SUCCEEDED':
                if 'Blocks' in job_status and job_status['Blocks']:
                    detected_text = [
                        item['Text'] for item in job_status['Blocks'] if item['BlockType'] == 'LINE'
                    ]
                    logger.info(f"Extracted text: {detected_text}")
                    return detected_text
                else:
                    logger.error("No text detected or invalid response from Textract.")
                    return None
            else:
                logger.error(f"Textract job failed with status: {status}")
                return None
        except Exception as e:
            logger.error(f"Error using AWS Textract: {e}")
            raise



    def convert_pdf_to_txt(self, pdf_stream: io.BytesIO):
        """
        Extracts text from the PDF using pdfplumber.
        Args:
            pdf_stream (io.BytesIO): The PDF file stream.
        Returns:
            tuple: Cleaned text lines and raw text.
        """
        try:
            with pdfplumber.open(pdf_stream) as pdf:
                raw_text = "".join([page.extract_text() + "\n" for page in pdf.pages])
            
            logger.debug(f"Raw extracted text: {raw_text}")  # Log raw text for debugging
    
            full_string = re.sub(r'\n+', '\n', raw_text).replace("\r", "\n").replace("\t", " ")
            full_string = re.sub(r"\uf0b7|\(cid:\d{0,3}\)|\u2022 ", " ", full_string)
            resume_lines = [
                re.sub(r'\s+', ' ', line.strip()) for line in full_string.splitlines(True) if line.strip()
            ]
            logger.debug(f"Processed resume lines: {resume_lines}")  # Log processed lines for debugging
            return resume_lines, raw_text
        except Exception as e:
            logger.error(f"Error in PDF file: {repr(e)}")
            raise



    def convert_docx_to_txt(self, docx_file, docx_parser=None):
        try:
            import docx
            doc = docx.Document(docx_file)
            allText = [docpara.text for docpara in doc.paragraphs]
            text = " ".join(allText)
    
            clean_text = re.sub(r"\n+", "\n", text).replace("\r", "\n").replace("\t", " ")
            resume_lines = [
                re.sub(r"\s+", " ", line.strip()) for line in clean_text.splitlines() if line.strip()
            ]
    
            # Log both the clean and raw text for debugging
            logger.debug(f"Raw text extracted from DOCX: {text}")
            logger.debug(f"Cleaned text from DOCX: {clean_text}")
            logger.debug(f"Processed resume lines from DOCX: {resume_lines}")
    
            return resume_lines, text
        except Exception as e:
            logger.error(f"Error in DOCX file: {repr(e)}")
            raise
            


    def read_file(self, file_content: bytes, url_path: str, docx_parser="tika"):
        try:
            # Convert HttpUrl to string if necessary
            if isinstance(url_path, urllib.parse.ParseResult):
                url_path = str(url_path)

            file_extension = os.path.splitext(url_path)[1].lower()

            if file_extension == '.pdf':
                pdf_stream = io.BytesIO(file_content)
                if self.extract_text_or_check_scanned(pdf_stream):
                    logger.info("PDF contains scanned images, using OCR.")
                    return self.aws_textract(url_path)
                else:
                    logger.info("PDF contains extractable text.")
                    resume_lines, raw_text = self.convert_pdf_to_txt(pdf_stream)
                    logger.info(f"Extracted text from PDF: {raw_text}")  # Log extracted text
                    return raw_text  # Return raw text for readable PDFs

            elif file_extension in ['.doc', '.docx']:
                docx_stream = io.BytesIO(file_content)
                logger.info(f"Processing DOCX file.")
                resume_lines, raw_text = self.convert_docx_to_txt(docx_stream)
                # logger.info(f"Extracted text from DOCX: {raw_text}")  # Log the extracted text from DOCX
                return raw_text

            elif file_extension == '.txt':
                logger.info("Processing TXT file.")
                text = file_content.decode('utf-8')
                clean_text = re.sub(r'\n+', '\n', text).replace("\r", "\n").replace("\t", " ")
                return clean_text

            else:
                logger.error("Unsupported file format.")
                raise ValueError("Unsupported file format. Only PDF, DOCX, TXT, and image files are supported.")
        except Exception as e:
            logger.error(f"Error reading file: {repr(e)}")
            raise

