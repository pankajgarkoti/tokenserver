import time
import datetime
from django.utils import timezone
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse

import firebase_admin
from firebase_admin import credentials, firestore
from .RtcTokenBuilder import RtcTokenBuilder, Role_Publisher
from .models import APIUser

cred = credentials.Certificate('hearus-4f2fe-firebase-adminsdk-37hja-d20110c311.json')
firebase_admin.initialize_app(cred)

# returns true if uid is in cloud firestore and false otherwise
def does_user_exist_fb(uid):
    try:
        db = firestore.client()
        user = db.collection(u'users').document(uid).get()
        if user.exists:
            return True
        else:
            return False
    
    except Exception as exc:
        print(exc)
        return exc


# returns true if uid is in api db and false otherwise
def does_user_exist_db(uid):
    try:
        user = APIUser.objects.get(pk=uid)
        
        return True

    except APIUser.DoesNotExist:
        return False


# returns token
def get_token(ag_uid, channel):
    app_id = 'e6ff91cb78314130abfbcbcbde53967b'
    cert = '099723247ea34270900a955a6a70d239'
    expire_time = 21600 # 6 hrs
    current_timestamp = int(time.time())
    expire_timestamp = current_timestamp + expire_time
    token = RtcTokenBuilder.buildTokenWithUid(app_id, cert, channel, ag_uid, Role_Publisher, expire_timestamp)

    return token


# returns an agora token valid for 6 hours
def get_token_and_add_to_db(fb_uid, ag_uid, channel):
    try:
        if does_user_exist_db(fb_uid) == True:
            user = APIUser.objects.get(pk=fb_uid)
            
            if user.recent_request() == True:
                token = user.current_token

                return (True, token)
            
            else:
                try:
                    token = get_token(ag_uid, channel)
                    user.current_token = token
                    user.last_successful_request = datetime.datetime.now(tz=timezone.utc)
                    user.save()

                    return (True, token)

                except Exception as exc:
                    token = ''

                    return (False, token)

        else:
            try:
                token = get_token(ag_uid, channel)
                user = APIUser(uid=fb_uid)
                user.current_token = token
                user.last_successful_request = datetime.datetime.now(tz=timezone.utc)
                user.save()

                return (True, token)

            except:
                token = ''

                return (False, token)

    except Exception as exc:
        token = ''

        return (False, token)


def index(request, fb_uid, ag_uid, channel):
    is_user = does_user_exist_fb(fb_uid)
    
    if type(is_user) == bool:
        if is_user == False:
            response_data = {}
            response_data['status'] = 'error'
            response_data['message'] = 'user_not_verified'
            
            return JsonResponse(response_data)
        
        else:
            succeeded, token = get_token_and_add_to_db(fb_uid, ag_uid, channel)
            
            if succeeded == True:
                response_data = {}
                response_data['status'] = 'success'
                response_data['message'] = 'user_verified_and_token_generated_successfully'
                response_data['token'] = token

                return JsonResponse(response_data)
            
            else:
                response_data = {}
                response_data['status'] = 'error'
                response_data['message'] = 'user_verified_but_token_not_generated'

                return JsonResponse(response_data)
    else:
        response_data = {}
        response_data['status'] = 'error'
        response_data['message'] = 'internal_error_while_user_verification'

        return JsonResponse(response_data)