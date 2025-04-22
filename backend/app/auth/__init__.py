import firebase_admin
from firebase_admin import credentials, auth
from .middleware import get_current_user

# Initialize Firebase Admin SDK only if not already initialized
try:
    firebase_admin.get_app()
except ValueError:
    cred = credentials.Certificate("service-account.json")
    firebase_admin.initialize_app(cred)

__all__ = ['get_current_user'] 