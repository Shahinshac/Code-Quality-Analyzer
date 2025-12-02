"""Run the Flask application with environment variables loaded from .env file"""
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Import and run the Flask app
from code_quality_analyzer.webapp import create_app

if __name__ == '__main__':
    app = create_app()
    
    # Get configuration from environment variables
    host = os.getenv('HOST', '127.0.0.1')
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', '0') == '1'
    
    print(f"🚀 Starting Code Quality Analyzer")
    print(f"📍 Server: http://{host}:{port}")
    print(f"🔧 Debug mode: {debug}")
    print(f"📁 Model path: {os.getenv('MODEL_PATH', 'Not set')}")
    print("-" * 50)
    
    app.run(host=host, port=port, debug=debug)
