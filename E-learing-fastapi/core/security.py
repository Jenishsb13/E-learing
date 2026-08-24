from datetime import datetime, timedelta, timezone
from jose import jwt


# Secret key
SECRET_KEY = "your-secret-key-change-this"

# JWT algorithm
ALGORITHM = "HS256"

# Token expiry
ACCESS_TOKEN_EXPIRE_MINUTES = 60


def create_access_token(data: dict):
    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    to_encode.update({
        "exp": expire
    })

    token = jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return token