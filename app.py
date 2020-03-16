#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, jsonify
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
from sqlalchemy import func
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

migrate = Migrate(app, db)

# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=True)
    city = db.Column(db.String(120), nullable=True)
    state = db.Column(db.String(120), nullable=True)
    address = db.Column(db.String(120), nullable=True)
    seeking_talent = db.Column(db.Boolean, nullable=True)
    
    phone = db.Column(db.String(120), nullable=True)
    image_link = db.Column(db.String(500), nullable=True)
    facebook_link = db.Column(db.String(120), nullable=True)
    website = db.Column(db.String(500), nullable=True)
    seeking_description = db.Column(db.String, nullable=True)
    
    genres = db.relationship('Venue_Genre', backref='venue', lazy=True)
    shows = db.relationship('Show', backref='venue', lazy=True)

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=True)
    city = db.Column(db.String(120), nullable=True)
    state = db.Column(db.String(120), nullable=True)
    seeking_venue = db.Column(db.Boolean, nullable=True)
    
    phone = db.Column(db.String(120), nullable=True)
    image_link = db.Column(db.String(500), nullable=True)
    facebook_link = db.Column(db.String(120), nullable=True)
    website = db.Column(db.String(500), nullable=True)
    seeking_description = db.Column(db.String, nullable=True)
    
    genres = db.relationship('Artist_Genre', backref='artist', lazy=True)
    shows = db.relationship('Show', backref='artist', lazy=True)

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist_Genre(db.Model):
    __tablename__ = 'Artist_Genre'
    id = db.Column(db.Integer, primary_key=True)
    genre = db.Column(db.String, nullable=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=True)
    
class Venue_Genre(db.Model):
    __tablename__ = 'Venue_Genre'
    id = db.Column(db.Integer, primary_key=True)
    genre = db.Column(db.String, nullable=True)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=True)
    
class Show(db.Model):
    __tablename__ = 'Show'
    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=True)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=True)
    start_time = db.Column(db.DateTime, nullable=True)
    
#artist_genres = db.Table('artist_genres',
#    db.Column('artist_id', db.Integer, db.ForeignKey('Artist.id'), primary_key=True),
#    db.Column('genre_id', db.Integer, db.ForeignKey('Genre.id'), primary_key=True)
#)
#
#venue_genres = db.Table('venue_genres',
#    db.Column('venue_id', db.Integer, db.ForeignKey('Venue.id'), primary_key=True),
#    db.Column('genre_id', db.Integer, db.ForeignKey('Genre.id'), primary_key=True)
#)

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

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
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
    venues = Venue.query.order_by('id').all()
    jsonarray = []
    
    for venue in venues:
        jsonarray.append({ 
            'id': venue.id,
            'name': venue.name,
            'num_upcoming_shows': Show.query.filter_by(venue_id=venue.id).count()
        })
        
    data=[{
        "city": "City",
        "state": "State",
        "venues": jsonarray
    }]

    return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"

    search_term = request.form.get('search_term').lower()
    venue_name_lower = func.lower(Venue.name)
    filter = Venue.query.filter(venue_name_lower.contains('%'+search_term+'%'))
    venues = filter.order_by('id').all()
    count = filter.count()
    jsonarray = []
    
    for venue in venues:
        jsonarray.append({ 
            'id': venue.id,
            'name': venue.name,
            'num_upcoming_shows': Show.query.filter_by(venue_id=venue.id).count()
        })
    
    response={
        "count": count,
        "data": jsonarray
    }

    return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))
  

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
    
    venues = Venue.query.order_by('id').all()
    shows = Show.query.order_by('id').all()
    jsonarray = []
    date_time_now = datetime.now()
    
    for venue in venues:
        past_show_array = []
        upcoming_show_array = []
        past_show_count = 0;
        upcoming_show_count = 0;
        for show in Show.query.filter_by(venue_id=venue.id).all():
            if show.start_time < date_time_now:
                past_show_count = past_show_count + 1
                past_show_array.append({ 
                    'artist_id': show.artist_id,
                    'artist_name': Artist.query.filter_by(id=show.artist_id).first().name,
                    'artist_image_link': Artist.query.filter_by(id=show.artist_id).first().image_link,
                    'start_time': str(show.start_time)
                })
        for show in Show.query.filter_by(venue_id=venue.id).all():
            if show.start_time > date_time_now:
                upcoming_show_count = upcoming_show_count + 1
                upcoming_show_array.append({ 
                    'artist_id': show.artist_id,
                    'artist_name': Artist.query.filter_by(id=show.artist_id).first().name,
                    'artist_image_link': Artist.query.filter_by(id=show.artist_id).first().image_link,
                    'start_time': str(show.start_time)
                })
        try:
            genres_result = str(Venue_Genre.query.filter_by(venue_id=venue.id).first().genre).replace("{", "").replace("}", "").split(',')
        except:
            genres_result = ""
        jsonarray.append({ 
            'id': venue.id,
            'name': venue.name,
            'genres': genres_result,
            'address': venue.address,
            'city': venue.city,
            'state': venue.state,
            'phone': venue.phone,
            'website': venue.website,
            'facebook_link': venue.facebook_link,
            'seeking_talent': venue.seeking_talent,
            'seeking_description': venue.seeking_description,
            'image_link': venue.seeking_description,
            'past_shows': past_show_array,
            'upcoming_shows': upcoming_show_array,
            'past_shows_count': past_show_count,
            'upcoming_shows_count': upcoming_show_count
        
        })

#    flash(Venue.query.filter_by(id=17).first().name)
    data = list(filter(lambda d: d['id'] == venue_id, jsonarray))[0]
    return render_template('pages/show_venue.html', venue=data)
  

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    error = False
    try:
        name = request.form['name']
        city = request.form['city']
        state = request.form['state']
        address = request.form['address']
        phone = request.form['phone']
        genres = request.form.to_dict(flat=False)['genres']
        facebook_link = request.form['facebook_link']
#        image_link = request.form['image_link']
#        website = request.form['website']
#        seeking_talent = request.form['seeking_talent']
#        seeking_description = request.form['seeking_description']
#        venue = Venue(image_link=image_link)
#        venue = Venue(website=website)
#        venue = Venue(seeking_description=seeking_description)
        venue = Venue(name=name, city=city, state=state, address=address, phone=phone, facebook_link=facebook_link)
        db.session.add(venue)
        db.session.flush()
        genre = Venue_Genre(genre=genres, venue_id=venue.id)
        db.session.add(genre)
        db.session.commit()
    except:
        db.session.rollback()
    finally:
        db.session.close()
    if error:
        flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
    else:
        flash('Venue ' + request.form['name'] + ' was successfully listed!')
    return render_template('pages/home.html')

  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion

  # on successful db insert, flash success
    
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    error = False
    try:
        venue = Venue.query.get(venue_id)
        name = venue.name
        db.session.delete(venue)
        db.session.commit()
    except:
        db.session.rollback()
        error = True
    finally:
        db.session.close()
    if error:
        flash('An error occurred. Venue ' + name + ' could not be deleted.')
    else:
        flash('Venue ' + name + ' was successfully deleted!')
    return render_template('pages/home.html')
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database

    artists = Artist.query.order_by('id').all()
    jsonarray = []
    
    for artist in artists:
        jsonarray.append({ 
            'id': artist.id,
            'name': artist.name})

    data=jsonarray

    return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".

    search_term = request.form.get('search_term').lower()
    artist_name_lower = func.lower(Artist.name)
    filter = Artist.query.filter(artist_name_lower.contains('%'+search_term+'%'))
    artists = filter.order_by('id').all()
    count = filter.count()
    jsonarray = []
    
    for artist in artists:
        jsonarray.append({ 
            'id': artist.id,
            'name': artist.name,
            'num_upcoming_shows': Show.query.filter_by(artist_id=artist.id).count()})
    
    response={
        "count": count,
        "data": jsonarray
    }

    return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
    
    artists = Artist.query.order_by('id').all()
    shows  = Show.query.order_by('id').all()
    jsonarray = []
#    x = datetime.fromisoformat('2020-05-15 17:12:43')
    date_time_now = datetime.now()
    
    for artist in artists:
        past_show_array = []
        upcoming_show_array = []
        past_show_count = 0;
        upcoming_show_count = 0;
        for show in Show.query.filter_by(artist_id=artist.id).all():
            if show.start_time < date_time_now:
                past_show_count = past_show_count + 1
                past_show_array.append({ 
                    'venue_id': show.venue_id,
                    'venue_name': Venue.query.filter_by(id=show.venue_id).first().name,
                    'venue_image_link': Venue.query.filter_by(id=show.venue_id).first().image_link,
                    'start_time': str(show.start_time)
                })
        for show in Show.query.filter_by(artist_id=artist.id).all():
            if show.start_time > date_time_now:
                upcoming_show_count = upcoming_show_count + 1
                upcoming_show_array.append({ 
                    'venue_id': show.venue_id,
                    'venue_name': Venue.query.filter_by(id=show.venue_id).first().name,
                    'venue_image_link': Venue.query.filter_by(id=show.venue_id).first().image_link,
                    'start_time': str(show.start_time)
                })
        try:
            genres_result = str(Artist_Genre.query.filter_by(artist_id=artist.id).first().genre).replace("{", "").replace("}", "").split(',')
        except:
            genres_result = ""
        jsonarray.append({ 
            'id': artist.id,
            'name': artist.name,
            'genres': genres_result,
            'city': artist.city,
            'state': artist.state,
            'phone': artist.phone,
            'website': artist.website,
            'facebook_link': artist.facebook_link,
            'seeking_venue': artist.seeking_venue,
            'seeking_description': artist.seeking_description,
            'image_link': artist.seeking_description,
            'past_shows': past_show_array,
            'upcoming_shows': upcoming_show_array,
            'past_shows_count': past_show_count,
            'upcoming_shows_count': upcoming_show_count
        
        })

    data = list(filter(lambda d: d['id'] == artist_id, jsonarray))[0]
    return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()
    
    artist = Artist.query.filter_by(id=artist_id).first()

    artist={
        "id": artist.id,
        "name": artist.name,
        "genres": artist.genres,
        "city": artist.city,
        "state": artist.state,
        "phone": artist.phone,
        "website": artist.website,
        "facebook_link": artist.facebook_link,
        "seeking_venue": artist.seeking_venue,
        "seeking_description": artist.seeking_description,
        "image_link": artist.image_link
    }
  # TODO: populate form with fields from artist with ID <artist_id>
    return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    error = False
    try:
        artist = Artist.query.get(artist_id)
        artist.name = request.form['name']
        artist.city = request.form['city']
        artist.state = request.form['state']
        artist.phone = request.form['phone']
        genres = request.form.to_dict(flat=False)['genres']
        artist.facebook_link = request.form['facebook_link']
#        website = request.form['website']
#        seeking_venue = request.form['seeking_venue']
#        seeking_description = request.form['seeking_description']
#        image_link = request.form['image_link']

        Artist_Genre.query.filter_by(artist_id=artist_id).first().genres = genres
        db.session.commit()
    except:
        db.session.rollback()
        error = True
    finally:
        db.session.close()
    if error:
        flash('An error occurred. Artist ' + request.form['name'] + ' could not be edited.')
    else:
        flash('Artist ' + request.form['name'] + ' was successfully edited!')
    return redirect(url_for('show_artist', artist_id=artist_id))
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()

    venue = Venue.query.filter_by(id=venue_id).first()

    venue={
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
        "image_link": venue.image_link
    }

  # TODO: populate form with values from venue with ID <venue_id>
    return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    error = False
    try:
        venue = Venue.query.get(venue_id)
        venue.name = request.form['name']
        venue.city = request.form['city']
        venue.state = request.form['state']
        venue.address = request.form['address']
        venue.phone = request.form['phone']
        genres = request.form.to_dict(flat=False)['genres']
        venue.facebook_link = request.form['facebook_link']     
#        image_link = request.form['image_link']
#        website = request.form['website']
#        venue.seeking_talent = request.form['seeking_talent']
#        seeking_description = request.form['seeking_description']
#        venue = Venue(image_link=image_link)
#        venue = Venue(website=website)
#        venue = Venue(seeking_description=seeking_description)
        Venue_Genre.query.filter_by(venue_id=venue_id).first().genres = genres
        db.session.commit()
    except:
        db.session.rollback()
    finally:
        db.session.close()
    if error:
        flash('An error occurred. Venue ' + request.form['name'] + ' could not be edited.')
    else:
        flash('Venue ' + request.form['name'] + ' was successfully edited!')
    return redirect(url_for('show_venue', venue_id=venue_id))
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
    

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
        name = request.form['name']
        city = request.form['city']
        state = request.form['state']
        phone = request.form['phone']
        genres = request.form.to_dict(flat=False)['genres']
        facebook_link = request.form['facebook_link']
#        website = request.form['website']
#        seeking_venue = request.form['seeking_venue']
#        seeking_description = request.form['seeking_description']
#        image_link = request.form['image_link']
        artist = Artist(name=name, city=city, state=state, phone=phone, facebook_link=facebook_link)
        db.session.add(artist)
        db.session.flush()
#        for g in genres:
        genre = Artist_Genre(genre=genres, artist_id=artist.id)
        db.session.add(genre)
        db.session.commit()
    except:
        db.session.rollback()
        error = True
    finally:
        db.session.close()
    if error:
        flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
    else:
        flash('Artist ' + request.form['name'] + ' was successfully listed!')
    return render_template('pages/home.html')
    
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion

  # on successful db insert, flash success
    
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.

    shows = Show.query.order_by('id').all()
    jsonarray = []
    
    for show in shows:
        jsonarray.append({ 
            "venue_id": show.venue_id,
            "venue_name": Venue.query.filter_by(id=show.venue_id).first().name,
            "artist_id": show.artist_id,
            "artist_name": Artist.query.filter_by(id=show.artist_id).first().name,
            "artist_image_link": Artist.query.filter_by(id=show.artist_id).first().image_link,
            "start_time": str(show.start_time)
        })

    data=jsonarray
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
        artist_id = request.form['artist_id']
        venue_id = request.form['venue_id']
        start_time = str(request.form['start_time'])
        show = Show(artist_id=artist_id, venue_id=venue_id, start_time=start_time)
        db.session.add(show)
        db.session.commit()
    except:
        db.session.rollback()
        error = True
    finally:
        db.session.close()
    if error:
        flash('An error occurred. Show could not be listed.')
    else:
        flash('Show was successfully listed!')
    return render_template('pages/home.html')

  # on successful db insert, flash success

  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/


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
#if __name__ == '__main__':
#    app.run(host='127.0.0.1', port=81)
    
