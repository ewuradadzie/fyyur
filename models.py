#from app import db, func
from sqlalchemy import func
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Venue(db.Model):
    __tablename__ = 'venues'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)
    genres = db.Column(db.ARRAY(db.String()))
    shows = db.relationship('Show', backref='venue')
    address = db.Column(db.String(120))
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    website_link = db.Column(db.String(120))
    facebook_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(500))
    image_link = db.Column(db.String(500))
    created_at = db.Column(db.DateTime)


class Artist(db.Model):
    __tablename__ = 'artists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)
    genres = db.Column(db.ARRAY(db.String()))
    shows = db.relationship('Show', backref='artist')
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    website_link = db.Column(db.String(120))
    facebook_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(120), nullable=True)
    image_link = db.Column(db.String(500))
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())

class Show(db.Model):
    __tablename__ = 'shows'

    id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey('venues.id'))
    artist_id = db.Column(db.Integer, db.ForeignKey('artists.id'))
    start_time = db.Column(db.DateTime)
