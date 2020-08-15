from sqlalchemy import Column, String, Integer, ARRAY, create_engine
from flask_sqlalchemy import SQLAlchemy
import json
import os

database_path = os.environ['DATABASE_URL']

db = SQLAlchemy()

def setup_db(app, database_path=database_path):
    app.config["SQLALCHEMY_DATABASE_URI"] = database_path
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.app = app
    db.init_app(app)
    db.create_all()

def rollback():
    db.session.rollback()

class Word(db.Model):
    __tablename__ = 'words'

    id = Column(Integer, primary_key=True)
    word = Column(String, nullable=False)
    meaning = Column(String, nullable=False)
    options = Column(ARRAY(String),nullable=False)
    hint = Column(String,nullable=False)
    completed = Column(String,nullable=False)

    
    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def format(self):
        return {
            'id': self.id,
            'word': self.word,
            'answer': self.answer,
            'options': self.options,
            'completed': self.completed
        }
    
