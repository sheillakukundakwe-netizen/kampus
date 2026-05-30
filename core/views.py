from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CampusRegistrationForm, ClaimRequestForm, ItemReportForm
from .models import ClaimRequest, Item


def home(request):
    query = request.GET.get('q', '')
    filter_status = request.GET.get('status', '')
    items = Item.objects.all().search(query)

    if filter_status == Item.Status.LOST:
        items = items.lost()
    elif filter_status == Item.Status.FOUND:
        items = items.found()

    return render(
        request,
        'core/home.html',
        {
            'items': items,
            'query': query,
            'filter_status': filter_status,
        },
    )


def landing(request):
    lost_count = Item.objects.filter(status=Item.Status.LOST).count()
    found_count = Item.objects.filter(status=Item.Status.FOUND).count()
    recent = Item.objects.all()[:6]
    return render(
        request,
        'core/landing.html',
        {
            'lost_count': lost_count,
            'found_count': found_count,
            'recent': recent,
        },
    )


def register(request):
    if request.user.is_authenticated:
        return redirect('core:home')

    if request.method == 'POST':
        form = CampusRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Welcome! Your campus account is ready.')
            return redirect('core:home')
    else:
        form = CampusRegistrationForm()

    return render(request, 'core/register.html', {'form': form})


@login_required
def report_item(request, status):
    if request.method == 'POST':
        form = ItemReportForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            item.status = status
            item.reporter = request.user
            item.save()
            messages.success(request, f"{item.get_status_display()} report created. Campus community notified.")
            return redirect('core:home')
    else:
        form = ItemReportForm()

    return render(
        request,
        'core/report_form.html',
        {
            'form': form,
            'status': status,
        },
    )


def report_lost(request):
    return report_item(request, Item.Status.LOST)


def report_found(request):
    return report_item(request, Item.Status.FOUND)


def item_detail(request, pk):
    item = get_object_or_404(Item, pk=pk)
    claim_form = None
    existing_claim = None
    pending_requests = None

    if request.user.is_authenticated:
        if item.is_claimable and item.reporter != request.user:
            existing_claim = item.claim_requests.filter(requester=request.user).first()
            if not existing_claim:
                claim_form = ClaimRequestForm()
        if request.user == item.reporter:
            pending_requests = item.claim_requests.filter(status=ClaimRequest.Status.PENDING)

    return render(
        request,
        'core/item_detail.html',
        {
            'item': item,
            'claim_form': claim_form,
            'existing_claim': existing_claim,
            'pending_requests': pending_requests,
        },
    )


@login_required
def claim_item(request, pk):
    item = get_object_or_404(Item, pk=pk)
    if not item.is_claimable or item.reporter == request.user:
        messages.error(request, 'You cannot request a claim for this item.')
        return redirect('core:item_detail', pk=pk)

    if request.method == 'POST':
        form = ClaimRequestForm(request.POST)
        if form.is_valid():
            claim = form.save(commit=False)
            claim.item = item
            claim.requester = request.user
            claim.save()
            messages.success(request, 'Claim request submitted. The reporter can now approve it.')
            return redirect('core:item_detail', pk=pk)
    else:
        form = ClaimRequestForm()

    return render(request, 'core/claim_form.html', {'item': item, 'form': form})


@login_required
def respond_claim_request(request, pk):
    claim = get_object_or_404(ClaimRequest, pk=pk)
    if request.user != claim.item.reporter:
        messages.error(request, 'Only the item reporter can respond to claim requests.')
        return redirect('core:item_detail', pk=claim.item.pk)

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'accept':
            claim.accept(request.user)
            messages.success(request, 'Claim request accepted and item marked as resolved.')
        elif action == 'decline':
            claim.decline(request.user)
            messages.info(request, 'Claim request declined.')
        else:
            messages.error(request, 'Invalid action.')

    return redirect('core:item_detail', pk=claim.item.pk)


@login_required
def profile(request):
    profile = request.user.profile
    reports = request.user.reported_items.all()
    requests = request.user.claim_requests.all()
    return render(
        request,
        'core/profile.html',
        {
            'profile': profile,
            'reports': reports,
            'requests': requests,
        },
    )
