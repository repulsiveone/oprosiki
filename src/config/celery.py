import os
import redis
from celery import shared_task
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('apps.oprosweb')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

# подумать над тем как сделать тесты
@shared_task
def update_user_tag(user_id, tags_id):

    redis_client = redis.StrictRedis(
        host='127.0.0.1',
        port='6379',
        db='1',
        )
    
    key = f'user:{user_id}'
    for tag_id in tags_id:
        tag = f'survey_tag:{tag_id}'
        tag_weight = f'{tag}_weight'

        if redis_client.hexists(key, tag):
            redis_client.hincrby(key, tag, 1)
        else:
            redis_client.hset(key, tag, 1)

        tags = redis_client.hgetall(key)
        tags = {k.decode('utf-8'): float(v) for k, v in tags.items()}
        total_weight = sum(tags.values())
        curr_tag_weight = tags[tag]
        new_weight = curr_tag_weight / total_weight

        redis_client.hset(key, tag_weight, new_weight)