import pytest

from utils.fields_validators import FieldValidator



class TestValidators:
    @pytest.mark.parametrize(
            "email_input, expected", [
                ("mail@gmail.com", True),
                ("mailgmail.com", False),
                ("mail@@gmail.com", False),
                ("mail@", False),
                ("@gmail.com", False),
                ("mail-mail-mail-mail-mail-mail-mail-mail-mail-mail-mail-mail-mail-mail@gmail.com", False),
                (".mail@gmail.com", False),
                ("mail.@gmail.com", False),
                ("ma..il@gmail.com", False),
                ("mail@gmailgmailgmailgmailgmailgmailgmailgmailgmailgmailgmailgmailgmailgmailgmailgmailgmailgmailgmailgmailgmailgmailgmailgmailgmailgmailgmailgmailgmailgmailgmailgmailgmailgmailgmailgmailgmailgmailgmailgmailgmailgmailgmailgmailgmailgmailgmailgmailgmailgmailgmailgmail.com", False),
                ("mail@gmailcom", False),
                ("mail@gmail.", False),
                ("mail@.gmail.com", False),
                ("mail@gmail..com", False),
            ]
    )
    def test_email_validator(self, email_input, expected):
        assert FieldValidator.validate_email(email_input) == expected


    @pytest.mark.parametrize(
            "password_input, expected", [
                ("1234567", False),
                ("qwertyui", False),
                ("1qwertyu", False),
                ("1QWERTYU", False),
                ("1Qwertyu", False),
                ("-1Qwerty", True),
            ]
    )
    def test_password_validator(self, password_input, expected):
        assert FieldValidator.validate_password(password_input) == expected

    @pytest.mark.parametrize(
        "password_input, expected_validity", [
            ("-1Qwerty", [True, True, True, True, True]),  # Correct password
            ("1Qwerty", [False, False, True, True, True]), # Too short (7), have not special characters
            ("password", [True, False, False, False, True]), # Have not special characters, digits, upper case letter
            ("PASSWORD", [True, False, False, True, False]), # Have not special characters, digits, lower case letter
            ("12345678", [True, False, True, False, False]), # Have not special characters, letters
            ("!@#$%", [False, True, False, False, False]),   # Too short, only special characters
            ("", [False, False, False, False, False]),       # Empty
        ]
    )
    def test_get_password_validation_status(self, password_input, expected_validity):
        status = FieldValidator.get_password_validation_status(password_input)
        validity = [item["valid"] for item in status]
        assert validity == expected_validity
