class PublicationValidationError(Exception):
    ###
    #  class for publication validation errors
    # ###
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code


class FeedbackValidationError(Exception):
    ###
    #  class for feedback validation errors
    # ###
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code


class WorkflowError(Exception):
    ###
    #  class for feedback validation errors
    # ###
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code


class AuthError(Exception):
    ###
    # class for Authentification errors
    ###
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code
