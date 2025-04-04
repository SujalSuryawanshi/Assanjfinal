from allauth.account.adapter import DefaultAccountAdapter

class NoConfirmationAdapter(DefaultAccountAdapter):
    def is_open_for_signup(self, request):
        return True  # Skip intermediate confirmation view.
