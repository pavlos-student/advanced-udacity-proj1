#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, current_app
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text
from sqlalchemy.dialects import postgresql
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import func, inspect
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    genres = db.Column(db.String(120))
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    website = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    venue_shows = db.relationship('Show', backref='Venue', lazy="dynamic")
    # reference for Dynamic relationship loaders: https://docs.sqlalchemy.org/en/13/orm/collections.html

    # TODO - Done: implement any missing fields, as a database migration using Flask-Migrate

    # initializing data - constructor
    def __init__(self, name, genres, city, state, address, phone, website, image_link, facebook_link):
      self.name = name
      self.genres = genres
      self.city = city
      self.state = state
      self.address = address
      self.phone = phone
      self.website = website
      self.image_link = image_link
      self.facebook_link = facebook_link

    def addVenue(self):
      db.session.add(self)
      db.session.commit()

    def updateVenue(self):
      db.session.commit()

    def deleteVenue(self):
      db.session.delete(self)
      db.session.commit()

    def getDetails(self):
      return {
        'id': self.id,
        'name': self.name,
        'genres': self.genres,
        'city': self.city,
        'state': self.state,
        'address': self.address,
        'phone': self.phone,
        'website': self.website,
        'image_link': self.image_link,
        'facebook_link': self.facebook_link
      }
    
    def getShortDisplay(self):
      return {
        'id': self.id,
        'name': self.name
      }

class Artist(db.Model):
    __tablename__ = 'Artist'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    website = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    artist_shows = db.relationship('Show', backref='Artist', lazy="dynamic")
    # reference for Dynamic relationship loaders: https://docs.sqlalchemy.org/en/13/orm/collections.html

    # TODO - Done : implement any missing fields, as a database migration using Flask-Migrate

    # initializing data - constructor
    def __init__(self, name, city, state, phone, website, genres, image_link, facebook_link):
      self.name = name
      self.city = city
      self.state = state
      self.phone = phone
      self.website = website
      self.genres = genres
      self.image_link = image_link
      self.facebook_link = facebook_link

    def addArtist(self):
      db.session.add(self)
      db.session.commit()

    def updateArtist(self):
      db.session.commit()

    def deleteArtist(self):
      db.session.delete(self)
      db.session.commit()

    def getDetails(self):
      return {
        'id': self.id,
        'name': self.name,
        'city': self.city,
        'state': self.state,
        'phone': self.phone,
        'website': self.website,
        'genres': self.genres,
        'image_link': self.image_link,
        'facebook_link': self.facebook_link
      }

    def getShortDisplay(self):
      return {
        'id': self.id,
        'name': self.name
      }

# TODO - Done: Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
class Show(db.Model):
  __tablename__ = 'Show'
  id = db.Column(db.Integer, primary_key=True)
  venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
  artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)
  start_time = db.Column(db.DateTime, nullable=False)

  # initializing data - constructor
  def __init__(self, venue_id, artist_id, start_time):
    self.venue_id = venue_id
    self.artist_id = artist_id
    self.start_time = start_time

  def addShow(self):
    db.session.add(self)
    db.session.commit()

  def getDetails(self):
    return {
      'id': self.id,
      'venue_id': self.venue_id,
      'venue_name': self.Venue.name,
      'artist_id': self.artist_id,
      'artist_name': self.Artist.name,
      'artist_image_link': self.Artist.image_link,
      'start_time': self.start_time
    }

  def getArtistDetails(self):
    return {
      'artist_id': self.artist_id,
      'artist_name': self.Artist.name,
      'artist_image_link': self.Artist.image_link,
      'start_time': self.start_time
    }
  
  def getVenueDetails(self):
    return {
      'venu_id': self.venue_id,
      'venu_name': self.Venue.name,
      'venue_image_link': self.Venue.image_link,
      'start_time': self.start_time
    }

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
  
  current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
  city_state = ''
  data = []

  # SQL query
  # SELECT * from Venue Group By id, city & state
  query_venue = Venue.query.group_by(Venue.id, Venue.city, Venue.state).all()

  # get the upcoming shows for every venue where the show will be after the current time (futur/upcoming show)
  # then assign to each venue the appropriate data grouping by the city & state
  # here we use the one-to-many relationship between Venue & Show from the attribute venue_shows to access the venue show start time
  for venue in query_venue:
    upcoming_shows = venue.venue_shows.filter(Show.start_time > current_time).all()
    # SQL query
    # SELECT * FROM Venue as v INNER JOIN Show as s ON s.venue_id = s.venue_id WHERE start_time > current time

    # if city & state are equal to the venues city & state then just append the upcoming number of shows to the venues JSON
    # otherwise set the city & state to the venues + the upcoming show numbers
    #  data[len(data) - 1]["venues"] to append to the venues place in the JSON object according to its place (the data length may change in the future that's why it's generic)
    if city_state == venue.city + venue.state:
      data[len(data) - 1]["venues"].append({
        'id': venue.id,
        'name': venue.name,
        'num_upcoming_shows': len(upcoming_shows)
      })
    else:
      city_state = venue.city + venue.state
      data.append({
        'city': venue.city,
        'state': venue.state,
        'venues': [{
          'id': venue.id,
          'name': venue.name,
          'num_upcoming_shows': len(upcoming_shows)
        }]
      })

  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # SQL query:
  # SELECT id, name FROM Venue WHERE name LIKE '%' + search_term + '%'  
  query_venu = Venue.query.filter(Venue.name.ilike('%' + request.form['search_term'] + '%'))
  for result in query_venu:
    venue_array = list(map(Venue.getShortDisplay, query_venu))
    
  response = {
    "count": len(venue_array),
    "data": venue_array
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO - Done: replace with real venue data from the venues table, using venue_id
  
  # get venue from the db
  venue_inDB = Venue.query.get(venue_id)

  # check if venue exists, otherwise redirect to 404 page (NOT FOUND)
  if venue_inDB:
    venue_details = Venue.getDetails(venue_inDB)
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    ## Get upcoming shows & its' count ## 
    # perform a JOIN SQL statement between the Show & Artist in order to get the upcoming show (new shows) where the start time will be after the current time
    # SQL statement:
    # SELECT * FROM Show as s INNER JOIN Artist as a ON s.venue_id = a.venue_id WHERE start_time > current_time
    query_new_show = Show.query.options(db.joinedload('Artist')).filter(Show.venue_id == venue_id).filter(Show.start_time > current_time).all()
    # list of mapped Artist's show details according to the above JOIN statement (query_new_show)
    new_show = list(map(Show.getArtistDetails, query_new_show))
    venue_details['upcoming_shows'] = new_show
    venue_details['upcoming_shows_count'] = len(new_show)

    ## Get past shows & its' count ##
    # perform a JOIN SQL statement between the Show & Artist in order to get the past show where the start time will be before the current time
    query_past_show = Show.query.options(db.joinedload('Artist')).filter(Show.venue_id == venue_id).filter(Show.start_time <= current_time).all()
    # list of mapped Artist's show details according to the above JOIN statement (query_past_show)
    past_shows = list(map(Show.getArtistDetails, query_past_show))
    venue_details['past_shows'] = past_shows
    venue_details['past_shows_count'] = len(past_shows)

    return render_template('pages/show_venue.html', venue=venue_details)
  else:
    return render_template('errors/404.html')

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():

  dataFromForm = request.form

  try:
    # retrieve venue's data from the form submitted by the user 
    newVenue = Venue(
      name = dataFromForm.get('name'),
      genres = dataFromForm.getlist('genres'),
      website = dataFromForm.get('website'),
      city = dataFromForm.get('city'),
      state = dataFromForm.get('state'),
      address = dataFromForm.get('address'),
      phone = dataFromForm.get('phone'),
      image_link = dataFromForm.get('image_link'),
      facebook_link = dataFromForm.get('facebook_link')
    )
    # SQL query
    # INSERT INTO Venue (name, genres, website, city, state, address, phone, image_link, facebook_link) VALUES (newVenue.name, newVenue.genres, newVenue.website, newVenue.city, newVenue.state, newVenue.address, newVenue.phone, newVenue.image_link, newVenue.facebook_link)
    # add the new venue to the DB
    Venue.addVenue(newVenue)
    # on successful db insert, flash success
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
    return render_template('pages/home.html')
  except:
    flash('the following error occured: ' + SQLAlchemyError.message + 'Venue ' + dataFromForm.name + ' could not be listed.')
    db.session.rollback()

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  venue_query = Venue.query.get(venue_id)
  
  if venue_query:
    Venue.deleteVenue(venue_query)
    # SQL query:
    # DELETE FROM Venue WHERE id = venue_id
  else:
    flash('An error occurred while deleting the venue, please try again later')
  return None

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # get all artists from the db by sqlalchemy queries
  query_artist = Artist.query.all()
  
  # get all artists from the db by SQL queries didn't work
  # sql = text('select * from Artist')
  # artists = db.engine.execute(sql)
  # artists_list = artists.fetchall()

  # map retrieved artists to the display short form
  mapped_artists = list(map(Artist.getShortDisplay, query_artist))

  return render_template('pages/artists.html', artists=mapped_artists)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  
  # SQL query:
  # SELECT id, name FROM Artist WHERE name LIKE '%' + search_term + '%'
  query_artist = Artist.query.filter(Artist.name.ilike('%' + request.form['search_term'] + '%'))
  for result in query_artist:
    artist_array = list(map(Artist.getShortDisplay, query_artist))
    
  response = {
    "count": len(artist_array),
    "data": artist_array
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  
  # get artist from the db
  artist_inDB = Artist.query.get(artist_id)

  # check if artist exists, otherwise redirect to 404 page (NOT FOUND)
  if artist_inDB:
    artist_details = Artist.getDetails(artist_inDB)
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    ## Get upcoming shows & its' count ## 
    # perform a JOIN SQL statement between the Show & Artist in order to get the upcoming show (new shows) where the start time will be after the current time
    # SQL statement:
    # SELECT * FROM Show as s INNER JOIN Artist as a ON s.artist_id = a.artist_id WHERE start_time > current_time
    query_new_show = Show.query.options(db.joinedload('Artist')).filter(Show.artist_id == artist_id).filter(Show.start_time > current_time).all()
    # list of mapped Venue's show details that are related to this artist (according to the above JOIN statement - query_new_show)
    new_show = list(map(Show.getVenueDetails, query_new_show))
    artist_details['upcoming_shows'] = new_show
    artist_details['upcoming_shows_count'] = len(new_show)

    ## Get past shows & its' count ##
    # perform a JOIN SQL statement between the Show & Artist in order to get the past show where the start time will be before the current time
    query_past_show = Show.query.options(db.joinedload('Artist')).filter(Show.artist_id == artist_id).filter(Show.start_time <= current_time).all()
    # list of mapped Venue's show details that are related to this artist (according to the above JOIN statement - query_past_show)
    past_shows = list(map(Show.getVenueDetails, query_past_show))
    artist_details['past_shows'] = past_shows
    artist_details['past_shows_count'] = len(past_shows)

    return render_template('pages/show_artist.html', artist=artist_details)
  else:
    return render_template('errors/404.html')

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
# TODO - Done: populate form with fields from artist with ID <artist_id>

  form = ArtistForm()
  # SQL query:
  # SELECT * FROM Artist WHERE id = artist_id
  query_artist = Artist.query.get(artist_id)

  # fill the form with the data already available, what isn't available will remain empty for the user to fill in
  if query_artist:
    artist_details = Artist.getDetails(query_artist)
    form.name.data = artist_details["name"]
    form.genres.data = artist_details["genres"]
    form.city.data = artist_details["city"]
    form.state.data = artist_details["state"]
    form.phone.data = artist_details["phone"]
    form.website.data = artist_details["website"]
    form.facebook_link.data = artist_details["facebook_link"]
    return render_template('forms/edit_artist.html', form=form, artist=artist_details) 
  return render_template('errors/404.html')

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # SQL query:
  # SELECT * FROM Artist WHERE id = artist_id
  artist_query = Artist.query.get(artist_id)

  # upating the form with the user's entered data
  if artist_query:
    setattr(artist_query, 'name', request.form.get('name'))
    setattr(artist_query, 'genres', request.form.getlist('genres'))
    setattr(artist_query, 'city', request.form.get('city'))
    setattr(artist_query, 'state', request.form.get('state'))
    setattr(artist_query, 'website', request.form.get('website'))
    setattr(artist_query, 'phone', request.form.get('phone'))
    setattr(artist_query, 'facebook_link', request.form.get('facebook_link'))
    Artist.updateArtist(artist_query)
    # SQL query:
    # UPDATE Artist SET 'name' = request.form.get('name'), 'genres'= request.form.getlist('genres'))...WHERE id = artist_id
    
    return redirect(url_for('show_artist', artist_id=artist_id))
  else:
    flash('Updating the form was not successful')
  return render_template('errors/404.html')

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  # SQL query:
  # SELECT * FROM Venue WHERE id = venue_id
  venue_query = Venue.query.get(venue_id)

  # fill the form with the data already available, what isn't available will remain empty for the user to fill in
  if venue_query:
    venue_details = Venue.getDetails(venue_query)
    form.name.data = venue_details["name"]
    form.genres.data = venue_details["genres"]
    form.address.data = venue_details["address"]
    form.website.data = venue_details["website"]
    form.city.data = venue_details["city"]
    form.state.data = venue_details["state"]
    form.phone.data = venue_details["phone"]
    form.facebook_link.data = venue_details["facebook_link"]
    return render_template('forms/edit_venue.html', form=form, venue=venue_details)
  return render_template('errors/404.html')

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # venue record with ID <venue_id> using the new attributes
  # SQL query:
  # SELECT * FROM Venue WHERE id = venue_id
  venue_query = Venue.query.get(venue_id)

  # upating the form with the user's entered data
  if venue_query:
    setattr(venue_query, 'name', request.form.get('name'))
    setattr(venue_query, 'genres', request.form.getlist('genres'))
    setattr(venue_query, 'city', request.form.get('city'))
    setattr(venue_query, 'website', request.form.get('website'))
    setattr(venue_query, 'state', request.form.get('state'))
    setattr(venue_query, 'address', request.form.get('address'))
    setattr(venue_query, 'phone', request.form.get('phone'))
    setattr(venue_query, 'facebook_link', request.form.get('facebook_link'))
    Venue.updateVenue(venue_query)
    # SQL query:
    # UPDATE Venue SET 'name' = request.form.get('name'), 'genres'= request.form.getlist('genres'))...WHERE id = venue_id
    return redirect(url_for('show_venue', venue_id=venue_id))
  return render_template('errors/404.html')

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  #  modify data to be the data object returned from db insertion
  dataFromForm = request.form

  try:
    # retrieve artist's data from the form submitted by the user 
    newArtist = Artist(
      name = dataFromForm.get('name'),
      city = dataFromForm.get('city'),
      website = dataFromForm.get('website'),
      state = dataFromForm.get('state'),
      phone = dataFromForm.get('phone'),
      genres = dataFromForm.getlist('genres'),
      image_link = dataFromForm.get('image_link'),
      facebook_link = dataFromForm.get('facebook_link')
    )
    # SQL query
    # INSERT INTO Artist (name, city, website, state, phone, genres, image_link, facebook_link) VALUES (newArtist.name, newArtist.city, newArtist.website, newArtist.state, newArtist.phone, newArtist.genres, newArtist.image_link, newArtist.facebook_link)
    # add the new artist to the DB
    Artist.addArtist(newArtist)
    # on successful db insert, flash success
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
    return render_template('pages/home.html')
  except:
    flash('the following error occured: ' + SQLAlchemyError.message + 'Artist ' + dataFromForm.name + ' could not be listed.')
    db.session.rollback()

#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  query_shows = Show.query.all()
  mapped_shows = list(map(Show.getDetails, query_shows))
  data = mapped_shows
  
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  dataFromForm = request.form

  try:
    # retrieve show's data from the form submitted by the user 
    newShow = Show(
      venue_id = dataFromForm.get('venue_id'),
      artist_id = dataFromForm.get('artist_id'),
      start_time = dataFromForm.get('start_time')
    )
    # add the new show to the DB
    Show.addShow(newShow)
  except:
    flash('An error occurred. Show could not be listed.')
    db.session.rollback()
  finally:
    # on successful db show, flash success
    flash('Show was successfully listed!')
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
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
