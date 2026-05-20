class ForceIPMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Tenta pegar o IP do cabeçalho que o Nginx envia
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
            request.META['REMOTE_ADDR'] = ip
        else:
            # Se não tiver, chuta um IP local para o allauth parar de chorar
            request.META.setdefault('REMOTE_ADDR', '127.0.0.1')
        
        response = self.get_response(request)
        return response