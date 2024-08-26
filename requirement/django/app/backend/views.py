import os
import json
from django.urls import reverse
from django.conf import settings
from .models import Notification, BlockedList
from django.shortcuts import render, redirect
from django.middleware.csrf import get_token
from django.contrib.sessions.models import Session
from django.http import JsonResponse, HttpResponse
from django.contrib.auth import authenticate, login, logout, get_user_model
from authlib.integrations.requests_client import OAuth2Session
from django.contrib.auth.hashers import make_password

import io
import jwt
import json
import pyotp
import qrcode
from jwt.exceptions import ExpiredSignatureError
from django.test import Client
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken

class CustomRefreshToken(RefreshToken):
    @property
    def access_token(self):
        token = super().access_token
        CustomUser = get_user_model()
        # Add custom claims
        token['user_id'] = self['user_id']
        user = CustomUser.objects.get(id=self['user_id'])
        token['username'] = user.username
        token['score'] = user.score
        token['is_online'] = user.is_online
        token['avatar'] = user.avatar.url if user.avatar else None

        return token

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        token['user_id'] = user.id
        token['username'] = user.username
        token['score'] = user.score
        token['is_online'] = user.is_online
        token['avatar'] = user.avatar.url if user.avatar else None

        print(token)
        return token

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer  

def index(request):   
    # context = {
    #     'access': request.session['access_token'],
    #     'refresh': request.session['refresh_token']
    # }
    # return render(request, 'backend/login.html', {'token': context})
    return render(request, 'backend/login.html')


def two_factor_auth(request):
    return render(request, 'backend/two_factor_auth.html')

def get_csrf_token_and_session_id(request):
    csrf_token = get_token(request)
    session_id = request.session.session_key
    return JsonResponse({'csrf_token': csrf_token, 'sessionid': session_id}, status=200)

def user_register(request):
    return render(request, 'backend/register.html')

def getUserProfile(User, user, owner, func):
    blocker = User.objects.get(id=user.id)
    try:
        if func == 'blocklist':
            if BlockedList.objects.filter(blocked=owner, blocker=blocker).exists():
                return
        else:
            if BlockedList.objects.filter(blocked=owner, blocker=blocker).exists() or BlockedList.objects.filter(blocked=blocker, blocker=owner).exists():
                return
    except BlockedList.DoesNotExist:
        pass
    avatar_url = str(user.avatar)
    if not avatar_url.startswith("https://cdn.intra.42.fr"):
        avatar_url = f'{settings.MEDIA_URL}{user.avatar}'
    return( {
        'id': user.id,
        'username': user.username,
        'avatar': avatar_url,
        'is_online': user.is_online
    })

def getUserNotification(User, noti, request):
    try:
        user = User.objects.get(id=noti.sender.id)
        blockedlist = BlockedList.objects.get(blocked=request.user, blocker=user)
        if blockedlist:
            return None
    except BlockedList.DoesNotExist:
        pass 
    except User.DoesNotExist:
        return ({'error': 'User not found'})
    avatar_url = str(user.avatar)
    if not avatar_url.startswith("https://cdn.intra.42.fr"):
        avatar_url = f'{settings.MEDIA_URL}{user.avatar}'
    return( {
        'noti_id': noti.id,
        'user_id': user.id,
        'username': user.username, 
        'avatar': avatar_url,
        'is_online': user.is_online
    })

def get_jwt_token(username, password):
    client = Client()
    response = client.post('/api/token/', 
                           json.dumps({
                                        'username': username, 
                                        'password': password
                            }), 
                            content_type='application/json')
    print("Response Status Code:", response.status_code)
    print("Response Content:", response.content)
    
    token = response.json()
    return token

def get_token_for_authenticated_user(request):
    if request.user.is_authenticated:
        refresh = CustomRefreshToken.for_user(request.user)
        return ({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        })

def jwt_manual_validate(request):
    try:
        auth = JWTAuthentication()
        header = auth.get_header(request)
        if header is None:
            return ({'error': 'JWT token is missing'})
            # return JsonResponse({'error': 'JWT token is missing'}, status=401)
        raw_token = auth.get_raw_token(header)
        jwt.decode(raw_token, settings.SECRET_KEY, algorithms=[settings.SIMPLE_JWT['ALGORITHM']])
    except ExpiredSignatureError:
        return ({'error': 'Token has expired'})
        # return JsonResponse({'error': 'Token has expired'}, status=401)
    except Exception:
        return ({'error': 'Authentication failed'})
        # return JsonResponse({'error': 'Authentication failed'}, status=401)
    return

def generate_totp_secret(request):
    if request.method == 'GET':
        if request.user.is_authenticated:
            user = request.user
            if user.totp_secret is None:
                #User login to website first time
                totp_secret = pyotp.random_base32()
                user.totp_secret = totp_secret
                user.save()
            else:
                totp_secret = user.totp_secret
            totp_uri = pyotp.totp.TOTP(totp_secret).provisioning_uri(
                user.username, issuer_name="Transcendence"
            )

            qr = qrcode.make(totp_uri)
            stream = io.BytesIO() #creates an in-memory binary stream to store the QR code image
            qr.save(stream, 'PNG') #saves the QR code image into the stream in PNG format.
            stream.seek(0) #moves the stream pointer to the beginning, preparing it for reading.
            return HttpResponse(stream.getvalue(), content_type='image/png')
        else:
            return JsonResponse({'error': 'User is not logged in'}, status=401)
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)

def verify_totp(request):
    if request.method == 'POST':
        if request.user.is_authenticated:
            try:
                data = json.loads(request.body)
                otp = data.get('otp')
            except json.JSONDecodeError :
                return JsonResponse({'error':"Invalid OTP. Please try again."}, status=401)
            user = request.user
            totp = pyotp.TOTP(user.totp_secret)
            if totp.verify(otp):
                jwt_token = get_token_for_authenticated_user(request)
                request.session['access_token'] = jwt_token['access']
                request.session['refresh_token'] = jwt_token['refresh']
                access_token = request.session['access_token']
                refresh_token = request.session['refresh_token']
                user.is_online = True
                user.save()
                return JsonResponse({
                                'message': 'Login success',
                                'owner_id': user.id,
                                'refresh': refresh_token,
                                'access': access_token,
                                }, status=200)
                # return redirect ('backend:index')
            else:
                logout(request)
                return JsonResponse({'error':"Invalid OTP. Please try again."}, status=401)
        else:
            return JsonResponse({'error': 'User is not logged in'}, status=401)
    return JsonResponse({'error': 'Method not allowed'}, status=405)

def jwt_and_auth_validate(request, owner_id):
    if settings.ALLOW_API_WITHOUT_JWT == False:
        err = jwt_manual_validate(request)
        if err is not None:
            return err
    if settings.ALLOW_API_WITHOUT_AUTH == False:
        if request.user.id != int(owner_id):
            return ({'error': 'Session mismatch'})
    return

#1.1 POST /api/auth/login
def UserLogin(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')

        if request.user.is_authenticated:
            return redirect ("frontend:dashboard")
            # return JsonResponse({'error': 'User is already logged in'}, status=400)
        user = authenticate(request, username=username, password=password)
        if user is not None:
            if settings.ALLOW_API_WITHOUT_JWT == False:
                login(request, user)
                user.save()
                return JsonResponse({'message': '2fa'}, status=200)
                # return redirect (two_factor_auth) #change to message redirect to 2fa
            else:
                login(request, user)
                user.is_online = True
                user.save()
                # return redirect ("frontend:dashboard")
                return JsonResponse({
                            'message': 'Login success',
                            'owner_id': user.id
                            }, status=200)
        else:
            return JsonResponse({'error': 'Invalid username or password'}, status=401)    
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
#1.2 POST /api/auth/register
def UserRegister(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        avatar = request.FILES.get('avatar')
        
        if not username or not password:
            return JsonResponse({'error': 'Both username and password are required'}, status=400)
        User = get_user_model()
        if User.objects.filter(username=username).exists():
            return JsonResponse({'error': 'Username already exists'}, status=400)

        user = User.objects.create_user(username=username, password=password)
        if avatar:
            user.avatar = avatar
        login(request, user)
        user.is_online = True
        user.save()
        
        return JsonResponse({'message': 'Create user success'}, status=201)
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)

#1.3 POST /api/auth/logout
def UserLogout(request):
    if request.method == 'POST':
        if request.user.is_authenticated:
            if settings.ALLOW_API_WITHOUT_JWT == False:
                err = jwt_manual_validate(request)
                if err is not None:
                    return JsonResponse(err, status=401)
            User = get_user_model()
            user = User.objects.get(id=request.user.id)
            user.is_online = False
            user.save()
            logout(request)
            return JsonResponse({'message': 'Logout success'}, status=200)
        else:
            return JsonResponse({'error': 'User is not logged in'}, status=401)
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)

#1.4 POST /api/auth/login42
def UserLogin42(request):
    client = OAuth2Session(settings.CLIENT_ID, redirect_uri=settings.REDIRECT_URI)
    authorization_url, state = client.create_authorization_url(settings.AUTHORIZATION_URL)
    request.session['oauth_state'] = state
    return redirect(authorization_url)

def callback(request):
    if 'oauth_token' in request.session:
        return redirect ("frontend:dashboard")
        # return JsonResponse({'error': 'User is already logged in'}, status=400)
    
    stored_state = request.session.get('oauth_state')
    received_state = request.GET.get('state')
    if stored_state != received_state:
        return JsonResponse({'error': 'State mismatch. Possible CSRF attack.'}, status=400)
    
    User = get_user_model()
    client = OAuth2Session(settings.CLIENT_ID, 
                           state=request.session['oauth_state'], 
                           redirect_uri=settings.REDIRECT_URI
                           )
    # Need to fetch access token for get 42User's Profile
    request.session['oauth_token'] = client.fetch_token(settings.TOKEN_URL, 
                               client_secret=settings.CLIENT_SECRET, 
                               authorization_response=request.build_absolute_uri()
                               )
    user_info = client.get(settings.PROFILE_URL).json()
    username = user_info['login']
    user_id = user_info['id']
    avatar = user_info['image']['link']
    hash_password = make_password(f'{username}{user_id}')

    if User.objects.filter(username=username).exists():
        user = User.objects.get(username=username)
        user.backend = 'django.contrib.auth.backends.ModelBackend'
    else:
        user = User.objects.create_user(username=username, password=hash_password, avatar=avatar)
    if settings.ALLOW_API_WITHOUT_JWT == False:
        login(request, user)
        user.save()
        # return JsonResponse({'message': '2fa'}, status=200)
        return redirect (two_factor_auth)
    else:
        login(request, user)
        user.is_online = True
        user.save()
        return redirect ("frontend:dashboard")

#2.1.1 /api/users/:user_id/:owner_id/profile
def UserProfile(request, user_id, owner_id):
    if request.method == 'GET':
            # if request.user.is_authenticated:
            if settings.ALLOW_API_WITHOUT_AUTH or request.user.is_authenticated:
                if request.user.is_authenticated or settings.ALLOW_API_WITHOUT_AUTH:
                    if settings.ALLOW_API_WITHOUT_JWT == False:
                        err = jwt_and_auth_validate(request, owner_id)
                        if err is not None:
                            return JsonResponse(err, status=401)
                    User = get_user_model()
                    try:
                        user = User.objects.get(id = user_id)
                        owner = User.objects.get(id = owner_id)
                    except User.DoesNotExist:
                        return JsonResponse({'error': 'User not found'}, status=404)     
                    # avatar_url = f'{settings.MEDIA_ROOT}/{user.avatar}'
                    avatar_url = str(request.user.avatar)
                    if not avatar_url.startswith("https://cdn.intra.42.fr"):
                        avatar_url = f'{settings.MEDIA_URL}{request.user.avatar}'
                        if not (avatar_url and os.path.exists(avatar_url)):
                            return JsonResponse({'error': 'Not Found the avatar file'}, status=404) 
                    payload = getUserProfile(User=User, user=user, owner=owner, func='general')
                    if payload is None:
                        return JsonResponse({'error': 'User was blocked'}, status=401)
                    return JsonResponse(payload, status=200, safe=False)
            else:
                return JsonResponse({'error': 'User is not logged in'}, status=401)  
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)

#2.1.2 POST /api/users/update_avatar
def UpdateUserAvatar(request):
    if request.method == 'POST':
        # if request.user.is_authenticated:
        if settings.ALLOW_API_WITHOUT_AUTH or request.user.is_authenticated:
            if request.user.is_authenticated or settings.ALLOW_API_WITHOUT_AUTH:
                user_id = request.POST.get('user_id')
                if settings.ALLOW_API_WITHOUT_JWT == False:
                    err = jwt_and_auth_validate(request, user_id)
                    if err is not None:
                        return JsonResponse(err, status=401)
                User = get_user_model()
                try:
                    user = User.objects.get(id = user_id)
                except User.DoesNotExist:
                    return JsonResponse({'error': 'User not found'}, status=404)
                avatar = request.FILES.get('avatar')
                if avatar:
                    old_avatar_path = user.avatar
                    if old_avatar_path != f'avatars/default.png' and os.path.isfile(f'{settings.MEDIA_ROOT}/{old_avatar_path}'):
                        os.remove(f'{settings.MEDIA_ROOT}/{old_avatar_path}')
                    user.avatar = avatar
                    user.save()
                    return JsonResponse({
                            'message': 'User update avatar success',
                            'avatar_url': user.avatar.url
                            }, status=201)

                else:
                    return JsonResponse({'error': 'Not Found the avatar file'}, status=404) 
        else:
            return JsonResponse({'error': 'User is not logged in'}, status=401)
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)

#2.1.5 POST /api/users/block
def BlockUser(request):
    if request.method == 'POST':
            data = json.loads(request.body)
            owner_id = data.get('owner_id')
            user_id = data.get('user_id')
            # if request.user.is_authenticated:
            if settings.ALLOW_API_WITHOUT_AUTH or request.user.is_authenticated:
                if request.user.is_authenticated or settings.ALLOW_API_WITHOUT_AUTH:
                    if settings.ALLOW_API_WITHOUT_JWT == False:
                        err = jwt_and_auth_validate(request, owner_id)
                        if err is not None:
                            return JsonResponse(err, status=401)
                    if (request.user.id == user_id):
                        return JsonResponse({'error': 'Users try to block themselves'}, status=400)
                    User = get_user_model()
                    try:    
                        blocker = User.objects.get(id=owner_id)
                        blocked = User.objects.get(id=user_id)
                    except User.DoesNotExist:
                        return JsonResponse({'error': 'User not found'}, status=404)  
                    try:
                        BlockedList.objects.get(blocker=blocked, blocked=blocker)
                        return JsonResponse({'error': 'Users is blocked now'}, status=400)
                    except BlockedList.DoesNotExist:
                        pass
                    try:
                        BlockedList.objects.get(blocker=blocker, blocked=blocked)
                        return JsonResponse({'error': 'Users is blocker now'}, status=400)
                    except BlockedList.DoesNotExist:
                        blockedlist = BlockedList(blocker=blocker, blocked=blocked)
                        blockedlist.save()
                        return JsonResponse({'message': 'Block user success'}, status=200)
            else:
                return JsonResponse({'message': 'User is not logged in'}, status=401)
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
#2.1.7 POST /api/users/unblock
def UnblockUser(request):
    if request.method == 'POST':
            data = json.loads(request.body)
            owner_id = data.get('owner_id')
            user_id = data.get('user_id')
            # if request.user.is_authenticated:
            if settings.ALLOW_API_WITHOUT_AUTH or request.user.is_authenticated:
                if request.user.is_authenticated or settings.ALLOW_API_WITHOUT_AUTH:
                    if settings.ALLOW_API_WITHOUT_JWT == False:
                        err = jwt_and_auth_validate(request, owner_id)
                        if err is not None:
                            return JsonResponse(err, status=401)
                    if (request.user.id == user_id):
                        return JsonResponse({'error': 'Users try to unblock themselves'}, status=400) 
                    User = get_user_model()
                    try:
                        blocker = User.objects.get(id=request.user.id)
                        blocked = User.objects.get(id=user_id)
                    except User.DoesNotExist:
                        return JsonResponse({'error': 'User not found'}, status=404)
                    try:
                        BlockedList.objects.get(blocker=blocked, blocked=blocker)
                        return JsonResponse({'error': 'Blocked users cannot unblock blocker'}, status=400)
                    except BlockedList.DoesNotExist:
                        pass
                    try:
                        blocked_list = BlockedList.objects.get(blocker=blocker, blocked=blocked)
                        blocked_list.delete()
                        return JsonResponse({'message': 'Unblock success'}, status=200)
                    except BlockedList.DoesNotExist:
                        return JsonResponse({'error': 'BlockedList not found'}, status=404)
            else:
                return JsonResponse({'message': 'User is not logged in'}, status=401)
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)

#2.1.6 GET: /api/users/user_id/blocked_list
def GetUserBlockedList(request, user_id):
    if request.method == 'GET':
        #    if request.user.is_authenticated:
        if settings.ALLOW_API_WITHOUT_AUTH or request.user.is_authenticated:
            if request.user.is_authenticated or settings.ALLOW_API_WITHOUT_AUTH:
                if settings.ALLOW_API_WITHOUT_JWT == False:
                        err = jwt_and_auth_validate(request, user_id)
                        if err is not None:
                            return JsonResponse(err, status=401)
                User = get_user_model()
                try:
                    user = User.objects.get(id=user_id)
                except User.DoesNotExist:
                    return JsonResponse({'error': 'User not found'}, status=404)
                try:
                    blocked_set = BlockedList.objects.filter(blocker=user)
                except BlockedList.DoesNotExist:
                    return JsonResponse({'error': 'Blockedlist not found'}, status=404)
                blocked_list = [getUserProfile(User=User, user=blockeds.blocked, owner=user, func='blocklist') for blockeds in blocked_set]
                if len(blocked_list) == 0:
                    return JsonResponse({'error': 'BlockedList not found'}, status=404)
                return JsonResponse(blocked_list, status=200 , safe=False)
        else:
            return JsonResponse({'error': 'User is not logged in'}, status=401)
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)

#2.2.1 GET /api/users/user_id/friends
def GetAllFriends(request, user_id):
    if request.method == 'GET':
            # if request.user.is_authenticated:
            if settings.ALLOW_API_WITHOUT_AUTH or request.user.is_authenticated:
                if request.user.is_authenticated or settings.ALLOW_API_WITHOUT_AUTH:
                    if settings.ALLOW_API_WITHOUT_JWT == False:
                        err = jwt_and_auth_validate(request, user_id)
                        if err is not None:
                            return JsonResponse(err, status=401)
                    User = get_user_model()
                    try:
                        user = User.objects.get(id=user_id)
                    except User.DoesNotExist:
                        return JsonResponse({'error': 'User not found'}, status=404)
                    friend_set = user.friend.all()
                    friends = []
                    for friend in friend_set:
                        profile = getUserProfile(User=User, user=friend, owner=user, func='general')
                        if profile is not None:
                            friends.append(profile)
                    if len(friends) == 0:
                        return JsonResponse({'error': 'Friends not found'}, status=404)
                    return JsonResponse(friends, status=200 , safe=False)
            else:
                return JsonResponse({'error': 'User is not logged in'}, status=401)
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)

#2.2.2 GET: /api/users/user_id/friends/find_new
def FindNewFriends(request, user_id):
    if request.method == 'GET':
            # if request.user.is_authenticated:
            if settings.ALLOW_API_WITHOUT_AUTH or request.user.is_authenticated:
                if request.user.is_authenticated or settings.ALLOW_API_WITHOUT_AUTH:
                    if settings.ALLOW_API_WITHOUT_JWT == False:
                        err = jwt_and_auth_validate(request, user_id)
                        if err is not None:
                            return JsonResponse(err, status=401)
                    User = get_user_model()
                    try:
                        user = User.objects.get(id=user_id)
                    except User.DoesNotExist:
                        return JsonResponse({'error': 'User not found'}, status=404)
                    not_friend_set =  User.objects.exclude(id=user_id).exclude(friend=user)
                    not_friends = []
                    for not_friend in not_friend_set:
                        if (not Notification.objects.filter(sender=user, accepter=not_friend).exists() and
                    not Notification.objects.filter(sender=not_friend, accepter=user).exists()):
                            profile = getUserProfile(User=User, user=not_friend, owner=user, func='general')
                            if profile is not None:
                                not_friends.append(profile)
                    if len(not_friends) == 0:
                        return JsonResponse({'error': 'User was blocked by all users'}, status=401)
                    return JsonResponse(not_friends, status=200 , safe=False)
            else:
                return JsonResponse({'error': 'User is not logged in'}, status=401)
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
#2.3.1 GET /api/users/user_id/notifications
def GetNotifications(request, user_id):
    if request.method == 'GET':
        # if request.user.is_authenticated:
        if settings.ALLOW_API_WITHOUT_AUTH or request.user.is_authenticated:
            if request.user.is_authenticated or settings.ALLOW_API_WITHOUT_AUTH:
                if settings.ALLOW_API_WITHOUT_JWT == False:
                        err = jwt_and_auth_validate(request, user_id)
                        if err is not None:
                            return JsonResponse(err, status=401)
                User = get_user_model()
                try:
                    user = User.objects.get(id=user_id)
                except User.DoesNotExist:
                    return JsonResponse({'error': 'User not found'}, status=404)
                try:
                    requester_set = Notification.objects.filter(accepter=user)
                except Notification.DoesNotExist:
                    return JsonResponse({'error': 'Notifications not found'}, status=404)
                requesters = []
                for requester in requester_set:
                    profile = getUserNotification(User=User, noti=requester, request=request)
                    if profile is not None:
                        requesters.append(profile)
                if len(requesters) == 0:
                    return JsonResponse({'error': 'Notifications not found'}, status=404)
                return JsonResponse(requesters, status=200 , safe=False)
        else:
            return JsonResponse({'error': 'User is not logged in'}, status=401)
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
#2.3.2 POST: /api/users/friends/accept
def AcceptFriend(request):
    if request.method == 'POST':
            data = json.loads(request.body)
            owner_id = data.get('owner_id')
            user_id = data.get('user_id')
            # if request.user.is_authenticated:
            if settings.ALLOW_API_WITHOUT_AUTH or request.user.is_authenticated:
                if request.user.is_authenticated or settings.ALLOW_API_WITHOUT_AUTH:
                    if settings.ALLOW_API_WITHOUT_JWT == False:
                        err = jwt_and_auth_validate(request, owner_id)
                        if err is not None:
                            return JsonResponse(err, status=401)
                    if (request.user.id == user_id):
                        return JsonResponse({'error': 'Users try to accept friend to themselves'}, status=400) 
                    User = get_user_model()
                    try:
                        accepter = User.objects.get(id=owner_id)
                        sender = User.objects.get(id=user_id)
                    except User.DoesNotExist:
                        return JsonResponse({'error': 'User not found'}, status=404)
                    try:
                        blockedlist = BlockedList.objects.get(blocked=accepter, blocker=sender)
                        if blockedlist:
                            return JsonResponse({'error': 'User was blocked'}, status=401)
                    except BlockedList.DoesNotExist:
                        pass          
                    if sender in accepter.friend.all():
                        return JsonResponse({'error': 'User was already be friends'}, status=400)      
                    try:
                        notification = Notification.objects.get(sender=sender, accepter=accepter)
                        notification.delete()
                        accepter.add_friend(sender)
                        accepter.save()
                        return JsonResponse({'message': 'Accept friend success'}, status=201)
                    except Notification.DoesNotExist:
                        return JsonResponse({'error': 'Notification was not found'}, status=404)
            else:
                return JsonResponse({'error': 'User is not logged in'}, status=401)
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)

#2.3.3 POST: /api/users/notifications/friend_request 
def SendFriendRequest(request):
    if request.method == 'POST':
        try:
            # if request.user.is_authenticated:
            data = json.loads(request.body)
            owner_id = data.get('owner_id')
            user_id = data.get('user_id')
            if settings.ALLOW_API_WITHOUT_AUTH or request.user.is_authenticated:
                if request.user.is_authenticated or settings.ALLOW_API_WITHOUT_AUTH:
                    if settings.ALLOW_API_WITHOUT_JWT == False:
                        err = jwt_and_auth_validate(request, owner_id)
                        if err is not None:
                            return JsonResponse(err, status=401)
                    if (owner_id == user_id):
                        return JsonResponse({'error': 'Users try to send request to themselves'}, status=400) 
                    User = get_user_model()
                    accepter = User.objects.get(id = user_id)
                    sender = User.objects.get(id = owner_id)
                    try:
                        blockedlist = BlockedList.objects.get(blocked=sender, blocker=accepter)
                        if blockedlist:
                            return JsonResponse({'error': 'User was blocked'}, status=401)
                    except BlockedList.DoesNotExist:
                        pass
                    try:
                        Notification.objects.get(sender=sender, accepter=accepter)
                        return JsonResponse({'error': 'User already send friend request'}, status=400)
                    except Notification.DoesNotExist:
                        notification = Notification(sender=sender, accepter=accepter)
                        notification.save()
                    return JsonResponse({'message': 'Send friend request success'}, status=200)
            else:
                return JsonResponse({'message': 'User is not logged in'}, status=401)
        except User.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=404) 
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)

#2.3.4 DELETE: /api/users/notifications/delete
def DeleteNotification(request):
    if request.method == 'DELETE':
            data = json.loads(request.body)
            owner_id = data.get('owner_id')
            user_id = data.get('user_id')
            # if request.user.is_authenticated:
            if settings.ALLOW_API_WITHOUT_AUTH or request.user.is_authenticated:
                if request.user.is_authenticated or settings.ALLOW_API_WITHOUT_AUTH:
                    if settings.ALLOW_API_WITHOUT_JWT == False:
                        err = jwt_and_auth_validate(request, owner_id)
                        if err is not None:
                            return JsonResponse(err, status=401)              
                    User = get_user_model()
                    try:    
                        accpeter = User.objects.get(id=owner_id)
                        sender = User.objects.get(id=user_id)
                    except User.DoesNotExist:
                        return JsonResponse({'error': 'User not found'}, status=404)
                    try:
                        notification = Notification.objects.get(sender=sender, accepter=accpeter)
                    except Notification.DoesNotExist:
                        return JsonResponse({'error': 'Notification was not found'}, status=404)
                    notification.delete()
                    return JsonResponse({'message': 'Delete Notificantion Success'}, status=200)
            else:
                return JsonResponse({'message': 'User is not logged in'}, status=401)

    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)
