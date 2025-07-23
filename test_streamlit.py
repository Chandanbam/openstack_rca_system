#!/usr/bin/env python3

import sys
import os
sys.path.append('/app')

print("Testing Streamlit app import...")

try:
    from streamlit_app.chatbot import main
    print("✅ Successfully imported chatbot")
    
    # Test if we can create the app instance
    from streamlit_app.chatbot import OpenStackRCAAssistant
    app = OpenStackRCAAssistant()
    print("✅ Successfully created app instance")
    
    print("✅ All imports successful!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc() 