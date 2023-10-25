from rest_framework.authentication import TokenAuthentication

class TokenAuthGet(TokenAuthentication):
    """
    Extends the class to support token as "key" in a GET Query Parameter.
    Supports standard method in header as a default.
    """
    def authenticate(self, request):
        token = request.query_params.get("key", False)

        if token and "HTTP_AUTHORIZATION" not in request.META:
            return self.authenticate_credentials(token)
        else:
            return super().authenticate(request)