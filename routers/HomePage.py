import os
from fastapi import APIRouter, HTTPException, Form, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
import numpy as np
from typing import Dict, Any

from pydantic.v1 import BaseSettings

from config import BASE_DIR
from tools import JsonReader
from tools.JsonReader import load_products
from dotenv import load_dotenv, find_dotenv
import telebot

load_dotenv()

TOKEN = os.getenv("TOKEN_TG")
TOKEN_REVIEWS = os.getenv("TOKEN_TG_REVIEWS")

def tg(text: str):
    chat_id = '578552563'
    text_to_send = f'{text}'
    bot = telebot.TeleBot(TOKEN)
    bot.send_message(chat_id, text_to_send)

def tg_reviews(text: str):
    chat_id = '578552563'
    text_to_send = f'{text}'
    bot = telebot.TeleBot(TOKEN_REVIEWS)
    bot.send_message(chat_id, text_to_send)

templates = Jinja2Templates(os.path.join(BASE_DIR, 'templates'))

router = APIRouter()

# Хранилище состояния корзины (ТОЛЬКО дополнительные товары)
cart_state: Dict[int, int] = {}
current_main_pizza_id: int = None
current_main_pizza_price: int = 0
current_main_pizza_title: str = ""

products = load_products('information', 'data.json')
cards = load_products('information', 'cards.json')


def calculate_delivery(total_price: int) -> int:
    """Рассчитывает стоимость доставки на основе общей суммы"""
    if total_price < 300:
        return 399
    elif 300 <= total_price < 450:
        return 249
    elif 450 <= total_price < 600:
        return 149
    elif 600 <= total_price < 869:
        return 49
    else:
        return 0


def get_cart_total() -> Dict[str, Any]:
    global final_total
    """Рассчитывает общую сумму корзины"""

    # Начинаем с цены основной пиццы
    total_price = current_main_pizza_price
    items = [
        {
            "name": current_main_pizza_title,
            "price": current_main_pizza_price,
            "quantity": 1,
            "total": current_main_pizza_price
        }
    ]

    print(f"=== РАСЧЕТ КОРЗИНЫ ===")
    print(f"Основная пицца: {current_main_pizza_title} - {current_main_pizza_price} руб")

    # Добавляем дополнительные товары из cart_state
    additional_total = 0
    for product_id, quantity in cart_state.items():
        if quantity == 0:
            continue

        # Ищем товар в карточках (основные пиццы уже не ищем, только дополнительные товары)
        product = None
        for card in cards:
            if card['id'] == product_id:
                product = card
                break

        if product:
            product_total = product['price'] * quantity
            additional_total += product_total
            total_price += product_total

            items.append({
                "name": product['title'],
                "price": product['price'],
                "quantity": quantity,
                "total": product_total
            })

            print(f"Доп. товар: {product['title']} - {product['price']} руб x {quantity} = {product_total} руб")

    delivery_price = calculate_delivery(total_price)
    final_total = total_price + delivery_price


    print(f"Сумма товаров: {total_price} руб")
    print(f"Доставка: {delivery_price} руб")
    print(f"ИТОГО: {final_total} руб")
    print(f"=====================")

    return {
        "total_price": total_price,
        "delivery_price": delivery_price,
        "final_total": final_total,
        "items_count": len(items),
        "main_pizza_price": current_main_pizza_price,
        "additional_total": additional_total,
        "items": items
    }


@router.get('/{pizza_id}')
def homebutton(request: Request, pizza_id: int):
    global current_main_pizza_id, current_main_pizza_price, current_main_pizza_title

    # Очищаем корзину от предыдущих товаров
    cart_state.clear()

    # Устанавливаем основную пиццу
    current_main_pizza_id = pizza_id

    class Pizza:
        def __init__(self, id, price, title, delivery):
            self.id: int = id
            self.price: int = price
            self.title: str = title
            self.delivery: int = delivery

    main_pizza = None
    for i in products:
        if i['id'] == pizza_id:
            delivery = calculate_delivery(i['price'])
            main_pizza = Pizza(pizza_id, i['price'], i['title'], delivery)
            current_main_pizza_price = i['price']
            current_main_pizza_title = i['title']

    if not main_pizza:
        raise HTTPException(status_code=404, detail="Pizza not found")

    # Получаем актуальные данные корзины
    cart_total = get_cart_total()

    return templates.TemplateResponse('cart.html', {
        'request': request,
        'main_pizza': main_pizza,
        'cardss': cards,
        'cart_total': cart_total,
        'pizza_id': pizza_id
    })


class AddToCartRequest(BaseModel):
    product_id: int
    quantity: int

@router.get('/')
def homepage(request: Request, refresh: bool = False):
    if not refresh:
        return RedirectResponse(f"/?refresh=true")
    return templates.TemplateResponse('home.html', {
        'request': request,
        'products': products,
    })

@router.post('/api/add_to_cart/{id_card}')
def add_to_cart(id_card: int, request: AddToCartRequest):
    print(f"=== ДОБАВЛЕНИЕ ТОВАРА ===")
    print(f"Товар ID: {id_card}, Количество: {request.quantity}")
    print(f"До добавления: {cart_state}")

    # Обновляем состояние корзины
    if id_card in cart_state:
        cart_state[id_card] += request.quantity
    else:
        cart_state[id_card] = request.quantity

    print(f"После добавления: {cart_state}")

    # Получаем актуальные данные корзины
    cart_total = get_cart_total()

    return {
        "status": "success",
        "message": f"Product {id_card} added to cart",
        "product_id": id_card,
        "quantity": cart_state[id_card],
        "cart_total": cart_total
    }


@router.post('/api/remove_from_cart/{id_card}')
def remove_from_cart(id_card: int, request: AddToCartRequest):
    print(f"=== УДАЛЕНИЕ ТОВАРА ===")
    print(f"Товар ID: {id_card}, Количество: {request.quantity}")
    print(f"До удаления: {cart_state}")

    # Обновляем состояние корзины
    if id_card in cart_state:
        cart_state[id_card] = max(0, cart_state[id_card] - request.quantity)
        if cart_state[id_card] == 0:
            del cart_state[id_card]

    print(f"После удаления: {cart_state}")

    # Получаем актуальные данные корзины
    cart_total = get_cart_total()

    return {
        "status": "success",
        "message": f"Product {id_card} removed from cart",
        "product_id": id_card,
        "quantity": cart_state.get(id_card, 0),
        "cart_total": cart_total
    }


@router.get('/api/cart_total')
def get_cart_total_api():
    """API для получения текущего состояния корзины"""
    return get_cart_total()


@router.get('/api/calculate_delivery_for_product/{product_id}')
def calculate_delivery_for_product(product_id: int):
    """Рассчитывает доставку для конкретного товара с учетом основной пиццы"""

    # Находим товар в карточках
    product = None
    product_price = 0
    product_name = ""

    for card in cards:
        if card['id'] == product_id:
            product = card
            product_price = card['price']
            product_name = card['title']
            break

    if not product:
        return {
            "error": "Product not found"
        }

    # Рассчитываем текущую общую сумму
    current_total = current_main_pizza_price
    for prod_id, quantity in cart_state.items():
        for card in cards:
            if card['id'] == prod_id:
                current_total += card['price'] * quantity
                break

    current_delivery = calculate_delivery(current_total)

    # Рассчитываем сумму с новым товаром
    total_with_product = current_total + product_price
    delivery_with_product = calculate_delivery(total_with_product)

    print(f"Расчет доставки для {product_name}:")
    print(f"Текущая сумма: {current_total} руб, доставка: {current_delivery} руб")
    print(f"С товаром: {total_with_product} руб, доставка: {delivery_with_product} руб")

    return {
        "product_id": product_id,
        "product_name": product_name,
        "product_price": product_price,
        "current_total": current_total,
        "total_with_product": total_with_product,
        "delivery_with_product": delivery_with_product,
        "current_delivery": current_delivery,
        "delivery_change": f"🚚 {current_delivery} -> {delivery_with_product}" if delivery_with_product != 0 else "🚚 Бесплатная доставка!"
    }

@router.get("/{pizza_id}/final")
def submitbutton(pizza_id: int, total: int, request: Request, username: str):
    for i in products:
        if i['id'] == pizza_id:
            price_before = i['price']
            product_title = i['title']
    print('Цена до:', price_before)
    print("Итоговый прайс:", final_total)
    delivery_before = calculate_delivery(price_before)
    delivery_after = calculate_delivery(final_total)

    earnings = final_total - (price_before + delivery_before)  # на сколько мы подняли средний чек
    sebes_after = 200/final_total
    sebes_do = 200/(price_before + delivery_before)

    class Sebes:
        def __init__(self, sebes_do, sebes_after, sebes_total):
            self.sebes_do: int = np.round(sebes_do, 2) * 100
            self.sebes_after: int = np.round(sebes_after, 2) * 100
            self.sebes_total: int = np.round(sebes_total, 2) * 100

    sebes_total = np.round((sebes_do - sebes_after), 2)

    sebes = Sebes(sebes_do, sebes_after, sebes_total)

    sebes_total = np.round(sebes.sebes_do, 2) - np.round(sebes.sebes_after, 2)

    if username:
        username = username.capitalize()
    else: username = 'Гость'

    try:
        if TOKEN:
            tg(f'Name: {username}\nВыбрал товар: {product_title}\nЗаработок: {earnings} ({price_before} -> {final_total})\nуменьшили на: {sebes_total}%')
    except Exception as e:
        print('Ничего, в другой раз получится')

    return templates.TemplateResponse('final.html', {
        'request': request,
        'earnings': earnings,
        'sebes': sebes,
        'username': username
    })

@router.post("/feedback")
def feedback(
        request: Request,
        star: int = Form(...),
        comment: str = Form(...),
        platform: str = Form(...),
        personalization: str = Form(...)
):
    try:
        if TOKEN_REVIEWS:
            if platform == 'app': platform = 'Mobile App'
            else: platform = 'Website'

            if personalization == 'yes': personalization_emoji = 'Yes'
            elif personalization == 'no': personalization_emoji = 'No'
            else: personalization_emoji = 'Not Sure'

            tg_reviews(f'FEEDBACK\nзвезд: {star}\nPlatform: {platform}\nХотел ли бы видеть "Добавить к заказу": {personalization_emoji}\ncomment: {comment}')

    except Exception as e:
        print('Ничего, в другой раз получится')

    return templates.TemplateResponse('feedback_page.html', {
        'request': request,
        'my_tg': '@axelaxD',
        'tg_Samira': '@s_yakupovaaa',
        'tg_Danya': '@bolcharaa'
    })