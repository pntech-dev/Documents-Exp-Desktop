import string


class FieldValidator:
    @staticmethod
    def validate_email(email: str) -> bool:
        """Simple email validation method."""

        if "@" not in email or email.count("@") >= 2:
            return False

        if email.startswith("@") or email.endswith("@"):
            return False

        local_part, domain_part = email.split("@")

        if not local_part or not domain_part:
            return False

        # Local part verification
        if len(local_part) > 64:
            return False

        if local_part.startswith(".") or local_part.endswith("."):
            return False

        if ".." in local_part:
            return False

        # Domain part verification
        if len(domain_part) > 255:
            return False

        if "." not in domain_part:
            return False
        
        if domain_part.startswith(".") or domain_part.endswith("."):
            return False

        if ".." in domain_part:
            return False

        return True
    

    @staticmethod
    def validate_password(password: str) -> bool:
        """Simple password validation method."""

        # Password length
        if len(password) < 8:
            return False
        
        # Minimum one symbol is digit
        if not any(char.isdigit() for char in password):
            return False
        
        # Minimum one symbol is uppercase
        if not any(char.isupper() for char in password):
            return False
        
        # Minimum one symbol is lowercase
        if not any(char.islower() for char in password):
            return False
        
        # Minimum one symbol is special character
        if not any(char in string.punctuation for char in password):
            return False

        return True

    @staticmethod
    def get_password_validation_status(password: str) -> list[dict]:
        """Returns a list of validation rules and their status."""
        return [
            {"text": "Минимум 8 символов", "valid": len(password) >= 8},
            {"text": "Один спецсимвол", "valid": any(char in string.punctuation for char in password)},
            {"text": "Одна цифра", "valid": any(char.isdigit() for char in password)},
            {"text": "Одна заглавная буква", "valid": any(char.isupper() for char in password)},
            {"text": "Одна строчная буква", "valid": any(char.islower() for char in password)},
        ]