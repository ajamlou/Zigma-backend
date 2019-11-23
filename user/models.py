from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile_picture", db_index=True)
    image = models.ImageField(upload_to='profile_pictures', null=True)

    def __str__(self):
        return self.user.username

    def save(self, *args, **kwargs):
        # delete old file when replacing by updating the file
        try:
            this = UserProfile.objects.get(user=self.user.id)
            if this.image != self.image:
                this.image.delete(save=False)
        except: pass # when new photo then we do nothing, normal case
        super(UserProfile, self).save(*args, **kwargs)

@receiver(post_delete, sender=UserProfile)
def submission_delete(sender, instance, **kwargs):
    instance.image.delete(False)
