
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from datetime import date
from typing import List


class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class = Base)



service_mechanics = db.Table(
    'service_mechanics',
    Base.metadata,
    db.Column('service_ticket_id', db.Integer, db.ForeignKey('service_tickets.id'), primary_key=True),
    db.Column('mechanic_id', db.Integer, db.ForeignKey('mechanics.id'), primary_key=True)
)

# service_inventory = db.Table(
#     'service_inventory',
#     Base.metadata,
#     db.Column('service_ticket_id', db.Integer, db.ForeignKey('service_tickets.id'), primary_key=True),
#     db.Column('inventory_id', db.Integer, db.ForeignKey('inventory.id'), primary_key=True)
# )

class ServiceInventory(Base):
    __tablename__ = 'service_inventory'

    id: Mapped[int] = mapped_column(primary_key=True)
    service_ticket_id: Mapped[int] = mapped_column(db.ForeignKey("service_tickets.id"), nullable=False)
    inventory_id: Mapped[int] = mapped_column(db.ForeignKey("inventory.id"), nullable=False)
    quantity: Mapped[int] = mapped_column(nullable=False,)

    inventory: Mapped["Inventory"] = db.relationship(back_populates="service_tickets")
    service_tickets: Mapped["ServiceTickets"] = db.relationship(back_populates="inventory")


class Customer(Base):
    __tablename__ = 'customers'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(db.String(225),nullable=False)
    email: Mapped[str] = mapped_column(db.String(360),nullable=False,unique=True)
    phone: Mapped[str] = mapped_column(db.String(20), unique=True)
    password: Mapped[str] = mapped_column(db.String(225),nullable=False)

    tickets: Mapped[List['ServiceTickets']] = db.relationship(back_populates='customer')
    


class ServiceTickets(Base):
    __tablename__ = 'service_tickets'

    id: Mapped[int] = mapped_column(primary_key=True)
    vin: Mapped[str] = mapped_column(db.String(30), nullable=False, unique=True)
    service_date: Mapped[date] = mapped_column(db.Date)
    service_desc: Mapped[str] = mapped_column(db.String(300))
    customer_id: Mapped[int] = mapped_column(db.ForeignKey('customers.id'), nullable=False)

    customer: Mapped[Customer] = db.relationship(back_populates='tickets', passive_deletes=True)
    mechanics: Mapped[List['Mechanics']] = db.relationship(secondary='service_mechanics', back_populates='service_tickets')
    inventory: Mapped[List['ServiceInventory']] = db.relationship(back_populates='service_tickets')

class Mechanics(Base):
    __tablename__ = 'mechanics'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(db.String(225),nullable=False)
    email: Mapped[str] = mapped_column(db.String(360),nullable=False,unique=True)
    phone: Mapped[str] = mapped_column(db.String(20), unique=True)
    salary: Mapped[float] = mapped_column(db.Numeric(10,2), nullable=False)
    password: Mapped[str] = mapped_column(db.String(225),nullable=False)

    service_tickets: Mapped[List['ServiceTickets']] = db.relationship(secondary='service_mechanics', back_populates='mechanics')


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(db.String(225),nullable=False)
    email: Mapped[str] = mapped_column(db.String(360),nullable=False,unique=True)
    phone: Mapped[float] = mapped_column(db.Numeric(10,2), unique=True)


class Inventory(Base):
    __tablename__ = 'inventory'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(db.String(225),nullable=False)
    price: Mapped[float] = mapped_column(db.Numeric(10,2),nullable=False)

    service_tickets: Mapped[List['ServiceInventory']] = db.relationship(back_populates='inventory')
    

