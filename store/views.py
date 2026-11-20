import uuid
from datetime import timedelta
from decimal import Decimal
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Q, Avg, Sum, Count
from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST
from .models import Category, Product, Brand, Address, Coupon, Order, OrderItem, Review, ReturnRequest, Notification
from .forms import RegisterForm, AddressForm, ReviewForm, ReturnForm
from .utils import send_order_email

def home(request):
    featured=Product.objects.filter(is_active=True).select_related("category","brand").order_by("-created_at")[:12]
    categories=Category.objects.all()
    recently=[]
    ids=request.session.get("recently_viewed",[])[:6]
    if ids: recently=list(Product.objects.filter(id__in=ids,is_active=True))
    return render(request,"store/home.html",{"featured":featured,"categories":categories,"recently":recently})

def product_list(request,slug=None):
    products=Product.objects.filter(is_active=True).select_related("category","brand")
    category=get_object_or_404(Category,slug=slug) if slug else None
    if category: products=products.filter(category=category)
    q=request.GET.get("q","").strip()
    if q: products=products.filter(Q(name__icontains=q)|Q(description__icontains=q)|Q(brand__name__icontains=q))
    brand=request.GET.get("brand")
    if brand: products=products.filter(brand__name__iexact=brand)
    size=request.GET.get("size")
    if size: products=products.filter(sizes__icontains=size)
    colour=request.GET.get("colour")
    if colour: products=products.filter(colours__icontains=colour)
    max_price=request.GET.get("max_price")
    if max_price:
        try: products=products.filter(price__lte=Decimal(max_price))
        except: pass
    if request.GET.get("sort")=="price_low": products=products.order_by("price")
    elif request.GET.get("sort")=="price_high": products=products.order_by("-price")
    elif request.GET.get("sort")=="discount": products=products.order_by("-discount_percent")
    elif request.GET.get("sort")=="rating": products=products.order_by("-rating")
    else: products=products.order_by("-created_at")
    page=Paginator(products,12).get_page(request.GET.get("page"))
    return render(request,"store/product_list.html",{"page":page,"category":category,"q":q,"brands":Brand.objects.all()})

def product_detail(request,slug):
    product=get_object_or_404(Product,slug=slug,is_active=True)
    recent=request.session.get("recently_viewed",[])
    request.session["recently_viewed"]=([product.id]+[x for x in recent if x!=product.id])[:8]
    related=Product.objects.filter(category=product.category,is_active=True).exclude(id=product.id)[:4]
    reviews=product.reviews.select_related("user").order_by("-created_at")
    form=ReviewForm()
    return render(request,"store/product_detail.html",{"product":product,"related":related,"reviews":reviews,"form":form})

def register(request):
    if request.method=="POST":
        form=RegisterForm(request.POST)
        if form.is_valid():
            user=form.save(); login(request,user)
            messages.success(request,"Your account has been created.")
            return redirect("home")
    else: form=RegisterForm()
    return render(request,"store/form_page.html",{"form":form,"title":"Create account","button":"Register"})

@login_required
def profile(request):
    orders=Order.objects.filter(user=request.user).order_by("-created_at")
    addresses=Address.objects.filter(user=request.user)
    notifications=Notification.objects.filter(user=request.user).order_by("-created_at")[:10]
    return render(request,"store/profile.html",{"orders":orders,"addresses":addresses,"notifications":notifications})

@login_required
def add_address(request):
    if request.method=="POST":
        form=AddressForm(request.POST)
        if form.is_valid():
            address=form.save(commit=False); address.user=request.user; address.save()
            messages.success(request,"Address saved.")
            return redirect("checkout")
    else: form=AddressForm()
    return render(request,"store/form_page.html",{"form":form,"title":"Add delivery address","button":"Save address"})

def _cart_products(request):
    cart=request.session.get("cart",{})
    ids=[int(k) for k in cart.keys() if str(k).isdigit()]
    products=Product.objects.filter(id__in=ids,is_active=True)
    rows=[]; subtotal=Decimal("0")
    for p in products:
        data=cart.get(str(p.id),{})
        qty=max(1,min(int(data.get("quantity",1)),20))
        size=data.get("size",""); colour=data.get("colour","")
        line=p.selling_price*qty; subtotal+=line
        rows.append({"product":p,"quantity":qty,"size":size,"colour":colour,"line_total":line})
    return rows,subtotal

def cart_view(request):
    rows,subtotal=_cart_products(request)
    return render(request,"store/cart.html",{"rows":rows,"subtotal":subtotal})

@require_POST
def add_to_cart(request,product_id):
    product=get_object_or_404(Product,id=product_id,is_active=True)
    if product.stock<1:
        messages.error(request,"This product is out of stock."); return redirect("product_detail",slug=product.slug)
    cart=request.session.get("cart",{})
    key=str(product.id); old=cart.get(key,{"quantity":0})
    try: qty=max(1,min(20,int(request.POST.get("quantity",1))))+int(old.get("quantity",0))
    except: qty=1
    cart[key]={"quantity":min(qty,product.stock),"size":request.POST.get("size",""),"colour":request.POST.get("colour","")}
    request.session["cart"]=cart; request.session.modified=True
    messages.success(request,"Added to your bag.")
    return redirect("cart")

@require_POST
def update_cart(request,product_id):
    cart=request.session.get("cart",{}); key=str(product_id)
    if key in cart:
        try: qty=int(request.POST.get("quantity",1))
        except: qty=1
        if qty<=0: cart.pop(key)
        else:
            p=Product.objects.filter(id=product_id).first()
            cart[key]["quantity"]=min(qty,p.stock if p else 20,20)
    request.session["cart"]=cart; request.session.modified=True
    return redirect("cart")

@require_POST
def remove_cart(request,product_id):
    cart=request.session.get("cart",{}); cart.pop(str(product_id),None)
    request.session["cart"]=cart; request.session.modified=True
    return redirect("cart")

@login_required
def wishlist(request):
    ids=request.session.get("wishlist",[])
    products=Product.objects.filter(id__in=ids,is_active=True)
    return render(request,"store/wishlist.html",{"products":products})

@login_required
@require_POST
def toggle_wishlist(request,product_id):
    get_object_or_404(Product,id=product_id)
    ids=request.session.get("wishlist",[])
    if product_id in ids: ids.remove(product_id); messages.info(request,"Removed from wishlist.")
    else: ids.append(product_id); messages.success(request,"Added to wishlist.")
    request.session["wishlist"]=ids
    return redirect(request.POST.get("next") or "wishlist")

@login_required
def checkout(request):
    rows,subtotal=_cart_products(request)
    if not rows:
        messages.info(request,"Your bag is empty."); return redirect("product_list")
    addresses=Address.objects.filter(user=request.user)
    code=request.session.get("coupon_code",""); coupon=Coupon.objects.filter(code__iexact=code).first()
    discount=coupon.discount(subtotal) if coupon else Decimal("0")
    delivery=Decimal("0") if subtotal>=999 else Decimal("49")
    total=subtotal-discount+delivery
    if request.method=="POST":
        address=addresses.filter(id=request.POST.get("address_id")).first()
        if not address:
            form=AddressForm(request.POST)
            if form.is_valid():
                address=form.save(commit=False); address.user=request.user; address.save()
            else:
                messages.error(request,"Select an address or enter a valid new address.")
                return render(request,"store/checkout.html",locals())
        with transaction.atomic():
            for row in rows:
                p=Product.objects.select_for_update().get(id=row["product"].id)
                if p.stock<row["quantity"]:
                    messages.error(request,f"Only {p.stock} left for {p.name}."); return redirect("cart")
            order=Order.objects.create(user=request.user,address=address,order_id="MM"+uuid.uuid4().hex[:10].upper(),subtotal=subtotal,discount=discount,delivery_charge=delivery,total=total,coupon_code=code,payment_method="cod",expected_delivery=timezone.localdate()+timedelta(days=5))
            for row in rows:
                p=Product.objects.select_for_update().get(id=row["product"].id)
                OrderItem.objects.create(order=order,product=p,product_name=p.name,unit_price=p.selling_price,quantity=row["quantity"],size=row["size"],colour=row["colour"])
                p.stock-=row["quantity"]; p.save(update_fields=["stock"])
            request.session["cart"]={}; request.session.pop("coupon_code",None)
        send_order_email(order,"Your My Myntra order is confirmed")
        Notification.objects.create(user=request.user,title="Order placed",message=f"Your order {order.order_id} has been placed successfully.")
        messages.success(request,"Order placed successfully!")
        return redirect("order_detail",order_id=order.order_id)
    form=AddressForm()
    return render(request,"store/checkout.html",{"rows":rows,"subtotal":subtotal,"discount":discount,"delivery":delivery,"total":total,"addresses":addresses,"form":form,"coupon":coupon})

@login_required
@require_POST
def apply_coupon(request):
    rows,subtotal=_cart_products(request); code=request.POST.get("code","").strip().upper()
    coupon=Coupon.objects.filter(code__iexact=code,active=True).first()
    if coupon and coupon.valid(subtotal):
        request.session["coupon_code"]=coupon.code; messages.success(request,"Coupon applied.")
    else:
        request.session.pop("coupon_code",None); messages.error(request,"Coupon is invalid, expired or does not meet the minimum order.")
    return redirect("checkout")

@login_required
def orders(request):
    return render(request,"store/orders.html",{"orders":Order.objects.filter(user=request.user).order_by("-created_at")})

@login_required
def order_detail(request,order_id):
    order=get_object_or_404(Order,user=request.user,order_id=order_id)
    return render(request,"store/order_detail.html",{"order":order})

@login_required
@require_POST
def cancel_order(request,order_id):
    order=get_object_or_404(Order,user=request.user,order_id=order_id)
    if order.status not in ("placed","confirmed","processing"):
        messages.error(request,"This order can no longer be cancelled."); return redirect("order_detail",order_id=order_id)
    with transaction.atomic():
        order.status="cancelled"; order.save(update_fields=["status"])
        for item in order.items.all():
            p=item.product; p.stock+=item.quantity; p.save(update_fields=["stock"])
    send_order_email(order,"Your My Myntra order was cancelled")
    messages.success(request,"Order cancelled.")
    return redirect("order_detail",order_id=order_id)

@login_required
@require_POST
def add_review(request,slug):
    product=get_object_or_404(Product,slug=slug)
    form=ReviewForm(request.POST)
    if form.is_valid():
        review,created=Review.objects.update_or_create(product=product,user=request.user,defaults=form.cleaned_data)
        product.rating=product.reviews.aggregate(avg=Avg("rating"))["avg"] or 0; product.save(update_fields=["rating"])
        messages.success(request,"Review saved.")
    else: messages.error(request,"Please check your review.")
    return redirect("product_detail",slug=slug)

@login_required
def return_request(request,item_id):
    item=get_object_or_404(OrderItem,id=item_id,order__user=request.user,order__status="delivered")
    if request.method=="POST":
        form=ReturnForm(request.POST)
        if form.is_valid():
            obj=form.save(commit=False); obj.order_item=item; obj.user=request.user; obj.save()
            messages.success(request,"Your return/exchange request has been submitted.")
            return redirect("order_detail",order_id=item.order.order_id)
    else: form=ReturnForm()
    return render(request,"store/form_page.html",{"form":form,"title":"Return or exchange","button":"Submit request"})

@user_passes_test(lambda u:u.is_staff)
def dashboard(request):
    context={"products":Product.objects.count(),"orders":Order.objects.count(),"customers":User.objects.filter(is_staff=False).count(),"revenue":Order.objects.exclude(status="cancelled").aggregate(v=Sum("total"))["v"] or 0,"recent_orders":Order.objects.select_related("user").order_by("-created_at")[:10],"low_stock":Product.objects.filter(stock__lt=5).order_by("stock")[:8]}
    return render(request,"store/dashboard.html",context)

def chatbot(request):
    question=request.GET.get("q","").lower()
    if "return" in question: answer="To request a return, open My Account → Orders → select a delivered order → Return/Exchange."
    elif "track" in question or "order" in question: answer="Sign in and open My Account → My Orders to view the latest order status."
    elif "size" in question: answer="Please check the size options and size guide on each product page. If unsure, compare the measurements with a garment you own."
    elif "discount" in question or "coupon" in question: answer="Enter an active coupon code at checkout. The minimum order and expiry rules are checked automatically."
    else: answer="Welcome to My Myntra! I can help with products, sizes, coupons, orders, tracking and returns. Ask me a question."
    return JsonResponse({"answer":answer})
