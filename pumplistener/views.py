# from django.shortcuts import render

# Create your views here.
# pumplistener/views.py

from django.http import HttpResponse
import os
from django.http import HttpResponse, JsonResponse
from django.core.management import call_command

# #################################################################################
from django.shortcuts import render # Add this import at the top
from .models import Token           # Add this import at the top
from datetime import datetime, timedelta # Add this import at the top
#####################################################################################

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

def trigger_token_cleanup(request):
    """
    A view that triggers the delete_old_tokens command, secured by a secret key.
    """
    # Get the secret key from the request's query parameters (?secret=...)
    provided_secret = request.GET.get('secret')

    # Get the expected secret key from your environment variables
    expected_secret = os.environ.get('CLEANUP_SECRET_KEY')

    # If the keys don't match or no key is provided, deny access
    if not expected_secret or provided_secret != expected_secret:
        return HttpResponse('Unauthorized', status=401)

    try:
        # Run the management command's logic
        call_command('delete_old_tokens')
        return JsonResponse({'status': 'success', 'message': 'Cleanup command executed.'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

#####################################################################################
def preview_email_report(request):
    """
    A view to render the email_report.html template directly in the browser for testing.
    """
    # Fetch all tokens and their related data points, just like in the email command
    all_tokens = Token.objects.prefetch_related('data_points').order_by('-timestamp')
    
    # Get the current time for the report title
    report_time_str = (datetime.utcnow() + timedelta(hours=5, minutes=30)).strftime('%Y-%m-%d %H:%M:%S IST')

    # Prepare the context data for the template
    context = {
        'tokens': all_tokens,
        'report_time': report_time_str
    }
    
    # Render the template to the browser instead of sending an email
    return render(request, 'pumplistener/email_report.html', context)

#####################################################################################