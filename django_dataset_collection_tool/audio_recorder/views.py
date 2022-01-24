from enum import unique
from django.http import HttpResponse, HttpResponseForbidden
from django.http.response import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.views.generic import ListView, DetailView, CreateView, DeleteView, UpdateView
from django.views.generic.edit import FormMixin
from django.urls import reverse
from django.views import View

from .models import Utterances
from .forms import RecordingUpdateForm

class HomeView(View):
	def get(self, request, *args, **kwargs):
		return render(request, 'audio_recorder/home.html')

class AboutView(View):
	def get(self, request, *args, **kwargs):
		return render(request, 'audio_recorder/about.html')

class UtteranceDetailView(LoginRequiredMixin, UserPassesTestMixin, FormMixin, DetailView):
	model = Utterances
	form_class = RecordingUpdateForm

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['form'] = self.get_form()
		return context

	def get_success_url(self):
		if self.get_queryset().filter(pk=self.object.pk+1).exists():
			return reverse('utterance-detail', kwargs={'pk': self.object.pk+1})
		else:
			messages.success(self.request, 'Nothing else left, please go back to any you have skipped, otherwise let the reseachers know you have finished :)')
			return reverse('utterance-detail', kwargs={'pk': self.object.pk})

	def post(self, request, *args, **kwargs):
		if not request.user.is_authenticated:
			return HttpResponseForbidden()
		form = RecordingUpdateForm(request.POST)

		if form.is_valid():
			return self.form_valid(form)
		else:
			return self.form_invalid(form)

	def form_valid(self, form) -> HttpResponse:
		self.object.author = self.request.user
		self.object.audio_recording = self.request.FILES.get("recorded_audio")
		self.object.save()

		return JsonResponse({
				"url": reverse('utterance-detail', kwargs={'pk': self.object.pk}),
				"success": True,
			})

	def test_func(self):
		self.object = self.get_object()

		if self.request.user == self.object.author or \
				self.request.user.groups.filter(user=self.request.user).filter(user=self.object.author).exists() or \
				self.request.user.is_superuser: # Checking if the user has permissions to modify the post
			return True
		return False

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

class UtteranceListView(LoginRequiredMixin, ListView):
	model = Utterances
	ordering = ['prosody']
	paginate_by = 10

class UserUtteranceListView(LoginRequiredMixin, ListView):
	model = Utterances
	template_name = 'audio_recorder/utterances_list.html'
	context_object_name = 'posts'
	paginate_by = 10

	def get_queryset(self):
		user = get_object_or_404(User, username=self.kwargs.get('username'))
		return Utterances.objects.filter(author=user).order_by('-date_created').order_by('-prosody')


class UtteranceCreateView(LoginRequiredMixin, CreateView):
	model = Utterances
	fields = ['utterance', 'prosody']

	def form_valid(self, form) -> HttpResponse:
		form.instance.author = self.request.user
		return super().form_valid(form)

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