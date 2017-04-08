from oauth2client import client, crypt

GOOGLE_CLIENT_ID_ANDROID = '1079439277366-nrb4v40jbmgismg5uf01tc37c1b1gjv5.apps.googleusercontent.com'
GOOGLE_CLIENT_ID_ANDROID_DEBUG = '1079439277366-rki3ghhgvug6cudh3jo0cug3jkcghm4v.apps.googleusercontent.com'
GOOGLE_CLIENT_ID_SERVER = '1079439277366-1h6iqgbsbarooaduafnf8pf5gf82t7h0.apps.googleusercontent.com'


def google_validate_token(token: str):
    try:
        # Or, if multiple clients access the backend server:
        idinfo = client.verify_id_token(token, None)
        if idinfo['azp'] not in [GOOGLE_CLIENT_ID_ANDROID, GOOGLE_CLIENT_ID_ANDROID_DEBUG]:
            raise crypt.AppIdentityError("Unrecognized client.")

        if idinfo['aud'] != GOOGLE_CLIENT_ID_SERVER:
            raise crypt.AppIdentityError("Wrong audience.")

        if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
            raise crypt.AppIdentityError("Wrong issuer.")
    except crypt.AppIdentityError as e:
        print(e)
        # Invalid token
        return None
    return idinfo
