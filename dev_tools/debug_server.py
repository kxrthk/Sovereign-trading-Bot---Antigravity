import sys
import traceback
import json

try:
    # Append path just in case
    sys.path.append('.')
    from dashboard_server import get_performance
    
    print("Invoking get_performance()...")
    result = get_performance()
    print("Function returned. Serializing to JSON...")
    
    # Simulate FastAPI validation
    json_output = json.dumps(result)
    print("Serialization Success!")
    print(json_output)

except Exception:
    print("CRASH DETECTED!")
    traceback.print_exc()
