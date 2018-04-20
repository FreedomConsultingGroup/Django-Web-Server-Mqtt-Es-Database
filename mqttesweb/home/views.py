from django.shortcuts import render
from django.http import HttpResponse
import os

# Create your views here.

FOLD_DIR = os.path.dirname(os.path.abspath(__file__))


def index(request):
    return HttpResponse(open(os.path.join(FOLD_DIR, "statics/index.html")).read())


def esGET():
    pass
