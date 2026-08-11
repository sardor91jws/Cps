import secrets
import string
from utils.logger import setup_logger

logger = setup_logger(__name__)

def generate_password(
    length: int = 16,
    use_upper: bool = True,
    use_lower: bool = True,
    use_digits: bool = True,
    use_symbols: bool = True,
) -> str:
    if length < 4 or length > 128:
        raise ValueError("Length must be between 4 and 128")

    alphabet = ""
    if use_upper:
        alphabet += string.ascii_uppercase
    if use_lower:
        alphabet += string.ascii_lowercase
    if use_digits:
        alphabet += string.digits
    if use_symbols:
        alphabet += "!@#$%^&*()-_=+[]{}|;:,.<>?"

    if not alphabet:
        raise ValueError("At least one character set must be enabled")

    # Ensure at least one character from each selected set
    password_chars = []
    if use_upper:
        password_chars.append(secrets.choice(string.ascii_uppercase))
    if use_lower:
        password_chars.append(secrets.choice(string.ascii_lowercase))
    if use_digits:
        password_chars.append(secrets.choice(string.digits))
    if use_symbols:
        password_chars.append(secrets.choice("!@#$%^&*()-_=+[]{}|;:,.<>?"))

    remaining = length - len(password_chars)
    password_chars.extend(secrets.choice(alphabet) for _ in range(remaining))
    secrets.SystemRandom().shuffle(password_chars)

    result = "".join(password_chars)
    logger.info(f"Password generated, length={length}")
    return result
