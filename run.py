#!/usr/bin/env python3
"""
Maternal and Child Health Monitoring System
Main application entry point
"""

import os
import sys
import traceback
import webbrowser
import time
from threading import Timer
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def open_browser(url):
    """Open browser after a short delay"""
    time.sleep(1.5)
    try:
        webbrowser.open(url)
        print(f"🌐 Opened browser to {url}")
    except Exception as e:
        print(f"⚠️ Could not open browser automatically: {e}")
        print(f"Please manually open: {url}")

try:
    print("=" * 60)
    print("🍼 PREGNANCY BABY CARE SYSTEM")
    print("=" * 60)
    print("🔍 Starting application...")
    print(f"Python version: {sys.version}")
    print(f"Working directory: {os.getcwd()}")

    print("\n📦 Importing Flask...")
    import flask
    print(f"✅ Flask version: {flask.__version__}")

    print("📦 Importing app module...")
    from app import create_app
    print("✅ App module imported successfully")

    print("🏗️ Creating Flask application...")
    # Create Flask application
    app = create_app(os.environ.get('FLASK_ENV', 'development'))
    print("✅ Flask app created successfully")

    print("\n🔧 App configuration:")
    print(f"   Debug mode: {app.config.get('DEBUG')}")
    print(f"   Secret key configured: {'Yes' if app.config.get('SECRET_KEY') else 'No'}")
    print(f"   Database path: {app.config.get('DATABASE_PATH')}")

    # Check if database file exists
    db_file = app.config.get('DATABASE_PATH')
    if db_file and os.path.exists(db_file):
        print(f"   Database exists: ✅")
        print(f"   Database size: {os.path.getsize(db_file)} bytes")
    else:
        print(f"   Database will be created: ⚠️")

except Exception as e:
    print(f"❌ Error creating app: {e}")
    print("Full traceback:")
    traceback.print_exc()
    input("Press Enter to exit...")
    sys.exit(1)

if __name__ == '__main__':
    try:
        # Development server configuration
        debug_mode = os.environ.get('FLASK_ENV') != 'production'
        port = int(os.environ.get('PORT', 5000))
        host = os.environ.get('HOST', '127.0.0.1')

        server_url = f"http://{host}:{port}"

        print(f"\n🚀 Starting Maternal and Child Health Monitoring System...")
        print("=" * 60)
        print(f"🌐 Server URL: {server_url}")
        print(f"🔧 Debug mode: {debug_mode}")
        print("=" * 60)
        print(f"🎯 Starting server...")
        print(f"🌐 Browser will open automatically...")
        print(f"🛑 Press Ctrl+C to stop the server")
        print("=" * 60)

        # Open browser automatically after server starts
        Timer(2.0, open_browser, [server_url]).start()

        app.run(
            host=host,
            port=port,
            debug=debug_mode,
            threaded=True,
            use_reloader=False  # Disable reloader to prevent double browser opening
        )

    except KeyboardInterrupt:
        print(f"\n🛑 Server stopped by user")
        print("Thank you for using Pregnancy Baby Care System!")

    except Exception as e:
        print(f"❌ Error starting server: {e}")
        traceback.print_exc()
        input("Press Enter to exit...")

    finally:
        print("👋 Goodbye!")