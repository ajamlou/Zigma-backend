from django.contrib.auth.models import User

from django.core.management.base import BaseCommand

    #class Command(NoArgsCommand):
class Command(BaseCommand):

    #def handle_noargs(self, **options):
    def handle(self, *args, **options):
        queryset = User.objects.all()
        for user in queryset:
            if user.id != 1:
                user.delete()
            else:
                for advert in user.adverts.all():
                    advert.delete()
