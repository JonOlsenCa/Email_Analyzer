"""
Email Parser Module

This module provides functionality to parse email files in various formats
and extract relevant information for analysis.
"""

import email
import email.policy
import os
from email import message_from_file, message_from_bytes
from email.parser import BytesParser, Parser
from email.utils import parseaddr, parsedate_to_datetime
import logging

logger = logging.getLogger(__name__)

class EmailData:
    """Class to store parsed email data."""

    def __init__(self):
        self.headers = {}
        self.from_address = ""
        self.to_addresses = []
        self.cc_addresses = []
        self.bcc_addresses = []
        self.subject = ""
        self.date = None
        self.body_text = ""
        self.body_html = ""
        self.attachments = []
        self.raw_content = ""
        self.file_path = None  # Path to the email file if available

        # Additional fields for structured data
        self.email_body = ""  # The main content of the email
        self.description = ""  # The description/message from the email sender
        self.subject_template = ""  # E.g., "Incorrect Vendor Prediction"
        self.invoice_id = ""
        self.invoice_id_url = ""  # URL for the invoice ID
        self.invoice_number = ""
        self.company_name = ""
        self.company_id = ""
        self.client_name = ""
        self.client_id = ""
        self.user_email = ""
        self.user_name = ""
        self.user_id = ""

    def __str__(self):
        """Return a string representation of the email data."""
        return f"Email: {self.subject} from {self.from_address} to {', '.join(self.to_addresses)}"

class Attachment:
    """Class to store email attachment data."""

    def __init__(self, filename, content_type, content):
        self.filename = filename
        self.content_type = content_type
        self.content = content
        self.size = len(content) if content else 0

    def __str__(self):
        """Return a string representation of the attachment."""
        return f"Attachment: {self.filename} ({self.content_type}, {self.size} bytes)"

class EmailParser:
    """Class to parse email files and extract data."""

    def __init__(self):
        self.supported_formats = ['.eml', '.msg', '.txt']

    def parse_file(self, file_path):
        """
        Parse an email file and return the extracted data.

        Args:
            file_path (str): Path to the email file

        Returns:
            EmailData: Object containing the parsed email data

        Raises:
            FileNotFoundError: If the file does not exist
            ValueError: If the file format is not supported
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Email file not found: {file_path}")

        _, file_ext = os.path.splitext(file_path)
        file_ext = file_ext.lower()

        if file_ext not in self.supported_formats:
            raise ValueError(f"Unsupported email format: {file_ext}")

        logger.info(f"Parsing email file: {file_path}")

        if file_ext == '.eml':
            return self._parse_eml(file_path)
        elif file_ext == '.msg':
            return self._parse_msg(file_path)
        else:  # Default to .txt or other formats
            return self._parse_txt(file_path)

    def _parse_eml(self, file_path):
        """Parse an EML format email file."""
        email_data = EmailData()
        email_data.file_path = file_path

        with open(file_path, 'rb') as f:
            msg = BytesParser(policy=email.policy.default).parse(f)
            email_data.raw_content = msg.as_string()

        # Extract headers
        for header, value in msg.items():
            email_data.headers[header] = value

        # Extract basic metadata
        email_data.subject = msg.get('Subject', '')
        email_data.from_address = parseaddr(msg.get('From', ''))[1]

        # Extract To, CC, BCC addresses
        if msg.get('To'):
            email_data.to_addresses = [addr[1] for addr in email.utils.getaddresses([msg.get('To', '')])]
        if msg.get('Cc'):
            email_data.cc_addresses = [addr[1] for addr in email.utils.getaddresses([msg.get('Cc', '')])]
        if msg.get('Bcc'):
            email_data.bcc_addresses = [addr[1] for addr in email.utils.getaddresses([msg.get('Bcc', '')])]

        # Extract date
        if msg.get('Date'):
            try:
                email_data.date = parsedate_to_datetime(msg.get('Date'))
            except Exception as e:
                logger.warning(f"Could not parse date: {e}")

        # Extract body and attachments
        self._process_payload(msg, email_data)

        return email_data

    def _parse_msg(self, file_path):
        """
        Parse an MSG format email file.

        Note: This is a placeholder. Parsing MSG files requires additional libraries
        like 'extract_msg' which would need to be installed.
        """
        # This is a placeholder - in a real implementation, you would use a library
        # like 'extract_msg' to parse MSG files
        email_data = EmailData()
        email_data.file_path = file_path
        email_data.subject = "MSG parsing not implemented"
        logger.warning("MSG parsing not fully implemented - requires additional libraries")
        return email_data

    def _parse_txt(self, file_path):
        """Parse a plain text email file."""
        email_data = EmailData()
        email_data.file_path = file_path

        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
            email_data.raw_content = content
            email_data.body_text = content

        # Try to extract basic headers if they exist
        lines = content.split('\n')
        in_headers = True

        for line in lines:
            if in_headers and line.strip() == '':
                in_headers = False
                continue

            if in_headers:
                if ':' in line:
                    header, value = line.split(':', 1)
                    header = header.strip()
                    value = value.strip()
                    email_data.headers[header] = value

                    if header.lower() == 'subject':
                        email_data.subject = value
                    elif header.lower() == 'from':
                        email_data.from_address = parseaddr(value)[1]
                    elif header.lower() == 'to':
                        email_data.to_addresses = [addr[1] for addr in email.utils.getaddresses([value])]
                    elif header.lower() == 'cc':
                        email_data.cc_addresses = [addr[1] for addr in email.utils.getaddresses([value])]
                    elif header.lower() == 'date':
                        try:
                            email_data.date = parsedate_to_datetime(value)
                        except Exception as e:
                            logger.warning(f"Could not parse date: {e}")

        return email_data

    def _process_payload(self, msg, email_data):
        """Process the payload of an email message to extract body and attachments."""
        if msg.is_multipart():
            for part in msg.iter_parts():
                self._process_part(part, email_data)
        else:
            self._process_part(msg, email_data)

    def _process_part(self, part, email_data):
        """Process a single part of a multipart email message."""
        content_type = part.get_content_type()
        content_disposition = part.get_content_disposition()

        # Handle attachments
        if content_disposition == 'attachment':
            filename = part.get_filename()
            if filename:
                content = part.get_payload(decode=True)
                attachment = Attachment(filename, content_type, content)
                email_data.attachments.append(attachment)
                logger.debug(f"Found attachment: {filename}")

        # Handle body parts
        elif content_type == 'text/plain' and not email_data.body_text:
            email_data.body_text = part.get_payload(decode=True).decode(part.get_content_charset() or 'utf-8', errors='replace')
        elif content_type == 'text/html' and not email_data.body_html:
            email_data.body_html = part.get_payload(decode=True).decode(part.get_content_charset() or 'utf-8', errors='replace')
