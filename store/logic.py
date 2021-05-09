from django.db.models import Avg


def set_rating(obj, relation, par):
    rating = relation.objects.filter(**{par: obj}).aggregate(rating=Avg('rate')).get('rating')
    obj.rating = rating
    obj.save()
