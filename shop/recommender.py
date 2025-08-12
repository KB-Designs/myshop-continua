import redis
from django.conf import settings
from .models import Product

# CONNECT TO REDIS
r = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB
)

class Recommender(object):
    def get_product_key(self, id):
        return f'product:{id}:purchased_with'
    
    def products_bought(self, products):
        product_ids = [p.id for p in products]
        for product_id in product_ids:
            for with_id in product_ids:
                if product_id != with_id:
                    # Increment score for products bought together
                    r.zincrby(self.get_product_key(product_id), 1, with_id) 
                
    def suggest_products_for(self, products, max_results=6):
        if not products:
            return []  # No products to suggest
        
        product_ids = [p.id for p in products]
        
        if len(products) == 1:
            # Only one product — fetch its recommendations directly
            suggestions = r.zrange(
                self.get_product_key(product_ids[0]),
                0, -1, desc=True
            )[:max_results]
        else:
            # Multiple products — combine their recommendation scores
            flat_ids = ''.join(str(id) for id in product_ids)
            tmp_key = f'tmp_{flat_ids}'
            keys = [self.get_product_key(id) for id in product_ids]

            # Store combined scores in a temporary key
            r.zunionstore(tmp_key, keys, aggregate='SUM')

            # Remove IDs of the products we are making suggestions for
            r.zrem(tmp_key, *product_ids)

            # Fetch top results
            suggestions = r.zrange(tmp_key, 0, -1, desc=True)[:max_results]

            # Delete temporary key
            r.delete(tmp_key)
        
        suggested_product_ids = [int(id) for id in suggestions]

        # Get suggested products from DB and keep order
        suggested_products = list(Product.objects.filter(id__in=suggested_product_ids))
        suggested_products.sort(key=lambda x: suggested_product_ids.index(x.id))
        
        return suggested_products
    
    def clear_purchases(self):
        for id in Product.objects.values_list('id', flat=True):
            r.delete(self.get_product_key(id))
