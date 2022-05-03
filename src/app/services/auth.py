import requests, json
from fastapi import (Depends, HTTPException, status, )
from fastapi.security import OAuth2PasswordBearer
from .. import (models)
from ..settings import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=settings.bl_auth_url)


def get_current_user(token: str = Depends(oauth2_scheme)) -> models.User:
    return AuthService.verify_token(token)


class AuthService:

    @classmethod
    def get_service_token(cls, exception: HTTPException):
        data = {"username": settings.bl_auth_user, "password": settings.bl_auth_password}
        headers = {"accept": "application/json", "Content-Type": "application/x-www-form-urlencoded"}
        response = requests.post(settings.bl_auth_url, data=data, headers=headers)
        if response.status_code == 200:
            try:
                data = json.loads(response.text)
                token = data['access_token']
                return token
            except TypeError:
                raise exception
        return None

    @classmethod
    def get_user(cls, service_token: str, user_token: str, exception: HTTPException):
        headers = {"accept": "application/json", "Authorization": "Bearer " + service_token}
        response = requests.get(settings.bl_auth_verify_url + '?token=' + user_token, headers=headers)
        if response.status_code == 200:
            try:
                data = json.loads(response.text)
                if data['status'] is not True:
                    raise exception
            except TypeError:
                raise exception
            return data
        return None

    @classmethod
    def verify_token(cls, user_token: str) -> models.User:
        exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Could not validate credentials',
            headers={'WWW-Authenticate': 'Bearer'},
        )
        service_token = cls.get_service_token(exception)
        return cls.get_user(service_token, user_token, exception)
