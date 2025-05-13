#!/usr/bin/env python3
"""
Unit tests for the Email Analyzer.
"""

import unittest
import os
import tempfile
from email_parser import EmailParser, EmailData
from analyzer import Analyzer, AnalysisResults
from utils import extract_domain_from_email, sanitize_filename

class TestEmailParser(unittest.TestCase):
    """Tests for the EmailParser class."""

    def setUp(self):
        """Set up test fixtures."""
        self.parser = EmailParser()

        # Create a temporary test email file
        self.test_email_content = """From: test@example.com
To: recipient@example.com
Subject: Test Email
Date: Mon, 13 May 2023 10:00:00 -0400

This is a test email.
"""
        # Create a temporary file
        fd, self.temp_file_path = tempfile.mkstemp(suffix='.eml')
        os.close(fd)  # Close the file descriptor

        # Write the content to the file
        with open(self.temp_file_path, 'w') as f:
            f.write(self.test_email_content)

    def tearDown(self):
        """Tear down test fixtures."""
        try:
            os.unlink(self.temp_file_path)
        except (OSError, PermissionError):
            pass  # Ignore errors if file can't be deleted

    def test_parse_file(self):
        """Test parsing an email file."""
        email_data = self.parser.parse_file(self.temp_file_path)

        self.assertIsInstance(email_data, EmailData)
        self.assertEqual(email_data.subject, "Test Email")
        self.assertEqual(email_data.from_address, "test@example.com")
        self.assertEqual(email_data.to_addresses, ["recipient@example.com"])
        self.assertIn("This is a test email.", email_data.body_text)

    def test_file_not_found(self):
        """Test handling of non-existent files."""
        with self.assertRaises(FileNotFoundError):
            self.parser.parse_file("nonexistent_file.eml")

    def test_unsupported_format(self):
        """Test handling of unsupported file formats."""
        # Create a temporary file with an unsupported extension
        fd, temp_file_path = tempfile.mkstemp(suffix='.xyz')
        os.close(fd)  # Close the file descriptor

        try:
            with self.assertRaises(ValueError):
                self.parser.parse_file(temp_file_path)
        finally:
            try:
                os.unlink(temp_file_path)
            except (OSError, PermissionError):
                pass  # Ignore errors if file can't be deleted

class TestAnalyzer(unittest.TestCase):
    """Tests for the Analyzer class."""

    def setUp(self):
        """Set up test fixtures."""
        self.analyzer = Analyzer()

        # Create a test EmailData object
        self.email_data = EmailData()
        self.email_data.subject = "Test Email"
        self.email_data.from_address = "sender@example.com"
        self.email_data.to_addresses = ["recipient@example.com"]
        self.email_data.body_text = "This is a test email with a link: https://example.com"
        self.email_data.body_html = "<p>This is a test email with a link: <a href='https://example.com'>Click here</a></p>"
        self.email_data.headers = {
            "From": "sender@example.com",
            "To": "recipient@example.com",
            "Subject": "Test Email",
            "Date": "Mon, 13 May 2023 10:00:00 -0400"
        }

    def test_analyze(self):
        """Test analyzing an email."""
        results = self.analyzer.analyze(self.email_data)

        self.assertIsInstance(results, AnalysisResults)
        self.assertEqual(results.metadata["Subject"], "Test Email")
        self.assertEqual(results.metadata["From"], "sender@example.com")

        # Check if URLs were extracted
        self.assertIn("URLs", results.security_analysis)
        self.assertEqual(results.security_analysis["URLs"]["Count"], 2)  # One in text, one in HTML

        # Check if the domain was extracted
        self.assertEqual(results.security_analysis["Sender Domain"], "example.com")

    def test_phishing_detection(self):
        """Test phishing detection."""
        # Create an email with phishing indicators
        phishing_email = EmailData()
        phishing_email.subject = "Urgent: Verify your account now"
        phishing_email.from_address = "security@bank-secure.com"
        phishing_email.to_addresses = ["victim@example.com"]
        phishing_email.body_text = """
        Dear customer,

        We have detected unusual activity on your account.
        Please verify your account immediately by clicking the link below:

        https://bank-secure.phishing-site.com/login

        Failure to verify will result in account suspension.

        Thank you,
        Security Team
        """

        results = self.analyzer.analyze(phishing_email)

        # Check if phishing was detected
        self.assertIn("Phishing Assessment", results.security_analysis)
        self.assertIn("Risk Level", results.security_analysis["Phishing Assessment"])

        # The risk level should be at least Medium due to the phishing indicators
        risk_level = results.security_analysis["Phishing Assessment"]["Risk Level"]
        self.assertIn(risk_level, ["Medium", "High", "Critical"])

    def test_output_formats(self):
        """Test different output formats."""
        results = self.analyzer.analyze(self.email_data)

        # Test text format
        text_output = results.to_format("text")
        self.assertIsInstance(text_output, str)
        self.assertIn("EMAIL METADATA", text_output)
        self.assertIn("SECURITY ANALYSIS", text_output)

        # Test JSON format
        json_output = results.to_format("json")
        self.assertIsInstance(json_output, str)
        self.assertIn("metadata", json_output)
        self.assertIn("security_analysis", json_output)

        # Test HTML format
        html_output = results.to_format("html")
        self.assertIsInstance(html_output, str)
        self.assertIn("<html>", html_output)
        self.assertIn("Email Analysis Report", html_output)

class TestUtils(unittest.TestCase):
    """Tests for utility functions."""

    def test_extract_domain_from_email(self):
        """Test extracting domain from email address."""
        self.assertEqual(extract_domain_from_email("user@example.com"), "example.com")
        self.assertEqual(extract_domain_from_email("user@subdomain.example.com"), "subdomain.example.com")
        self.assertEqual(extract_domain_from_email("invalid-email"), "")

    def test_sanitize_filename(self):
        """Test sanitizing filenames."""
        self.assertEqual(sanitize_filename("file.txt"), "file.txt")
        self.assertEqual(sanitize_filename("file?.txt"), "file_.txt")
        self.assertEqual(sanitize_filename("file:with:colons.txt"), "file_with_colons.txt")

        # Test long filename
        long_name = "a" * 300 + ".txt"
        sanitized = sanitize_filename(long_name)
        self.assertLessEqual(len(sanitized), 255)
        self.assertTrue(sanitized.endswith(".txt"))

if __name__ == "__main__":
    unittest.main()
