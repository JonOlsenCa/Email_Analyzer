#!/usr/bin/env python3
"""
Data Normalizer

This module provides normalization functionality for company names, support categories,
and subject templates. It detects new entities, suggests standardized forms, and
maintains mapping files for consistent normalization.
"""

import os
import json
import re
from difflib import SequenceMatcher
from typing import Dict, List, Set, Tuple, Optional, Any

# Default paths for mapping files
DEFAULT_MAPPINGS_DIR = "mappings"
DEFAULT_COMPANY_MAPPINGS = os.path.join(DEFAULT_MAPPINGS_DIR, "company_mappings.json")
DEFAULT_CATEGORY_MAPPINGS = os.path.join(DEFAULT_MAPPINGS_DIR, "category_mappings.json")
DEFAULT_TEMPLATE_MAPPINGS = os.path.join(DEFAULT_MAPPINGS_DIR, "template_mappings.json")

# Default confidence thresholds
DEFAULT_AUTO_THRESHOLD = 0.9  # Automatically accept matches above this threshold (increased for stability)
DEFAULT_SUGGEST_THRESHOLD = 0.7  # Suggest matches above this threshold for review (increased for stability)

class Normalizer:
    """Base class for entity normalization."""

    def __init__(self, mappings_file: str, auto_threshold: float = DEFAULT_AUTO_THRESHOLD,
                 suggest_threshold: float = DEFAULT_SUGGEST_THRESHOLD):
        """
        Initialize the normalizer.

        Args:
            mappings_file: Path to the JSON file containing mappings
            auto_threshold: Threshold for automatic matching (0.0-1.0)
            suggest_threshold: Threshold for suggesting matches (0.0-1.0)
        """
        self.mappings_file = mappings_file
        self.auto_threshold = auto_threshold
        self.suggest_threshold = suggest_threshold
        self.mappings = {}
        self.standardized_entities = set()
        self.pending_review = {}  # Entities pending review with suggested mappings

        # Create mappings directory if it doesn't exist
        os.makedirs(os.path.dirname(mappings_file), exist_ok=True)

        # Load existing mappings if available
        self.load_mappings()

    def load_mappings(self) -> None:
        """Load mappings from the JSON file."""
        try:
            if os.path.exists(self.mappings_file):
                with open(self.mappings_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.mappings = data.get('mappings', {})
                    self.standardized_entities = set(data.get('standardized_entities', []))
                    print(f"Loaded {len(self.mappings)} mappings from {self.mappings_file}")
            else:
                print(f"Mappings file {self.mappings_file} not found, starting with empty mappings")
                self.mappings = {}
                self.standardized_entities = set()
        except Exception as e:
            print(f"Error loading mappings: {str(e)}")
            self.mappings = {}
            self.standardized_entities = set()

    def save_mappings(self) -> None:
        """Save mappings to the JSON file."""
        try:
            data = {
                'mappings': self.mappings,
                'standardized_entities': list(self.standardized_entities)
            }
            with open(self.mappings_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            print(f"Saved {len(self.mappings)} mappings to {self.mappings_file}")
        except Exception as e:
            print(f"Error saving mappings: {str(e)}")

    def normalize(self, entity: str) -> str:
        """
        Normalize an entity using existing mappings or fuzzy matching.

        Args:
            entity: The entity to normalize

        Returns:
            The normalized entity name
        """
        if not entity or entity.lower() in ('n/a', 'unknown', ''):
            return self.get_default_entity()

        # Clean the entity name
        cleaned_entity = self.clean_entity(entity)

        # Check if we have an exact mapping
        if cleaned_entity in self.mappings:
            return self.mappings[cleaned_entity]

        # Check if the entity is already a standardized form
        if cleaned_entity in self.standardized_entities:
            return cleaned_entity

        # Try fuzzy matching
        best_match, score = self.find_best_match(cleaned_entity)

        # Use a higher threshold for automatic matching to preserve established entities
        if score >= self.auto_threshold:
            # Automatically add the mapping if confidence is high
            self.add_mapping(cleaned_entity, best_match)
            print(f"Added mapping: {cleaned_entity} -> {best_match} (score: {score:.2f})")
            return best_match
        elif score >= self.suggest_threshold:
            # Add to pending review if confidence is moderate
            self.pending_review[cleaned_entity] = {
                'suggested': best_match,
                'score': score
            }
            print(f"Added to pending review: {cleaned_entity} -> {best_match} (score: {score:.2f})")
            # Return the suggested match but don't save it yet
            return best_match
        else:
            # If no good match, treat as a new standardized entity
            self.add_standardized_entity(cleaned_entity)
            print(f"Added new standardized entity: {cleaned_entity}")
            return cleaned_entity

    def find_best_match(self, entity: str) -> Tuple[str, float]:
        """
        Find the best match for an entity among standardized entities.

        Args:
            entity: The entity to match

        Returns:
            Tuple of (best_match, score)
        """
        best_score = 0
        best_match = entity

        # First check against standardized entities
        for std_entity in self.standardized_entities:
            score = self.similarity(entity, std_entity)
            if score > best_score:
                best_score = score
                best_match = std_entity

        # Also check against values in mappings
        for mapped_value in set(self.mappings.values()):
            score = self.similarity(entity, mapped_value)
            if score > best_score:
                best_score = score
                best_match = mapped_value

        return best_match, best_score

    def similarity(self, a: str, b: str) -> float:
        """
        Calculate similarity between two strings.

        Args:
            a: First string
            b: Second string

        Returns:
            Similarity score between 0.0 and 1.0
        """
        # Basic implementation using SequenceMatcher
        return SequenceMatcher(None, a.lower(), b.lower()).ratio()

    def add_mapping(self, entity: str, standardized: str) -> None:
        """
        Add a new mapping.

        Args:
            entity: The entity variant
            standardized: The standardized form
        """
        self.mappings[entity] = standardized
        self.standardized_entities.add(standardized)

        # Remove from pending review if it was there
        if entity in self.pending_review:
            del self.pending_review[entity]

    def add_standardized_entity(self, entity: str) -> None:
        """
        Add a new standardized entity.

        Args:
            entity: The entity to add as standardized
        """
        self.standardized_entities.add(entity)

    def get_pending_reviews(self) -> Dict[str, Dict[str, Any]]:
        """
        Get entities pending review.

        Returns:
            Dictionary of entities pending review with suggested mappings
        """
        return self.pending_review

    def approve_mapping(self, entity: str, standardized: str = None) -> None:
        """
        Approve a suggested mapping or specify a custom mapping.

        Args:
            entity: The entity to map
            standardized: The standardized form (if None, use the suggested mapping)
        """
        if entity in self.pending_review:
            if standardized is None:
                standardized = self.pending_review[entity]['suggested']

            self.add_mapping(entity, standardized)
            print(f"Approved mapping: {entity} -> {standardized}")
        else:
            print(f"No pending review for {entity}")

    def clean_entity(self, entity: str) -> str:
        """
        Clean an entity name for normalization.

        Args:
            entity: The entity to clean

        Returns:
            Cleaned entity name
        """
        # Basic cleaning: trim whitespace and convert to string
        return str(entity).strip()

    def get_default_entity(self) -> str:
        """
        Get the default entity name for empty/unknown values.

        Returns:
            Default entity name
        """
        return "Unknown"

    def get_all_standardized(self) -> List[str]:
        """
        Get all standardized entities.

        Returns:
            List of all standardized entities
        """
        return sorted(list(self.standardized_entities))

    def get_mappings_for_js(self) -> Dict[str, str]:
        """
        Get mappings formatted for JavaScript.

        Returns:
            Dictionary of mappings suitable for JavaScript
        """
        return self.mappings


class CompanyNormalizer(Normalizer):
    """Normalizer for company names."""

    def __init__(self, mappings_file: str = DEFAULT_COMPANY_MAPPINGS,
                 auto_threshold: float = DEFAULT_AUTO_THRESHOLD,
                 suggest_threshold: float = DEFAULT_SUGGEST_THRESHOLD):
        """Initialize the company normalizer."""
        super().__init__(mappings_file, auto_threshold, suggest_threshold)

        # Known valid company names
        self.known_companies = [
            "Beacon Communications, LLC",
            "Ben Hur Construction Co.",
            "BluSky Restoration Contractors, LLC",
            "Concrete & Materials Placement",
            "Doggett Concrete Construction",
            "GBI",
            "Gulf Stream Construction Co., Inc.",
            "H&M Mechanical Constructors, Inc.",
            "Haskell Lemon",
            "NP Mechanical, Inc.",
            "S.M. Hentges",
            "TSU One, Inc.",
            "TaftElectric",
            "Moisture Loc",
            "Comtel Systems Technology",
            "Great Basin Industrial",
            "Doggett Residential"
        ]

        # Patterns to exclude (UUIDs, numeric IDs, error messages)
        self.exclude_patterns = [
            r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$',  # UUID
            r'^[0-9]+$',  # Numeric ID
            r'^[0-9.-]+$',  # Numeric ID with dots or dashes
            r'^<',  # HTML tags
            r'error|issue|warning|incorrect|wrong|missing|invoice|wizard|system|prediction|vendor|document',  # Error messages
            r'^The\s',  # Sentences starting with "The"
            r'^There\s',  # Sentences starting with "There"
            r'^Is\s',  # Sentences starting with "Is"
            r'^We\s',  # Sentences starting with "We"
            r'^Not\s',  # Sentences starting with "Not"
            r'^This\s',  # Sentences starting with "This"
            r'^All\s',  # Sentences starting with "All"
            r'^Due\s',  # Sentences starting with "Due"
            r'^Changed\s',  # Sentences starting with "Changed"
            r'^Data\s',  # Sentences starting with "Data"
            r'^PO\s',  # Sentences starting with "PO"
            r'^SQL\s',  # Sentences starting with "SQL"
            r'^SHOULD\s',  # Sentences starting with "SHOULD"
            r'^WIZARD\s',  # Sentences starting with "WIZARD"
            r'^GRANT\s',  # Sentences starting with "GRANT"
            r'^email\s',  # Sentences starting with "email"
            r'^invoice\s',  # Sentences starting with "invoice"
            r'^sales\s',  # Sentences starting with "sales"
            r'^the\s',  # Sentences starting with "the"
            r'^this\s'  # Sentences starting with "this"
        ]

    def normalize(self, entity: str) -> str:
        """
        Normalize a company name, with additional validation.

        Args:
            entity: The entity to normalize

        Returns:
            The normalized entity name
        """
        # Skip normalization for invalid company names
        if self.is_invalid_company(entity):
            return self.get_default_entity()

        # Proceed with normal normalization for valid company names
        return super().normalize(entity)

    def is_invalid_company(self, entity: str) -> bool:
        """
        Check if an entity is an invalid company name.

        Args:
            entity: The entity to check

        Returns:
            True if invalid, False if valid
        """
        if not entity or entity.lower() in ('n/a', 'unknown', ''):
            return True

        # Check against exclude patterns
        for pattern in self.exclude_patterns:
            if re.search(pattern, entity, re.IGNORECASE):
                return True

        # If it's a known company or looks like a company name, it's valid
        if entity in self.known_companies:
            return False

        # Check if it's too long to be a company name (likely an error message)
        if len(entity) > 50:
            return True

        # Check if it contains too many words to be a company name
        words = entity.split()
        if len(words) > 8:
            return True

        return False

    def clean_entity(self, entity: str) -> str:
        """Clean a company name for normalization."""
        # Start with basic cleaning
        cleaned = super().clean_entity(entity)

        # Remove common suffixes for better matching
        cleaned = re.sub(r'\s+(Inc\.?|LLC\.?|Ltd\.?|Co\.?|Corp\.?|Corporation|Limited)$', '', cleaned, flags=re.IGNORECASE)

        return cleaned

    def get_default_entity(self) -> str:
        """Get the default company name."""
        return "Unknown Company"


class CategoryNormalizer(Normalizer):
    """Normalizer for support categories."""

    def __init__(self, mappings_file: str = DEFAULT_CATEGORY_MAPPINGS,
                 auto_threshold: float = DEFAULT_AUTO_THRESHOLD,
                 suggest_threshold: float = DEFAULT_SUGGEST_THRESHOLD):
        """Initialize the category normalizer."""
        super().__init__(mappings_file, auto_threshold, suggest_threshold)

    def get_default_entity(self) -> str:
        """Get the default category."""
        return "Other"


class TemplateNormalizer(Normalizer):
    """Normalizer for subject templates."""

    def __init__(self, mappings_file: str = DEFAULT_TEMPLATE_MAPPINGS,
                 auto_threshold: float = DEFAULT_AUTO_THRESHOLD,
                 suggest_threshold: float = DEFAULT_SUGGEST_THRESHOLD):
        """Initialize the template normalizer."""
        super().__init__(mappings_file, auto_threshold, suggest_threshold)

        # Valid template keywords
        self.valid_keywords = [
            "vendor", "prediction", "system", "performance",
            "error", "upload", "document", "integration",
            "erp", "accounting", "invoice", "submit", "unexpected"
        ]

        # Patterns to exclude (UUIDs, email addresses)
        self.exclude_patterns = [
            r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$',
            r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        ]

    def normalize(self, entity: str) -> str:
        """
        Normalize a subject template, with additional validation.

        Args:
            entity: The entity to normalize

        Returns:
            The normalized entity name
        """
        # Skip normalization for invalid templates
        if self.is_invalid_template(entity):
            return self.get_default_entity()

        # Proceed with normal normalization for valid templates
        return super().normalize(entity)

    def is_invalid_template(self, entity: str) -> bool:
        """
        Check if an entity is an invalid template.

        Args:
            entity: The entity to check

        Returns:
            True if invalid, False if valid
        """
        if not entity or entity.lower() in ('n/a', 'unknown', ''):
            return True

        # Check against exclude patterns
        for pattern in self.exclude_patterns:
            if re.match(pattern, entity):
                return True

        # Check if it contains any valid keywords
        entity_lower = entity.lower()
        has_valid_keyword = any(keyword in entity_lower for keyword in self.valid_keywords)

        # If it doesn't have any valid keywords, it's probably not a template
        return not has_valid_keyword

    def get_default_entity(self) -> str:
        """Get the default template."""
        return "Other"
