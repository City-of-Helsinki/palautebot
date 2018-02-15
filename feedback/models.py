from django.db import models
from django.utils.translation import pgettext_lazy


class Feedback(models.Model):
    SOURCE_TWITTER = 'twitter'

    SOURCE_CHOICES = (
        (SOURCE_TWITTER, 'Twitter'),
    )

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    source = models.CharField(max_length=2048, choices=SOURCE_CHOICES)
    source_id = models.CharField(max_length=2048)
    source_created_at = models.DateTimeField(db_index=True)
    ticket_id = models.CharField(max_length=2048, blank=True, db_index=True)
    user_identifier = models.CharField(max_length=2048, blank=True, db_index=True)

    class Meta:
        verbose_name = pgettext_lazy('singular', 'feedback')
        verbose_name_plural = pgettext_lazy('plural', 'feedback')
        unique_together = ('source', 'source_id')

    def __str__(self):
        return '{} {}'.format(self.source, self.source_id)
