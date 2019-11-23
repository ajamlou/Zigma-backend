from django.db import models
# Create your models here.
class Book(models.Model):
    
    book_title = models.CharField(max_length=250)
    ISBN = models.CharField(max_length=100, blank = True, default='')
    authors = models.CharField(max_length=250, blank = True, default='')
    edition = models.CharField(max_length=100, blank = True, default='')

    def __str__(self):
        return self.book_title + ", " + self.ISBN
