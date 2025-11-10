"""Admin interface for analysis models."""
from django.contrib import admin
from .models import (
    AnalysisJob,
    BillTextAnalysis,
    LegislatorProfile,
    VoteAnalysis,
    DataIngestionLog,
)


@admin.register(AnalysisJob)
class AnalysisJobAdmin(admin.ModelAdmin):
    list_display = ('id', 'job_type', 'status', 'created_at', 'progress_display')
    list_filter = ('job_type', 'status', 'created_at')
    search_fields = ('id', 'parameters')
    readonly_fields = ('created_at', 'updated_at')
    
    def progress_display(self, obj):
        if obj.total_items > 0:
            percent = (obj.processed_items / obj.total_items) * 100
            return f"{obj.processed_items}/{obj.total_items} ({percent:.1f}%)"
        return "N/A"
    progress_display.short_description = "Progress"


@admin.register(BillTextAnalysis)
class BillTextAnalysisAdmin(admin.ModelAdmin):
    list_display = ('bill', 'sentiment_label', 'sentiment_score', 'analyzed_at')
    list_filter = ('sentiment_label', 'analyzed_at')
    search_fields = ('bill__identifier', 'bill__title', 'summary')
    readonly_fields = ('analyzed_at',)


@admin.register(LegislatorProfile)
class LegislatorProfileAdmin(admin.ModelAdmin):
    list_display = ('person', 'total_votes', 'total_sponsored_bills', 'updated_at')
    search_fields = ('person__name',)
    readonly_fields = ('updated_at',)


@admin.register(VoteAnalysis)
class VoteAnalysisAdmin(admin.ModelAdmin):
    list_display = ('vote_event', 'party_line_score', 'bipartisan_score', 'analyzed_at')
    list_filter = ('analyzed_at',)
    readonly_fields = ('analyzed_at',)


@admin.register(DataIngestionLog)
class DataIngestionLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'database_type', 'status', 'started_at', 'stats_display')
    list_filter = ('status', 'database_type', 'started_at')
    readonly_fields = ('started_at', 'completed_at')
    
    def stats_display(self, obj):
        return f"Bills: {obj.total_bills}, Votes: {obj.total_votes}, People: {obj.total_people}"
    stats_display.short_description = "Stats"
