from django.core.management.base import BaseCommand
from django.utils.text import slugify
from store.models import Category, Brand, Product


class Command(BaseCommand):
    help = "Create 4 fashion categories and 50 sample products in each (200 total)."

    def handle(self, *args, **options):
        collections = {
            "Ethnic Wear": ["Kurti", "Saree", "Lehenga", "Salwar Suit", "Anarkali"],
            "Western Wear": ["Top", "Dress", "Jeans", "Skirt", "Jumpsuit"],
            "Men's Fashion": ["Shirt", "T-Shirt", "Jeans", "Jacket", "Trousers"],
            "Accessories": ["Handbag", "Sneakers", "Watch", "Sunglasses", "Wallet"],
        }
        photos = {
            "Ethnic Wear": ["1610030469983-98e550d6193c","1583391733956-6c78276477e3","1617627143750-d86bc21e42bb","1597983073493-88cd35cf93b0","1594633312681-425c7b97ccd1","1610189012906-4c5f7f3a7f3b"],
            "Western Wear": ["1539109136881-3be0616acf4b","1483985988355-763728e1935b","1529139574466-a303027c1d8b","1551232864-3f0890e580d9","1595777457583-95e059d581b8","1515886657613-9f3515b0c78f","1485230895905-ec40ba36b9bc","1509631179647-0177331693ae"],
            "Men's Fashion": ["1618354691373-d851c5c3a990","1516257984-b1b4d707412e","1617137968427-85924c800a22","1598033129183-c4f50c736f10","1521572163474-6864f9cf17ab","1516826957135-700dedea698c"],
            "Accessories": ["1548036328-c9fa89d128fa","1584917865442-de89df76afd3","1590874103328-eac38a683ce7","1553062407-98eeb64c6a62","1523275335684-37898b6baf30","1526170375885-4d8ecf77b99f","1511499767150-a48a237f0083"],
        }
        brands = ["StyleNest", "UrbanThread", "EverydayEdit", "AuraWear", "ModeHouse"]
        palettes = ["Black", "Blue", "White", "Pink", "Beige", "Green"]
        sizes = ["XS,S,M,L,XL", "S,M,L,XL,XXL", "Free Size"]
        total = 0
        for category_name, types in collections.items():
            category, _ = Category.objects.get_or_create(name=category_name, defaults={"slug": slugify(category_name)})
            for brand_name in brands:
                Brand.objects.get_or_create(name=brand_name)
            for i in range(50):
                kind = types[i % len(types)]
                brand = Brand.objects.get(name=brands[i % len(brands)])
                name = f"{brand.name} {kind} {i + 1:02d}"
                slug = slugify(f"{category_name}-{name}")
                photo_id = photos[category_name][i % len(photos[category_name])]
                image_url = f"https://images.unsplash.com/photo-{photo_id}?auto=format&fit=crop&w=700&q=85"
                Product.objects.update_or_create(slug=slug, defaults={
                    "category": category, "brand": brand, "name": name,
                    "description": f"Discover this versatile {kind.lower()} from {brand.name}. Designed for everyday comfort and effortless style. Check available sizes and colours before ordering.",
                    "image_url": image_url, "price": round(499 + (i * 137) % 3500, 2),
                    "discount_percent": 10 + (i % 6) * 5, "sizes": sizes[i % len(sizes)],
                    "colours": ",".join(palettes[:3 + (i % 4)]), "stock": 5 + (i % 30),
                    "rating": round(3.5 + (i % 15) / 10, 1), "is_active": True,
                })
                total += 1
        self.stdout.write(self.style.SUCCESS(f"Seeded/updated {total} sample products."))