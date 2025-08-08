#!/usr/bin/env python3
"""
Simple HTTP Server for Data Classification Research Web Application

This server provides a local development environment for the research data visualization web app.
It serves static files and can be extended to handle API requests for file operations.

Usage:
    python server.py [port]

Default port: 8000
"""

import http.server
import socketserver
import os
import sys
import json
from urllib.parse import urlparse, parse_qs
import mimetypes

class ResearchDataHandler(http.server.SimpleHTTPRequestHandler):
    """Custom HTTP request handler for the research data web application."""
    
    def __init__(self, *args, **kwargs):
        # Set up MIME types for better file serving
        mimetypes.add_type('application/javascript', '.js')
        mimetypes.add_type('text/css', '.css')
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        """Handle GET requests."""
        parsed_url = urlparse(self.path)
        path = parsed_url.path
        
        # Handle API endpoints
        if path.startswith('/api/'):
            self.handle_api_request(path, parsed_url.query)
            return
        
        # Serve static files
        super().do_GET()
    

    
    def handle_api_request(self, path, query):
        """Handle API requests for file operations."""
        try:
            if path == '/api/files':
                self.handle_files_api()
            elif path == '/api/file-content':
                self.handle_file_content_api(query)
            else:
                self.send_error(404, "API endpoint not found")
        except Exception as e:
            self.send_error(500, f"Internal server error: {str(e)}")
    
    def handle_files_api(self):
        """Return list of available files."""
        try:
            files = []
            august_dir = 'August'
            
            if os.path.exists(august_dir):
                for filename in os.listdir(august_dir):
                    if filename.endswith(('.csv', '.txt')):
                        file_path = os.path.join(august_dir, filename)
                        file_size = os.path.getsize(file_path)
                        
                        # Extract country code from filename
                        if filename.startswith('done_processed_') and filename.endswith('_data.csv'):
                            country_code = filename[15:-9]  # Extract country code
                            file_type = 'csv'
                            records = self.count_csv_records(file_path)
                        elif filename.startswith('done_processed_') and filename.endswith('_data_stats.txt'):
                            country_code = filename[15:-14]  # Extract country code
                            file_type = 'stats'
                            records = None
                        else:
                            continue
                        
                        files.append({
                            'countryCode': country_code,
                            'fileName': filename,
                            'fileType': file_type,
                            'filePath': file_path,
                            'size': round(file_size / 1024, 1),  # Convert to KB
                            'records': records
                        })
            
            self.send_json_response(files)
            
        except Exception as e:
            self.send_error(500, f"Error reading files: {str(e)}")
    
    def handle_file_content_api(self, query):
        """Return content of a specific file."""
        try:
            params = parse_qs(query)
            file_path = params.get('path', [None])[0]
            
            if not file_path or not os.path.exists(file_path):
                self.send_error(404, "File not found")
                return
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            self.send_json_response({
                'content': content,
                'filename': os.path.basename(file_path)
            })
            
        except Exception as e:
            self.send_error(500, f"Error reading file: {str(e)}")
    
    def count_csv_records(self, file_path):
        """Count records in a CSV file (excluding header)."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                return max(0, len(lines) - 1)  # Subtract header
        except:
            return None
    
    def send_json_response(self, data):
        """Send JSON response."""
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))
    
    def log_message(self, format, *args):
        """Custom logging to show requests."""
        print(f"[{self.log_date_time_string()}] {format % args}")

def main():
    """Main function to start the server."""
    # Get port from environment variable (for Railway) or command line argument
    port = int(os.environ.get('PORT', 8000))
    
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            print("Invalid port number. Using default port 8000.")
    
    # Change to the directory containing this script
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    with socketserver.TCPServer(("", port), ResearchDataHandler) as httpd:
        print(f"🚀 Research Data Web Application Server")
        print(f"📍 Serving at: http://localhost:{port}")
        print(f"📁 Root directory: {os.getcwd()}")
        print(f"📊 Data directory: {os.path.join(os.getcwd(), 'August')}")
        print("\n✨ Features:")
        print("   • Static file serving")
        print("   • API endpoints for file operations")
        print("   • CSV and stats file handling")
        print("   • Cross-origin resource sharing enabled")
        print("\n🛑 Press Ctrl+C to stop the server")
        print("=" * 50)
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n🛑 Server stopped by user")
            httpd.shutdown()

if __name__ == "__main__":
    main()
