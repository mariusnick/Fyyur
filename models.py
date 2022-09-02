
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime
import logging




db = SQLAlchemy()
#migrate = Migrate(app, db)
#db.create_all()

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50),nullable=False)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String(120)))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(150))
    seeking_talent =  db.Column(db.Boolean) 
    seeking_description =  db.Column(db.String(300))               
    past_shows_count = db.Column(db.Integer)
    upcoming_shows_count = db.Column(db.Integer)
    shows = db.relationship('Show', backref=db.backref('venues'), lazy="joined", cascade="all, delete")
    
    def past_shows(self):
        show_list = []
        
        shows = Show.query.filter(Show.venue_id==self.id).filter(Show.start_time < datetime.now()).all()
        for show in shows:
            artist = Artist.query.filter(Artist.id == show.artist_id).first()
            dict_shows ={'artist_id':show.artist_id,
                         'start_time' : str(show.start_time),
                         'artist_name': artist.name,
                         "artist_image_link":artist.image_link
                         }
            show_list.append(dict_shows)
          
   
        return show_list
    
    def future_shows(self):
        show_list = []
        shows = Show.query.filter(Show.venue_id==self.id).filter(Show.start_time > datetime.now()).all()
        for show in shows:
            artist = Artist.query.filter(id == show.artist_id).first()
            dict_shows ={'artist_id':show.id,
                         'start_time' : str(show.start_time),
                         "artist_name":artist.name,
                         "artist_image_link":artist.image_link
                         }
            show_list.append(dict_shows)
        return show_list
   

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50),nullable=False)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String(120)))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(150))
    seeking_venue =  db.Column(db.Boolean) 
    seeking_description =  db.Column(db.String(300))               
    past_shows_count = db.Column(db.Integer)
    upcoming_shows_count = db.Column(db.Integer)
    shows = db.relationship('Show', backref=db.backref('artists'), lazy="joined", cascade="all, delete")
    
    
    def past_shows(self):
        show_list = []
        
        shows = Show.query.filter(Show.venue_id==self.id).filter(Show.start_time < datetime.now()).all()
        for show in shows:
            venue = Venue.query.filter(Artist.id == show.artist_id).first()
            dict_shows ={'venue_id':show.venue_id,
                         'start_time' : str(show.start_time),
                         'venue_name': venue.name,
                         "venue_image_link":venue.image_link
                         }
            show_list.append(dict_shows)
          
   
        return show_list
    
    
   
    
    def future_shows(self):
        show_list = []
        shows = Show.query.filter(Show.venue_id==self.id).filter(Show.start_time > datetime.now()).all()
    
        for show in shows:
            venue = Venue.query.filter(Artist.id == show.artist_id).first()
            dict_shows ={'venue_id':show.venue_id,
                         'start_time' : str(show.start_time),
                         'venue_name': venue.name,
                         "venue_image_link":venue.image_link
                         }
            show_list.append(dict_shows)
          
        return show_list
    
    
class Show(db.Model):
    __tablename__ = 'Show'
    
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'),nullable=False, primary_key = True)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'),nullable=False, primary_key = True)
    start_time = db.Column(db.DateTime, nullable=False,  primary_key = True)
     
   
    

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
