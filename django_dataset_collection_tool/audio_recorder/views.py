from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, DetailView

# from .form import UploadAudioForm
from .models import Utterances


# Dummy data created for now, but in the future this could be my pandas df or a csv containing a list of utterances
data = [
    {
        'author':'test author1',
        'utterance':'Hello World! 1',
        'prosody':'Happy',
        'date_created':'January 4, 2022',
        'audio_recording':'some/file/dir1.wav'

    },
    {
        'author':'test author2',
        'utterance':'Hello World! 2',
        'prosody':'angry',
        'date_created':'January 5, 2022',
        'audio_recording':'some/file/dir1.wav'
    },
    {
        'author':'test author1',
        'utterance':'fgsdfgh sdfg sdfgsdf gsadrfg dfga r rae gdafga raee gaeerg',
        'prosody':'Happy',
        'date_created':'January 4, 2022',
        'audio_recording':'some/file/dir1.wav'

    },
    {
        'author':'test author1',
        'utterance':'gafgarag fag aesrgash rbjkhasf dbkjhsb dfjkhagsdf hgshfd jhasgdfjhgkfjhgakjshbfjhber kfj ahsgf hasgfjkh sba',
        'prosody':'Happy',
        'date_created':'January 4, 2022',
        'audio_recording':'some/file/dir1.wav'

    },
    {
        'author':'test author1',
        'utterance':'dfs ajsduf uavsukfghvksbdvfjkhsvbaiuf dgty akuehbfkhdu gsf jbwjkfv sudtgf ahebkfjhbsdku ygfUKYfaf',
        'prosody':'Happy',
        'date_created':'January 4, 2022',
        'audio_recording':'some/file/dir1.wav'

    },
    {
        'author':'test author1',
        'utterance':' ahuFukhaiwjh fjkzshbdjfghvszyuteff  sguuydgf jzshbdvfgs ff shfuskh',
        'prosody':'Happy',
        'date_created':'January 4, 2022',
        'audio_recording':'some/file/dir1.wav'

    },
]


def home(request):
    return render(request, 'audio_recorder/home.html')

def about(request):
    return render(request, 'audio_recorder/about.html')

@login_required
def utterances(request):
    context = {'posts':data}
    return render(request, 'audio_recorder/recorder.html', context)

class UtteranceListView(ListView):
    model = Utterances
    template_name = 'audio_recorder/recorder.html'
    context_object_name = 'posts'
    ordering = ['prosody']

class UtteranceDetailView(DetailView):
    model = Utterances