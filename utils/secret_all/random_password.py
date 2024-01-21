
import random
import string


def reset_password(length: int):
    choice_password = "".join(
        random.choice(string.ascii_letters + string.digits) for _ in range(length)
    )
    return choice_password