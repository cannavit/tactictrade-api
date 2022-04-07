import os
from django.conf import settings
import json
import requests

def upload_image_imagekit(image_url):

    IMAGE_KIT_URL_UPLOAD = settings.IMAGE_KIT_URL_UPLOAD
    MEDIA_ROOT = settings.MEDIA_ROOT

    file_name = image_url[MEDIA_ROOT.find('/') + 1: len(image_url)]

    payload = {
        'fileName': file_name,
        'tags': settings.IMAGE_KIT_TAGS,
        'folder': settings.IMAGE_KIT_TAGS
    }

    image_url = str(MEDIA_ROOT) + '/' + image_url

    print(image_url)

    files = [
        ('file', (file_name, open(image_url, 'rb'), 'image/png'))
    ]

    headers = {
        'Authorization': 'Basic ' + settings.IMAGE_KIT_TOKEN

    }

    response = requests.request(
        "POST", IMAGE_KIT_URL_UPLOAD, headers=headers, data=payload, files=files)

    print(response.text)
    data = json.loads(response.text)

    os.remove(image_url)
    
    return {
        "url": data['url'],
        "image_dir": IMAGE_KIT_URL_UPLOAD
    }