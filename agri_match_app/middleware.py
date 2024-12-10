from django.shortcuts import redirect

class RoleRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            user = request.user
            if not (user.is_machinery_lister or user.is_operator_lister or user.is_renter):
                if request.path not in ['/register-role/', '/logout/']:  # Exclude specific paths
                    return redirect('register_role')
        return self.get_response(request)
