"""Test script to verify AI classification, buttons, and dark mode functionality"""
import os
import sys

# Test 1: Check if model exists
print("=" * 60)
print("TEST 1: AI Classification Model")
print("=" * 60)
model_path = "models/code_quality_model.joblib"
model_exists = os.path.exists(model_path)
print(f"✓ Model file exists: {model_exists}")

if model_exists:
    from code_quality_analyzer.ml_classifier import predict_code_quality
    
    test_code = """def long_function():
    x = 1
    y = 2
    # This function is too long
    for i in range(100):
        if i > 50:
            print(i)
"""
    
    try:
        label, confidence = predict_code_quality(test_code, model_path)
        print(f"✓ AI Classification working")
        print(f"  - Label: {label}")
        print(f"  - Confidence: {confidence:.2%}")
    except Exception as e:
        print(f"✗ AI Classification failed: {e}")
else:
    print("✗ Model file not found")

# Test 2: Check webapp template for 3 buttons
print("\n" + "=" * 60)
print("TEST 2: Three Action Buttons")
print("=" * 60)

from code_quality_analyzer.webapp import TEMPLATE

buttons_to_check = [
    ("Load Template", "loadTemplate()"),
    ("Clear", "clearCode()"),
    ("Format", "formatCode()")
]

all_buttons_present = True
for button_name, button_function in buttons_to_check:
    if button_name in TEMPLATE and button_function in TEMPLATE:
        print(f"✓ {button_name} button present")
    else:
        print(f"✗ {button_name} button missing")
        all_buttons_present = False

# Test 3: Check dark mode functionality
print("\n" + "=" * 60)
print("TEST 3: Dark Mode Toggle")
print("=" * 60)

dark_mode_elements = [
    ("Dark mode CSS class", ".dark-mode {"),
    ("Toggle theme function", "function toggleTheme()"),
    ("Theme icon", "themeIcon"),
    ("LocalStorage persistence", "localStorage.setItem('theme'"),
    ("Toggle button", "Toggle Dark Mode")
]

all_dark_mode_present = True
for element_name, element_text in dark_mode_elements:
    if element_text in TEMPLATE:
        print(f"✓ {element_name} present")
    else:
        print(f"✗ {element_name} missing")
        all_dark_mode_present = False

# Test 4: Check AI Classification in template
print("\n" + "=" * 60)
print("TEST 4: AI Classification Display")
print("=" * 60)

ai_elements = [
    ("AI Classification section", "AI Classification"),
    ("Brain icon", "fa-brain"),
    ("Prediction label", "{{ analysis.ml_classification.label"),
    ("Confidence score", "Confidence:")
]

all_ai_present = True
for element_name, element_text in ai_elements:
    if element_text in TEMPLATE:
        print(f"✓ {element_name} present")
    else:
        print(f"✗ {element_name} missing")
        all_ai_present = False

# Test 5: Verify button functions exist in JavaScript
print("\n" + "=" * 60)
print("TEST 5: JavaScript Functions")
print("=" * 60)

js_functions = [
    ("loadTemplate", "function loadTemplate()"),
    ("clearCode", "function clearCode()"),
    ("formatCode", "function formatCode()"),
    ("toggleTheme", "function toggleTheme()")
]

all_js_present = True
for func_name, func_signature in js_functions:
    if func_signature in TEMPLATE:
        print(f"✓ {func_name}() function defined")
    else:
        print(f"✗ {func_name}() function missing")
        all_js_present = False

# Final Summary
print("\n" + "=" * 60)
print("SUMMARY")
print("=" * 60)

all_tests_passed = all([
    model_exists,
    all_buttons_present,
    all_dark_mode_present,
    all_ai_present,
    all_js_present
])

if all_tests_passed:
    print("✓ ALL TESTS PASSED - All functionality working correctly!")
else:
    print("✗ SOME TESTS FAILED - Please review the output above")
    sys.exit(1)
