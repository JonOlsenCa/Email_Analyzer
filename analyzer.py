"""
Email Analyzer Module

This module provides functionality to analyze email content and metadata,
identifying potential security risks, extracting insights, and generating reports.
"""

import re
import json
import logging
from datetime import datetime
from email.utils import parseaddr
import html

logger = logging.getLogger(__name__)

class AnalysisResults:
    """Class to store and format email analysis results."""
    
    def __init__(self):
        self.metadata = {}
        self.security_analysis = {}
        self.content_analysis = {}
        self.summary = {}
        
    def to_format(self, format_type):
        """
        Convert analysis results to the specified format.
        
        Args:
            format_type (str): The output format ('text', 'json', or 'html')
            
        Returns:
            str: Formatted analysis results
        """
        if format_type == 'json':
            return self._to_json()
        elif format_type == 'html':
            return self._to_html()
        else:  # Default to text
            return self._to_text()
    
    def _to_json(self):
        """Convert analysis results to JSON format."""
        data = {
            'metadata': self.metadata,
            'security_analysis': self.security_analysis,
            'content_analysis': self.content_analysis,
            'summary': self.summary
        }
        return json.dumps(data, indent=2, default=str)
    
    def _to_text(self):
        """Convert analysis results to plain text format."""
        lines = []
        
        # Add metadata
        lines.append("=== EMAIL METADATA ===")
        for key, value in self.metadata.items():
            lines.append(f"{key}: {value}")
        lines.append("")
        
        # Add security analysis
        lines.append("=== SECURITY ANALYSIS ===")
        for key, value in self.security_analysis.items():
            if isinstance(value, dict):
                lines.append(f"{key}:")
                for subkey, subvalue in value.items():
                    lines.append(f"  {subkey}: {subvalue}")
            else:
                lines.append(f"{key}: {value}")
        lines.append("")
        
        # Add content analysis
        lines.append("=== CONTENT ANALYSIS ===")
        for key, value in self.content_analysis.items():
            if isinstance(value, dict):
                lines.append(f"{key}:")
                for subkey, subvalue in value.items():
                    lines.append(f"  {subkey}: {subvalue}")
            elif isinstance(value, list):
                lines.append(f"{key}:")
                for item in value:
                    lines.append(f"  - {item}")
            else:
                lines.append(f"{key}: {value}")
        lines.append("")
        
        # Add summary
        lines.append("=== SUMMARY ===")
        for key, value in self.summary.items():
            lines.append(f"{key}: {value}")
        
        return "\n".join(lines)
    
    def _to_html(self):
        """Convert analysis results to HTML format."""
        html_parts = []
        
        html_parts.append("<!DOCTYPE html>")
        html_parts.append("<html>")
        html_parts.append("<head>")
        html_parts.append("  <title>Email Analysis Report</title>")
        html_parts.append("  <style>")
        html_parts.append("    body { font-family: Arial, sans-serif; margin: 20px; }")
        html_parts.append("    h1 { color: #333366; }")
        html_parts.append("    h2 { color: #333366; margin-top: 20px; }")
        html_parts.append("    .section { margin-bottom: 20px; }")
        html_parts.append("    .item { margin: 5px 0; }")
        html_parts.append("    .key { font-weight: bold; }")
        html_parts.append("    .warning { color: #cc3300; }")
        html_parts.append("    .safe { color: #009900; }")
        html_parts.append("  </style>")
        html_parts.append("</head>")
        html_parts.append("<body>")
        
        html_parts.append("  <h1>Email Analysis Report</h1>")
        
        # Add metadata
        html_parts.append("  <div class='section'>")
        html_parts.append("    <h2>Email Metadata</h2>")
        for key, value in self.metadata.items():
            html_parts.append(f"    <div class='item'><span class='key'>{html.escape(key)}:</span> {html.escape(str(value))}</div>")
        html_parts.append("  </div>")
        
        # Add security analysis
        html_parts.append("  <div class='section'>")
        html_parts.append("    <h2>Security Analysis</h2>")
        for key, value in self.security_analysis.items():
            if isinstance(value, dict):
                html_parts.append(f"    <div class='item'><span class='key'>{html.escape(key)}:</span></div>")
                for subkey, subvalue in value.items():
                    css_class = 'warning' if 'risk' in subkey.lower() and subvalue else ''
                    html_parts.append(f"    <div class='item' style='margin-left: 20px;'><span class='key'>{html.escape(subkey)}:</span> <span class='{css_class}'>{html.escape(str(subvalue))}</span></div>")
            else:
                css_class = 'warning' if ('risk' in key.lower() or 'threat' in key.lower()) and value else ''
                html_parts.append(f"    <div class='item'><span class='key'>{html.escape(key)}:</span> <span class='{css_class}'>{html.escape(str(value))}</span></div>")
        html_parts.append("  </div>")
        
        # Add content analysis
        html_parts.append("  <div class='section'>")
        html_parts.append("    <h2>Content Analysis</h2>")
        for key, value in self.content_analysis.items():
            if isinstance(value, dict):
                html_parts.append(f"    <div class='item'><span class='key'>{html.escape(key)}:</span></div>")
                for subkey, subvalue in value.items():
                    html_parts.append(f"    <div class='item' style='margin-left: 20px;'><span class='key'>{html.escape(subkey)}:</span> {html.escape(str(subvalue))}</div>")
            elif isinstance(value, list):
                html_parts.append(f"    <div class='item'><span class='key'>{html.escape(key)}:</span></div>")
                html_parts.append("    <ul>")
                for item in value:
                    html_parts.append(f"      <li>{html.escape(str(item))}</li>")
                html_parts.append("    </ul>")
            else:
                html_parts.append(f"    <div class='item'><span class='key'>{html.escape(key)}:</span> {html.escape(str(value))}</div>")
        html_parts.append("  </div>")
        
        # Add summary
        html_parts.append("  <div class='section'>")
        html_parts.append("    <h2>Summary</h2>")
        for key, value in self.summary.items():
            css_class = ''
            if 'risk' in key.lower() or 'threat' in key.lower():
                if value.lower() in ['low', 'none']:
                    css_class = 'safe'
                elif value.lower() in ['high', 'critical']:
                    css_class = 'warning'
            html_parts.append(f"    <div class='item'><span class='key'>{html.escape(key)}:</span> <span class='{css_class}'>{html.escape(str(value))}</span></div>")
        html_parts.append("  </div>")
        
        html_parts.append("</body>")
        html_parts.append("</html>")
        
        return "\n".join(html_parts)

class Analyzer:
    """Class to analyze email content and metadata."""
    
    def __init__(self):
        # Patterns for security analysis
        self.url_pattern = re.compile(r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+')
        self.ip_pattern = re.compile(r'\b(?:\d{1,3}\.){3}\d{1,3}\b')
        self.email_pattern = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')
        
        # Common phishing keywords
        self.phishing_keywords = [
            'account', 'update', 'verify', 'login', 'password', 'security',
            'urgent', 'attention', 'important', 'alert', 'suspended',
            'unusual activity', 'confirm your', 'validate', 'click here',
            'bank', 'paypal', 'amazon', 'microsoft', 'apple', 'google'
        ]
        
    def analyze(self, email_data):
        """
        Analyze an email and return the results.
        
        Args:
            email_data (EmailData): The parsed email data to analyze
            
        Returns:
            AnalysisResults: Object containing the analysis results
        """
        logger.info(f"Analyzing email: {email_data.subject}")
        
        results = AnalysisResults()
        
        # Analyze metadata
        self._analyze_metadata(email_data, results)
        
        # Analyze security aspects
        self._analyze_security(email_data, results)
        
        # Analyze content
        self._analyze_content(email_data, results)
        
        # Generate summary
        self._generate_summary(results)
        
        return results
    
    def _analyze_metadata(self, email_data, results):
        """Analyze email metadata."""
        metadata = {}
        
        metadata['Subject'] = email_data.subject
        metadata['From'] = email_data.from_address
        metadata['To'] = ', '.join(email_data.to_addresses)
        
        if email_data.cc_addresses:
            metadata['CC'] = ', '.join(email_data.cc_addresses)
            
        if email_data.date:
            metadata['Date'] = email_data.date
        
        if email_data.attachments:
            metadata['Attachments'] = [
                f"{attachment.filename} ({attachment.content_type}, {attachment.size} bytes)"
                for attachment in email_data.attachments
            ]
            
        # Add any other interesting headers
        for header in ['Message-ID', 'X-Mailer', 'User-Agent', 'X-Spam-Status']:
            if header in email_data.headers:
                metadata[header] = email_data.headers[header]
        
        results.metadata = metadata
    
    def _analyze_security(self, email_data, results):
        """Analyze email security aspects."""
        security = {}
        
        # Check sender domain
        from_name, from_addr = parseaddr(email_data.from_address)
        if from_addr:
            domain = from_addr.split('@')[-1] if '@' in from_addr else ''
            security['Sender Domain'] = domain
            
            # Check for common security headers
            spf_pass = False
            dkim_pass = False
            dmarc_pass = False
            
            for header, value in email_data.headers.items():
                if header.lower() == 'authentication-results':
                    if 'spf=pass' in value.lower():
                        spf_pass = True
                    if 'dkim=pass' in value.lower():
                        dkim_pass = True
                    if 'dmarc=pass' in value.lower():
                        dmarc_pass = True
            
            security['Authentication'] = {
                'SPF': 'Pass' if spf_pass else 'Not found or failed',
                'DKIM': 'Pass' if dkim_pass else 'Not found or failed',
                'DMARC': 'Pass' if dmarc_pass else 'Not found or failed'
            }
        
        # Extract and analyze URLs
        urls = self.url_pattern.findall(email_data.body_text)
        if email_data.body_html:
            urls.extend(self.url_pattern.findall(email_data.body_html))
        
        if urls:
            security['URLs'] = {
                'Count': len(urls),
                'Unique Count': len(set(urls)),
                'Domains': list(set([url.split('/')[2] for url in urls if '/' in url]))
            }
        
        # Check for IP addresses in the content
        ips = self.ip_pattern.findall(email_data.body_text)
        if email_data.body_html:
            ips.extend(self.ip_pattern.findall(email_data.body_html))
        
        if ips:
            security['IP Addresses'] = list(set(ips))
        
        # Analyze attachments for potential risks
        if email_data.attachments:
            risky_extensions = ['.exe', '.bat', '.cmd', '.scr', '.js', '.vbs', '.ps1', '.jar']
            risky_attachments = [
                attachment.filename
                for attachment in email_data.attachments
                if any(attachment.filename.lower().endswith(ext) for ext in risky_extensions)
            ]
            
            security['Attachments'] = {
                'Count': len(email_data.attachments),
                'Risky Attachments': risky_attachments,
                'Risk Level': 'High' if risky_attachments else 'Low'
            }
        
        # Assess phishing risk
        phishing_score = 0
        phishing_indicators = []
        
        # Check for phishing keywords in subject
        for keyword in self.phishing_keywords:
            if keyword.lower() in email_data.subject.lower():
                phishing_score += 1
                phishing_indicators.append(f"Subject contains '{keyword}'")
        
        # Check for phishing keywords in body
        for keyword in self.phishing_keywords:
            if keyword.lower() in email_data.body_text.lower():
                phishing_score += 0.5
                if f"Body contains '{keyword}'" not in phishing_indicators:
                    phishing_indicators.append(f"Body contains '{keyword}'")
        
        # Check for mismatched URLs (text says one thing, link goes elsewhere)
        if email_data.body_html:
            href_pattern = re.compile(r'href=[\'"]?([^\'" >]+)')
            hrefs = href_pattern.findall(email_data.body_html)
            
            for href in hrefs:
                # Simple check for misleading URLs
                if 'http' in href.lower():
                    display_text = email_data.body_html.split(href)[0].split('>')[-1]
                    if 'http' in display_text.lower() and display_text not in href:
                        phishing_score += 2
                        phishing_indicators.append("Mismatched URL detected")
                        break
        
        # Determine phishing risk level
        phishing_risk = 'Low'
        if phishing_score > 5:
            phishing_risk = 'Critical'
        elif phishing_score > 3:
            phishing_risk = 'High'
        elif phishing_score > 1:
            phishing_risk = 'Medium'
        
        security['Phishing Assessment'] = {
            'Risk Level': phishing_risk,
            'Score': phishing_score,
            'Indicators': phishing_indicators
        }
        
        results.security_analysis = security
    
    def _analyze_content(self, email_data, results):
        """Analyze email content."""
        content = {}
        
        # Basic text analysis
        if email_data.body_text:
            words = re.findall(r'\b\w+\b', email_data.body_text.lower())
            content['Text Analysis'] = {
                'Word Count': len(words),
                'Character Count': len(email_data.body_text),
                'Has HTML Content': bool(email_data.body_html)
            }
            
            # Extract potential sensitive information
            emails_in_body = self.email_pattern.findall(email_data.body_text)
            if emails_in_body:
                content['Emails Mentioned'] = list(set(emails_in_body))
            
            # Simple sentiment analysis (very basic)
            positive_words = ['good', 'great', 'excellent', 'thank', 'thanks', 'appreciate', 'happy', 'pleased']
            negative_words = ['bad', 'issue', 'problem', 'concern', 'sorry', 'regret', 'unfortunate', 'disappointed']
            
            positive_count = sum(1 for word in words if word in positive_words)
            negative_count = sum(1 for word in words if word in negative_words)
            
            sentiment = 'Neutral'
            if positive_count > negative_count * 2:
                sentiment = 'Very Positive'
            elif positive_count > negative_count:
                sentiment = 'Positive'
            elif negative_count > positive_count * 2:
                sentiment = 'Very Negative'
            elif negative_count > positive_count:
                sentiment = 'Negative'
                
            content['Sentiment'] = sentiment
        
        results.content_analysis = content
    
    def _generate_summary(self, results):
        """Generate a summary of the analysis results."""
        summary = {}
        
        # Overall security assessment
        security_risk = 'Low'
        if 'Phishing Assessment' in results.security_analysis:
            phishing_risk = results.security_analysis['Phishing Assessment'].get('Risk Level', 'Low')
            if phishing_risk == 'Critical':
                security_risk = 'Critical'
            elif phishing_risk == 'High' and security_risk != 'Critical':
                security_risk = 'High'
            elif phishing_risk == 'Medium' and security_risk not in ['Critical', 'High']:
                security_risk = 'Medium'
        
        if 'Attachments' in results.security_analysis:
            attachment_risk = results.security_analysis['Attachments'].get('Risk Level', 'Low')
            if attachment_risk == 'High' and security_risk not in ['Critical']:
                security_risk = 'High'
        
        summary['Overall Security Risk'] = security_risk
        
        # Authentication summary
        if 'Authentication' in results.security_analysis:
            auth = results.security_analysis['Authentication']
            if auth.get('SPF') == 'Pass' and auth.get('DKIM') == 'Pass' and auth.get('DMARC') == 'Pass':
                summary['Authentication Status'] = 'Fully Authenticated'
            elif auth.get('SPF') == 'Pass' or auth.get('DKIM') == 'Pass':
                summary['Authentication Status'] = 'Partially Authenticated'
            else:
                summary['Authentication Status'] = 'Not Authenticated'
        
        # Content summary
        if 'Text Analysis' in results.content_analysis:
            summary['Content Type'] = 'HTML and Text' if results.content_analysis['Text Analysis'].get('Has HTML Content') else 'Text Only'
        
        if 'Sentiment' in results.content_analysis:
            summary['Content Sentiment'] = results.content_analysis['Sentiment']
        
        # Add timestamp
        summary['Analysis Timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        results.summary = summary
