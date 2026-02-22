from datetime import datetime
from flask import abort, session
from app.models import Building, Apartment, Owner, Charge, Payment
from PIL import Image, ImageDraw
import random
import io
import base64


def parse_address(raw_address):
    """
    Парсинг полного адреса на отдельные компоненты: город, улица, номер дома.
    Пример: "Москва, Ленина ул., 15" → {'city': 'Москва', 'street': 'Ленина ул.', 'house_number': '15'}
    Возвращает словарь. Если формат некорректен — возвращает пустой словарь.
    """
    if not raw_address or not isinstance(raw_address, str):
        return {}
    parts = [part.strip() for part in raw_address.split(',') if part.strip()]
    components = {}
    if len(parts) >= 3:
        components['city'] = parts[0]
        components['street'] = parts[1]
        components['house_number'] = parts[2]
    elif len(parts) == 2:
        components['city'] = parts[0]
        components['street'] = parts[1]
        components['house_number'] = ''
    elif len(parts) == 1:
        components['city'] = parts[0]
        components['street'] = ''
        components['house_number'] = ''
    return components


def calculate_current_debt(apartment_id):
    """
    Вычисляет текущую задолженность по квартире.
    Возвращает сумму: (начисления - платежи).
    Если квартира не найдена — возвращает 0.
    """
    if not apartment_id:
        return 0

    try:
        charges_sum = db.session.query(db.func.coalesce(db.func.sum(Charge.amount), 0)) \
                                .filter(Charge.apartment_id == apartment_id).scalar()

        payments_sum = db.session.query(db.func.coalesce(db.func.sum(Payment.paid_amount), 0)) \
                                 .filter(Payment.apartment_id == apartment_id).scalar()

        return float(charges_sum - payments_sum)
    except Exception as e:
        print(f"[ERROR] Failed to calculate debt for apartment {apartment_id}: {str(e)}")
        return 0


def get_all_houses_and_addresses():
    """
    Возвращает список всех домов с их ID и адресами.
    Формат: [{'id': 1, 'address': 'г. Москва, ул. Ленина, д. 15'}, ...]
    """
    try:
        houses = Building.query.with_entities(Building.id, Building.address).all()
        return [{'id': h.id, 'address': h.address} for h in houses]
    except Exception as e:
        print(f"[ERROR] Failed to fetch buildings: {str(e)}")
        return []


def get_available_services():
    """
    Возвращает список всех доступных услуг.
    """
    try:
        services = Service.query.all()
        return services
    except Exception as e:
        print(f"[ERROR] Failed to fetch services: {str(e)}")
        return []


def log_activity(description):
    """
    Запись активности в консоль с временной меткой.
    Можно заменить на запись в файл или логгер.
    """
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{timestamp}] {description}")


def convert_period(period_str):
    """
    Преобразует строку формата 'YYYY-MM' в объект даты (первый день месяца).
    При ошибке выбрасывает HTTP 400.
    """
    if not period_str or not isinstance(period_str, str):
        abort(400, description="Период не указан.")
    try:
        return datetime.strptime(period_str.strip(), '%Y-%m').date()
    except ValueError:
        abort(400, description="Некорректный формат периода. Ожидается ГГГГ-ММ.")


def extract_phone(phone_str):
    """
    Извлекает только цифры из строки и возвращает первые 11 (российский формат).
    Если вход None или не строка — возвращает пустую строку.
    """
    if not phone_str or not isinstance(phone_str, str):
        return ""
    digits = ''.join(filter(str.isdigit, phone_str))
    return digits[:11] if digits else ""


PUZZLE_WIDTH = 200
PUZZLE_HEIGHT = 100
SLICE_WIDTH = 50

def generate_puzzle():
    """
    Генерирует фоновое изображение и фрагмент для капчи-пазла.
    Сохраняет правильную позицию в сессии.
    Возвращает: (bg_image_b64, piece_image_b64, slice_width, max_width)
    """
    img = Image.new('RGB', (PUZZLE_WIDTH, PUZZLE_HEIGHT), color=(200, 200, 200))
    draw = ImageDraw.Draw(img)

    for _ in range(10):
        x1 = random.randint(0, PUZZLE_WIDTH)
        y1 = random.randint(0, PUZZLE_HEIGHT)
        x2 = random.randint(0, PUZZLE_WIDTH)
        y2 = random.randint(0, PUZZLE_HEIGHT)
        draw.line((x1, y1, x2, y2),
                  fill=(random.randint(0, 100), random.randint(0, 100), random.randint(0, 100)),
                  width=2)

    slice_x = random.randint(10, PUZZLE_WIDTH - SLICE_WIDTH - 10)
    slice_box = (slice_x, 0, slice_x + SLICE_WIDTH, PUZZLE_HEIGHT)
    puzzle_piece = img.crop(slice_box)

    draw.rectangle(slice_box, fill=(200, 200, 200))

    def image_to_b64(image):
        buf = io.BytesIO()
        image.save(buf, format='PNG')
        return base64.b64encode(buf.getvalue()).decode('utf-8')

    bg_image = image_to_b64(img)
    piece_image = image_to_b64(puzzle_piece)

    session['captcha_correct_x'] = slice_x
    session['captcha_shown'] = True

    return bg_image, piece_image, SLICE_WIDTH, PUZZLE_WIDTH