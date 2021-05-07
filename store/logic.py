from django.db.models import Avg

from store.models import UserBookRelation


def set_rating(obj, realation, par):
    rating = realation.objects.filter(**{par: obj}).aggregate(rating=Avg('rate')).get('rating')
    obj.rating = rating
    obj.save()
