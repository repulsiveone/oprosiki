import pytest
import redis
from services.redis_service import update_user_tag

test_redis_client = redis.StrictRedis(
    host='localhost',
    port='6379',
    db='2',
)

def test_update_user_tag():
    key = f'user:{1}'
    update_user_tag(1, 1, test_redis_client)
    assert test_redis_client.hgetall(key) == {b'survey_tag:1': b'1', b'survey_tag:1_weight': b'1.0'}
    test_redis_client.flushdb()