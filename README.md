# twitter_api_sample

## 使い方

```sh
$ vim test.py
```

```python
from twitter import Twitter
twitter_auth = Twitter('consumer_key', 'consumer_secret', '3075535693-access_token', 'access_token_secret')

twitter_auth.get_friends_list(screen_name='Yamada_info_pb')
```
