from django.core.management.base import BaseCommand
from django.utils.text import slugify
from store.models import Category, Brand, Product


class Command(BaseCommand):
    help = "Create/update 200 products with a different image URL for every product."

    def handle(self, *args, **options):
        collections = {
            "Ethnic Wear": {"types": ["Kurti", "Saree", "Lehenga", "Salwar Suit", "Anarkali"], "tag": "indian,women,fashion"},
            "Western Wear": {"types": ["Top", "Dress", "Jeans", "Skirt", "Jumpsuit"], "tag": "women,western,fashion"},
            "Men's Fashion": {"types": ["Shirt", "T-Shirt", "Jeans", "Jacket", "Trousers"], "tag": "men,fashion,clothing"},
            "Accessories": {"types": ["Handbag", "Sneakers", "Watch", "Sunglasses", "Wallet"], "tag": "fashion,accessories,handbag"},
        }
        brands = ["StyleNest", "UrbanThread", "EverydayEdit", "AuraWear", "ModeHouse"]
        palettes = ["Black", "Blue", "White", "Pink", "Beige", "Green"]
        sizes = ["XS,S,M,L,XL", "S,M,L,XL,XXL", "Free Size"]
        total = 0
        for category_index, (category_name, config) in enumerate(collections.items()):
            category, _ = Category.objects.get_or_create(name=category_name, defaults={"slug": slugify(category_name)})
            for brand_name in brands:
                Brand.objects.get_or_create(name=brand_name)
            for i in range(50):
                kind = config["types"][i % len(config["types"])]
                brand = Brand.objects.get(name=brands[i % len(brands)])
                name = f"{brand.name} {kind} {i + 1:02d}"
                slug = slugify(f"{category_name}-{name}")
                unique_lock = 260001 + category_index * 50 + i
                image_url = f"https://loremflickr.com/700/900/{config['tag']}?lock={unique_lock}"
                Product.objects.update_or_create(slug=slug, defaults={
                    "category": category, "brand": brand, "name": name,
                    "description": f"Discover this {kind.lower()} from {brand.name}. A stylish addition to your {category_name.lower()} collection. Check the available sizes and colours before ordering.",
                    "image_url": image_url, "image": None,
                    "price": round(499 + (i * 137) % 3500, 2),
                    "discount_percent": 10 + (i % 6) * 5,
                    "sizes": sizes[i % len(sizes)], "colours": ",".join(palettes[:3 + (i % 4)]),
                    "stock": 5 + (i % 30), "rating": round(3.5 + (i % 15) / 10, 1), "is_active": True,
                })
                total += 1
        self.stdout.write(self.style.SUCCESS(f"Updated {total} products. Each product now has its own image URL."))
