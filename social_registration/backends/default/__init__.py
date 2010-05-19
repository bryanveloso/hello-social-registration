class DefaultBackend(object):
    """
    A base backend that, when subclassed, allows various authentication
    workflows to be created.

    """
    def __init__(self):
        self.service = None

    def prepare(self, request, **kwargs):
        """
        Encapsulates logic needed prior to the account backend redirecting the
        user to authenticate with an external service. For example, an OAuth
        service provider will require this step grant the application a
        "request token" needed to proceed further.

        The return value must be:
            1.  A boolean value indicating if the operation succeeded.
            2.  URL that the user will be redirected to.

        """
        raise NotImplementedError('This method must be set by a subclass.')

    def authenticate(self, request, **kwargs):
        """
        Serves as a callback after authenticating with an external service.
        Handles all logic required to handle authentication with the
        application, creating an ``Association`` object and/or ``User`` object
        depending on if the given user already exists.

        The return value must be:
            1.  An instance referring to the authenticated user.

        """
        raise NotImplementedError('This method must be set by a subclass.')

    def deauthenticate(self, request, **kwargs):
        """
        Invoked when a user chooses to disable the link between the site and a
        previously authenticated external account including any extra logic
        that needs to be called at that time.

        The return value must be:
            1.  A boolean value indicating if the operation succeeded.

        """
        raise NotImplementedError('This method must be set by a subclass.')

    def create_user(self, request, user, **kwargs):
        """
        If after authenticating, the requesting user does not have an account
        or association in the database, any logic contained here will be
        executed to create that new ``User`` object along with the necessary
        ``Association`` reference.

        """
        raise NotImplementedError('This method must be set by a subclass.')

    def link_user(self, request, user, **kwargs):
        """
        If after authenticating, the requesting user does have an account in
        the database but NOT an association, any logic contained here will be
        executed to create an ``Association`` reference.

        """
        raise NotImplementedError('This method must be set by a subclass.')

    def grant_user(self, request, user, **kwargs):
        """
        If after authenticating, the requesting user has both an account and
        an association in the database, any logic contained here will be
        executed to log the user in.

        """
        raise NotImplementedError('This method must be set by a subclass.')

    def post_authentication_redirect(self, request):
        """
        Return the name of the URL to redirect to after a successful login.

        """
        return ('site-home', (), {})

    def post_deauthentication_redirect(self, request):
        """
        Return the name of the URL to redirect to after a successful logout.

        """
        return ('login', (), {})


