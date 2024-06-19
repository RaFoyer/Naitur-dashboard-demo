# path/src/create_db.py

import os
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, inspect
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
import datetime
from config.settings import DATABASE_URL

# Ensure database file exists
db_file = DATABASE_URL.split("///")[1]
if not os.path.exists(db_file):
    os.makedirs(os.path.dirname(db_file), exist_ok=True)
    open(db_file, 'w').close()

# Create an engine and session
engine = create_engine(DATABASE_URL)
inspector = inspect(engine)
Session = sessionmaker(bind=engine)
session = Session()

Base = declarative_base()

class Protocol(Base):
    __tablename__ = 'protocol'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

class Client(Base):
    __tablename__ = 'client'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

class Form(Base):
    __tablename__ = 'form'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
    type = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

class Question(Base):
    __tablename__ = 'question'
    id = Column(Integer, primary_key=True)
    text = Column(String)
    description = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

class FormQuestion(Base):
    __tablename__ = 'form_question'
    form_id = Column(Integer, ForeignKey('form.id'), primary_key=True)
    question_id = Column(Integer, ForeignKey('question.id'), primary_key=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

class Response(Base):
    __tablename__ = 'response'
    id = Column(Integer, primary_key=True)
    text = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

class QuestionResponse(Base):
    __tablename__ = 'question_response'
    id = Column(Integer, primary_key=True)
    question = Column(Integer, ForeignKey('question.id'))
    response = Column(Integer, ForeignKey('response.id'))
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

class ClientFormResponse(Base):
    __tablename__ = 'client_form_response'
    id = Column(Integer, primary_key=True)
    client_id = Column(Integer, ForeignKey('client.id'))
    form_id = Column(Integer, ForeignKey('form.id'))
    protocol_id = Column(Integer, ForeignKey('protocol.id'))
    question_id = Column(Integer, ForeignKey('question.id'))
    response_id = Column(Integer, ForeignKey('response.id'))
    time_point = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

class ProtocolForm(Base):
    __tablename__ = 'protocol_form'
    protocol_id = Column(Integer, ForeignKey('protocol.id'), primary_key=True)
    form_id = Column(Integer, ForeignKey('form.id'), primary_key=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

# Ensure all tables are created
tables = [
    ('protocol', Protocol),
    ('client', Client),
    ('form', Form),
    ('question', Question),
    ('form_question', FormQuestion),
    ('response', Response),
    ('question_response', QuestionResponse),
    ('client_form_response', ClientFormResponse),
    ('protocol_form', ProtocolForm)
]

try:
    for table_name, table_class in tables:
        if not inspector.has_table(table_name):
            table_class.__table__.create(engine)
            print(f"Table '{table_name}' created successfully.")
    print("DB integrity check... All necessary tables are ensured to exist.")
except Exception as e:
    print(f"Error creating tables: {e}")
