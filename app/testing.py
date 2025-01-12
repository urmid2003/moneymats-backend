# Test environment variable loading
from app.config import settings

print(settings.SECRET_KEY)
print(settings.DATABASE_URL)
print(settings.ACCESS_TOKEN_EXPIRE_MINUTES)
