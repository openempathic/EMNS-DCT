from email import header
import tablib
import random
import json

from urllib import response
from django.http import HttpResponse, HttpResponseForbidden
from django.http.response import JsonResponse

from django.shortcuts import render, get_object_or_404, redirect

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User

from django.views import View
from django.views.generic import ListView, DetailView, CreateView, DeleteView, UpdateView
from django.views.generic.edit import FormMixin, FormView

from django.urls import reverse

# used to update date created
from django.utils import timezone



from django_filters.views import FilterView
from django.core.mail import send_mail
from django.conf import settings


from .models import Utterances
from .forms import RecordingUpdateForm, ImportForm
from .filters import OrderFilter
from .admin import UtterancesResource

def HomeView(request, *args, **argv):
	if request.method == 'POST':
		name = request.POST['name']
		email = request.POST['email']
		subject = request.POST['subject']
		message = request.POST['message']

		message = f"MY DJANGO APP \n\n\nFrom: {name}\n\nemail: {email}\n\nmessage:\n\n{message}"

		send_mail(subject=subject, message=message, from_email=email, recipient_list=[settings.EMAIL_HOST_USER], fail_silently=False)
		messages.success(request, "Thank you for contacting us, we will be in touch soon.")

	return render(request, 'audio_recorder/home.html')

def AnnotationGuideView(request, *args, **argv):
	return render(request, 'audio_recorder/annotation_guide.html')

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
			print('form valid','#'*100)
			return self.form_valid(form)
		else:
			print('form invalid','#'*100)
			return self.form_invalid(form)

	def form_valid(self, form) -> HttpResponse:
		emotions = {
			'curious_and_fascinated':self.request.POST.get('curious_and_fascinated'),
			'pensive_and_reflective':self.request.POST.get('pensive_and_reflective'),
			'fearful_and_anxious':self.request.POST.get('fearful_and_anxious'),
			'happy_and_energetic':self.request.POST.get('happy_and_energetic'),
			'calm_and_composed':self.request.POST.get('calm_and_composed'),
			'focused_and_attentive':self.request.POST.get('focused_and_attentive'),
			'surprised_and_confused':self.request.POST.get('surprised_and_confused'),
			'sad_and_despondent':self.request.POST.get('sad_and_despondent'),
			'romantic_and_passionate':self.request.POST.get('romantic_and_passionate'),
			'seductive_and_enticing':self.request.POST.get('seductive_and_enticing'),
			'angry_and_irritated':self.request.POST.get('angry_and_irritated'),
			'persistent_and_determined':self.request.POST.get('persistent_and_determined'),
			'discomposed_and_unsettled':self.request.POST.get('discomposed_and_unsettled'),
			'grumpy_and_cranky':self.request.POST.get('grumpy_and_cranky'),
		}
		if self.request.user.profile.status == 'NLD':
			self.object.author = self.request.user
			self.object.gender = self.request.user.profile.gender
			self.object.age =  self.request.POST.get("age")
			self.object.date_created = timezone.now()
			self.object.level = self.request.POST.get("level_slider")
			self.object.arousal = self.request.POST.get("arousal_slider")
			self.object.valence = self.request.POST.get("valence_slider")
			self.object.description = self.request.POST.get("description_textarea")
			self.object.emotion = json.dumps(emotions)
			self.object.status = 'Awaiting Review'
			self.object.save()
		elif self.request.user.profile.status == 'Actor':
			self.object.author = self.request.user
			self.object.author = self.request.user
			self.object.gender = self.request.user.profile.gender
			self.object.age = self.request.user.profile.age
			self.object.level = self.request.POST.get("level_slider")
			self.object.status = 'Awaiting Review'
			self.object.audio_recording = self.request.FILES.get("recorded_audio")
			self.object.save()
		elif self.request.user.profile.status == 'Admin':
			self.object.status = self.request.POST.get("status")
			self.object.description = self.request.POST.get("description_textarea")
			self.object.save()
		
		return super().form_valid(form)



	def test_func(self):
		self.object = self.get_object()

		if self.request.user == self.object.author or \
				self.request.user.groups.filter(user=self.request.user).filter(user=self.object.author).exists() or \
				self.request.user.is_superuser: # Checking if the user has permissions to modify the post
			return True
		return False

class UtteranceUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
	model = Utterances
	fields = ['utterance', 'prosody', 'status']

	def form_valid(self, form) -> HttpResponse:
		form.instance.author = self.request.user
		return super().form_valid(form)

	def test_func(self):
		utterance = self.get_object()
		if self.request.user == utterance.author or self.request.user.is_superuser: # also allowing admin user to update posts
			return True
		return False

class UtteranceListView(LoginRequiredMixin, FilterView):
	model = Utterances
	paginate_by = 10
	filterset_class = OrderFilter

	def get_queryset(self):
		if self.request.user.groups.filter(user=self.request.user).exists():
			return 
		else:
			return Utterances.objects.filter(author=self.request.user)


class UserUtteranceListView(LoginRequiredMixin, FilterView):
	model = Utterances
	paginate_by = 10
	filterset_class = OrderFilter

	def get_queryset(self):
		user = get_object_or_404(User, username=self.kwargs.get('username'))
		return Utterances.objects.filter(author=user)#.order_by('-date_created')#.order_by('-prosody')

class UtteranceCreateView(LoginRequiredMixin, CreateView):
	model = Utterances
	fields = ['utterance', 'prosody']
	template_name = 'audio_recorder/create_new_utterance.html'

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

class Export(LoginRequiredMixin, UserPassesTestMixin, View):
	model = Utterances

	def get(self, *args, **kwargs ):
		dataset = UtterancesResource().export()
		response = HttpResponse(dataset.csv, content_type="text/csv")
		response['Content-Disposition'] = 'attachment; filename=dataset.csv'
		return response

	def test_func(self):
		if self.request.user.is_superuser or self.request.user.profile.status == 'Admin': # also allowing admin user to update posts
			return True
		return False

class Import(FormView):
	model = Utterances
	form_class = ImportForm
	template_name = 'audio_recorder/import_data.html'

	def get_success_url(self):
		messages.warning(self.request, 'Not implemented')
		# return reverse('audio-recorder-utterances')
		return reverse('import-utterances')
	
	def post(self, request, *args, **kwargs):
		form_class = self.get_form_class()
		form = self.get_form(form_class)

		if form.is_valid():
			file = request.FILES['file_field']
			return self.form_valid(form)
		else:
			return self.form_invalid(form)