from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, TextAreaField, DateField, DecimalField, IntegerField, BooleanField, SubmitField
from wtforms.validators import InputRequired, Email, EqualTo, ValidationError, Optional, NumberRange
from app.models import User, Owner, Apartment, Building, Service, Charge, Payment, Request, Staff, Expense, Resident


class RegistrationForm(FlaskForm):
    username = StringField('Имя пользователя:', validators=[InputRequired(message='Имя пользователя обязательно.')])
    password = PasswordField('Пароль:', validators=[
        InputRequired(message='Пароль обязателен.'),
        EqualTo('confirm_password', message='Пароли должны совпадать.')
    ])
    confirm_password = PasswordField('Подтверждение пароля:')
    submit = SubmitField('Зарегистрироваться')

    def validate_username(self, field):
        user = User.query.filter_by(username=field.data).first()
        if user:
            raise ValidationError('Такое имя пользователя уже занято.')


class LoginForm(FlaskForm):
    username = StringField('Имя пользователя:', validators=[InputRequired(message='Имя пользователя обязательно.')])
    password = PasswordField('Пароль:', validators=[InputRequired(message='Пароль обязателен.')])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


class ProfileForm(FlaskForm):
    username = StringField('Имя пользователя:', validators=[InputRequired(message='Имя пользователя обязательно.')])
    submit = SubmitField('Изменить профиль')


class BuildingRegistrationForm(FlaskForm):
    address = StringField('Адрес:', validators=[InputRequired(message='Адрес обязателен.')])
    start_management_date = DateField('Дата начала управления:', format='%Y-%m-%d', validators=[Optional()])
    floors = IntegerField('Количество этажей:', validators=[NumberRange(min=1, max=100, message='Недопустимое число этажей.')])
    year_built = IntegerField('Год постройки:', validators=[NumberRange(min=1900, max=2025, message='Некорректный год постройки.')])
    total_area = DecimalField('Общая площадь (м²):', places=2, validators=[NumberRange(min=0, message='Площадь должна быть положительной.')])
    city = StringField('Город:', validators=[InputRequired(message='Город обязателен.')])
    street = StringField('Улица:', validators=[InputRequired(message='Улица обязательна.')])
    house_number = StringField('Номер дома:', validators=[InputRequired(message='Номер дома обязателен.')])
    submit = SubmitField('Добавить здание')


class ApartmentRegistrationForm(FlaskForm):
    number = IntegerField('Номер квартиры:', validators=[InputRequired(message='Номер квартиры обязателен.')])
    area = DecimalField('Площадь (м²):', places=2, validators=[NumberRange(min=0, message='Площадь должна быть положительной.')])
    building_id = SelectField('Здание:', coerce=int, validators=[InputRequired(message='Выбор здания обязателен.')])
    owner_id = SelectField('Владелец:', coerce=lambda x: int(x) if x else None, validators=[Optional()])
    submit = SubmitField('Добавить квартиру')


class OwnerRegistrationForm(FlaskForm):
    full_name = StringField('ФИО:', validators=[InputRequired(message='ФИО обязательно.')])
    phone = StringField('Телефон:', validators=[InputRequired(message='Телефон обязателен.')])
    email = StringField('Email:', validators=[Email(message='Некорректный e-mail.'), Optional()])
    submit = SubmitField('Добавить владельца')


class ServiceSelectionForm(FlaskForm):
    service = SelectField('Вид услуги:', choices=[], validators=[InputRequired(message='Выбор услуги обязателен.')])
    submit = SubmitField('Выбрать услугу')


class ChargeEntryForm(FlaskForm):
    apartment_id = SelectField('Квартира:', coerce=int, validators=[InputRequired(message='Выбор квартиры обязателен.')])
    service_id = SelectField('Услуга:', coerce=int, validators=[InputRequired(message='Выбор услуги обязателен.')])
    period = StringField('Период начисления (гггг-мм):', validators=[InputRequired(message='Период обязателен.')])
    amount = DecimalField('Сумма начисления:', places=2, validators=[NumberRange(min=0, message='Сумма должна быть положительной.')])
    submit = SubmitField('Внести начисление')


class PaymentEntryForm(FlaskForm):
    apartment_id = SelectField('Квартира:', coerce=int, validators=[InputRequired(message='Выбор квартиры обязателен.')])
    service_id = SelectField('Услуга:', coerce=int, validators=[InputRequired(message='Выбор услуги обязателен.')])
    paid_amount = DecimalField('Сумма платежа:', places=2, validators=[NumberRange(min=0, message='Сумма должна быть положительной.')])
    payment_date = DateField('Дата платежа:', format='%Y-%m-%d', validators=[Optional()])
    submit = SubmitField('Внести оплату')


class RequestForm(FlaskForm):
    title = StringField('Заголовок:', validators=[InputRequired(message='Название обращения обязательно.')])
    description = TextAreaField('Описание проблемы:', validators=[InputRequired(message='Описание обязательно.')])
    status = SelectField('Статус:', choices=[('new', 'Новая'), ('in_progress', 'В работе'), ('completed', 'Завершена'), ('rejected', 'Отклонена')],
                         validators=[InputRequired(message='Статус обязателен.')])
    priority = SelectField('Приоритет:', choices=[('low', 'Низкий'), ('medium', 'Средний'), ('high', 'Высокий')],
                           validators=[InputRequired(message='Приоритет обязателен.')])
    apartment_id = SelectField('Квартира:', coerce=int, validators=[InputRequired(message='Выбор квартиры обязателен.')])
    submit = SubmitField('Отправить заявку')


class StaffForm(FlaskForm):
    first_name = StringField('Имя:', validators=[InputRequired(message='Имя обязательно.')])
    last_name = StringField('Фамилия:', validators=[InputRequired(message='Фамилия обязательна.')])
    position = StringField('Должность:', validators=[InputRequired(message='Должность обязательна.')])
    phone = StringField('Телефон:', validators=[InputRequired(message='Телефон обязателен.')])
    email = StringField('E-mail:', validators=[Email(message='Некорректный E-mail.')])
    submit = SubmitField('Добавить сотрудника')


class ExpenseForm(FlaskForm):
    date = DateField('Дата расхода:', format='%Y-%m-%d', validators=[InputRequired(message='Дата обязательна.')])
    amount = DecimalField('Сумма:', places=2, validators=[NumberRange(min=0, message='Сумма должна быть положительной.')])
    description = TextAreaField('Описание:', validators=[InputRequired(message='Описание обязательно.')])
    category = StringField('Категория:', validators=[InputRequired(message='Категория обязательна.')])
    submit = SubmitField('Добавить расход')


class ResidentForm(FlaskForm):
    name = StringField('ФИО:', validators=[InputRequired(message='ФИО обязательно.')])
    phone = StringField('Телефон:', validators=[InputRequired(message='Телефон обязателен.')])
    email = StringField('E-mail:', validators=[Email(message='Некорректный E-mail.')])
    relation_to_owner = SelectField('Родство с владельцем:',
                                   choices=[('owner', 'Владелец'), ('tenant', 'Арендатор'), ('family', 'Член семьи')],
                                   validators=[InputRequired(message='Тип родства обязателен.')])
    apartment_id = SelectField('Квартира:', coerce=int, validators=[InputRequired(message='Выбор квартиры обязателен.')])
    submit = SubmitField('Добавить жителя')