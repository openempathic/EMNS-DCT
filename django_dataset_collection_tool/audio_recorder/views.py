from django.db.models import fields
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.views.generic import ListView, DetailView, CreateView, DeleteView, UpdateView

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
    return render(request, 'audio_recorder/utterances.html', context)

class UtteranceListView(ListView):
    model = Utterances
    # template_name = 'audio_recorder/utterances.html'
    context_object_name = 'posts'
    ordering = ['prosody']
    paginate_by = 5

class UserUtteranceListView(ListView):
    model = Utterances
    template_name = 'audio_recorder/user_utterances_list.html'
    context_object_name = 'posts'
    paginate_by = 5

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        return Utterances.objects.filter(author=user).order_by('-date_created')



class UtteranceDetailView(DetailView):
    model = Utterances

class UtteranceCreateView(LoginRequiredMixin, CreateView):
    model = Utterances
    fields = ['utterance', 'prosody']

    def form_valid(self, form) -> HttpResponse:
        form.instance.author = self.request.user
        return super().form_valid(form)

class UtteranceUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Utterances
    fields = ['utterance', 'prosody']

    def form_valid(self, form) -> HttpResponse:
        form.instance.author = self.request.user
        return super().form_valid(form)

    def test_func(self):
        utterance = self.get_object()
        if self.request.user == utterance.author or self.request.user.is_superuser: # also allowing admin user to update posts
            return True
        return False

class UtteranceDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Utterances
    success_url = '/utterances/'

    def test_func(self):
        utterance = self.get_object()
        if self.request.user == utterance.author or self.request.user.is_superuser: # also allowing admin user to update posts
            return True
        return False