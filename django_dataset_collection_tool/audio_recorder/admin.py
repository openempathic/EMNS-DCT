from django.contrib import admin
from .models import Utterances, Report
from import_export import resources
from import_export.admin import ImportExportModelAdmin


class UtterancesResource(resources.ModelResource):
    class Meta:
        model = Utterances
        fields = ['utterance', 'prosody', 'author_id', 'age', 'gender', 'date_created', 'status', 'audio_recording']

@admin.register(Utterances)
class UtterancesAdmin(ImportExportModelAdmin):
    resource_class = UtterancesResource
    list_display = ('id', 'author', 'date_created', 'status')
    search_fields = ('id', 'utterance', 'author__username', 'author__email', 'author__first_name', 'author__last_name')
    list_filter = ('status', 'date_created')
@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('utterance', 'reported_by', 'reason', 'date_reported')
    search_fields = ('reason', 'utterance__id', 'reported_by__username')
    list_filter = ('date_reported',)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related('utterance', 'reported_by')