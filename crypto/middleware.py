from django.shortcuts import redirect

class RedirectMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if response.status_code == 404:
            # Redirect to the home page if a 404 error occurs
            return redirect('home')  # Replace 'home' with the name or URL of your home page
        return response
