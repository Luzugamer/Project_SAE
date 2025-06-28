
def dark_mode(request):
    return {
        'dark_mode': request.COOKIES.get('dark_mode', 'false') == 'true'
    }