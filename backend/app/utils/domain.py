import re

from fastapi import HTTPException, status

_DOMAIN_PATTERN = re.compile(
    r"^(?:https?://)?(?:localhost(?::\d+)?|(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,})(?::\d{1,5})?$",
    re.IGNORECASE,
)


def normalize_domain(domain: str) -> str:
    value = domain.strip().rstrip("/")
    if not value:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Domain cannot be empty",
        )

    host = value
    if value.startswith("http://") or value.startswith("https://"):
        host = value.split("://", 1)[1]

    if not _DOMAIN_PATTERN.match(host):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid domain format. Example: ",
        )

    return f"https://{host}"
