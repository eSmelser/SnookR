from django.db import models


class Statusable(models.Model):
    PENDING = 'P'
    APPROVED = 'A'
    DECLINED = 'D'
    STATUS_CHOICES = (
        (PENDING, 'Pending'),
        (APPROVED, 'Approved'),
        (DECLINED, 'Declined')
    )

    status = models.CharField(default=PENDING, max_length=1, choices=STATUS_CHOICES)

    class Meta:
        abstract = True

    @property
    def is_closed(self):
        return self.status != Statusable.PENDING

    def human_readable_status(self):
        for k, v in Statusable.STATUS_CHOICES:
            if self.status == k:
                return v

    def approve(self):
        self.status = Statusable.APPROVED
        self.save()

    def decline(self):
        self.status = Statusable.DECLINED
        self.save()

    def is_approved(self):
        return self.status == Statusable.APPROVED

    def is_pending(self):
        return self.status == Statusable.PENDING

    def is_declined(self):
        return self.status ==Statusable.DECLINED

class StatusableQuerySet(models.QuerySet):
    def pending(self):
        return self.filter(status=Statusable.PENDING)

    def approved(self):
        return self.filter(status=Statusable.APPROVED)

    def declined(self):
        return self.filter(status=Statusable.DECLINED)
