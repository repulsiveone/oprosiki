import redis
from celery import shared_task

redis_client = redis.StrictRedis(
    host='localhost',
    port='6379',
    db='1',
)

@shared_task
def update_user_tag(user_id, tags_id, redis_client): #передаем redis client в функцию
    key = f'user:{user_id}'
    for tag_id in tags_id:
        tag = f'survey_tag:{tag_id}'
        tag_weight = f'{tag}_weight'

        if redis_client.hexists(key, tag):
            redis_client.hincrby(key, tag, 1)
        else:
            redis_client.hset(key, tag, 1)

        tags = redis_client.hgetall(key)
        tags = {k.decode('utf-8'): int(v) for k, v in tags.items()}
        total_weight = sum(tags.values())
        curr_tag_weight = tags[tag]
        new_weight = curr_tag_weight / total_weight

        redis_client.hset(key, tag_weight, new_weight)
    
def get_user_tags():
    ...

