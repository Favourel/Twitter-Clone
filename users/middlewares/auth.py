from django.shortcuts import redirect


def LogoutCheckMiddleware(get_response):
    def middleware(request):
        if request.user.is_authenticated:
            return redirect('blog_home')
        return get_response(request)
    return middleware