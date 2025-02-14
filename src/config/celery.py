import os
import redis
import django
from celery import shared_task, Celery
from django.core.cache import cache

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()
from apps.oprosweb.models import Survey, TagsNames
app = Celery('config')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()


redis_client = redis.StrictRedis(
        host='127.0.0.1',
        port='6379',
        db='1',
        )


@shared_task
def update_user_tag(user_id, tags_id):
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


@shared_task
def get_user_tag(user_id):
    cache_key = f'user:{user_id}:surveys'
    
    key = f'user:{user_id}'
    data = redis_client.hgetall(key)

    tags_with_weights = [((k.decode('utf-8'), float(v.decode('utf-8')))) for k, v in data.items() if k.endswith(b'_weight')]
    sorted_tags = sorted(tags_with_weights, key=lambda x: x[1], reverse=True)
    sorted_tags_ids = [tag.replace('_weight', '') for tag, weight in sorted_tags]
    
    tags_names = [
        tag for tag in TagsNames.objects.filter(
            tag_name__in=(
                i.split(':')[1] for i in sorted_tags_ids
                ))
    ]

    list_of_surveys = []

    for tag in tags_names:
        surveys = Survey.objects.filter(tagssurvey__tag=tag).distinct()
        list_of_surveys.extend(surveys)
    
    unique_surveys = set(list_of_surveys)

    cache.set(cache_key, unique_surveys, 60*60*24)