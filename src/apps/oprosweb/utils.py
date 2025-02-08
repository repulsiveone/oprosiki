import string
import secrets
from django.core.signing import Signer, BadSignature


# генерация ссылки для закрытия всех сессий пользователя
def generate_secure_link(user_id):
    signer = Signer()
    signed_value = signer.sign(user_id)
    return f'http://127.0.0.1:8000/secure-logout/{signed_value}/'


# генерация кода подтверждения для регистрации пользователя
def generate_confirmation_code(length=6):
    characters = string.ascii_letters + string.digits
    return ''.join(secrets.choice(characters) for _ in range(length))