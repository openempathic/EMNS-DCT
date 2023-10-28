from email import header
import random
import json
import re

from django.http import HttpResponse, HttpResponseForbidden
from django.http.response import JsonResponse

from django.shortcuts import render, get_object_or_404, redirect

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User

from rest_framework.views import APIView
from rest_framework.response import Response as RestResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle
from .auth import TokenAuthGet

from django.views import View
from django.views.generic import DetailView, CreateView, DeleteView, UpdateView
from django.views.generic.edit import FormMixin, FormView
from django.urls import reverse
from django import forms
# used to update date created
from django.utils import timezone

from django_filters.views import FilterView
from django.core.mail import send_mail
from django.conf import settings
from django.db.models import Count, Avg, F, Q

from urllib.parse import urlparse


from .models import Utterances
from .forms import RecordingUpdateForm, ImportForm
from .filters import OrderFilter
from .admin import UtterancesResource

import logging
logger = logging.getLogger(__name__)

def HomeView(request, *args, **argv):
	if request.method == 'POST':
		name = request.POST['name']
		email = request.POST['email']
		subject = request.POST['subject']
		message = request.POST['message']

		message = f"DCT OpenEmpathic \n\n\nFrom: {name}\n\nemail: {email}\n\nmessage:\n\n{message}"

		send_mail(subject=subject, message=message, from_email=email, recipient_list=[settings.EMAIL_HOST_USER], fail_silently=False)
		messages.success(request, "Thank you for contacting us, we will be in touch soon.")

	return render(request, 'audio_recorder/home.html')

def AnnotationGuideView(request, *args, **argv):
	return render(request, 'audio_recorder/annotation_guide.html')

class GetRandomSample(LoginRequiredMixin, DetailView):
    model = Utterances  
    form_class = RecordingUpdateForm

    def get(self, request, *args, **kwargs):

        # Get random utterance
        count = self.get_queryset().count()
        if count > 0:
            random_index = random.randint(0, count-1)
            random_object = self.get_queryset()[random_index]
            return redirect(reverse('utterance-detail', kwargs={'pk': random_object.pk}))
        
        # If no utterances, redirect home
        messages.warning(request, 'No utterances available')  
        return redirect('audio-recorder-home')

class UtteranceDetailView(LoginRequiredMixin, UserPassesTestMixin, FormMixin, DetailView):
	model = Utterances
	form_class = RecordingUpdateForm

	def acquire_lock(self):
		if not self.object.locked_by:
			self.object.locked_by = self.request.user
			self.object.save()

	def release_lock(self):
		if self.object.locked_by == self.request.user:
			self.object.locked_by = None
			self.object.save()

	def get(self, request, *args, **kwargs):
		self.object = self.get_object()
		if self.object.locked_by and self.object.locked_by != self.request.user:
			if self.get_queryset().filter(pk=self.object.pk+1).exists():
				return redirect(reverse('utterance-detail', kwargs={'pk': self.object.pk+1}))  # Replace 'home' with the name of your home view
			else:
				messages.success(self.request, 'Nothing else left, please go back to any you have skipped, otherwise let the reseachers know you have finished :)')
				return redirect(reverse('utterance-detail', kwargs={'pk': self.object.pk-1}))
		self.acquire_lock()
		context = self.get_context_data(object=self.object)
		return self.render_to_response(context)

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['form'] = self.get_form()
		return context

	def get_success_url(self):
		messages.success(self.request, 'Submission saved successfully!')
		# Try to get a random object where status is 'Pending'
		count = self.get_queryset().filter(status='Pending').count()
		
		if count > 0:
			random_index = random.randint(0, count - 1)
			next_object = self.get_queryset().filter(status='Pending')[random_index]
			# If such an object exists, redirect to its detail view
			return reverse('utterance-detail', kwargs={'pk': next_object.pk})
		else:
			# If no such object exists, display a message and redirect to the current object's detail view
			messages.success(self.request, 'Nothing else left, please go back to any you have skipped, otherwise let the reseachers know you have finished :)')
			return reverse('utterance-detail', kwargs={'pk': self.object.pk})

	def post(self, request, *args, **kwargs):
		if not request.user.is_authenticated:
			return HttpResponseForbidden()

		utterance = self.get_object()
		self.release_lock()

		if "Next" in self.request.POST and not utterance.acquire_lock(request.user) and self.get_queryset().filter(pk=self.object.pk+1).exists():
			return redirect(reverse('utterance-detail', kwargs={'pk': utterance.pk+1}))
		
		if "Previous" in self.request.POST and not utterance.acquire_lock(request.user) and self.get_queryset().filter(pk=self.object.pk-1).exists():
			return redirect(reverse('utterance-detail', kwargs={'pk': utterance.pk-1}))

		form = self.get_form()

		if form.is_valid():
			self.form_valid(form)
			return JsonResponse({'messages': [str(message) for message in messages.get_messages(request)], 'redirect_url': self.get_success_url()})
		else:
			messages.success(self.request, 'Submission Failed!')
			self.form_invalid(form)
			return JsonResponse({'messages': [str(message) for message in messages.get_messages(request)], 'redirect_url': self.get_success_url()})

	def form_valid(self, form) -> HttpResponse:
		emotions = {
			'curious_and_fascinated':self.request.POST.getlist('curious_and_fascinated'),
			'pensive_and_reflective':self.request.POST.getlist('pensive_and_reflective'),
			'fearful_and_anxious':self.request.POST.getlist('fearful_and_anxious'),
			'happy_and_energetic':self.request.POST.getlist('happy_and_energetic'),
			'calm_and_composed':self.request.POST.getlist('calm_and_composed'),
			'focused_and_attentive':self.request.POST.getlist('focused_and_attentive'),
			'surprised_and_confused':self.request.POST.getlist('surprised_and_confused'),
			'sad_and_despondent':self.request.POST.getlist('sad_and_despondent'),
			'romantic_and_passionate':self.request.POST.getlist('romantic_and_passionate'),
			'seductive_and_enticing':self.request.POST.getlist('seductive_and_enticing'),
			'angry_and_irritated':self.request.POST.getlist('angry_and_irritated'),
			'persistent_and_determined':self.request.POST.getlist('persistent_and_determined'),
			'discomposed_and_unsettled':self.request.POST.getlist('discomposed_and_unsettled'),
			'grumpy_and_cranky':self.request.POST.getlist('grumpy_and_cranky'),
			'disgusted':self.request.POST.getlist('disgusted'),
		}
		emotions = {key: value for key, value in emotions.items() if value != []}

		accent = self.request.POST.getlist('accent')
		gender = self.request.POST.getlist('gender')
		bg_sounds = self.request.POST.getlist('background_sounds')

		other_accent = self.request.POST.getlist('other_accent')
		other_gender = self.request.POST.getlist('other_gender')
		other_bg_sounds = self.request.POST.getlist('other_background_sounds')

		# Create a list containing all the 'other' inputs
		other_values = [other_accent, other_gender, other_bg_sounds]

		# Create a list containing all the form data
		form_data = [accent, gender, bg_sounds]

		# Iterate over the form data
		for i in range(len(form_data)):
			if 'other' in form_data[i]:
				form_data[i].remove('other')
				if other_values[i]:
					form_data[i].extend(other_values[i])


		if self.request.user.profile.status == 'NLD':
			self.object.author = self.request.user
			self.object.gender = self.request.POST.get('gender')
			self.object.audio_quality = self.request.POST.get("audio_quality")
			self.object.age =  self.request.POST.get("age")
			self.object.date_created = timezone.now()
			self.object.level = self.request.POST.get("level_slider")
			self.object.arousal = self.request.POST.get("arousal_slider")
			self.object.valence = self.request.POST.get("valence_slider")
			self.object.audio_description = self.request.POST.get("audio_description_textarea")
			self.object.video_description = self.request.POST.get("video_description_textarea")
			self.object.emotion = json.dumps(emotions)
			self.object.status = 'Awaiting Review'
			self.object.time_spent = self.request.POST.get('time_spent')

			self.object.accent = accent[0]
			self.object.bg_sounds = bg_sounds

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
			self.object.audio_description = self.request.POST.get("audio_description_textarea")
			self.object.video_description = self.request.POST.get("video_description_textarea")
			self.object.save()
		return super().form_valid(form)
	
	# def test_func(self):
	# 	utterance = self.get_object()
	# 	return utterance.author == self.request.user
	def test_func(self):
		self.object = self.get_object()

		if self.request.user == self.object.author or \
				self.request.user.groups.filter(user=self.request.user).filter(user=self.object.author).exists() or \
				self.request.user.is_superuser: # Checking if the user has permissions to modify the post
			return True
		return False
	
class ReleaseLockView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        utterance_id = request.POST.get('utterance_id')
        utterance = get_object_or_404(Utterances, id=utterance_id)
        if utterance.locked_by == request.user:
            utterance.locked_by = None
            utterance.save()
            return JsonResponse({'success': True})
        return JsonResponse({'success': False})

class UtteranceUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
	model = Utterances
	fields = ['utterance', 'emotion', 'status']

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
	template_name = 'audio_recorder/create_new_utterance.html'
	fields = ['audio_recording']

	def get_form(self, form_class=None):
		logger.info("Entered get_form method")
		form = super().get_form(form_class)
		form.fields['audio_recording'].widget = forms.URLInput(attrs={'class': 'form-control'})

		return form
	
	def is_valid_youtube_url(self, url):
		parsed_url = urlparse(url)
		return parsed_url.netloc in ('youtube.com', 'www.youtube.com', 'youtu.be') and \
			parsed_url.path.startswith('/watch')

	def convert_time_to_seconds(self, timestr):
		try: 
			time_components = list(map(int, timestr.split(':')))
		except ValueError:
			raise ValueError("Please check the time format.")
		
		if len(time_components) == 3:  # HH:MM:SS format
			hours, minutes, seconds = time_components
		elif len(time_components) == 2:  # MM:SS format
			hours = 0
			minutes, seconds = time_components
		elif len(time_components) == 1:  # SS format
			hours = minutes = 0
			seconds, = time_components
		else:
			raise ValueError("Please check the time format.")
		return hours * 3600 + minutes * 60 + seconds

	def create_youtube_embed_url(self, youtube_url, start_time_str, end_time_str):
		start = self.convert_time_to_seconds(start_time_str)
		end = self.convert_time_to_seconds(end_time_str)
		if start >= end:
			raise ValueError("Start time should be less than end time.")
		elif end - start > 30:
			raise ValueError("Maximum duration of an clip is 30 seconds.")
		elif start < 0 or end < 0:
			raise ValueError("Time cannot be negative.")

		video_id_pattern = re.compile(r"watch\?v=(.*?)(?:&|$)")
		match = video_id_pattern.search(youtube_url)

		if not self.is_valid_youtube_url(youtube_url):
			raise ValueError(f"Invalid YouTube URL: {youtube_url}")		
		
		video_id = match.group(1)
		base_url = "https://www.youtube.com/embed/"
		
		
		return f"{base_url}{video_id}?modestbranding=1&loop=1&start={start}&end={end}"
	
	def form_valid(self, form) -> HttpResponse:
		youtube_url = str(self.request.POST.get('audio_recording'))
		start_time = self.request.POST.get('start_time')
		end_time = self.request.POST.get('end_time')
		
		try:
			embed_url = self.create_youtube_embed_url(youtube_url, start_time, end_time)
			obj = form.save(commit=False)
			obj.audio_recording = embed_url  # This is the correction. Directly set the attribute of model instance.
			obj.author = self.request.user
			obj.save()
			return super().form_valid(form)
		except ValueError as e:
			logger.error(f"Unexpected error in form_valid: {e}")
			form.add_error(None, str(e))
			return self.form_invalid(form)

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
		
class StaffUserRateThrottle(UserRateThrottle):
	rate = '5/min'
	def allow_request(self, request, view):
		# Replace "your_username" with the specific username you want to give unlimited access to
		if request.user.is_staff:
			return True
		return super().allow_request(request, view)
	
from rest_framework import permissions
from rest_framework.exceptions import PermissionDenied

class CanUsePaidParameter(permissions.BasePermission):
	"""
	Custom permission to check if a user belongs to the 'CanViewPaidUsersGroup' and can use the 'paid' parameter.
	"""

	def has_permission(self, request, view):
		paid_param = request.GET.get('paid', None)
		if paid_param:
			return request.user.groups.filter(name='CanViewPaidUsersGroup').exists() or request.user.is_superuser
		return True

class GetStatsView(APIView):
	authentication_classes = [TokenAuthGet]
	permission_classes = [IsAuthenticated, CanUsePaidParameter]
	throttle_classes = [StaffUserRateThrottle, AnonRateThrottle]

	def check_permissions(self, request):
		"""
		Override the default method to check for 'paid' parameter specifically.
		"""
		paid_param = request.GET.get('paid', None)
		if paid_param and paid_param.lower() not in ['true', 'false']:
			raise PermissionDenied(detail="Invalid 'paid' parameter value.")
		return super().check_permissions(request)
	
	def get(self, request, *args, **kwargs):
		# Extract the 'paid' parameter from the URL
		paid_param = request.GET.get('paid', None)
		
		samples = Utterances.objects.filter(status='Awaiting Review')

		# Use the paid parameter to conditionally filter the samples query
		if paid_param.lower() == 'true':
			samples = (samples.filter(author__profile__paid=True)
			.exclude(author__profile__paid=False)
			.values('author__username')
			.annotate(submission_count=Count('author'))
			)
			return RestResponse({'users': samples})

		total_samples = samples.count()
		status_distribution = samples.values('status').annotate(count=Count('status'))
		top_users_query = (samples.exclude(author__profile__paid=True)
							.values('author__username')
							.annotate(submission_count=Count('author'))
							.order_by('-submission_count')[:10])
		
		avg_time_spent = samples.aggregate(average_time=Avg('time_spent'))['average_time']
		gender_distribution = samples.values('gender').annotate(count=Count('gender'))
		audio_quality_distribution = samples.values('audio_quality').annotate(count=Count('audio_quality'))
		age_distribution = samples.values('age').annotate(count=Count('age'))

		top_users = [
			{
				'author__username': user['author__username'].split("@")[0] if "@" in user['author__username'] else user['author__username'],
				'submission_count': user['submission_count']
			} 
			for user in top_users_query
		]

		emotion_keys = [
			'curious_and_fascinated', 'pensive_and_reflective', 'fearful_and_anxious', 
			'happy_and_energetic', 'calm_and_composed', 'focused_and_attentive', 
			'surprised_and_confused', 'sad_and_despondent', 'romantic_and_passionate',
			'seductive_and_enticing', 'angry_and_irritated', 'persistent_and_determined',
			'discomposed_and_unsettled', 'grumpy_and_cranky', 'disgusted'
		]
		emotion_conditions = [Q(emotion__contains=emotion_key) for emotion_key in emotion_keys]
		emotion_counts = {
			emotion_key: samples.filter(condition).count()
			for emotion_key, condition in zip(emotion_keys, emotion_conditions)
		}

		return RestResponse({
			'total_samples': total_samples,
			'status_distribution': status_distribution,
			'top_users': top_users,
			'avg_time_spent': avg_time_spent,
			'gender_distribution': gender_distribution,
			'audio_quality_distribution': audio_quality_distribution,
			'age_distribution': age_distribution,
			'emotion_counts': emotion_counts,
		})