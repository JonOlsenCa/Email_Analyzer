#!/usr/bin/env python3
"""
Review Mappings

This script provides a simple interface to review and approve pending mappings
for company names, support categories, and subject templates.
"""

import os
import sys
from data_normalizer import CompanyNormalizer, CategoryNormalizer, TemplateNormalizer

def review_normalizer(normalizer, entity_type):
    """
    Review pending mappings for a normalizer.
    
    Args:
        normalizer: The normalizer instance
        entity_type: String describing the entity type
    """
    pending = normalizer.get_pending_reviews()
    
    if not pending:
        print(f"No pending {entity_type} mappings to review.")
        return
    
    print(f"\nReviewing {len(pending)} pending {entity_type} mappings:")
    print("-" * 60)
    
    for entity, info in pending.items():
        suggested = info['suggested']
        score = info['score']
        
        print(f"Entity: {entity}")
        print(f"Suggested mapping: {suggested} (confidence: {score:.2f})")
        
        while True:
            choice = input("Options: (a)ccept, (r)eject, (c)ustom mapping, (s)kip: ").lower()
            
            if choice == 'a':
                normalizer.approve_mapping(entity)
                print(f"Approved mapping: {entity} -> {suggested}")
                break
            elif choice == 'r':
                # Add as a new standardized entity
                normalizer.add_standardized_entity(entity)
                print(f"Rejected mapping. Added {entity} as a new standardized entity.")
                break
            elif choice == 'c':
                custom = input(f"Enter custom mapping for {entity}: ")
                if custom:
                    normalizer.approve_mapping(entity, custom)
                    print(f"Approved custom mapping: {entity} -> {custom}")
                    break
                else:
                    print("Custom mapping cannot be empty.")
            elif choice == 's':
                print("Skipped.")
                break
            else:
                print("Invalid choice. Please try again.")
        
        print("-" * 60)
    
    # Save the updated mappings
    normalizer.save_mappings()
    print(f"Saved updated {entity_type} mappings.")

def main():
    """Main function."""
    print("=== Mapping Review Tool ===")
    
    # Initialize normalizers
    company_normalizer = CompanyNormalizer()
    category_normalizer = CategoryNormalizer()
    template_normalizer = TemplateNormalizer()
    
    while True:
        print("\nSelect entity type to review:")
        print("1. Company Names")
        print("2. Support Categories")
        print("3. Subject Templates")
        print("4. Review All")
        print("5. Exit")
        
        choice = input("Enter choice (1-5): ")
        
        if choice == '1':
            review_normalizer(company_normalizer, "company name")
        elif choice == '2':
            review_normalizer(category_normalizer, "support category")
        elif choice == '3':
            review_normalizer(template_normalizer, "subject template")
        elif choice == '4':
            review_normalizer(company_normalizer, "company name")
            review_normalizer(category_normalizer, "support category")
            review_normalizer(template_normalizer, "subject template")
        elif choice == '5':
            print("Exiting.")
            break
        else:
            print("Invalid choice. Please try again.")
    
    # Update the dashboard with the normalized data
    try:
        from update_dashboard import update_dashboard
        update_dashboard()
    except ImportError:
        print("Could not import update_dashboard module. Please run update_dashboard.py separately.")

if __name__ == "__main__":
    main()
