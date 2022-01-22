import time
from django.http import JsonResponse

import firebase_admin
from firebase_admin import credentials, firestore
from .RtcTokenBuilder import RtcTokenBuilder, Role_Publisher, Role_Subscriber

cred = credentials.Certificate('hearus-4f2fe-firebase-adminsdk-37hja-d20110c311.json')
firebase_admin.initialize_app(cred)
db = firestore.client()


# returns true if uid is in cloud firestore and false otherwise
def does_channel_exist_fb(channel):
    try:
        # db = firestore.client()
        curr = db.collection(u'chatRooms').document(channel).get()

        if curr.exists:
            return True
        else:
            return False

    except Exception as exc:
        # print(exc)
        return exc


# returns token
def get_token(utype, channel, uid):
    app_id = 'e6ff91cb78314130abfbcbcbde53967b'
    cert = '099723247ea34270900a955a6a70d239'
    expire_time = 86400  # 6 hrs
    current_timestamp = int(time.time())
    expire_timestamp = current_timestamp + expire_time
    print(expire_timestamp)
    token = RtcTokenBuilder.buildTokenWithUid(app_id, cert, channel, uid, Role_Publisher, expire_timestamp)

    return token


# generate a token and add it to firebase
def get_token_and_add_to_fb(utype, channel, uid):
    try:
        udict = {}
        udict[utype + '_token'] = get_token(utype, channel, 0)
        udict[utype + '_last_token_request'] = firestore.SERVER_TIMESTAMP

        db = firestore.client()
        db.collection('chatRooms').document(channel).update(udict)

        return True

    except Exception as exc:
        # print(exc)
        return False


def index(request, utype, channel, uid):
    is_channel = does_channel_exist_fb(channel)

    if type(is_channel) == bool:
        if is_channel is False:
            response_data = {}
            response_data['status'] = 'error'
            response_data['message'] = 'channel_not_verified'

            return JsonResponse(response_data)

        else:
            succeeded = get_token_and_add_to_fb(utype, channel, uid)

            if succeeded is True:
                response_data = {}
                response_data['status'] = 'success'
                response_data['message'] = 'channel_verified_and_token_generated_successfully'

                return JsonResponse(response_data)

            else:
                response_data = {}
                response_data['status'] = 'error'
                response_data['message'] = 'channel_verified_but_token_not_generated'

                return JsonResponse(response_data)
    else:
        response_data = {}
        response_data['status'] = 'error'
        response_data['message'] = 'internal_error_while_channel_verification'

        return JsonResponse(response_data)
