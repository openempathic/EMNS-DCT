from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required


# Dummy data created for now, but in the future this could be my pandas df or a csv containing a list of utterances
data = [
    {
        'author':'test author1',
        'utterance':'Hello World! 1',
        'prosody':'Happy',
        'date_created':'January 4, 2022'
    },
    {
        'author':'test author2',
        'utterance':'Hello World! 2',
        'prosody':'angry',
        'date_created':'January 5, 2022'
    }
]


def home(request):
    context = {'data':data}
    return render(request, 'audio_recorder/home.html', context)

def about(request):
    return render(request, 'audio_recorder/about.html')

@login_required
def record(request):
    return render(request, 'audio_recorder/recorder.html')