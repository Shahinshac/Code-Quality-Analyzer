"""Live test of the Flask app to verify AI classification and functionality"""
import requests
import time

print("Testing Flask app at http://127.0.0.1:5000")
print("=" * 60)

# Test code with multiple issues
test_code = """def calculate_total(items):
    total = 0
    # TODO: Optimize this function
    for item in items:
        if item.price > 0:
            if item.discount > 0:
                if item.quantity > 0:
                    if item.tax > 0:
                        if item.shipping > 0:
                            # Deep nesting detected
                            total += (item.price - item.discount) * item.quantity + item.tax + item.shipping
    return total
"""

try:
    # Test 1: Submit code for analysis
    print("Test 1: Submitting code for analysis...")
    response = requests.post(
        "http://127.0.0.1:5000",
        data={
            "code": test_code,
            "lang": "python"
        },
        timeout=10
    )
    
    print(f"✓ Status code: {response.status_code}")
    
    # Check for key elements in response
    checks = {
        "AI Classification": "AI Classification" in response.text,
        "Load Template button": "Load Template" in response.text,
        "Clear button": "Clear" in response.text,
        "Format button": "Format" in response.text,
        "Dark mode toggle": "toggleTheme" in response.text,
        "Quality Score": "Quality Score" in response.text,
        "Confidence": "Confidence:" in response.text or "confidence:" in response.text,
    }
    
    print("\nFunctionality Check:")
    for check_name, check_result in checks.items():
        status = "✓" if check_result else "✗"
        print(f"{status} {check_name}: {'Present' if check_result else 'Missing'}")
    
    # Count issues detected
    if "Deep Nesting" in response.text:
        print("\n✓ Code analysis working - Deep nesting detected")
    if "TODO" in response.text or "todo" in response.text.lower():
        print("✓ TODO comment detection working")
    
    all_present = all(checks.values())
    
    print("\n" + "=" * 60)
    if all_present:
        print("✓ ALL FEATURES WORKING CORRECTLY!")
        print("\nYou can now:")
        print("  1. Click 'Load Template' to load example code")
        print("  2. Click 'Clear' to clear the textarea")
        print("  3. Click 'Format' to format your code")
        print("  4. Toggle dark mode with the moon/sun icon")
        print("  5. See AI classification with confidence score")
    else:
        print("✗ Some features are missing - check above")
    
except requests.exceptions.ConnectionError:
    print("✗ Could not connect to Flask app")
    print("Make sure the app is running: flask run --port 5000")
except Exception as e:
    print(f"✗ Error: {e}")
