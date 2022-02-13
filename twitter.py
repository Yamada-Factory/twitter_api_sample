from asyncio.windows_events import NULL
import time
import hashlib
import hmac
import base64
import requests
import os
from operator import itemgetter

import util


class Twitter:
    consumer_key = ''
    access_token = ''
    signature_key = ''

    # API endpoint
    V1_GET_FRIENDS_LIST = 'https://api.twitter.com/1.1/friends/list.json'
    V1_GET_USERS_SHOW = 'https://api.twitter.com/1.1/users/show.json'

    # 初期化
    def __init__(self, consumer_key, consumer_secret, access_token, access_token_secret):
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.access_token = access_token

        self.signature_key = '&'.join([consumer_secret, access_token_secret]).encode('utf-8')

    # リクエストヘッダー生成
    def make_oauth_params(self):
        return {
            'oauth_token': self.access_token,
            'oauth_consumer_key': self.consumer_key,
            'oauth_signature_method': 'HMAC-SHA1',
            'oauth_timestamp': int(time.time()),
            'oauth_nonce': os.urandom(10).hex(),
            'oauth_version': '1.0',
        }
    
    def common_request(self, input_params={}, request_url='', http_method='GET'):
        # 認証系 パラメータ
        oauth_params = self.make_oauth_params()

        # 実際に投げるパラメータ類処理
        params = dict(input_params)
        params.update(oauth_params)
        req_params = sorted(params.items(), key=itemgetter(0))
        req_params = util.encodeUrl(req_params)
        req_params = util.quote(req_params, safe='')

        enc_req_method = util.quote(http_method, safe='')
        enc_req_url = util.quote(request_url, safe='')
        signature_data = '&'.join([enc_req_method, enc_req_url, req_params])
        signature_data = signature_data.encode('utf-8')

        digester = hmac.new(self.signature_key, signature_data, hashlib.sha1)

        signature = base64.b64encode(digester.digest())
        params['oauth_signature'] = signature

        headers = {
            'Authorization': 'OAuth ' + util.encodeUrl(params).replace('&', ',')
        }

        req_url = request_url + '?' + util.encodeUrl(params)

        return  requests.get(req_url, headers=headers).json()


    # フォローしているユーザーをオブジェクトの一覧で取得する
    #
    # https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/follow-search-get-users/api-reference/get-friends-list
    def get_friends_list(self, user_id='', screen_name='', cursor='-1', count='20'):
        http_method = 'GET'

        # 入力パラメータ
        req_get_params = {
            'cursor': cursor,
            'count': count
        }

        # ユーザID or 表示名のどちらかは必須
        if (user_id != ''):
            req_get_params['user_id'] = user_id
        elif (screen_name != ''):
            if (screen_name[0] != '@'):
                screen_name = '@' + screen_name
            req_get_params['screen_name'] = screen_name
        else:
            return None

        return self.common_request(req_get_params, self.V1_GET_FRIENDS_LIST, http_method)

    # フォローしているユーザーを全件取得する
    def get_friends_list_all(self, user_id='', screen_name=''):
        next_cursor = '-1'
        friends = []

        while(True):
            _friends = self.get_friends_list(user_id=user_id, screen_name=screen_name, cursor=next_cursor, count='200')
            if 'users' in _friends:
                friends.append(_friends.get['users'])
            
            # friends.append(_friends['users'])

            if 'next_cursor_str' in _friends:
                next_cursor =  _friends['next_cursor_str']
            else:
                break
        
        return friends

    # ユーザ情報取得
    #
    # https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/follow-search-get-users/api-reference/get-users-show
    def get_users_show(self, user_id='', screen_name=''):
        http_method = 'GET'

        # 入力パラメータ
        req_get_params = {
        }

        # ユーザID or 表示名のどちらかは必須
        if (user_id != ''):
            req_get_params['user_id'] = user_id
        elif (screen_name != ''):
            if (screen_name[0] != '@'):
                screen_name = '@' + screen_name
            req_get_params['screen_name'] = screen_name
        else:
            return None

        return self.common_request(req_get_params, self.V1_GET_USERS_SHOW, http_method)
