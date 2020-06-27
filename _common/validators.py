from django.core.validators import RegexValidator


alphanumeric_validator = RegexValidator(r'^[a-zA-Z]*$', 'Only alphanumeric characters are allowed.')
