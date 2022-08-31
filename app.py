#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
from re import A

import sys
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, session, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from datetime import datetime
from flask_migrate import Migrate
from flask_wtf import FlaskForm
from forms import *

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Models
from models import *
# TODO: connect to a local postgresql database

#db.create_all()
#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
  
  
  V = Venue.query.all()
  data = []
  locations = [(v.city,v.state) for v in V]
  locations = list(set(locations))
  for city,state in locations:
        city_state = {"city":city,
                      "state":state}
        venues =[]  
        for v in V :         
              if v.city == city and v.state== state:
                    upcoming_show_query = Show.query.filter_by(venue_id = v.id).filter(Show.start_time < (datetime.now())).all()
                    venues.append({"id":v.id,
                                   "name":v.name,
                                   "num_upcoming_shows":len(upcoming_show_query)})
        city_state['venues']=venues
        data.append(city_state)
  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  word = request.form.get('search_term', '')
  
  data = Venue.query.filter(Venue.name.ilike(f'%{word}%')).all()
  
  response ={'count': len(data),
             'data':data}
  
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
 
  venue = Venue.query.filter_by(id = venue_id).first()
  upcoming_show_query = Show.query.filter_by(venue_id = venue.id).filter(Show.start_time > (datetime.now())).join(Artist).all()
  upcoming_show_list =[]
  past_show_list = []
  for show in upcoming_show_query:
       dict_artist= {'artist_id': show.artist_id,
                    'artist_name':show.artists.name,
                    'artist_image_link':show.artists.image_link,
                    'start_time': str(show.start_time)}
       upcoming_show_list.append(dict_artist)
  past_show_query = Show.query.filter_by(venue_id = venue.id).filter(Show.start_time < (datetime.now())).join(Artist).all()
  for show in past_show_query:
      dict_artist= {'artist_id': show.venue_id,
                    'artist_name':show.artists.name,
                    'artist_image_link':show.artists.image_link,
                    'start_time': str(show.start_time)}
      past_show_list.append(dict_artist)
  
  data = {
    "id": venue.id,
    "name": venue.name,
    "genres": venue.genres,
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "image_link": venue.image_link,
    "past_shows":past_show_list,
    "upcoming_shows":upcoming_show_list,
    "past_shows_count": len(past_show_list),
    "upcoming_shows_count": len(upcoming_show_list)
  }

  # data = list(filter(lambda d: d['id'] == venue_id, [data1, data2, data3]))[0]
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
   
  form = VenueForm()
  if form.validate():
        try:
          venue_new = Venue(name=form.name.data,
                            city=form.city.data,
                            state=form.state.data,
                            address=form.address.data,
                            phone=form.phone.data,
                            genres=form.genres.data,
                            facebook_link=form.facebook_link.data,
                            image_link=form.image_link.data,
                            website=form.website_link.data,
                            seeking_talent=form.seeking_talent.data,
                            seeking_description=form.seeking_description.data)
          db.session.add(venue_new)
          db.session.commit()
          flash('Venue ' + venue_new.name + ' was successfully listed!')
        except:
          flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
          db.session.rollback()
          # print(sys.exc_info())
        finally:
          db.session.close()
  else:
        flash('The data in the form is not ok')
          

  # on successful db insert, flash success
  
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  try:
        Venue.query.filter_by(id=venue_id).delete()
        db.session.commit()
  except:
        db.session.rollback()
  finally:
        db.session.close()
  return redirect(url_for('index'))
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
 

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  data=[]
  artists =Artist.query.all()
  for artist in artists:
        data.append({'id':artist.id,
                     'name':artist.name})
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  
  word = request.form.get('search_term', '')
  
  data = Artist.query.filter(Artist.name.ilike(f'%{word}%')).all()
  
  response ={'count': len(data),
             'data':data}
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  
  artist = Artist.query.filter_by(id = artist_id).first()
  upcoming_show_query = Show.query.filter_by(artist_id = artist.id).filter(Show.start_time > (datetime.now())).join(Venue).all()
  upcoming_show_list =[]
  past_show_list = []
  for show in upcoming_show_query:
       dict_venue= {'venue_id': show.venue_id,
                    'venue_name':show.venues.name,
                    'venue_image_link':show.venues.image_link,
                    'start_time': str(show.start_time)}
       upcoming_show_list.append(dict_venue)
  past_show_query = Show.query.filter_by(artist_id = artist.id).filter(Show.start_time < (datetime.now())).join(Venue).all()
  for show in past_show_query:
      dict_venue= {'venue_id': show.venue_id,
                    'venue_name':show.venues.name,
                    'venue_image_link':show.venues.image_link,
                    'start_time': str(show.start_time)}
      past_show_list.append(dict_venue)
  data = artist.__dict__
  data['past_shows']= past_show_list
  data['upcoming_shows'] = upcoming_show_list
  data['past_shows_count'] = len(past_show_list)
  data["upcoming_shows_count"]= len(upcoming_show_list)
  
  
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  
  artist = Artist.query.filter_by(id = artist_id).first()
  form = ArtistForm(obj=artist)
  
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  artist = Artist.query.filter_by(id = artist_id).first()
  form = ArtistForm()
  if form.validate():
      try:
            artist.name = form.name.data
            artist.city = form.city.data
            artist.state = form.state.data
            artist.phone = form.phone.data
            artist.genres = form.genres.data
            artist.seeking_venue = form.seeking_venue.data
            artist.seeking_description = form.seeking_description.data
            artist.image_link = form.image_link.data
            artist.website = form.website_link
            artist.facebook_link = form.facebook_link.data
            db.session.add(artist)
            db.session.commit()
            
      except:
            db.session.rollback()
            print(sys.exc_info())
      finally:
            db.session.close()
  else:
        flash('Data is not ok')
        return render_template('forms/edit_artist.html', form=form, artist=artist)
  return redirect(url_for('show_artist', artist_id=artist_id))
  

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  venue = Venue.query.filter_by(id = venue_id).first()
  form = VenueForm(obj=venue)
  
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  venue = Venue.query.filter_by(id = venue_id).first()
  form = VenueForm(obj=venue)
  if form.validate() :
    try:
        venue.name=form.name.data
        venue.city=form.city.data
        venue.state=form.state.data
        venue.address=form.address.data
        venue.phone=form.phone.data
        venue.genres=form.genres.data
        venue.facebook_link=form.facebook_link.data
        venue.image_link=form.image_link.data
        venue.website=form.website_link.data
        venue.seeking_talent=form.seeking_talent.data
        venue.seeking_description=form.seeking_description.data
        db.session.add(venue)
        db.session.commit()
        flash('Venue ' + venue.name + ' was successfully edit!')
    except:
        flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
  else:
        flash('The data in the form is not ok')
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  form = VenueForm()
  form = ArtistForm()
  if 1==1:
        try :
          artist_new = Artist(name= form.name.data,
                            genres= form.genres.data,
                            city=form.city.data,
                            state= form.state.data,
                            phone= form.phone.data,
                            website= form.website_link.data,
                            facebook_link= form.facebook_link.data,
                            seeking_venue= form.seeking_venue.data,
                            seeking_description= form.seeking_description.data,
                            image_link= form.image_link.data)
          db.session.add(artist_new)
          db.session.commit()
         
          flash('Venue ' + artist_new.name + ' was successfully listed!')
        except:
          flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
          db.session.rollback()
          print(sys.exc_info())
        finally:
          db.session.close()
  else:
        flash('The data in the form is not ok')
          
  
  # on successful db insert, flash success
  flash('Artist ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  data = []
  #shows = Show.query.all()
  shows = db.session.query(Show).all()
  for show in shows:
        artist = Artist.query.filter_by(id=show.artist_id).first()
        venue = Venue.query.with_entities(Venue.name).filter_by(id=show.venue_id).first(),
        show_dict = {'venue_id':show.venue_id,
                     "venue_name":venue,
                     "artist_id":show.artist_id,
                     "artist_name":artist.name,
                     "artist_image_link":artist.image_link,
                     "start_time":str(show.start_time)
                     }
        data.append(show_dict)
 
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  form = ShowForm()
  if form.validate():
        try:
          show_new = Show(venue_id=form.venue_id.data,
                            artist_id=form.artist_id.data,
                            start_time=form.start_time.data,
                            )
          db.session.add(show_new)
          db.session.commit()
          flash('Show was successfully listed!')
        except:
          flash('An error occurred. Shows ' + request.form['artist_id'] + ' could not be listed.')
          db.session.rollback()
          # print(sys.exc_info())
        finally:
          db.session.close()
  else:
        flash('The data in the form is not ok')
      
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead

  # on successful db insert, flash success
  
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:

# if __name__ == '__main__':
#     port = int(os.environ.get('PORT', 3000))
#     app.run(host='0.0.0.0', port=port)

