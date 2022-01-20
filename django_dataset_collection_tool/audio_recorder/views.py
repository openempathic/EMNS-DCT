from django.db.models import fields

from django.http import HttpResponse
from django.http.response import JsonResponse

from django.shortcuts import render, get_object_or_404

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User

from django.views.generic import ListView, DetailView, CreateView, DeleteView, UpdateView

from .models import Utterances


def home(request):
    return render(request, 'audio_recorder/home.html')

def about(request):
    return render(request, 'audio_recorder/about.html')

def record(request):
    if request.method == "POST":
        audio_file = request.FILES.get("recorded_audio")
        record = Utterances(audio_recording=audio_file)
        record.save()
        messages.success(request, "Audio recording successfully added!")
        return JsonResponse({ "success": True })

    context = {"page_title": "Record audio"}
    return render(request, "audio_recorder/record.html", context)

class UpdateRecordingView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Utterances
    fields = ['audio_recording']

    def form_valid(self, form) -> HttpResponse:
        form.instance.author = self.request.user
        return super().form_valid(form)

    def test_func(self):
        utterance = self.get_object()
        if self.request.user == utterance.author or self.request.user.is_superuser: # also allowing admin user to update posts
            return True
        return False


class UtteranceListView(LoginRequiredMixin, ListView):
    model = Utterances
    # template_name = 'audio_recorder/utterances.html'
    context_object_name = 'posts'
    ordering = ['prosody']
    paginate_by = 5

class UserUtteranceListView(LoginRequiredMixin, ListView):
    model = Utterances
    template_name = 'audio_recorder/user_utterances_list.html'
    context_object_name = 'posts'
    paginate_by = 5

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        return Utterances.objects.filter(author=user).order_by('-date_created')

class UtteranceDetailView(LoginRequiredMixin, DetailView):
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

    def post(self, request, *args, **kwargs):
        if self.request.method == "POST":
            audio_file = self.request.FILES.get("recorded_audio")
            record = Utterances.objects.update(audio_recording=audio_file)
            record.save()
            messages.success(self.request, "Audio recording successfully added!")
            return JsonResponse({ "success": True })
        # return self.get(request, *args, **kwargs)
        return render(request, "core/record.html")

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

def handler404(request, *args, **argv):
    return render(request, 'audio_recorder/404.html')