"""
Outlook Connector Module

This module provides functionality to connect to Microsoft Outlook
and retrieve emails from specific folders.
"""

import os
import re
import tempfile
import logging
import win32com.client
from datetime import datetime
from email_parser import EmailData, Attachment

logger = logging.getLogger(__name__)

class OutlookConnector:
    """Class to connect to Outlook and retrieve emails."""

    def __init__(self):
        """Initialize the Outlook connector."""
        self.outlook = None
        self.namespace = None

    def connect(self):
        """
        Connect to Outlook application.

        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            logger.info("Connecting to Outlook...")
            self.outlook = win32com.client.Dispatch("Outlook.Application")
            self.namespace = self.outlook.GetNamespace("MAPI")
            logger.info("Successfully connected to Outlook")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Outlook: {str(e)}")
            return False

    def get_folder_by_path(self, email_account, folder_path):
        """
        Get an Outlook folder by its path.

        Args:
            email_account (str): Email account (e.g., 'jon@olsenconsulting.ca')
            folder_path (str): Path to the folder (e.g., 'Inbox/APWizard_Tickets')

        Returns:
            folder: Outlook folder object or None if not found
        """
        try:
            # Get the root folder for the specified account
            root_folder = None
            for account in self.namespace.Accounts:
                if account.DisplayName.lower() == email_account.lower() or account.SmtpAddress.lower() == email_account.lower():
                    root_folder = account.DeliveryStore.GetRootFolder()
                    break

            if not root_folder:
                logger.error(f"Could not find account: {email_account}")
                return None

            # Split the folder path and navigate to the target folder
            folders = folder_path.split('/')
            current_folder = root_folder

            for folder_name in folders:
                found = False
                for subfolder in current_folder.Folders:
                    if subfolder.Name.lower() == folder_name.lower():
                        current_folder = subfolder
                        found = True
                        break

                if not found:
                    logger.error(f"Could not find folder: {folder_name} in path {folder_path}")
                    return None

            logger.info(f"Found folder: {current_folder.Name}")
            return current_folder

        except Exception as e:
            logger.error(f"Error getting folder: {str(e)}")
            return None

    def get_emails_from_folder(self, folder, limit=None, save_to_eml=False, output_dir=None, min_date=None):
        """
        Get emails from an Outlook folder.

        Args:
            folder: Outlook folder object
            limit (int, optional): Maximum number of emails to retrieve
            save_to_eml (bool): Whether to save emails as EML files
            output_dir (str, optional): Directory to save EML files
            min_date (datetime, optional): Only retrieve emails received after this date

        Returns:
            list: List of EmailData objects
        """
        emails = []

        try:
            # Create output directory if needed
            if save_to_eml and output_dir:
                os.makedirs(output_dir, exist_ok=True)

            # Get emails from the folder
            items = folder.Items
            items.Sort("[ReceivedTime]", True)  # Sort by received time, newest first

            # If we have a min_date, create a filter to only get emails after that date
            if min_date:
                # Format the date for Outlook filter
                # Format: "2/16/2022 12:00 AM"
                filter_date = min_date.strftime("%m/%d/%Y %I:%M %p")
                # Create a filter string for emails received after min_date
                filter_str = f"[ReceivedTime] > '{filter_date}'"
                logger.info(f"Applying Outlook filter: {filter_str}")

                # Apply the filter to the items collection
                filtered_items = items.Restrict(filter_str)
                logger.info(f"Filter applied, found {filtered_items.Count} emails after {filter_date}")

                # Use the filtered items
                items = filtered_items

            count = 0
            for item in items:
                if limit is not None and count >= limit:
                    break

                try:
                    # Check if it's an email item
                    if item.Class == 43:  # 43 is the class for MailItem
                        email_data = self._convert_outlook_item_to_email_data(item)

                        # Save as EML if requested
                        if save_to_eml and output_dir:
                            eml_path = self._save_as_eml(item, output_dir)
                            if eml_path:
                                email_data.file_path = eml_path

                        emails.append(email_data)
                        count += 1
                        logger.info(f"Processed email: {email_data.subject}")

                except Exception as e:
                    logger.error(f"Error processing email: {str(e)}")

            logger.info(f"Retrieved {len(emails)} emails from folder: {folder.Name}")
            return emails

        except Exception as e:
            logger.error(f"Error getting emails from folder: {str(e)}")
            return emails

    def _convert_outlook_item_to_email_data(self, item):
        """
        Convert an Outlook MailItem to EmailData.

        Args:
            item: Outlook MailItem

        Returns:
            EmailData: Converted email data
        """
        email_data = EmailData()

        # Extract basic metadata
        email_data.subject = item.Subject or ""
        email_data.from_address = item.SenderEmailAddress or ""

        # Extract recipients
        if item.To:
            email_data.to_addresses = [addr.strip() for addr in item.To.split(';') if addr.strip()]

        if item.CC:
            email_data.cc_addresses = [addr.strip() for addr in item.CC.split(';') if addr.strip()]

        if item.BCC:
            email_data.bcc_addresses = [addr.strip() for addr in item.BCC.split(';') if addr.strip()]

        # Extract date
        if item.ReceivedTime:
            email_data.date = item.ReceivedTime

        # Extract body
        email_data.body_text = item.Body or ""
        if item.HTMLBody:
            email_data.body_html = item.HTMLBody

        # Extract headers
        if item.PropertyAccessor.GetProperty("http://schemas.microsoft.com/mapi/proptag/0x007D001E"):
            headers_text = item.PropertyAccessor.GetProperty("http://schemas.microsoft.com/mapi/proptag/0x007D001E")
            for line in headers_text.splitlines():
                if ':' in line:
                    key, value = line.split(':', 1)
                    email_data.headers[key.strip()] = value.strip()

        # Extract attachments
        if item.Attachments.Count > 0:
            for i in range(1, item.Attachments.Count + 1):
                attachment = item.Attachments.Item(i)

                # Save attachment to a temporary file
                temp_dir = tempfile.gettempdir()
                temp_file = os.path.join(temp_dir, attachment.FileName)

                try:
                    attachment.SaveAsFile(temp_file)

                    # Read the content
                    with open(temp_file, 'rb') as f:
                        content = f.read()

                    # Create Attachment object
                    email_attachment = Attachment(
                        filename=attachment.FileName,
                        content_type=attachment.PropertyAccessor.GetProperty("http://schemas.microsoft.com/mapi/proptag/0x370E001E") if hasattr(attachment, "PropertyAccessor") else "application/octet-stream",
                        content=content
                    )

                    email_data.attachments.append(email_attachment)

                    # Clean up
                    os.remove(temp_file)

                except Exception as e:
                    logger.error(f"Error processing attachment: {str(e)}")

        # Extract structured data
        self._extract_structured_data(email_data)

        return email_data

    def _extract_structured_data(self, email_data):
        """
        Extract structured data from the email.

        Args:
            email_data (EmailData): The email data object to populate
        """
        # Set email body (main content)
        email_data.email_body = email_data.body_text

        # Extract subject template from subject
        # Format is typically: [SUPPORT] [Company] Subject Template
        subject = email_data.subject
        if subject:
            # Try to extract the subject template
            parts = subject.split(']')
            if len(parts) >= 3:
                # The subject template is likely the last part
                email_data.subject_template = parts[-1].strip()
            elif len(parts) == 2:
                email_data.subject_template = parts[-1].strip()

            # Try to extract company name from subject
            if '[' in subject and ']' in subject:
                company_parts = subject.split('[')
                if len(company_parts) > 2:
                    company_name = company_parts[2].split(']')[0].strip()
                    email_data.company_name = company_name

        # Extract structured data from body text
        body = email_data.body_text
        if body:
            # Extract the description (main message content)
            # Look for the actual message content, not URLs or structured data
            lines = body.split('\n')
            description_lines = []

            # First, try to find a line that looks like a message (not a URL, not structured data)
            for line in lines:
                line = line.strip()
                # Skip empty lines, URLs, and structured data fields
                if (line and
                    not line.startswith('http') and
                    not '<https://' in line and
                    not line.startswith('Invoice') and
                    not line.startswith('Company') and
                    not line.startswith('Client') and
                    not line.startswith('User') and
                    not line.startswith('To:') and
                    not line.startswith('From:') and
                    not line.startswith('Date:')):

                    # This looks like actual message content
                    description_lines.append(line)
                    # Get a few lines of context if they exist
                    if len(description_lines) >= 3:  # Limit to first few lines
                        break

            # If we found message content, use it
            if description_lines:
                email_data.description = ' '.join(description_lines)
            else:
                # Fallback: Look for the first line that's not a URL or structured data
                for line in lines:
                    line = line.strip()
                    if line and not '<https://' in line and not 'http' in line:
                        email_data.description = line
                        break
                else:
                    email_data.description = "No description available"
            # Extract the main content (first paragraph that's not a greeting)
            main_content_match = re.search(r'\n\s*([^\n]+)\s*\n', body)
            if main_content_match:
                email_data.email_body = main_content_match.group(1).strip()

            # Extract Invoice ID - format: "Invoice ID: b75dbfe0-4f0f-4348-81ad-acfaab025c6d"
            invoice_id_match = re.search(r'Invoice\s*ID:?\s*([A-Za-z0-9\-_]+)', body, re.IGNORECASE)
            if invoice_id_match:
                invoice_id = invoice_id_match.group(1).strip()
                email_data.invoice_id = invoice_id

                # Look for a URL containing the invoice ID to create a hyperlink
                url_match = re.search(r'(https?://[^\s<>"]+?' + invoice_id + r'[^\s<>"]*)', body, re.IGNORECASE)
                if url_match:
                    email_data.invoice_id_url = url_match.group(1)
                else:
                    # If no direct URL found, create a default URL to the APWizard system using the correct format
                    email_data.invoice_id_url = f"https://platform.apwizard.ai/ap-task/{invoice_id}"

            # Extract Invoice Number - format: "Invoice Number: 61"
            invoice_number_match = re.search(r'Invoice\s*Number:?\s*(\d+)', body, re.IGNORECASE)
            if invoice_number_match:
                email_data.invoice_number = invoice_number_match.group(1).strip()

            # Extract Company Name - format: "Company Name: BluSky Restoration Contractors, LLC"
            company_name_match = re.search(r'Company\s*Name:?\s*([^\n]+)', body, re.IGNORECASE)
            if company_name_match:
                email_data.company_name = company_name_match.group(1).strip()

            # Extract Company ID - format: "Company ID: 0c4ccc2b-2968-4c96-b62f-475068dfc97f"
            company_id_match = re.search(r'Company\s*ID:?\s*([A-Za-z0-9\-_]+)', body, re.IGNORECASE)
            if company_id_match:
                email_data.company_id = company_id_match.group(1).strip()

            # Extract Client Name - format: "Client Name: BluSky"
            client_name_match = re.search(r'Client\s*Name:?\s*([^\n]+)', body, re.IGNORECASE)
            if client_name_match:
                email_data.client_name = client_name_match.group(1).strip()

            # Extract Client ID - format: "Client ID: 7cebab3c-f1e8-403f-9681-f23e23a28267"
            client_id_match = re.search(r'Client\s*ID:?\s*([A-Za-z0-9\-_]+)', body, re.IGNORECASE)
            if client_id_match:
                email_data.client_id = client_id_match.group(1).strip()

            # Extract User Email - format: "User Email: Tracy.Eley@goblusky.com"
            user_email_match = re.search(r'User\s*Email:?\s*([^\s\n]+@[^\s\n]+)', body, re.IGNORECASE)
            if user_email_match:
                email_data.user_email = user_email_match.group(1).strip()
            else:
                # If not found explicitly, check if there's an email in the body
                email_in_body = re.search(r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', body)
                if email_in_body:
                    email_data.user_email = email_in_body.group(1).strip()
                else:
                    # Use the sender's email as a fallback
                    email_data.user_email = email_data.from_address

            # Extract User Name - format: "User Name: Tracy Eley"
            user_name_match = re.search(r'User\s*Name:?\s*([^\n]+)', body, re.IGNORECASE)
            if user_name_match:
                email_data.user_name = user_name_match.group(1).strip()

            # Extract User ID - format: "User ID: b97c35a4-4e5f-4932-ba4f-58e43c44c61e"
            user_id_match = re.search(r'User\s*ID:?\s*([A-Za-z0-9\-_]+)', body, re.IGNORECASE)
            if user_id_match:
                email_data.user_id = user_id_match.group(1).strip()

            # If we have HTML body, try to extract from there as well if we're missing data
            if email_data.body_html and (not email_data.invoice_id or not email_data.company_name):
                html_body = email_data.body_html

                # Extract from HTML using more specific patterns that might appear in the HTML
                if not email_data.invoice_id:
                    invoice_id_html = re.search(r'Invoice\s*ID:?\s*<[^>]*>([A-Za-z0-9\-_]+)', html_body, re.IGNORECASE)
                    if invoice_id_html:
                        email_data.invoice_id = invoice_id_html.group(1).strip()

                if not email_data.invoice_number:
                    invoice_number_html = re.search(r'Invoice\s*Number:?\s*<[^>]*>(\d+)', html_body, re.IGNORECASE)
                    if invoice_number_html:
                        email_data.invoice_number = invoice_number_html.group(1).strip()

                if not email_data.company_name:
                    company_name_html = re.search(r'Company\s*Name:?\s*<[^>]*>([^<]+)', html_body, re.IGNORECASE)
                    if company_name_html:
                        email_data.company_name = company_name_html.group(1).strip()

                # Extract other fields similarly if needed

    def _save_as_eml(self, item, output_dir):
        """
        Save an Outlook MailItem as an EML file.

        Args:
            item: Outlook MailItem
            output_dir (str): Directory to save the EML file

        Returns:
            str: Path to the saved EML file or None if failed
        """
        try:
            # Create a safe filename from the subject
            safe_subject = "".join([c if c.isalnum() or c in " -_" else "_" for c in item.Subject])
            safe_subject = safe_subject[:50]  # Limit length

            # Add timestamp to make filename unique
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{safe_subject}_{timestamp}.eml"
            file_path = os.path.join(output_dir, filename)

            # Save as MSG first (Outlook native format)
            msg_path = os.path.join(output_dir, f"{safe_subject}_{timestamp}.msg")
            item.SaveAs(msg_path, 3)  # 3 is the value for olMSG format

            # Convert MSG to EML (simplified approach)
            # In a real implementation, you would use a library like 'extract_msg'
            # to properly convert MSG to EML
            with open(msg_path, 'rb') as f:
                msg_content = f.read()

            with open(file_path, 'wb') as f:
                f.write(msg_content)

            # Clean up the MSG file
            os.remove(msg_path)

            logger.info(f"Saved email as EML: {file_path}")
            return file_path

        except Exception as e:
            logger.error(f"Error saving email as EML: {str(e)}")
            return None

    def delete_email_by_id(self, folder, email_id):
        """
        Delete an email from an Outlook folder by its ID.

        The email_id is a combination of subject, date, and sender that uniquely identifies the email.

        Args:
            folder: Outlook folder object
            email_id: Unique identifier for the email (subject|date|from_address)

        Returns:
            bool: True if deletion was successful, False otherwise
        """
        try:
            # Parse the email_id to get subject, date, and from_address
            parts = email_id.split('|')
            if len(parts) != 3:
                logger.error(f"Invalid email_id format: {email_id}")
                return False

            subject, date_str, from_address = parts

            # Get emails from the folder
            items = folder.Items

            # Find the email that matches the criteria
            for item in items:
                try:
                    # Check if it's an email item
                    if item.Class == 43:  # 43 is the class for MailItem
                        # Check if this is the email we want to delete
                        if (item.Subject == subject and
                            item.SenderEmailAddress.lower() == from_address.lower()):

                            # If date is provided, check that too
                            if date_str and item.ReceivedTime:
                                # Convert item.ReceivedTime to string for comparison
                                item_date_str = str(item.ReceivedTime)
                                if date_str != item_date_str:
                                    continue

                            # Delete the email
                            item.Delete()
                            logger.info(f"Deleted email: {subject}")
                            return True

                except Exception as e:
                    logger.error(f"Error processing email during deletion: {str(e)}")

            logger.warning(f"Could not find email to delete with ID: {email_id}")
            return False

        except Exception as e:
            logger.error(f"Error deleting email: {str(e)}")
            return False
