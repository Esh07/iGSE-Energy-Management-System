from wtforms.validators import ValidationError


def validate_is_integer(form, field):
    if not isinstance(field.data, int):
        raise ValueError(f"{field.name} must be an integer.")


class IsInteger(object):
    def __init__(self, message=None):
        self.message = message

    def __call__(self, form, field):
        validate_is_integer(form, field)
