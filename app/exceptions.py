from fastapi import HTTPException, status


class CustomHTTPException(HTTPException):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = None
    headers = None

    def __init__(self, *args, **kwargs):
        if 'status_code' not in kwargs:
            kwargs['status_code'] = self.status_code
        if 'detail' not in kwargs:
            kwargs['detail'] = self.detail
        if 'headers' not in kwargs:
            kwargs['headers'] = self.headers
        super().__init__(*args, **kwargs)


class UserNotLoggedInException(CustomHTTPException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = 'You must be logged in to view this page'


class ImageNotFoundException(CustomHTTPException):
    status_code = status.HTTP_404_NOT_FOUND
    detail = 'This image does not exist or is private.'


class UserNotFoundException(CustomHTTPException):
    status_code = status.HTTP_404_NOT_FOUND
    detail = 'This user does not exist'


class UsernameTakenException(CustomHTTPException):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = 'This username is already taken'


class EmailTakenException(CustomHTTPException):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = 'This email is already taken'


class CredentialsException(CustomHTTPException):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = 'Incorrect username or password'


class GeneratingImageException(CustomHTTPException):
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    detail = 'An error occurred while generating the image. Please try again'


class ChangingVisibilityImageException(CustomHTTPException):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = 'Failed to change image visibility'


class PlacingLikeException(CustomHTTPException):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = 'This image cannot be liked'
