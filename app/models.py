from datetime import datetime
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db


class User(UserMixin, db.Model):
      __tablename__ = 'users'
      id = db.Column(db.Integer, primary_key=True)
      username = db.Column(db.String(64), unique=True, nullable=False)
      password_hash = db.Column(db.String(128), nullable=False)
      role = db.Column(db.String(20), default='User')
      blocked = db.Column(db.Boolean, default=False)

      def set_password(self, password):
          """Устанавливает хэш пароля"""
          self.password_hash = generate_password_hash(password)

      def check_password(self, password):
          """Проверяет вводимый пароль с сохраненным хэшем"""
          return check_password_hash(self.password_hash, password)


class Building(db.Model):
      __tablename__ = 'buildings'
      id = db.Column(db.Integer, primary_key=True)
      address = db.Column(db.String(255), nullable=False)
      start_management_date = db.Column(db.DateTime, default=datetime.utcnow())
      floors = db.Column(db.Integer)
      year_built = db.Column(db.Integer)
      total_area = db.Column(db.Float)
      city = db.Column(db.String(100))
      street = db.Column(db.String(100))
      house_number = db.Column(db.String(20))

      apartments = relationship('Apartment', backref='building', lazy=True)


class Apartment(db.Model):
      __tablename__ = 'apartments'
      id = db.Column(db.Integer, primary_key=True)
      number = db.Column(db.Integer, nullable=False)
      area = db.Column(db.Float)
      building_id = db.Column(db.Integer, db.ForeignKey('buildings.id'), nullable=False)

      owner_id = db.Column(db.Integer, db.ForeignKey('owners.id'), nullable=True)

      charges = relationship('Charge', backref='apartment', lazy=True)
      payments = relationship('Payment', backref='apartment', lazy=True)


class Owner(db.Model):
      __tablename__ = 'owners'
      id = db.Column(db.Integer, primary_key=True)
      full_name = db.Column(db.String(100), nullable=False)
      phone = db.Column(db.String(20))
      email = db.Column(db.String(120))

      apartments = relationship('Apartment', backref='owner', lazy=True)


class Service(db.Model):
      __tablename__ = 'services'
      id = db.Column(db.Integer, primary_key=True)
      name = db.Column(db.String(100), nullable=False)

      charges = relationship('Charge', backref='service', lazy=True)
      payments = relationship('Payment', backref='service', lazy=True)


class Charge(db.Model):
      __tablename__ = 'charges'
      id = db.Column(db.Integer, primary_key=True)
      apartment_id = db.Column(db.Integer, db.ForeignKey('apartments.id'), nullable=False)
      service_id = db.Column(db.Integer, db.ForeignKey('services.id'), nullable=False)
      period = db.Column(db.String(10), nullable=False)
      amount = db.Column(db.Float, nullable=False)
      created_at = db.Column(db.DateTime, default=datetime.utcnow())


class Payment(db.Model):
      __tablename__ = 'payments'
      id = db.Column(db.Integer, primary_key=True)
      apartment_id = db.Column(db.Integer, db.ForeignKey('apartments.id'), nullable=False)
      service_id = db.Column(db.Integer, db.ForeignKey('services.id'), nullable=False)
      paid_amount = db.Column(db.Float, nullable=False)
      payment_date = db.Column(db.DateTime, default=datetime.utcnow())


class Request(db.Model):
      __tablename__ = 'requests'
      id = db.Column(db.Integer, primary_key=True)
      title = db.Column(db.String(255), nullable=False)
      description = db.Column(db.Text)
      status = db.Column(db.String(20), default='Новый')
      priority = db.Column(db.String(20), default='Средняя')
      created_at = db.Column(db.DateTime, default=datetime.utcnow())
      updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow())
      apartment_id = db.Column(db.Integer, db.ForeignKey('apartments.id'), nullable=False)
      staff_id = db.Column(db.Integer, db.ForeignKey('staff.id'), nullable=True)


class Staff(db.Model):
      __tablename__ = 'staff'
      id = db.Column(db.Integer, primary_key=True)
      first_name = db.Column(db.String(100), nullable=False)
      last_name = db.Column(db.String(100), nullable=False)
      position = db.Column(db.String(100))
      phone = db.Column(db.String(20))
      email = db.Column(db.String(120))

      requests = relationship('Request', backref='staff', lazy=True)


class Expense(db.Model):
      __tablename__ = 'expenses'
      id = db.Column(db.Integer, primary_key=True)
      date = db.Column(db.DateTime, default=datetime.utcnow())
      amount = db.Column(db.Float, nullable=False)
      description = db.Column(db.Text)
      category = db.Column(db.String(100))

      staff_id = db.Column(db.Integer, db.ForeignKey('staff.id'), nullable=True)


class Resident(db.Model):
      __tablename__ = 'residents'
      id = db.Column(db.Integer, primary_key=True)
      name = db.Column(db.String(100), nullable=False)
      phone = db.Column(db.String(20))
      email = db.Column(db.String(120))
      relation_to_owner = db.Column(db.String(20))
      apartment_id = db.Column(db.Integer, db.ForeignKey('apartments.id'), nullable=False)

      apartment = relationship('Apartment', backref='resident', uselist=False)


request_statuses = db.Table(
      'request_statuses',
      db.Column('request_id', db.Integer, db.ForeignKey('requests.id')),
      db.Column('status', db.String(20)),
      db.Column('timestamp', db.DateTime, default=datetime.utcnow()),
      db.Column('staff_id', db.Integer, db.ForeignKey('staff.id'))
)