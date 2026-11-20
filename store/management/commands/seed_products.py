from django.core.management.base import BaseCommand
from django.utils.text import slugify
from store.models import Category,Brand,Product

class Command(BaseCommand):
    help="Create 4 fashion categories and 50 sample products in each (200 total)."
    def handle(self,*args,**options):
        collections={
          "Ethnic Wear":["Kurti","Saree","Lehenga","Salwar Suit","Anarkali"],
          "Western Wear":["Top","Dress","Jeans","Skirt","Jumpsuit"],
          "Men's Fashion":["Shirt","T-Shirt","Jeans","Jacket","Trousers"],
          "Accessories":["Handbag","Sneakers","Watch","Sunglasses","Wallet"],
        }
        brands=["StyleNest","UrbanThread","EverydayEdit","AuraWear","ModeHouse"]
        palettes=["Black","Blue","White","Pink","Beige","Green"]
        sizes=["XS,S,M,L,XL","S,M,L,XL,XXL","Free Size"]
        images={
          "Ethnic Wear":"https://images.unsplash.com/photo-1610030469983-98e550d6193c?w=700",
          "Western Wear":"https://images.unsplash.com/photo-1539109136881-3be0616acf4b?w=700",
          "Men's Fashion":"https://images.unsplash.com/photo-1618354691373-d851c5c3a990?w=700",
          "Accessories":"https://images.unsplash.com/photo-1548036328-c9fa89d128fa?w=700",
        }
        total=0
        for category_name,types in collections.items():
            category,_=Category.objects.get_or_create(name=category_name,defaults={"slug":slugify(category_name)})
            for brand_name in brands: Brand.objects.get_or_create(name=brand_name)
            for i in range(50):
                kind=types[i%len(types)]; brand=Brand.objects.get(name=brands[i%len(brands)])
                name=f"{brand.name} {kind} {i+1:02d}"
                slug=slugify(f"{category_name}-{name}")
                Product.objects.update_or_create(slug=slug,defaults={
                    "category":category,"brand":brand,"name":name,
                    "description":f"Discover this versatile {kind.lower()} from {brand.name}. Designed for everyday comfort and effortless style. Check available sizes and colours before ordering.",
                    "image_url":images[category_name],"price":round(499+(i*137)%3500,2),
                    "discount_percent":10+(i%6)*5,"sizes":sizes[i%len(sizes)],
                    "colours":",".join(palettes[:3+(i%4)]),"stock":5+(i%30),
                    "rating":round(3.5+(i%15)/10,1),"is_active":True})
                total+=1
        self.stdout.write(self.style.SUCCESS(f"Seeded/updated {total} sample products."))
