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


def micro_statements_explorer(request):
    """
    View for exploring and analyzing micro-statements.
    Supports filtering and binning by year, jurisdiction, party, district.
    """
    from analysis.models import MicroStatement
    from django.db.models import Count, Avg, Q
    
    # Get filter parameters
    year = request.GET.get('year')
    jurisdiction = request.GET.get('jurisdiction')
    party = request.GET.get('party')
    district = request.GET.get('district')
    sentiment = request.GET.get('sentiment')
    statement_type = request.GET.get('statement_type')
    
    # Build query
    statements = MicroStatement.objects.all()
    
    if year:
        statements = statements.filter(session_year=int(year))
    if jurisdiction:
        statements = statements.filter(jurisdiction=jurisdiction)
    if party:
        statements = statements.filter(party__icontains=party)
    if district:
        statements = statements.filter(district__icontains=district)
    if sentiment:
        statements = statements.filter(sentiment=sentiment)
    if statement_type:
        statements = statements.filter(statement_type=statement_type)
    
    # Get statistics
    total_count = statements.count()
    
    # Bin by year
    by_year = statements.values('session_year').annotate(
        count=Count('id'),
        avg_sentiment=Avg('sentiment_score')
    ).order_by('-session_year')
    
    # Bin by party
    by_party = statements.exclude(party='').values('party').annotate(
        count=Count('id'),
        avg_sentiment=Avg('sentiment_score')
    ).order_by('-count')[:10]
    
    # Bin by jurisdiction
    by_jurisdiction = statements.exclude(jurisdiction='').values('jurisdiction').annotate(
        count=Count('id'),
        avg_sentiment=Avg('sentiment_score')
    ).order_by('-count')[:15]
    
    # Bin by sentiment
    by_sentiment = statements.values('sentiment').annotate(
        count=Count('id')
    ).order_by('sentiment')
    
    # Get recent statements
    recent_statements = statements.select_related('bill').order_by('-extracted_at')[:50]
    
    # Get available filter options
    available_years = MicroStatement.objects.exclude(
        session_year__isnull=True
    ).values_list('session_year', flat=True).distinct().order_by('-session_year')
    
    available_parties = MicroStatement.objects.exclude(
        party=''
    ).values_list('party', flat=True).distinct().order_by('party')[:20]
    
    context = {
        'total_count': total_count,
        'by_year': by_year,
        'by_party': by_party,
        'by_jurisdiction': by_jurisdiction,
        'by_sentiment': by_sentiment,
        'recent_statements': recent_statements,
        'available_years': available_years,
        'available_parties': available_parties,
        'jurisdictions': Jurisdiction.objects.all().order_by('name'),
        'sentiment_choices': MicroStatement.SENTIMENT_CHOICES,
        'statement_type_choices': MicroStatement.STATEMENT_TYPES,
        # Current filters
        'selected_year': year,
        'selected_jurisdiction': jurisdiction,
        'selected_party': party,
        'selected_district': district,
        'selected_sentiment': sentiment,
        'selected_statement_type': statement_type,
    }
    
    return render(request, 'analysis/micro_statements_explorer.html', context)


def micro_statement_detail(request, statement_id):
    """View detailed information about a specific micro-statement."""
    from analysis.models import MicroStatement
    
    statement = get_object_or_404(
        MicroStatement.objects.select_related('bill', 'bill__legislative_session'),
        id=statement_id
    )
    
    # Find similar statements (by actor or target)
    similar_statements = MicroStatement.objects.filter(
        Q(actor__icontains=statement.actor.split()[0]) |
        Q(target__icontains=statement.target.split()[0])
    ).exclude(id=statement.id).order_by('-confidence_score')[:10]
    
    context = {
        'statement': statement,
        'similar_statements': similar_statements,
    }
    
    return render(request, 'analysis/micro_statement_detail.html', context)


def api_micro_statements_comparison(request):
    """
    API endpoint for comparing micro-statements across different dimensions.
    Returns aggregated statistics for comparison visualizations.
    """
    from analysis.models import MicroStatement
    from django.db.models import Count, Avg, F
    
    comparison_type = request.GET.get('type', 'year_party')
    
    if comparison_type == 'year_party':
        # Compare across years and parties
        data = MicroStatement.objects.exclude(
            party=''
        ).exclude(
            session_year__isnull=True
        ).values('session_year', 'party').annotate(
            count=Count('id'),
            positive_count=Count('id', filter=Q(sentiment='positive')),
            negative_count=Count('id', filter=Q(sentiment='negative')),
            neutral_count=Count('id', filter=Q(sentiment='neutral')),
            avg_sentiment=Avg('sentiment_score')
        ).order_by('session_year', 'party')
        
    elif comparison_type == 'jurisdiction_year':
        # Compare across jurisdictions and years
        data = MicroStatement.objects.exclude(
            jurisdiction=''
        ).exclude(
            session_year__isnull=True
        ).values('session_year', 'jurisdiction').annotate(
            count=Count('id'),
            positive_count=Count('id', filter=Q(sentiment='positive')),
            negative_count=Count('id', filter=Q(sentiment='negative')),
            avg_sentiment=Avg('sentiment_score')
        ).order_by('session_year', 'jurisdiction')
        
    elif comparison_type == 'statement_type':
        # Compare statement types
        data = MicroStatement.objects.values('statement_type', 'sentiment').annotate(
            count=Count('id')
        ).order_by('statement_type', 'sentiment')
        
    else:
        return JsonResponse({'error': 'Invalid comparison type'}, status=400)
    
    return JsonResponse({
        'comparison_type': comparison_type,
        'data': list(data)
    })


def api_micro_statements_search(request):
    """
    API endpoint for searching micro-statements by text content.
    """
    from analysis.models import MicroStatement
    
    query = request.GET.get('q', '')
    limit = int(request.GET.get('limit', 50))
    
    if not query:
        return JsonResponse({'error': 'Query parameter required'}, status=400)
    
    statements = MicroStatement.objects.filter(
        Q(statement_text__icontains=query) |
        Q(actor__icontains=query) |
        Q(action__icontains=query) |
        Q(target__icontains=query)
    ).select_related('bill').order_by('-confidence_score')[:limit]
    
    results = []
    for stmt in statements:
        results.append({
            'id': stmt.id,
            'actor': stmt.actor,
            'action': stmt.action,
            'target': stmt.target,
            'statement_text': stmt.statement_text,
            'sentiment': stmt.sentiment,
            'sentiment_score': stmt.sentiment_score,
            'bill_id': stmt.bill.identifier if stmt.bill else None,
            'jurisdiction': stmt.jurisdiction,
            'session_year': stmt.session_year,
            'party': stmt.party,
            'confidence_score': stmt.confidence_score,
        })
    
    return JsonResponse({
        'query': query,
        'count': len(results),
        'results': results
    })
