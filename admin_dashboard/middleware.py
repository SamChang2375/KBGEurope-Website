from .models import PageVisit

class StatsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Filter: Zähle keine Admin, Dashboard, Media oder Static Aufrufe
        path = request.path
        if not any(x in path for x in ['/admin/', '/dashboard/', '/media/', '/static/', 'favicon.ico']):
            # Besuch speichern
            if not request.session.session_key:
                request.session.save()

            PageVisit.objects.create(
                path=path,
                session_key=request.session.session_key
            )

        return response