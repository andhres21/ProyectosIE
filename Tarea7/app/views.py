from django.shortcuts import render
import datetime
from .models import *
from django.http import JsonResponse
import json
from . utils import cookieCart,cartData, guessOrder

def store(request):
    products = Product.objects.all()  # Obtener todos los productos de la base de datos
    cartItems = request.session.get('cartItems', 0)  # Obtener la cantidad de productos en el carrito si existe
    context = {
        'products': products,
        'cartItems': cartItems,
    }
    return render(request, 'Generales/store.html', context)

def cart(request):

    data = cartData(request)
    cartItems = data['cartItems']
    items = data['items']
    order = data['order']

    context = {'items':items, 'order':order,'cartItems':cartItems, }
    return render(request,'generales/cart.html',context)

def checkout(request):

    data = cartData(request)
    cartItems = data['cartItems']
    items = data['items']
    order = data['order']

    context = {'items':items, 'order':order,'cartItems':cartItems}

    return render(request,'generales/checkout.html',context)

def updateItem(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']
    customer = request.user.customer
    product = Product.objects.get(id = productId)
    order, created = Order.objects.get_or_create(customer=customer, complete=False)

    orderItem, created = OrderItem.objects.get_or_create(order=order, product= product)

    if action == 'add':
        orderItem.quantity = (orderItem.quantity + 1)
    elif action == 'remove':
        orderItem.quantity = (orderItem.quantity - 1)

    orderItem.save()

    if orderItem.quantity <= 0:    
        orderItem.delete()
    return JsonResponse('El producto fue agregado', safe=False)

from django.views.decorators.csrf import csrf_exempt
@csrf_exempt
def processOrder(request):
    transacion_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)

    else:
        customer, order = guessOrder(request,data)

    total = float(data['form']['total'])
    order.transaction_id = transacion_id

    if total == order.get_cart_total:
        order.complete = True
    order.save()

    if order.shipping == True:
        ShippingAddress.objects.create(
            customer=customer,
            order=order,
            address=data['shipping']['address'],
            city=data['shipping']['city'],
            state=data['shipping']['state'],
            zipcode=data['shipping']['zipcode'],
        )
    return JsonResponse('Pago completo', safe=False)

def add_to_cart(request, product_id):
    cart = request.session.get('cart', {})
    if product_id in cart:
        cart[product_id] += 1
    else:
        cart[product_id] = 1
    request.session['cart'] = cart
    return JsonResponse({'cart_count': sum(cart.values())})
