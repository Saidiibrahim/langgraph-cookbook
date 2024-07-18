from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.tools import BaseTool
from typing import Annotated, Type, List
from pydantic import EmailStr
import resend
from dotenv import load_dotenv
import os

load_dotenv()

class MailArgs(BaseModel):
    """
    Input for the email sender tool
    """
    subject: str = Field(..., description="The subject of the email")
    content: str = Field(..., description="The content of the email in HTML format")
    recipients: List[str] = Field(..., description="The list of recipients")

    
class EmailSender(BaseTool):
    """
    A tool for sending emails to a list of recipients.
    """
    name: str = "EmailSender"
    description: str = (
        "A tool for sending emails to a list of recipients."
        )
    args_schema: Type[BaseModel] = MailArgs

    def _run(
            self,
            subject: str,
            content: str,
            recipients: List[str]
            ):
        """
        Use the tool
        """
        try:
            resend.api_key = os.environ["RESEND_API_KEY"]
            params: resend.Emails.SendParams = {
                "from": "Acme <onboarding@resend.dev>",
                "to": recipients,
                "subject": subject,
                "html": content,
            }
            resend.Emails.send(params)
            return "Email sent successfully"
        except Exception as e:
            return repr(e)
        


