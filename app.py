#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
import os
import sys
import json
from unicodedata import name
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, session, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from sqlalchemy import or_
from forms import *
from jinja2.utils import markupsafe 
from flask_migrate import Migrate
from models import Artist, Show, Venue, db
import collections

collections.Callable = collections.abc.Callable
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
# db = SQLAlchemy(app)
db.init_app(app)

migrate = Migrate(app, db)

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
  data = []
  city_states = Venue.query.with_entities(Venue.city, Venue.state).distinct().all()  
  for city_state in city_states:
    city = city_state[0]
    state = city_state[1]
    venues = Venue.query.filter_by(city=city, state=state).all()   

    data.append({
      "city": city,
      "state": state,
      "venues": venues
      })

  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  
  search_term = request.form.get('search_term', '')
  venues = db.session.query(Venue).filter(Venue.name.ilike('%' + search_term + '%'))

  data = []
  for venue in venues:
    data.append({
      "id": venue.id,
      "name": venue.name,
      "city": venue.city,
      "state": venue.state,
      "num_upcoming_shows": len(db.session.query(Show).filter(Show.venue_id == venue.id).filter(Show.start_time > datetime.now()).all())
    })
  count = len(data)
  response = {
    "count": count,
    "data": data
  }
  
  return render_template('pages/search_venues.html', results=response, search_term=search_term)

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  venue = Venue.query.get(venue_id)
  shows = Show.query.filter_by(venue_id=venue_id).all()
  our_current_time = datetime.now()
  past_shows = []
  upcoming_shows = []
  for show in shows:
    data = {
      "artist_id": show.artist_id,
      "artist_name": show.artist.name,
      "artist_image_link": show.artist.image_link,
      "start_time": format_datetime(str(show.start_time))
    }
    if show.start_time > our_current_time:
      upcoming_shows.append(data)
    else:
      past_shows.append(data)
  data = {
      "id": venue.id,
      "name": venue.name,
      "genres": venue.genres,
      "address": venue.address,
      "city": venue.city,
      "state": venue.state,
      "phone": venue.phone,
      "website_link": venue.website_link,
      "facebook_link": venue.facebook_link,
      "seeking_talent": venue.seeking_talent,
      "seeking_description": venue.seeking_description,
      "image_link": venue.image_link,
      "past_shows": past_shows,
      "upcoming_shows": upcoming_shows,
      "past_shows_count": len(past_shows),
      "upcoming_shows_count": len(upcoming_shows),
    }  
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
  error = False
  try:
    venue = Venue(
      name=request.form['name'], 
      city=request.form['city'], 
      state=request.form['state'], 
      address=request.form['address'], 
      phone=request.form['phone'],  
      genres=request.form.getlist('genres'),
      image_link=request.form['image_link'], 
      facebook_link=request.form['facebook_link'], 
      website_link=request.form['website_link'], 
      seeking_talent=bool(request.form['seeking_talent']), 
      seeking_description=request.form['seeking_description']
    )
    db.session.add(venue)
    db.session.commit()
  except:
    db.session.rollback()
    error = True
    print(sys.exc_info())
  finally:
    db.session.close()
  if error == True:
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
  else:
    flash('Venue ' + request.form['name'] + ' was successfully listed!')

  # TODO: modify data to be the data object returned from db insertion
  # on successful db insert, flash success
  # flash('Venue ' + request.form['name'] + ' was successfully listed!')

  # TODO: on unsuccessful db insert, flash an error instead.
  # flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

# @app.route('/venues/<venue_id>', methods=['DELETE'])
@app.route('/venues/<venue_id>/delete', methods=['GET', 'POST', 'DELETE'])
def delete_venue(venue_id):
  form = VenueForm()
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  error = False
  try:
    venue = Venue.query.get_or_404(venue_id)
    print(venue.name)
    db.session.delete(venue)
    db.session.commit()
    #db.session.expire_on_commit = False
  except Exception as e:
    print(e)
    db.session.rollback() 
    error = True
    print(sys.exc_info())
  finally:
    db.session.close() 
  if error == True:
    flash('An error occurred. Venue could not be deleted.')
  else:
    flash('Venue was successfully deleted!')
  #return None
    
  return render_template('pages/home.html', form=form, venue_id=venue_id)

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  data = [] 
  artists = Artist.query.with_entities(Artist.id, Artist.name).distinct().all()  
  for artist in artists:
    id = artist[0]
    name = artist[1]

    data.append({
      "id": id,
      "name": name
      })

  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".

  search_term = request.form.get('search_term', '')
  artists = db.session.query(Artist).filter(Artist.name.ilike('%' + search_term + '%'))
  data = []
  for artist in artists:
    data.append({
      "id": artist.id,
      "name": artist.name,
      "num_upcoming_shows": len(db.session.query(Show).filter(Show.artist_id == artist.id).filter(Show.start_time > datetime.now()).all())
    })
  count = len(data)
  response = {
    "count": count,
    "data": data
  }
  
  return render_template('pages/search_artists.html', results=response, search_term=search_term)

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  artist = Artist.query.get(artist_id)
  shows = Show.query.filter_by(artist_id=artist_id).all()
  our_current_time = datetime.now()
  past_shows = []
  upcoming_shows = []
  for show in shows:
    data = {
      "venue_id": show.venue_id,
      "venue_name": show.venue.name,
      "venue_image_link": show.venue.image_link,
      "start_time": format_datetime(str(show.start_time))
    }
    if show.start_time > our_current_time:
      upcoming_shows.append(data)
    else:
      past_shows.append(data)
  data = {
      "id": artist.id,
      "name": artist.name,
      "genres": artist.genres,
      "city": artist.city,
      "state": artist.state,
      "phone": artist.phone,
      "website_link": artist.website_link,
      "facebook_link": artist.facebook_link,
      "seeking_venue": artist.seeking_venue,
      "seeking_description": artist.seeking_description,
      "image_link": artist.image_link,
      "past_shows": past_shows,
      "upcoming_shows": upcoming_shows,
      "past_shows_count": len(past_shows),
      "upcoming_shows_count": len(upcoming_shows),
    }  
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artists = Artist.query.get(artist_id)

  artist={
    "id": artists.id,
    "name": artists.name,
    "genres": artists.genres,
    "city": artists.city,
    "state": artists.state,
    "phone": artists.phone,
    "website_link": artists.website_link,
    "facebook_link": artists.facebook_link,
    "seeking_venue": artists.seeking_venue,
    "seeking_description": artists.seeking_description,
    "image_link": artists.image_link
  }

  print(artists.name)
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
# @app.route('/artists/artist_id/edit', methods=['PUT'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  artist = Artist.query.get(artist_id)      
  error = False
  if request.method == "POST":
    artist.name=request.form['name']
    artist.city=request.form['city'] 
    artist.state=request.form['state'] 
    artist.phone=request.form['phone'] 
    artist.genres=request.form.getlist('genres')
    artist.image_link=request.form['image_link']
    artist.facebook_link=request.form['facebook_link'] 
    artist.website_link=request.form['website_link']
    artist.seeking_venue=bool(request.form['seeking_venue'])
    artist.seeking_description=request.form['seeking_description']
    print(artist.phone)
    try:
      db.session.add(artist)
      db.session.commit()
      db.session.expire_on_commit = False
    except:
      error = True
      db.session.rollback() 
      print(sys.exc_info())
    finally:
      db.session.close()
      
    if error == True:
      flash('An error occurred. Artist ' + request.form['name'] + ' could not be edited.')
    else:
      flash('Artist ' + request.form['name'] + ' was successfully edited!')

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venues = Venue.query.get(venue_id)

  venue={
    "id": venues.id,
    "name": venues.name,
    "genres": venues.genres,
    "city": venues.city,
    "state": venues.state,
    "address": venues.address,
    "phone": venues.phone,
    "website_link": venues.website_link,
    "facebook_link": venues.facebook_link,
    "seeking_talent": venues.seeking_talent,
    "seeking_description": venues.seeking_description,
    "image_link": venues.image_link
  }
  print(venues.name)

  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  venue = Venue.query.get(venue_id)      
  error = False
  if request.method == "POST":
    venue.name=request.form['name']
    venue.city=request.form['city'] 
    venue.state=request.form['state']
    venue.address=request.form['address'] 
    venue.phone=request.form['phone']
    venue.genres=request.form.getlist('genres')
    venue.image_link=request.form['image_link']
    venue.facebook_link=request.form['facebook_link'] 
    venue.website_link=request.form['website_link']
    venue.seeking_talent=bool(request.form['seeking_talent'])
    venue.seeking_description=request.form['seeking_description']
    print(venue.phone)
    try:
      db.session.add(venue)
      db.session.commit()
      db.session.expire_on_commit = False
    except:
      error = True
      db.session.rollback() 
      print(sys.exc_info())
    finally:
      db.session.close() 
    if error == True:
      flash('An error occurred. Venue ' + request.form['name'] + ' could not be edited.')
    else:
      flash('Venue ' + request.form['name'] + ' was successfully edited!')

  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  error = False
  try:
    artist = Artist(
      name=request.form['name'], 
      city=request.form['city'], 
      state=request.form['state'], 
      phone=request.form['phone'],  
      genres=request.form.getlist('genres'),
      image_link=request.form['image_link'], 
      facebook_link=request.form['facebook_link'], 
      website_link=request.form['website_link'], 
      seeking_venue=bool(request.form['seeking_venue']), 
      seeking_description=request.form['seeking_description']
    )
    db.session.add(artist)
    db.session.commit()
  except:
    db.session.rollback()
    error = True
    print(sys.exc_info())
  finally:
    db.session.close()
  if error == True:
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
  else:
    flash('Artist ' + request.form['name'] + ' was successfully listed!')

  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion

  # on successful db insert, flash success
  # flash('Artist ' + request.form['name'] + ' was successfully listed!')
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
  shows = db.session.query(Show, Artist, Venue). \
    select_from(Show).join(Artist).join(Venue).distinct().all()

  for show, artist, venue in shows:
    data.append({
      "venue_id": show.venue_id,
      "venue_name": venue.name,
      "artist_id": show.artist_id,
      "artist_name": artist.name,
      "artist_image_link": artist.image_link,
      "start_time": str(show.start_time)
      })

  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  error = False
  try:
    show = Show(
      start_time=request.form['start_time'], 
      artist_id=request.form['artist_id'], 
      venue_id=request.form['venue_id']
    )
    db.session.add(show)
    db.session.commit()
  except:
    db.session.rollback()
    error = True
    print(sys.exc_info())
  finally:
    db.session.close()
  if error == True:
    flash('An error occurred. Show could not be listed.')
  else:
    flash('Show was successfully listed!')
    
  # on successful db insert, flash success
  # flash('Show was successfully listed!')
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
if __name__ == '__main__':
  port = int(os.environ.get('PORT', 5000))
  app.run(host='127.0.0.0', port=port)
