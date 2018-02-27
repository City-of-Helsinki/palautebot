from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _


class TwitterEntryQuerySet(models.QuerySet):
    def get_latest_source_id(self):
        try:
            return self.latest('source_created_at').source_id
        except self.model.DoesNotExist:
            return None


class TwitterEntry(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    source_id = models.CharField(max_length=255)
    source_created_at = models.DateTimeField(db_index=True)

    objects = TwitterEntryQuerySet.as_manager()

    class Meta:
        abstract = True

    def __str__(self):
        return self.source_id


class Tweet(TwitterEntry):
    user_identifier = models.CharField(max_length=255, blank=True, db_index=True)

    class Meta:
        verbose_name = _('tweet')
        verbose_name_plural = _('tweets')


class DirectMessage(TwitterEntry):
    class Meta:
        verbose_name = _('direct message')
        verbose_name_plural = _('direct messages')


class Feedback(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True, db_index=True)

    ticket_id = models.CharField(verbose_name=_('ticket ID'), max_length=255, unique=True)
    current_comment = models.TextField(verbose_name=_('current comment'), blank=True)
    tweet = models.ForeignKey(Tweet, verbose_name=_('tweet'), on_delete=models.CASCADE)

    class Meta:
        verbose_name = _('feedback item')
        verbose_name_plural = _('feedback items')

    def __str__(self):
        return self.ticket_id

    def get_url(self):
        return settings.OPEN311_FEEDBACK_URL.format(self.ticket_id)
