#!/usr/bin/env python3
"""
Test Normalization

This script tests the normalization system to ensure it works correctly.
It verifies that company names, support categories, and subject templates
are normalized consistently.
"""

import os
import json
from data_normalizer import CompanyNormalizer, CategoryNormalizer, TemplateNormalizer

def test_company_normalizer():
    """Test the company normalizer."""
    print("\n=== Testing Company Normalizer ===")
    
    # Initialize the normalizer
    normalizer = CompanyNormalizer()
    
    # Test cases with expected results
    test_cases = [
        ("BluSky", "BluSky Restoration Contractors, LLC"),
        ("BluSky Restoration", "BluSky Restoration Contractors, LLC"),
        ("Taft Electric", "TaftElectric"),
        ("TSU", "TSU One, Inc."),
        ("Gulf Stream", "Gulf Stream Construction Co., Inc."),
        ("S.M. Hentges & Sons", "S.M. Hentges"),
        ("Unknown Company", "Unknown Company"),
        ("", "Unknown Company"),
        ("N/A", "Unknown Company")
    ]
    
    # Run tests
    passed = 0
    for input_value, expected in test_cases:
        result = normalizer.normalize(input_value)
        if result == expected:
            print(f"✓ '{input_value}' -> '{result}'")
            passed += 1
        else:
            print(f"✗ '{input_value}' -> '{result}' (expected: '{expected}')")
    
    print(f"Passed {passed}/{len(test_cases)} company normalization tests")
    return passed, len(test_cases)

def test_category_normalizer():
    """Test the category normalizer."""
    print("\n=== Testing Category Normalizer ===")
    
    # Initialize the normalizer
    normalizer = CategoryNormalizer()
    
    # Test cases with expected results
    test_cases = [
        ("AI Model Issues", "AI Model Prediction & Extraction Issues"),
        ("Document Processing Issue", "Document Processing Failures"),
        ("System Bug", "System Bugs & Integration Issues"),
        ("Integration Issue", "System Bugs & Integration Issues"),
        ("Other Issue", "Other"),
        ("Unknown", "Other"),
        ("", "Other"),
        ("N/A", "Other")
    ]
    
    # Run tests
    passed = 0
    for input_value, expected in test_cases:
        result = normalizer.normalize(input_value)
        if result == expected:
            print(f"✓ '{input_value}' -> '{result}'")
            passed += 1
        else:
            print(f"✗ '{input_value}' -> '{result}' (expected: '{expected}')")
    
    print(f"Passed {passed}/{len(test_cases)} category normalization tests")
    return passed, len(test_cases)

def test_template_normalizer():
    """Test the template normalizer."""
    print("\n=== Testing Template Normalizer ===")
    
    # Initialize the normalizer
    normalizer = TemplateNormalizer()
    
    # Test cases with expected results
    test_cases = [
        ("Vendor Prediction Error", "Incorrect Vendor Prediction"),
        ("System Slow", "System Performance Issues"),
        ("Upload Error", "Error Uploading Documents"),
        ("ERP Integration Issue", "Integration Issue with ERP/Accounting System"),
        ("Cannot Submit Invoice", "Unable to Submit Invoice"),
        ("System Error", "Unexpected Error"),
        ("Unknown", "Other"),
        ("", "Other"),
        ("N/A", "Other")
    ]
    
    # Run tests
    passed = 0
    for input_value, expected in test_cases:
        result = normalizer.normalize(input_value)
        if result == expected:
            print(f"✓ '{input_value}' -> '{result}'")
            passed += 1
        else:
            print(f"✗ '{input_value}' -> '{result}' (expected: '{expected}')")
    
    print(f"Passed {passed}/{len(test_cases)} template normalization tests")
    return passed, len(test_cases)

def test_fuzzy_matching():
    """Test fuzzy matching for new entities."""
    print("\n=== Testing Fuzzy Matching ===")
    
    # Initialize normalizers
    company_normalizer = CompanyNormalizer()
    category_normalizer = CategoryNormalizer()
    template_normalizer = TemplateNormalizer()
    
    # Test cases with expected results
    test_cases = [
        # New company variations that should match existing companies
        (company_normalizer, "BlueSky", "BluSky Restoration Contractors, LLC"),
        (company_normalizer, "Taft Electric Co", "TaftElectric"),
        (company_normalizer, "Gulf Stream Const", "Gulf Stream Construction Co., Inc."),
        
        # New category variations that should match existing categories
        (category_normalizer, "AI Extraction Problem", "AI Model Prediction & Extraction Issues"),
        (category_normalizer, "Document Processing Error", "Document Processing Failures"),
        
        # New template variations that should match existing templates
        (template_normalizer, "Vendor Prediction Problem", "Incorrect Vendor Prediction"),
        (template_normalizer, "System is Slow", "System Performance Issues")
    ]
    
    # Run tests
    passed = 0
    for normalizer, input_value, expected in test_cases:
        result = normalizer.normalize(input_value)
        if result == expected:
            print(f"✓ '{input_value}' -> '{result}'")
            passed += 1
        else:
            print(f"✗ '{input_value}' -> '{result}' (expected: '{expected}')")
    
    print(f"Passed {passed}/{len(test_cases)} fuzzy matching tests")
    return passed, len(test_cases)

def test_new_entity_handling():
    """Test handling of completely new entities."""
    print("\n=== Testing New Entity Handling ===")
    
    # Create temporary normalizers with test mapping files
    os.makedirs("test_mappings", exist_ok=True)
    
    company_file = os.path.join("test_mappings", "company_test.json")
    category_file = os.path.join("test_mappings", "category_test.json")
    template_file = os.path.join("test_mappings", "template_test.json")
    
    # Initialize with empty mappings
    for file in [company_file, category_file, template_file]:
        with open(file, 'w') as f:
            json.dump({"mappings": {}, "standardized_entities": []}, f)
    
    company_normalizer = CompanyNormalizer(company_file)
    category_normalizer = CategoryNormalizer(category_file)
    template_normalizer = TemplateNormalizer(template_file)
    
    # Test adding new entities
    new_entities = [
        (company_normalizer, "New Company LLC"),
        (category_normalizer, "New Support Category"),
        (template_normalizer, "New Subject Template")
    ]
    
    # Run tests
    passed = 0
    for normalizer, entity in new_entities:
        # First normalization should add it as a new standardized entity
        result1 = normalizer.normalize(entity)
        
        # Second normalization of the same entity should return the same result
        result2 = normalizer.normalize(entity)
        
        # Variation of the entity should map to the standardized form
        variation = f"{entity} Variation"
        result3 = normalizer.normalize(variation)
        
        if result1 == entity and result2 == entity and result3 == entity:
            print(f"✓ New entity '{entity}' handled correctly")
            passed += 1
        else:
            print(f"✗ New entity '{entity}' not handled correctly:")
            print(f"  First call: '{result1}'")
            print(f"  Second call: '{result2}'")
            print(f"  Variation call: '{result3}'")
    
    # Clean up test files
    for file in [company_file, category_file, template_file]:
        if os.path.exists(file):
            os.remove(file)
    
    if os.path.exists("test_mappings"):
        try:
            os.rmdir("test_mappings")
        except:
            pass
    
    print(f"Passed {passed}/{len(new_entities)} new entity handling tests")
    return passed, len(new_entities)

def main():
    """Main function."""
    print("=== Normalization System Tests ===")
    
    # Run all tests
    results = []
    results.append(test_company_normalizer())
    results.append(test_category_normalizer())
    results.append(test_template_normalizer())
    results.append(test_fuzzy_matching())
    results.append(test_new_entity_handling())
    
    # Calculate overall results
    total_passed = sum(r[0] for r in results)
    total_tests = sum(r[1] for r in results)
    
    print("\n=== Test Summary ===")
    print(f"Total: {total_passed}/{total_tests} tests passed ({total_passed/total_tests*100:.1f}%)")
    
    if total_passed == total_tests:
        print("\n✓ All tests passed! The normalization system is working correctly.")
    else:
        print(f"\n✗ {total_tests - total_passed} tests failed. Please check the output above for details.")

if __name__ == "__main__":
    main()
