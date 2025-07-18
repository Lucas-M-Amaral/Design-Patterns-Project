class NotFoundError(Exception):
    """Exception raised when a resource is not found."""
    def __init__(self, message="Resource not found"):
        self.message = message
        super().__init__(self.message)


class PermissionDeniedError(Exception):
    """Exception raised when a user does not have permission to perform an action."""
    def __init__(self, message="Permission denied"):
        self.message = message
        super().__init__(self.message)


class ValidationError(Exception):
    """Exception raised for validation errors."""
    def __init__(self, message="Validation error"):
        self.message = message
        super().__init__(self.message)
