"""Views for the analysis dashboard."""
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Count, Q
from openstates.data.models import Person, Bill, VoteEvent, Jurisdiction, LegislativeSession
from .models import (
    AnalysisJob,
    BillTextAnalysis,
    LegislatorProfile,
    VoteAnalysis,
    DataIngestionLog,
)


def dashboard_home(request):
    """Main dashboard view with navigation menu."""
    context = {
        'recent_jobs': AnalysisJob.objects.all()[:10],
        'recent_ingestions': DataIngestionLog.objects.all()[:5],
        'total_analyses': BillTextAnalysis.objects.count(),
        'total_profiles': LegislatorProfile.objects.count(),
    }
    return render(request, 'analysis/dashboard.html', context)


def data_explorer(request):
    """Interactive data explorer with filters."""
    jurisdictions = Jurisdiction.objects.all().order_by('name')
    
    # Get filter parameters
    selected_jurisdiction = request.GET.get('jurisdiction')
    selected_session = request.GET.get('session')
    
    sessions = []
    if selected_jurisdiction:
        sessions = LegislativeSession.objects.filter(
            jurisdiction_id=selected_jurisdiction
        ).order_by('-identifier')
    
    context = {
        'jurisdictions': jurisdictions,
        'sessions': sessions,
        'selected_jurisdiction': selected_jurisdiction,
        'selected_session': selected_session,
    }
    return render(request, 'analysis/data_explorer.html', context)


def jobs_list(request):
    """List all analysis jobs."""
    jobs = AnalysisJob.objects.all().order_by('-created_at')
    
    # Filter by type if specified
    job_type = request.GET.get('type')
    if job_type:
        jobs = jobs.filter(job_type=job_type)
    
    # Filter by status if specified
    status = request.GET.get('status')
    if status:
        jobs = jobs.filter(status=status)
    
    context = {
        'jobs': jobs,
        'job_type': job_type,
        'status': status,
    }
    return render(request, 'analysis/jobs_list.html', context)


def job_detail(request, job_id):
    """View details of a specific analysis job."""
    job = get_object_or_404(AnalysisJob, id=job_id)
    context = {'job': job}
    return render(request, 'analysis/job_detail.html', context)


def legislator_profile_view(request, person_id):
    """Aggregated legislator profile view."""
    person = get_object_or_404(Person, id=person_id)
    
    # Get or create profile
    try:
        profile = LegislatorProfile.objects.get(person=person)
    except LegislatorProfile.DoesNotExist:
        profile = None
    
    # Get recent votes
    from openstates.data.models import PersonVote
    recent_votes = PersonVote.objects.filter(
        voter_name__icontains=person.name
    ).select_related('vote_event', 'vote_event__bill').order_by(
        '-vote_event__start_date'
    )[:20]
    
    # Get sponsored bills
    from openstates.data.models import BillSponsorship
    sponsored_bills = BillSponsorship.objects.filter(
        name__icontains=person.name
    ).select_related('bill', 'bill__legislative_session').order_by(
        '-bill__legislative_session__identifier'
    )[:20]
    
    # Get bill analyses if available
    analyzed_bills = []
    if profile:
        bill_ids = [s.bill_id for s in sponsored_bills]
        analyzed_bills = BillTextAnalysis.objects.filter(
            bill_id__in=bill_ids
        ).select_related('bill')
    
    context = {
        'person': person,
        'profile': profile,
        'recent_votes': recent_votes,
        'sponsored_bills': sponsored_bills,
        'analyzed_bills': analyzed_bills,
    }
    return render(request, 'analysis/legislator_profile.html', context)


def search_legislators(request):
    """Search for legislators."""
    query = request.GET.get('q', '')
    jurisdiction = request.GET.get('jurisdiction', '')
    
    legislators = Person.objects.all()
    
    if query:
        legislators = legislators.filter(
            Q(name__icontains=query) |
            Q(family_name__icontains=query) |
            Q(given_name__icontains=query)
        )
    
    if jurisdiction:
        legislators = legislators.filter(
            memberships__organization__jurisdiction_id=jurisdiction
        ).distinct()
    
    legislators = legislators.order_by('name')[:50]
    
    context = {
        'legislators': legislators,
        'query': query,
        'jurisdiction': jurisdiction,
        'jurisdictions': Jurisdiction.objects.all().order_by('name'),
    }
    return render(request, 'analysis/search_legislators.html', context)


@login_required
def run_analysis(request):
    """Form to submit new analysis jobs."""
    if request.method == 'POST':
        job_type = request.POST.get('job_type')
        parameters = {}
        
        # Parse parameters based on job type
        if job_type == 'nlp':
            parameters['jurisdiction'] = request.POST.get('jurisdiction')
            parameters['session'] = request.POST.get('session')
        
        # Create job
        job = AnalysisJob.objects.create(
            job_type=job_type,
            status='pending',
            parameters=parameters,
        )
        
        return JsonResponse({
            'status': 'success',
            'job_id': job.id,
            'message': f'Analysis job {job.id} created successfully'
        })
    
    context = {
        'job_types': AnalysisJob.JOB_TYPES,
        'jurisdictions': Jurisdiction.objects.all().order_by('name'),
    }
    return render(request, 'analysis/run_analysis.html', context)


def ingestion_logs(request):
    """View bulk data ingestion logs."""
    logs = DataIngestionLog.objects.all().order_by('-started_at')
    context = {'logs': logs}
    return render(request, 'analysis/ingestion_logs.html', context)


def api_job_status(request, job_id):
    """API endpoint for job status."""
    job = get_object_or_404(AnalysisJob, id=job_id)
    
    progress = 0
    if job.total_items > 0:
        progress = (job.processed_items / job.total_items) * 100
    
    return JsonResponse({
        'id': job.id,
        'job_type': job.job_type,
        'status': job.status,
        'progress': progress,
        'processed_items': job.processed_items,
        'total_items': job.total_items,
        'created_at': job.created_at.isoformat(),
        'error_message': job.error_message,
    })


def api_stats(request):
    """API endpoint for dashboard statistics."""
    stats = {
        'total_bills': Bill.objects.count(),
        'total_votes': VoteEvent.objects.count(),
        'total_people': Person.objects.count(),
        'total_analyses': BillTextAnalysis.objects.count(),
        'total_profiles': LegislatorProfile.objects.count(),
        'total_jobs': AnalysisJob.objects.count(),
        'pending_jobs': AnalysisJob.objects.filter(status='pending').count(),
        'running_jobs': AnalysisJob.objects.filter(status='running').count(),
    }
    return JsonResponse(stats)
