from django.conf import settings
from django.db import models
from django.db.models import Q
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone


class ItemQuerySet(models.QuerySet):
    def search(self, query):
        if not query:
            return self
        return self.filter(
            Q(title__icontains=query)
            | Q(description__icontains=query)
            | Q(location__icontains=query)
            | Q(contact_info__icontains=query)
        )

    def lost(self):
        return self.filter(status=Item.Status.LOST)

    def found(self):
        return self.filter(status=Item.Status.FOUND)


class Item(models.Model):
    class Status(models.TextChoices):
        LOST = 'lost', 'Lost'
        FOUND = 'found', 'Found'

    title = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    location = models.CharField(max_length=120, blank=True)
    contact_info = models.CharField(max_length=120)
    status = models.CharField(max_length=5, choices=Status.choices, default=Status.LOST)
    reporter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='reported_items',
    )
    claimed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='claimed_items',
    )
    claimed_at = models.DateTimeField(null=True, blank=True)
    is_resolved = models.BooleanField(default=False)
    resolved_at = models.DateTimeField(null=True, blank=True)
    reported_at = models.DateTimeField(auto_now_add=True)

    objects = ItemQuerySet.as_manager()

    class Meta:
        ordering = ['-reported_at']

    def __str__(self):
        return f"{self.title} ({self.get_status_display()})"

    @property
    def badge_class(self):
        return 'danger' if self.status == self.Status.LOST else 'success'

    @property
    def is_claimable(self):
        return (
            self.status == self.Status.FOUND
            and not self.is_resolved
            and self.claimed_by is None
        )

    @property
    def reporter_name(self):
        if self.reporter:
            return self.reporter.get_full_name() or self.reporter.email
        return self.contact_info

    def mark_claimed(self, user):
        self.claimed_by = user
        self.claimed_at = timezone.now()
        self.is_resolved = True
        self.resolved_at = self.claimed_at
        self.save()


class Profile(models.Model):
    class Role(models.TextChoices):
        STUDENT = 'student', 'Student'
        STAFF = 'staff', 'Staff'

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile',
    )
    campus_role = models.CharField(max_length=10, choices=Role.choices, default=Role.STUDENT)
    verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} profile"

    @property
    def badge_label(self):
        if self.verified:
            return f"Verified {self.get_campus_role_display()}"
        return 'Campus member'

    @property
    def reputation(self):
        points = self.user.reported_items.count() * 5
        points += self.user.claim_requests.filter(status=ClaimRequest.Status.ACCEPTED).count() * 10
        return points


class ClaimRequest(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        ACCEPTED = 'accepted', 'Accepted'
        DECLINED = 'declined', 'Declined'

    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='claim_requests')
    requester = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='claim_requests',
    )
    message = models.TextField(blank=True)
    status = models.CharField(max_length=8, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    responded_at = models.DateTimeField(null=True, blank=True)
    responded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='processed_claim_requests',
    )

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Claim request by {self.requester.email} for {self.item.title}"

    def accept(self, responder):
        self.status = self.Status.ACCEPTED
        self.responded_by = responder
        self.responded_at = timezone.now()
        self.save()
        self.item.mark_claimed(self.requester)

    def decline(self, responder):
        self.status = self.Status.DECLINED
        self.responded_by = responder
        self.responded_at = timezone.now()
        self.save()


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
