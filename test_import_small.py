#!/usr/bin/env python3
"""
Test script to import just a few tests
"""

import csv
import os

# Create a small test file with just 3 tests
test_data = []
with open('news_surface_cleaned.csv', 'r', encoding='iso-8859-1') as f:
    reader = csv.DictReader(f)
    fieldnames = reader.fieldnames
    for i, row in enumerate(reader):
        test_data.append(row)
        if i >= 2:  # Get just 3 tests
            break

# Write small test file
with open('test_small.csv', 'w', encoding='iso-8859-1', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(test_data)

print("Created test_small.csv with 3 tests")
print("Run: python3 xray_import_script.py test_small.csv")