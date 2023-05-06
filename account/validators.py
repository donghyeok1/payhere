import re

phone_number_regex = re.compile(r"^01[016789]\d{7,8}$")

password_regex = re.compile(
    "^(?=.*[A-Za-z])(?=.*\d)(?=.*[$@$!%*#?&])[A-Za-z\d$@$!%*#?&]{8,}$"
)
