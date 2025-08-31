# from django.shortcuts import render

# Create your views here.
# pumplistener/views.py

from django.http import HttpResponse
import os

# This is the name of the log file you defined in listener.py
LOG_FILE = 'token_log.txt'

def view_log_file(request):
    """
    A simple view to read and display the contents of the log file.
    """
    log_content = f"Log file '{LOG_FILE}' not found."

    try:
        # We use .read() to get the whole file content
        with open(LOG_FILE, 'r', encoding='utf-8') as f:
            log_content = f.read()
    except FileNotFoundError:
        # The message above will be used if the file doesn't exist yet
        pass
    except Exception as e:
        log_content = f"An error occurred while reading the file: {e}"

    # We wrap the content in <pre> tags to preserve line breaks and spacing
    return HttpResponse(f"<pre>{log_content}</pre>", content_type="text/plain; charset=utf-8")