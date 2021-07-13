import boto3
import logging
import praw
import prawcore
import os
import json
import time

from typing import Any

SERIALIZABLE_TYPES = (str, int, float, bool)
SUBMISSIONS_STREAM_NAME = os.environ['submissions_stream']
COMMENTS_STREAM_NAME = os.environ['comments_stream']

def is_serializable(key: str, value: Any) -> bool:
    return (type(value) in SERIALIZABLE_TYPES) and (not key.startswith('_'))

def to_record(obj : praw.models) -> dict:
    record  = {k:v for k,v in vars(obj).items() if is_serializable(k,v)}
    if obj.author:
        record.update({f'author_{k}':v for k,v in vars(obj.author).items() if is_serializable(k,v)})
    return {'Data':json.dumps(record)+'\n'}

handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
for logger_name in ("praw", "prawcore"):
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)

reddit = praw.Reddit(
    client_id=os.environ['client_id'],
    client_secret=os.environ['client_secret'],
    user_agent=os.environ['user_agent']
)

logger = logging.getLogger('reddit-wsb-crawler')
logger.setLevel(logging.DEBUG)
reddit.read_only = True
queries = ['flair:dd', 'flair:Technical Analysis']
wsb = reddit.subreddit('wallstreetbets')
client = boto3.client('firehose')

for query in queries:
    posts = wsb.search(query=query, limit=None, sort='top')
    for submission in posts:
        while True:
            try:
                submission.comments.replace_more(limit=None)
            except prawcore.exceptions.TooManyRequests:
                logger.log(logging.WARNING, 'Too many requests exception. Sleeping for 10 seconds...')
                time.sleep(10)
            else:
                break
        client.put_record(DeliveryStreamName=SUBMISSIONS_STREAM_NAME, Record=to_record(submission))
        for comment in submission.comments.list():
            client.put_record(DeliveryStreamName=COMMENTS_STREAM_NAME, Record=to_record(comment))