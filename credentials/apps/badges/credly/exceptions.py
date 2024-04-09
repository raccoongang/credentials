class BadgesError(Exception):
    """
    Generic Badges functionality error.
    """

    pass


class CredlyError(BadgesError):
    """
    Badges error that is specific to the Credly backend.
    """

    pass


class CredlyAPIError(CredlyError):
    """
    Credly API errors.
    """

    pass
