def shop_context(request):
    cart=request.session.get("cart",{})
    return {"cart_count":sum(int(x.get("quantity",1)) for x in cart.values())}
