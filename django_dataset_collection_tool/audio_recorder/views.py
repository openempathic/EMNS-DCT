from email import header
import random
import json
import re
import csv
import pandas as pd
from collections import defaultdict

from django.http import HttpResponse, HttpResponseForbidden
from django.http.response import JsonResponse

from django.shortcuts import render, get_object_or_404, redirect

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User

from rest_framework.views import APIView
from rest_framework.response import Response as RestResponse
from rest_framework import permissions, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle
from rest_framework.exceptions import PermissionDenied
from .auth import TokenAuthGet

from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator

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
from django.db.models import Count, Avg, F, Q, Sum, Max, Min

from urllib.parse import urlparse


from .models import Utterances, Report
from .forms import RecordingUpdateForm, ImportForm
from .filters import OrderFilter
from .admin import UtterancesResource
from .serializers import UtteranceSerializer

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

def handler400(request, *args, **argv):
	return render(request, 'audio_recorder/400.html')

def handler403(request, *args, **argv):
	return render(request, 'audio_recorder/403.html')

def handler404(request, *args, **argv):
	return render(request, 'audio_recorder/404.html')

def handler500(request, *args, **argv):
	return render(request, 'audio_recorder/500.html')


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
			'sarcasm':self.request.POST.getlist('sarcasm'),
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
			self.object.utterance = self.request.POST.get('utterance')
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

class CanUsePaidParameter(permissions.BasePermission):
	"""
	Custom permission to check if a user belongs to the 'CanViewPaidUsersGroup' and can use the 'paid' parameter.
	"""

	def has_permission(self, request, view):
		paid_param = request.GET.get('paid', None)
		if paid_param:
			return request.user.groups.filter(name='CanViewPaidUsersGroup').exists() or request.user.is_superuser
		return True



################## REST API VIEWS ##################
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
		is_paid = False

		try:
			limit_param = int(request.GET.get('limit', 10))
		except ValueError:
			raise PermissionDenied(detail="Invalid 'limit' parameter value.")

		base_query = Utterances.objects.filter(status='Awaiting Review')
		if paid_param:
			is_paid = paid_param.lower() == 'true'

		# Initial aggregations
		total_samples = base_query.count()
		status_distribution = base_query.values('status').annotate(count=Count('status'))
		avg_time_spent = base_query.aggregate(average_time=Avg('time_spent'))['average_time']
		gender_distribution = base_query.values('gender').annotate(count=Count('gender'))
		audio_quality_distribution = base_query.values('audio_quality').annotate(count=Count('audio_quality'))
		age_distribution = base_query.values('age').annotate(count=Count('age'))

		# Top users
		top_users_query = base_query.filter(author__profile__paid=is_paid).values('author__username').annotate(submission_count=Count('author')).order_by('-submission_count')
		if limit_param > 0:
			top_users_query = top_users_query[:limit_param]
		top_users = [{'author__username': user['author__username'], 'submission_count': user['submission_count']} for user in top_users_query]

		# Emotion and sub-emotion counting (assuming a JSON field or similar structure)
		emotion_counts = defaultdict(int)
		sub_emotion_counts = defaultdict(lambda: defaultdict(int))

		for utterance in base_query.only('emotion'):
			for emotion, sub_emotions in eval(utterance.emotion).items():
				emotion_counts[emotion] += 1
				for sub_emotion in sub_emotions:
					sub_emotion_counts[emotion][sub_emotion] += 1

		return RestResponse({
			'limit': limit_param,
			'total_samples': total_samples,
			'status_distribution': status_distribution,
			'avg_time_spent': avg_time_spent,
			'gender_distribution': gender_distribution,
			'audio_quality_distribution': audio_quality_distribution,
			'age_distribution': age_distribution,
			'top_users': top_users,
			'emotion_counts': dict(emotion_counts),
			'sub_emotion_counts': dict(sub_emotion_counts),
		})

class CreateUtteranceAPI(APIView):
    """
    API view to create a new utterance.

	example json:
	{
    "language": "English",
    "utterance": "This is an example utterance text.",
    "audio_description": "Description of the audio context and background.",
    "video_description": "Description of the video content if applicable.",
    "bg_sounds": "Traffic",
    "accent": "British",
    "emotion": "Happy",
    "status": "Awaiting Review",
    "gender": "Female",
    "audio_quality": "Good",
    "age": "25",
    "arousal": 5,
    "valence": 7,
    "time_spent": 3.5,
    "audio_recording": "https://www.youtube.com/embed/utF9adp1mh8?modestbranding=1&loop=1&start=38&end=50"
	}

    """
    authentication_classes = [TokenAuthGet]
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = UtteranceSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(author=request.user)
            return RestResponse(serializer.data, status=status.HTTP_201_CREATED)
        return RestResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserStatsView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        user = request.user

        # Aggregating various statistics
        user_stats = Utterances.objects.filter(author=user).aggregate(
            total_utterances=Count('id'),
            average_arousal=Avg('arousal'),
            average_valence=Avg('valence'),
            total_time_spent=Sum('time_spent'),
            max_time_spent=Max('time_spent'),
            min_time_spent=Min('time_spent'),
            utterances_by_language=Count('language', distinct=True),
            utterances_by_accent=Count('accent', distinct=True),
            utterances_by_audio_quality=Count('audio_quality', distinct=True),
            utterances_by_gender=Count('gender', distinct=True),
            average_time_spent=Avg('time_spent'),
            latest_utterance_date=Max('date_created'),
            earliest_utterance_date=Min('date_created')
        )

        # Counting utterances per status
        status_distribution = Utterances.objects.filter(author=user).values('status').annotate(count=Count('status'))

        # Counting utterances per language
        language_distribution = Utterances.objects.filter(author=user).values('language').annotate(count=Count('language'))

        # Combining various stats into context
        context = {
            'user_stats': user_stats,
            'status_distribution': status_distribution,
            'language_distribution': language_distribution
        }

        return render(request, 'audio_recorder/stats.html', context)


class DownloadView(APIView):
	authentication_classes = [TokenAuthGet]
	permission_classes = [IsAuthenticated, CanUsePaidParameter]
	throttle_classes = [StaffUserRateThrottle, AnonRateThrottle]
		
	def get(self, request, *args, **kwargs):
		# Add a download parameter check
		download_param = request.GET.get('download', None)
		if download_param not in [None, 'csv', 'parquet']:
			raise PermissionDenied(detail="Invalid 'download' parameter value.")
		
		# Query the database for all utterances
		utterances = Utterances.objects.filter(status='Awaiting Review').values()
		if download_param == 'csv':
			return self.create_csv_response(utterances)
		
		return self.create_parquet_response(utterances)

	def create_csv_response(self, data):
		response = HttpResponse(content_type='text/csv')
		response['Content-Disposition'] = 'attachment; filename="utterances.csv"'
		
		if data:
			writer = csv.writer(response)
			writer.writerow(data[0].keys())  # column headers
			for item in data:
				writer.writerow(item.values())

		return response

	def create_parquet_response(self, data):
		df = pd.DataFrame(data)
		response = HttpResponse(content_type='application/octet-stream')
		response['Content-Disposition'] = 'attachment; filename="utterances.parquet"'
		if not df.empty:
			df.to_parquet(response, index=False)
		
		return response

class GetUtterancesURLsView(APIView):
    authentication_classes = [TokenAuthGet]
    permission_classes = [IsAuthenticated]
    throttle_classes = [StaffUserRateThrottle, AnonRateThrottle]

    def get(self, request, *args, **kwargs):
        # Retrieve the status parameter from the query string
        status_param = request.GET.get('status', 'Awaiting Review')

        # Validate the status parameter
        valid_statuses = ['Pending', 'Awaiting Review', 'Complete', 'Needs Updating']
        if status_param not in valid_statuses:
            return RestResponse({'error': 'Invalid status parameter'}, status=400)

        # Retrieve and validate the limit parameter
        limit_param = request.GET.get('limit', None)
        if limit_param:
            try:
                limit = int(limit_param)
                MaxValueValidator(1000)(limit)  # Assuming a maximum limit of 1000
            except (ValueError, ValidationError):
                return RestResponse({'error': 'Invalid limit parameter'}, status=400)
        else:
            limit = None

        # Query the database for utterances with the specified status
        query = Utterances.objects.filter(status=status_param)
        if limit:
            query = query[:limit]
        utterances = query.values('pk', 'audio_recording')

        # Prepare the data for response
        response_data = [
            {
                'id': utterance['pk'],
                'url': utterance['audio_recording']
            }
            for utterance in utterances
        ]

        return RestResponse(response_data)

def report_utterance(request, utterance_id):
	utterance = get_object_or_404(Utterances, pk=utterance_id)

	if request.method == 'POST':
		reasons = request.POST.getlist('reason')

		# If 'Other' is selected, append the custom reason
		if 'Other' in reasons:
			other_reason = request.POST.get('other_reason', '').strip()
			if other_reason:
				reasons.append(f"Other: {other_reason}")

		# Join the reasons into a single string or use a JSON structure
		reasons_str = ', '.join(reasons)

		# Create and save the report instance
		report = Report(utterance=utterance, reported_by=request.user, reason=reasons_str)
		report.save()

		# Redirect to a success page or back to utterance detail with a success message
		messages.success(request, 'Your report has been submitted successfully.')
		return redirect('random-sample')

	# If not a POST request, or if the object does not exist, redirect to a suitable page
	messages.error(request, 'Invalid request or utterance not found.')
	return redirect('home')  # Replace 'home' with your appropriate view name