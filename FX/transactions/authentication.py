from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
import jwt  # Use the correct JWT library

class JWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        # Look for the Authorization header
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return None  # No token provided, authentication fails

        token = auth_header.split(' ')[1]  # Extract the token part
        try:
            # Decode the token with the secret key
            payload = jwt.decode(token, 'your_secret_key', algorithms=['HS256'])  # Replace with your actual secret key
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Token has expired')
        except jwt.InvalidTokenError:
            raise AuthenticationFailed('Invalid token')

        # Optionally, fetch the user from the payload
        # Assuming 'user_id' is in your JWT payload
        user = YourUserModel.objects.get(id=payload['user_id'])
        return (user, token)  # Return user and token if successful
