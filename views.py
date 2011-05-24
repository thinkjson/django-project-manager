from django.shortcuts import render_to_response

def handle_error(request):
    return render_to_response('400.html', {"request": request})