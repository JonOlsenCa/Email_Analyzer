#!/usr/bin/env python3
"""
Refresh Emails API

This script provides an API endpoint to fetch new emails that have arrived since the last check.
"""

import json
import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse
from outlook_connector import OutlookConnector
from utils import setup_logging

# Setup logging
logger = setup_logging()

# Default settings
DEFAULT_EMAIL_ACCOUNT = "jon@olsenconsulting.ca"
DEFAULT_FOLDER_PATH = "Inbox/APWizard_Tickets"
DEFAULT_HOST = "localhost"
DEFAULT_PORT = 8001
DEFAULT_MAX_EMAILS = 100

class RefreshEmailsHandler(BaseHTTPRequestHandler):
    """HTTP request handler for the Refresh Emails API."""

    def _set_headers(self, status_code=200, content_type="application/json"):
        """Set response headers."""
        self.send_response(status_code)
        self.send_header("Content-type", content_type)
        self.send_header("Access-Control-Allow-Origin", "*")  # Allow CORS
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_OPTIONS(self):
        """Handle OPTIONS requests for CORS preflight."""
        self._set_headers()

    def do_GET(self):
        """Handle GET requests."""
        # Parse URL and query parameters
        parsed_url = urlparse(self.path)
        path = parsed_url.path
        query_params = parse_qs(parsed_url.query)

        # Check if this is a refresh request
        if path == "/refresh":
            # Get parameters from query
            email_account = query_params.get("email_account", [DEFAULT_EMAIL_ACCOUNT])[0]
            folder_path = query_params.get("folder_path", [DEFAULT_FOLDER_PATH])[0]
            max_emails = int(query_params.get("max_emails", [DEFAULT_MAX_EMAILS])[0])

            # Get the latest email date from query parameters
            latest_email_date_str = query_params.get("latest_email_date", [""])[0]
            latest_email_date = None
            if latest_email_date_str:
                try:
                    # Parse the date string to a datetime object
                    latest_email_date = datetime.datetime.strptime(latest_email_date_str, "%Y-%m-%d %H:%M:%S")
                except ValueError:
                    logger.error(f"Invalid date format: {latest_email_date_str}")
                    self._set_headers(400)
                    self.wfile.write(json.dumps({"error": "Invalid date format"}).encode())
                    return

            # Fetch new emails
            new_emails = self._fetch_new_emails(email_account, folder_path, max_emails, latest_email_date)

            # Return the new emails
            self._set_headers()
            self.wfile.write(json.dumps({"success": True, "new_emails": new_emails}).encode())
        else:
            # Unknown endpoint
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Endpoint not found"}).encode())

    def _fetch_new_emails(self, email_account, folder_path, max_emails, latest_email_date):
        """
        Fetch new emails from Outlook that are newer than the latest_email_date.

        Args:
            email_account (str): Email account to use
            folder_path (str): Path to the Outlook folder
            max_emails (int): Maximum number of emails to fetch
            latest_email_date (datetime): Date of the latest email we already have

        Returns:
            list: List of new email data
        """
        try:
            # Connect to Outlook
            connector = OutlookConnector()
            if not connector.connect():
                logger.error("Failed to connect to Outlook")
                return []

            # Get the specified folder
            folder = connector.get_folder_by_path(email_account, folder_path)
            if not folder:
                logger.error(f"Could not find folder: {folder_path}")
                return []

            # Log the latest email date we're using as a filter
            if latest_email_date:
                logger.info(f"Filtering emails newer than: {latest_email_date}")
            else:
                logger.info("No date filter applied, fetching all emails")

            # Get emails from the folder with our date filter
            # This will use Outlook's built-in filtering which is much more efficient
            emails = connector.get_emails_from_folder(folder, max_emails, min_date=latest_email_date)
            logger.info(f"Found {len(emails)} new emails after applying date filter")

            # Process the emails
            new_emails = []
            for email_data in emails:
                # The emails are already parsed by the OutlookConnector
                # But we need to make sure structured data is extracted

                if email_data:
                    # Force extraction of structured data to ensure we have client and user information
                    connector._extract_structured_data(email_data)

                    # Convert to a serializable format
                    email_dict = {
                        "subject": email_data.subject,
                        "date": str(email_data.date),
                        "from_address": email_data.from_address,
                        "body": email_data.body_text if hasattr(email_data, "body_text") else "",
                        "subject_template": email_data.subject_template if hasattr(email_data, "subject_template") else "",
                        "description": email_data.description if hasattr(email_data, "description") else "",
                        "company_name": email_data.company_name if hasattr(email_data, "company_name") else "",
                        "company_id": email_data.company_id if hasattr(email_data, "company_id") else "",
                        "invoice_id": email_data.invoice_id if hasattr(email_data, "invoice_id") else "",
                        "invoice_number": email_data.invoice_number if hasattr(email_data, "invoice_number") else "",
                        "client_name": email_data.client_name if hasattr(email_data, "client_name") else "",
                        "client_id": email_data.client_id if hasattr(email_data, "client_id") else "",
                        "user_email": email_data.user_email if hasattr(email_data, "user_email") else "",
                        "user_name": email_data.user_name if hasattr(email_data, "user_name") else "",
                        "user_id": email_data.user_id if hasattr(email_data, "user_id") else "",
                    }

                    # Log the extracted information for debugging
                    logger.info(f"Extracted email data: Subject={email_data.subject}, Client={email_dict['client_name']}, User={email_dict['user_name']}")

                    new_emails.append(email_dict)

            logger.info(f"Found {len(new_emails)} new emails")
            return new_emails

        except Exception as e:
            logger.error(f"Error fetching new emails: {str(e)}")
            return []

def run_server(host=DEFAULT_HOST, port=DEFAULT_PORT):
    """
    Run the HTTP server.

    Args:
        host (str): Host to bind to
        port (int): Port to bind to
    """
    server_address = (host, port)
    httpd = HTTPServer(server_address, RefreshEmailsHandler)
    logger.info(f"Starting server on {host}:{port}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        logger.info("Server stopped")
    httpd.server_close()

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run the Refresh Emails API server")
    parser.add_argument("--host", default=DEFAULT_HOST, help=f"Host to bind to (default: {DEFAULT_HOST})")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help=f"Port to bind to (default: {DEFAULT_PORT})")
    args = parser.parse_args()

    run_server(args.host, args.port)
