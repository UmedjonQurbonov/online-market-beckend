from django.db.models import Avg

def update_shop_rating(shop):
    avg = shop.review_set.aggregate(r=Avg("rating"))["r"]

    shop.rating = int(avg or 0)
    shop.save(update_fields=["rating"])