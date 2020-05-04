#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
from datetime import date
import config
import sys
import phonenumbers
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

migrate = Migrate(app, db)
## TODO: connect to a local postgresql database

now =datetime.utcnow()
#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    website = db.Column(db.String(500))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String))
    seeking_talent = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(500))
    shows = db.relationship('Show', backref="venue", lazy = True, cascade="all, delete-orphan")
    ## TODO: implement any missing fields, as a database migration using Flask-Migrate

##Inserts desired data structure into Venues page
    def get_venue(self):
        u_show = Venue.query.join(Show, Show.s_venue==Venue.id).filter(Show.s_venue==self.id, Show.s_start>now).count()
        v_record={
        'id': self.id,
        'name': self.name,
        'num_upcoming_shows': u_show
        }
        return v_record
## End description ______________________________________________________________

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String))
    website = db.Column(db.String(500))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(500))
    shows = db.relationship('Show', backref="artist", lazy=True, cascade="all, delete-orphan")

    ## TODO: implement any missing fields, as a database migration using Flask-Migrate
    def get_artist(self):
        u_show = Artist.query.join(Show, Show.s_venue==Artist.id).filter(Show.s_venue==self.id, Show.s_start>now).count()
        a_record={
        'id': self.id,
        'name': self.name,
        'num_upcoming_shows': u_show
        }
        return a_record


## TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
class Show(db.Model):
    __tablename__ = 'Show'
    id = db.Column(db.Integer, primary_key=True)
    s_start = db.Column(db.DateTime, nullable=False)
    s_artist = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)
    s_venue = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)

##Obtains number of upcoming and past shows for a given venue#
    @classmethod
    def up_shows_count(cls, venue_id):
        shows = Venue.query.join(cls).filter(Venue.id==venue_id, Show.s_start>now).count()
        return shows

    @classmethod
    def past_shows_count(cls, venue_id):
        shows = Venue.query.join(cls).filter(Venue.id== venue_id, Show.s_start<now).count()
        return shows
## End description  ----------------------------------------------------------#

##Obtains number of upcoming and past shows for a given venue#
    @classmethod
    def past_shows (cls, venue_id):
        shows = cls.query.join(Venue, Artist).with_entities(Show.s_artist, Show.s_start, Artist.name, Artist.image_link).filter(Venue.id==venue_id, Show.s_start<now).all()
        records =[]
        for show in shows:
            record ={
            "artist_id": show.s_artist,
            "artist_name": show.name,
            "artist_image_link": show.image_link,
            "start_time": str(show.s_start)
            }
            records.append(record)
        return records

    @classmethod
    def upcoming_shows (cls, venue_id):
        shows = cls.query.join(Venue, Artist).with_entities(Show.s_artist, Show.s_start, Artist.name, Artist.image_link).filter(Venue.id==venue_id, Show.s_start>now).all()
        records =[]
        for show in shows:
            record ={
            "artist_id": show.s_artist,
            "artist_name": show.name,
            "artist_image_link": show.image_link,
            "start_time": str(show.s_start)
            }
            records.append(record)
        return records
## End description ----------------------------------------------------------#

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

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
  ## TODO: replace with real venues data.
  ##       num_shows should be aggregated based on number of upcoming shows per venue.
  data= []
  areas = Venue.query.distinct('city','state').all()
  for area in areas:
      venues = Venue.query.filter(Venue.city==area.city, Venue.state==area.state).all()
      record = {
      'city': area.city,
      'state': area.state,
      'venues': [venue.get_venue() for venue in venues]
      }
      data.append(record)
  print(data)
  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  ## TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search_term = request.form.get('search_term','')
  venues_count = Venue.query.filter(Venue.name.ilike('%'+ search_term +'%')).count()
  venues = Venue.query.filter(Venue.name.ilike('%'+ search_term +'%')).all()
  data =[venue.get_venue() for venue in venues]
  response={
    "count": venues_count,
    "data": data
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  ## TODO: replace with real venue data from the venues table, using venue_id
    venue = Venue.query.filter(Venue.id == venue_id).one()
    upcoming_shows_count = Show.up_shows_count(venue_id = venue_id)
    upcoming_shows = Show.upcoming_shows(venue_id=venue_id)
    past_shows_count = Show.past_shows_count(venue_id = venue_id)
    past_shows = Show.past_shows(venue_id = venue_id)
    data= {
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
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": past_shows_count,
    "upcoming_shows_count": upcoming_shows_count
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
  ## TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  form = VenueForm(request.form)
  if form.validate():
      current_records = Venue.query.all()
      for record in current_records:
          if request.form['phone']== record.phone:
              flash('Venue ' + request.form['name'] + ' already exists.')
          else:
              try:
                  talent_input = request.form['seeking_talent']
                  if talent_input == 'Yes':
                      seeking_talent = True
                  else:
                      seeking_talent = False
                  new_venue = Venue(
                  name = request.form['name'],
                  city = request.form['city'],
                  state = request.form['state'],
                  address = request.form['address'],
                  phone = request.form['phone'],
                  website = request.form['website'],
                  image_link = request.form['image_link'],
                  facebook_link = request.form['facebook_link'],
                  genres = request.form.getlist('genres'),
                  seeking_talent = seeking_talent,
                  seeking_description = request.form['seeking_description']
                  )
                  ## on successful db insert, flash success
                  db.session.add(new_venue)
                  db.session.commit()
                  flash('Venue ' + request.form['name'] + ' was successfully listed!')
              except:
                  db.session.rollback()
                  print (sys.exc_info())
                  flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
                  ## TODO: on unsuccessful db insert, flash an error instead.
                  ## e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
                  ## see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
              finally:
                  db.session.close()
  else:
      flash( form.errors )
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  try:
      venue = Venue.query.filter(Venue.id == venue_id).one()
      db.session.delete(venue)
      db.session.commit()
      flash('Venue successfully deleted')
  except:
      print(str(venue) + "not deleted")
      db.session.rollback()
      flash('Error. Venue could not be deleted')
  finally:
      db.session.close()
  return None

  ## BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  ## TODO: replace with real data returned from querying the database
  data=Artist.query.with_entities(Artist.id, Artist.name).all()
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  ## TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search_term = request.form.get('search_term','')
  artists_count = Artist.query.filter(Artist.name.ilike('%'+ search_term +'%')).count()
  artists = Artist.query.filter(Artist.name.ilike('%'+ search_term +'%')).all()
  data =[artist.get_artist() for artist in artists]
  response={
  "count": artists_count,
  "data": data
    }

  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  ## TODO: replace with real venue data from the venues table, using venue_id

  artist = Artist.query.filter(Artist.id == artist_id).one()
  upcoming_shows_count = Show.query.filter(Show.s_artist==artist_id, Show.s_start>now).count()
  upcoming_shows = Show.query.join(Venue).with_entities(Show.s_venue, Show.s_start, Venue.name, Venue.image_link).filter(Show.s_artist==artist_id, Show.s_start>now).all()
  up_records =[]
  for show in upcoming_shows:
      record ={
      "venue_id": show.s_venue,
      "venue_name": show.name,
      "venue_image_link": show.image_link,
      "start_time": str(show.s_start)
      }
      up_records.append(record)

  past_shows_count = Show.query.filter(Show.s_artist==artist_id, Show.s_start<now).count()
  past_shows = Show.query.join(Venue).with_entities(Show.s_venue, Show.s_start, Venue.name, Venue.image_link).filter(Show.s_artist==artist_id, Show.s_start<now).all()
  past_records =[]
  for show in past_shows:
      record ={
      "venue_id": show.s_venue,
      "venue_name": show.name,
      "venue_image_link": show.image_link,
      "start_time": str(show.s_start)
      }
      past_records.append(record)

  data ={
  "id": artist.id,
  "name": artist.name,
  "genres": artist.genres,
  "city": artist.city,
  "state": artist.state,
  "phone": artist.phone,
  "website": artist.website,
  "image_link": artist.image_link,
  "facebook_link": artist.facebook_link,
  "seeking_venue": artist.seeking_venue,
  "seeking_description": artist.seeking_description,
  "past_shows": past_records,
  "upcoming_shows": up_records,
  "past_shows_count": past_shows_count,
   "upcoming_shows_count": upcoming_shows_count
  }

  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  data = Artist.query.filter(Artist.id == artist_id).one()

  #Populate the loaded form with prior data#
  form.name.data = data.name
  form.genres.data = data.genres
  form.city.data = data.city
  form.state.data = data.state
  form.website.data = data.website
  form.phone.data = data.phone
  form.facebook_link.data = data.facebook_link
  form.seeking_venue.data = data.seeking_venue
  form.seeking_description.data = data.seeking_description
  form.image_link.data = data.image_link


  artist={
    "id": data.id,
    "name": data.name,
    "genres": data.genres,
    "city": data.city,
    "state": data.state,
    "phone": data.phone,
    "website": data.website,
    "facebook_link": data.facebook_link,
    "seeking_venue": data.seeking_venue,
    "seeking_description": data.seeking_description,
    "image_link": data.image_link
  }
   #end description-----------------------------------------#

  ## TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
   form = ArtistForm(request.form)
   if form.validate():
       try:
           artist = Artist.query.filter(Artist.id == artist_id).one()
           venue_input = request.form['seeking_venue']
           if venue_input == 'Yes':
               seeking_venue = True
           else:
               seeking_venue = False
           artist.name = request.form['name']
           artist.city = request.form['city']
           artist.state = request.form['state']
           artist.phone = request.form['phone']
           artist.website = request.form['website']
           artist.image_link = request.form['image_link']
           artist.facebook_link = request.form['facebook_link']
           artist.seeking_venue = seeking_venue
           artist.seeking_description = request.form['seeking_description']
           ## on successful db insert, flash success
           db.session.commit()
           flash('Artist ' + request.form['name'] + ' was successfully updated!')
       except:
           db.session.rollback()
           print (sys.exc_info())
           flash('An error occurred. Artist ' + request.form['name'] + ' could not be updated.')
           ## TODO: on unsuccessful db insert, flash an error instead.
           ## e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
       finally:
           db.session.close()
   else:
       flash(form.errors )
       print('Error in validation')

   return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  data = Venue.query.filter(Venue.id == venue_id).one()

  #Populate the loaded form with prior data#
  form.name.data = data.name
  form.genres.data = data.genres
  form.city.data = data.city
  form.state.data = data.state
  form.website.data = data.website
  form.phone.data = data.phone
  form.facebook_link.data = data.facebook_link
  form.seeking_talent.data = data.seeking_talent
  form.seeking_description.data = data.seeking_description
  form.image_link.data = data.image_link

  venue={
    "id": data.id,
    "name": data.name,
    "genres": data.genres,
    "city": data.city,
    "state": data.state,
    "phone": data.phone,
    "website": data.website,
    "facebook_link": data.facebook_link,
    "seeking_talent": data.seeking_talent,
    "seeking_description": data.seeking_description,
    "image_link": data.image_link
  }
   #end description-----------------------------------------#

  ## TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  ## TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  form = VenueForm(request.form)
  if form.validate():
      try:
          venue = Venue.query.filter(Venue.id == venue_id).one()
          talent_input = request.form['seeking_talent']
          if talent_input == 'Yes':
              seeking_talent = True
          else:
              seeking_talent = False
          venue.name = request.form['name']
          venue.city = request.form['city']
          venue.state = request.form['state']
          venue.phone = request.form['phone']
          venue.website = request.form['website']
          venue.image_link = request.form['image_link']
          venue.facebook_link = request.form['facebook_link']
          venue.seeking_talent = seeking_talent
          venue.seeking_description = request.form['seeking_description']
          ## on successful db insert, flash success
          db.session.commit()
          flash('Venue ' + request.form['name'] + ' was successfully updated!')
      except:
          db.session.rollback()
          print (sys.exc_info())
          flash('An error occurred. Venue ' + request.form['name'] + ' could not be updated.')
          ## TODO: on unsuccessful db insert, flash an error instead.
          ## e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
      finally:
          db.session.close()
  else:
      flash(form.errors )
      print('Error in validation')

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
  ## TODO: insert form data as a new Venue record in the db, instead
  ## TODO: modify data to be the data object returned from db insertion
  form = ArtistForm(request.form)
  if form.validate():
      current_records = Artist.query.all()
      for record in current_records:
          if request.form['phone']== record.phone:
              flash('Artist ' + request.form['name'] + ' already exists.')
          else:
              try:
                  venue_input = request.form['seeking_venue']
                  if venue_input == 'Yes':
                      seeking_venue = True
                  else:
                      seeking_venue = False
                  new_artist = Artist(
                  name = request.form['name'],
                  city = request.form['city'],
                  state = request.form['state'],
                  phone = request.form['phone'],
                  website = request.form['website'],
                  image_link = request.form['image_link'],
                  facebook_link = request.form['facebook_link'],
                  seeking_venue = seeking_venue,
                  seeking_description = request.form['seeking_description']
                  )
                  ## on successful db insert, flash success
                  db.session.add(new_artist)
                  db.session.commit()
                  flash('Artist ' + request.form['name'] + ' was successfully listed!')
              except:
                  db.session.rollback()
                  print (sys.exc_info())
                  flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
                  ## TODO: on unsuccessful db insert, flash an error instead.
                  ## e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
              finally:
                  db.session.close()
  else:
      flash( form.errors )
      print('Error in validation')
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  ## TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  shows = Show.query.join(Artist, Venue).all()
  data =[]
  for show in shows:
      record ={
      "venue_id": show.venue,
      "venue_name": show.venue.name,
      "artist_id": show.artist,
      "artist_name": show.artist.name,
      "artist_image_link": show.artist.image_link,
      "start_time": str(show.s_start)
      }
      data.append(record)

  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
     form = ShowForm(request.form)
     # called to create new shows in the db, upon submitting new show listing form
     ## TODO: insert form data as a new Show record in the db, instead
     if form.validate():
         try:
             new_show = Show(
             s_artist = request.form['artist_id'],
             s_venue = request.form['venue_id'],
             s_start = request.form['start_time'],
             )
             ## on successful db insert, flash success
             db.session.add(new_show)
             db.session.commit()
             flash('Show was successfully listed!')
         except:
             db.session.rollback()
             print (sys.exc_info())
             flash('An error occurred. Show could not be listed.')
             ## TODO: on unsuccessful db insert, flash an error instead.
             ## e.g., flash('An error occurred. Show could not be listed.')
         finally:
             db.session.close()
     else:
         flash( form.errors )
         print('Error in validation')
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
    app.run(debug=True)

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
