from django.db import models
from django.utils.timezone import now
from django.contrib.auth.models import User
from django.db.models.signals import post_delete
from django.dispatch import receiver

class Advert(models.Model):
    STATE = (
        ('A','Active'),
        ('I','Inactive'),
    )
    TRANSACTION_TYPE = (
        ('S','Selling'),
        ('B','Buying'),
    )
    CONDITION = (
        ('1','Nyskick'),
        ('2','Mycket gott skick'),
        ('3','Gott skick'),
        ('4','Hyggligt skick'),
        ('5','Dåligt skick'),
        ('6','Ej angett'),
    )

    owner=models.ForeignKey(User, on_delete=models.CASCADE, related_name="adverts", db_index=True)
    responder=models.ForeignKey(User, on_delete=models.SET_NULL, related_name="accepted_adverts", null = True, blank=True)
    book_title = models.CharField(max_length=250, db_index=True)
    ISBN = models.CharField(max_length=100, blank = True, default='')
    price = models.PositiveSmallIntegerField()
    authors = models.CharField(max_length=250, blank = True, default='')
    edition = models.CharField(max_length=100, blank = True, default='')
    condition = models.CharField(max_length=1, choices=CONDITION, default='6')
    state = models.CharField(max_length=1, choices=STATE, default='A')
    transaction_type = models.CharField(max_length=1, choices=TRANSACTION_TYPE, default='S')
    contact_info = models.CharField(max_length=100)
    created_at = models.DateTimeField(default=now)

    def __str__(self):
        return self.book_title + ' - ' + self.contact_info


class AdvertImage(models.Model):
    advert = models.ForeignKey(Advert, on_delete=models.CASCADE, related_name="image", null=True, db_index=True)
    image = models.ImageField(upload_to = 'ad_images', null=True)
    
    def __str__(self):
        return self.image.name + str(self.advert)

#Tar bort filen om objektet AdvertImage raderas
@receiver(post_delete, sender=AdvertImage)
def submission_delete(sender, instance, **kwargs):
    instance.image.delete(False)
