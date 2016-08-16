from cart.cart import Cart

def cart(request):
    return {'number_of_cart_items': Cart(request).count()}