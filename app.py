#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, current_app
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError
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

# TODO - DONE: connect to a local postgresql database
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SQLALCHEMY_DATABASE_URI']
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

    # add: update & delete functions

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

class Artist(db.Model):
    __tablename__ = 'Artist'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    artist_shows = db.relationship('Show', backref='Artist', lazy="dynamic")
    # reference for Dynamic relationship loaders: https://docs.sqlalchemy.org/en/13/orm/collections.html

    # TODO - Done : implement any missing fields, as a database migration using Flask-Migrate

    # initializing data - constructor
    def __init__(self, name, city, state, phone, genres, image_link, facebook_link):
      self.name = name
      self.city = city
      self.state = state
      self.phone = phone
      self.genres = genres
      self.image_link = image_link
      self.facebook_link = facebook_link

    def addArtist(self):
      db.session.add(self)
      db.session.commit()

    # add: update & delete functions

    def getDetails(self):
      return {
        'id': self.id,
        'name': self.name,
        'city': self.city,
        'state': self.state,
        'phone': self.phone,
        'genres': self.genres,
        'image_link': self.image_link,
        'facebook_link': self.facebook_link
      }
    def getShortDisplay(self):
      return {
        'id': self.id,
        'name': self.name
      }

# TODO - Boulos : change Nullable to False after DB entries then mark as Done

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
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

    # add: update & delete functions

  def getDetails(self):
    return {
      'id': self.id,
      'venu_id': self.venue_id,
      'venu_name': self.Venue.name,
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
  # TODO - Done: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  
  current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
  city_state = ''
  data = []

  # SELECT fields from Venue Group By id, city & state
  query_venue = Venue.query.group_by(Venue.id, Venue.city, Venue.state).all()

  # get the upcoming shows for every venue where the show will be after the current time (futur/upcoming show)
  # then assign to each venue the appropriate data grouping by the city & state
  # here we use the one-to-many relationship between Venue & Show from the attribute venue_shows to access the venue show start time
  for venue in query_venue:
    upcoming_shows = venue.venue_shows.filter(Show.start_time > current_time).all()

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

  return render_template('pages/venues.html', areas=data);
  
  # data=[{
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "venues": [{
  #     "id": 1,
  #     "name": "The Musical Hop",
  #     "num_upcoming_shows": 0,
  #   }, {
  #     "id": 3,
  #     "name": "Park Square Live Music & Coffee",
  #     "num_upcoming_shows": 1,
  #   }]
  # }, {
  #   "city": "New York",
  #   "state": "NY",
  #   "venues": [{
  #     "id": 2,
  #     "name": "The Dueling Pianos Bar",
  #     "num_upcoming_shows": 0,
  #   }]
  # }]

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  response={
    "count": 1,
    "data": [{
      "id": 2,
      "name": "The Dueling Pianos Bar",
      "num_upcoming_shows": 0,
    }]
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  
  # get venue from the db
  venue_inDB = Venue.query.get(venue_id)

  # check if venue exists, otherwise redirect to 404 page (NOT FOUND)
  if venue_inDB:
    venue_details = Venue.getDetails(venue_inDB)
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    ## Get upcoming shows & its' count ## 
    # perform a JOIN SQL statement between the Show & Artist in order to get the upcoming show (new shows) where the start time will be after the current time
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
  
  # data1={
  #   "id": 1,
  #   "name": "The Musical Hop",
  #   "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
  #   "address": "1015 Folsom Street",
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "123-123-1234",
  #   "website": "https://www.themusicalhop.com",
  #   "facebook_link": "https://www.facebook.com/TheMusicalHop",
  #   "seeking_talent": True,
  #   "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
  #   "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
  #   "past_shows": [{
  #     "artist_id": 4,
  #     "artist_name": "Guns N Petals",
  #     "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
  #     "start_time": "2019-05-21T21:30:00.000Z"
  #   }],
  #   "upcoming_shows": [],
  #   "past_shows_count": 1,
  #   "upcoming_shows_count": 0,
  # }
  # data2={
  #   "id": 2,
  #   "name": "The Dueling Pianos Bar",
  #   "genres": ["Classical", "R&B", "Hip-Hop"],
  #   "address": "335 Delancey Street",
  #   "city": "New York",
  #   "state": "NY",
  #   "phone": "914-003-1132",
  #   "website": "https://www.theduelingpianos.com",
  #   "facebook_link": "https://www.facebook.com/theduelingpianos",
  #   "seeking_talent": False,
  #   "image_link": "https://images.unsplash.com/photo-1497032205916-ac775f0649ae?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=750&q=80",
  #   "past_shows": [],
  #   "upcoming_shows": [],
  #   "past_shows_count": 0,
  #   "upcoming_shows_count": 0,
  # }
  # data3={
  #   "id": 3,
  #   "name": "Park Square Live Music & Coffee",
  #   "genres": ["Rock n Roll", "Jazz", "Classical", "Folk"],
  #   "address": "34 Whiskey Moore Ave",
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "415-000-1234",
  #   "website": "https://www.parksquarelivemusicandcoffee.com",
  #   "facebook_link": "https://www.facebook.com/ParkSquareLiveMusicAndCoffee",
  #   "seeking_talent": False,
  #   "image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #   "past_shows": [{
  #     "artist_id": 5,
  #     "artist_name": "Matt Quevedo",
  #     "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
  #     "start_time": "2019-06-15T23:00:00.000Z"
  #   }],
  #   "upcoming_shows": [{
  #     "artist_id": 6,
  #     "artist_name": "The Wild Sax Band",
  #     "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #     "start_time": "2035-04-01T20:00:00.000Z"
  #   }, {
  #     "artist_id": 6,
  #     "artist_name": "The Wild Sax Band",
  #     "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #     "start_time": "2035-04-08T20:00:00.000Z"
  #   }, {
  #     "artist_id": 6,
  #     "artist_name": "The Wild Sax Band",
  #     "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #     "start_time": "2035-04-15T20:00:00.000Z"
  #   }],
  #   "past_shows_count": 1,
  #   "upcoming_shows_count": 1,
  # }

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO - Done: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion

  dataFromForm = request.form

  try:
    # retrieve venue's data from the form submitted by the user 
    newVenue = Venue(
      name = dataFromForm.get('name'),
      genres = dataFromForm.getlist('genres'),
      city = dataFromForm.get('city'),
      state = dataFromForm.get('state'),
      address = dataFromForm.get('address'),
      phone = dataFromForm.get('phone'),
      image_link = dataFromForm.get('image_link'),
      facebook_link = dataFromForm.get('facebook_link')
    )
    # add the new venue to the DB
    Venue.addVenue(newVenue)
  except:
    # TODO - Done: on unsuccessful db insert, flash an error instead.
    flash('the following error occured: ' + SQLAlchemyError.message + 'Venue ' + dataFromForm.name + ' could not be listed.')
    db.session.rollback()
  finally:
    # on successful db insert, flash success
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
    return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database

  # get all artists from the db
  query_artist = Artist.query.all()

  # map retrieved artists to the display short form
  mapped_artists = list(map(Artist.getShortDisplay, query_artist))

  return render_template('pages/artists.html', artists=mapped_artists)

  # data=[{
  #   "id": 4,
  #   "name": "Guns N Petals",
  # }, {
  #   "id": 5,
  #   "name": "Matt Quevedo",
  # }, {
  #   "id": 6,
  #   "name": "The Wild Sax Band",
  # }]

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  response={
    "count": 1,
    "data": [{
      "id": 4,
      "name": "Guns N Petals",
      "num_upcoming_shows": 0,
    }]
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id

  # get artist from the db
  artist_inDB = Artist.query.get(artist_id)

  # check if artist exists, otherwise redirect to 404 page (NOT FOUND)
  if artist_inDB:
    artist_details = Artist.getDetails(artist_inDB)
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    ## Get upcoming shows & its' count ## 
    # perform a JOIN SQL statement between the Show & Artist in order to get the upcoming show (new shows) where the start time will be after the current time
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

  # data1={
  #   "id": 4,
  #   "name": "Guns N Petals",
  #   "genres": ["Rock n Roll"],
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "326-123-5000",
  #   "website": "https://www.gunsnpetalsband.com",
  #   "facebook_link": "https://www.facebook.com/GunsNPetals",
  #   "seeking_venue": True,
  #   "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
  #   "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
  #   "past_shows": [{
  #     "venue_id": 1,
  #     "venue_name": "The Musical Hop",
  #     "venue_image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
  #     "start_time": "2019-05-21T21:30:00.000Z"
  #   }],
  #   "upcoming_shows": [],
  #   "past_shows_count": 1,
  #   "upcoming_shows_count": 0,
  # }
  # data2={
  #   "id": 5,
  #   "name": "Matt Quevedo",
  #   "genres": ["Jazz"],
  #   "city": "New York",
  #   "state": "NY",
  #   "phone": "300-400-5000",
  #   "facebook_link": "https://www.facebook.com/mattquevedo923251523",
  #   "seeking_venue": False,
  #   "image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
  #   "past_shows": [{
  #     "venue_id": 3,
  #     "venue_name": "Park Square Live Music & Coffee",
  #     "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #     "start_time": "2019-06-15T23:00:00.000Z"
  #   }],
  #   "upcoming_shows": [],
  #   "past_shows_count": 1,
  #   "upcoming_shows_count": 0,
  # }
  # data3={
  #   "id": 6,
  #   "name": "The Wild Sax Band",
  #   "genres": ["Jazz", "Classical"],
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "432-325-5432",
  #   "seeking_venue": False,
  #   "image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #   "past_shows": [],
  #   "upcoming_shows": [{
  #     "venue_id": 3,
  #     "venue_name": "Park Square Live Music & Coffee",
  #     "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #     "start_time": "2035-04-01T20:00:00.000Z"
  #   }, {
  #     "venue_id": 3,
  #     "venue_name": "Park Square Live Music & Coffee",
  #     "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #     "start_time": "2035-04-08T20:00:00.000Z"
  #   }, {
  #     "venue_id": 3,
  #     "venue_name": "Park Square Live Music & Coffee",
  #     "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #     "start_time": "2035-04-15T20:00:00.000Z"
  #   }],
  #   "past_shows_count": 0,
  #   "upcoming_shows_count": 3,
  # }

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist={
    "id": 4,
    "name": "Guns N Petals",
    "genres": ["Rock n Roll"],
    "city": "San Francisco",
    "state": "CA",
    "phone": "326-123-5000",
    "website": "https://www.gunsnpetalsband.com",
    "facebook_link": "https://www.facebook.com/GunsNPetals",
    "seeking_venue": True,
    "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
    "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80"
  }
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue={
    "id": 1,
    "name": "The Musical Hop",
    "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
    "address": "1015 Folsom Street",
    "city": "San Francisco",
    "state": "CA",
    "phone": "123-123-1234",
    "website": "https://www.themusicalhop.com",
    "facebook_link": "https://www.facebook.com/TheMusicalHop",
    "seeking_talent": True,
    "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
    "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"
  }
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
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
  # TODO - Done: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  dataFromForm = request.form

  try:
    # retrieve artist's data from the form submitted by the user 
    newArtist = Artist(
      name = dataFromForm.get('name'),
      city = dataFromForm.get('city'),
      state = dataFromForm.get('state'),
      phone = dataFromForm.get('phone'),
      genres = dataFromForm.getlist('genres'),
      image_link = dataFromForm.get('image_link'),
      facebook_link = dataFromForm.get('facebook_link')
    )
    # add the new artist to the DB
    Artist.addArtist(newArtist)
  except:
    # TODO - Done: on unsuccessful db insert, flash an error instead.
    flash('the following error occured: ' + SQLAlchemyError.message + 'Artist ' + dataFromForm.name + ' could not be listed.')
    db.session.rollback()
  finally:
    # on successful db insert, flash success
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
    return render_template('pages/home.html')

#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  query_shows = Show.query.all()
  mapped_shows = list(map(Show.getDetails, query_shows))
  data = mapped_shows
  
  return render_template('pages/shows.html', shows=data)

  # data=[{
  #   "venue_id": 1,
  #   "venue_name": "The Musical Hop",
  #   "artist_id": 4,
  #   "artist_name": "Guns N Petals",
  #   "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
  #   "start_time": "2019-05-21T21:30:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 5,
  #   "artist_name": "Matt Quevedo",
  #   "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
  #   "start_time": "2019-06-15T23:00:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 6,
  #   "artist_name": "The Wild Sax Band",
  #   "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #   "start_time": "2035-04-01T20:00:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 6,
  #   "artist_name": "The Wild Sax Band",
  #   "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #   "start_time": "2035-04-08T20:00:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 6,
  #   "artist_name": "The Wild Sax Band",
  #   "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #   "start_time": "2035-04-15T20:00:00.000Z"
  # }]

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO - Done: insert form data as a new Show record in the db, instead
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
    # TODO - Done: on unsuccessful db show, flash an error instead.
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
