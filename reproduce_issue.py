import os

# Scenario 1: SMTP_PORT is set to empty string (simulating the bug)
os.environ["SMTP_PORT"] = ""
print(f"Scenario 1: SMTP_PORT='{os.environ['SMTP_PORT']}'")
try:
    port = int(os.environ.get("SMTP_PORT", "587"))
    print(f"Result: {port}")
except ValueError as e:
    print(f"Error caught: {e}")

# Scenario 2: Proposed Fix
print("\nScenario 2: Testing fix with SMTP_PORT=''")
try:
    # Logic: if env var is empty string or None, use default
    port_str = os.environ.get("SMTP_PORT")
    port = int(port_str or 587)
    print(f"Result: {port}")
except ValueError as e:
    print(f"Error caught: {e}")

# Scenario 3: SMTP_PORT is not set
del os.environ["SMTP_PORT"]
print("\nScenario 3: SMTP_PORT is unset")
try:
    port_str = os.environ.get("SMTP_PORT")
    port = int(port_str or 587)
    print(f"Result: {port}")
except ValueError as e:
    print(f"Error caught: {e}")
