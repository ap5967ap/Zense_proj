from django.shortcuts import render

import logging

logger = logging.getLogger(__name__)
from django.http import HttpResponse

def print_hello(request):
    print("hello world")
    logger.info("cron job is running")
    return HttpResponse("hello")