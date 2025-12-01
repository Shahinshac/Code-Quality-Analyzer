"""
Vercel serverless function entrypoint for Flask application.
This file is required by Vercel to deploy the Flask app.
"""

from code_quality_analyzer.webapp import create_app

# Create the Flask app instance
app = create_app()

# Vercel will use this 'app' object as the WSGI application
