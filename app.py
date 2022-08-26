#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, abort
from flask_moment import Moment
#from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from flask_migrate import Migrate
from config import MyLocal
from forms import *
from datetime import datetime, timezone
from sqlalchemy import or_, desc
import sys
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object(MyLocal)

# TODO: connect to a local postgresql database
from models import db, Artist, Venue, Show
migrate = Migrate(app, db)

#----------------------------------------------------------------------------#


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
    #date = dateutil.parser.parse(value)
    if isinstance(value, str):
        date = dateutil.parser.parse(value)
    else:
        date = value
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
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
  
 
  get_locations= Venue.query.distinct(Venue.state, Venue.city).all() #Gets a list of all unique states and cities
 
  locations = {}
  for location in get_locations:
    locations = {
      "city": location.city,
      "state": location.state,
      "venues": [] # we will store all the venues with the specific location details in this list
    }
    
    venues = Venue.query.filter_by(state=location.state, city=location.city).all()
    for venue in venues:
      locations['venues'].append({
        "id": venue.id,
        "name": venue.name,
        "num_upcoming_shows" : Show.query.join(Venue).filter(Show.venue_id==venue.id).filter(Show.start_time>datetime.now()).count()
      })
  data = []
  data.append(locations)
  return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
    search_query=request.form.get('search_term', '')
    search_format = "%{}%".format(search_query)
    response = {
      "count": Venue.query.filter(Venue.name.ilike(search_format)).count(),
      "data": []
    }
 
    search_results = Venue.query.filter(Venue.name.ilike(search_format)).all()
 
    for result in search_results:
      response["data"].append({
        "id": result.id,
        "name": result.name,
        "num_upcoming_shows": Show.query.join(Venue).filter(Show.venue_id==result.id).filter(Show.start_time>datetime.now()).count()
      })
    return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    # TODO: replace with real venue data from the venues table, using venue_id
  past_shows_query = Show.query.join(Venue).filter(Show.venue_id==venue_id).filter(datetime.utcnow()>Show.start_time).all()
  past_shows = []
  for show in past_shows_query:
    past_shows.append({
      "artist_id": show.artist_id,
      "artist_name": Artist.query.get(show.artist_id).name,
      "artist_image_link": Artist.query.get(show.artist_id).image_link,
      "start_time": show.start_time
 
    })
 
  upcoming_shows_query = Show.query.join(Venue).filter(Show.venue_id==venue_id).filter(datetime.utcnow()<Show.start_time).all()
  upcoming_shows = []
  for show in upcoming_shows_query:
    upcoming_shows.append({
      "artist_id": show.artist_id,
      "artist_name": Artist.query.get(show.artist_id).name,
      "artist_image_link": Artist.query.get(show.artist_id).image_link,
      "start_time": show.start_time
 
    })
 
  past_shows_count = len(past_shows)
  upcoming_shows_count = len(upcoming_shows)
 
  venue_information = Venue.query.get(venue_id)
 
  data = {
    "id": venue_information.id,
    "name": venue_information.name,
    "genres": venue_information.genres.split(", "),
    "address": venue_information.address,
    "city": venue_information.city,
    "state": venue_information.state,
    "phone": venue_information.phone,
    "website": venue_information.website,
    "facebook_link": venue_information.facebook_link,
    "seeking_talent": venue_information.seeking_talent,
    "seeking_description": venue_information.seeking_description,
    "image_link": venue_information.image_link,
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
    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion
    error = False
    try:
        new_venue = Venue()
        new_venue.name = request.form.get('name')
        new_venue.genres = ', '.join(request.form.getlist('genres'))
        new_venue.address = request.form.get('address')
        new_venue.city = request.form.get('city')
        new_venue.state = request.form.get('state')
        new_venue.phone = request.form.get('phone')
        new_venue.facebook_link = request.form.get('facebook_link')
        new_venue.image_link = request.form.get('image_link')
        new_venue.website = request.form.get('website_link')
        new_venue.seeking_talent = True if request.form.get(
            'seeking_talent') != None else False
        new_venue.seeking_description = request.form.get('seeking_description')

        db.session.add(new_venue)
        db.session.commit()
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
    # on successful db insert, flash success
    if not error:
        flash('Venue ' + request.form.get('name') + ' was successfully listed!')
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
    else:
        flash('An error occurred. Venue ' +
              request.form.get('name') + ' could not be listed.')
        abort(500)
    return render_template('pages/home.html')

    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    return render_template('pages/home.html')

# DELETE VENUES

@app.route('/venues/<venue_id>/delete', methods=['GET'])
def delete_venue(venue_id):
    # TODO: Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
    error = False
    try:
        Show.query.filter_by(venue_id=venue_id).delete()
        Venue.query.filter_by(id=venue_id).delete()
        db.session.commit()
    except:
        error = True
        db.session.rollback()
    finally:
        db.session.close()
    if not error:
        flash('Venue delete was successfully!')
        return render_template('pages/home.html'), 200
    else:
        flash('Delete was unsuccessfully!')
        abort(500)
        
        # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
        # clicking that button delete it from the db then redirect the user to the homepage
        # return None

#  Artists
#  ----------------------------------------------------------------


@app.route('/artists')
def artists():
    # TODO: replace with real data returned from querying the database
    artists_list = []
    get_artists = db.session.query(Artist).order_by('id').all()
    for artist in get_artists:   
        artists_list.append({
          "id":artist.id,
          "name":artist.name,
          })
    return render_template('pages/artists.html', artists=artists_list)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".
    search_query=request.form.get('search_term', '')
    search_format = "%{}%".format(search_query)
    response = {
      "count": Artist.query.filter(Artist.name.ilike(search_format)).count(),
      "data": []
    }
 
    search_results = Artist.query.filter(Artist.name.ilike(search_format)).all()
 
    for result in search_results:
      response["data"].append({
        "id": result.id,
        "name": result.name,
        "num_upcoming_shows": Show.query.join(Venue).filter(Show.venue_id==result.id).filter(Show.start_time>datetime.now()).count()
      })
    return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the artist page with the given artist_id
    # TODO: replace with real artist data from the artist table, using artist_id
  
  get_artist = Artist.query.get(artist_id)
  past_shows=[] #prepare list of past shows
  past_shows_query = Show.query.join(Artist).filter(Show.artist_id==artist_id).filter(datetime.utcnow()>Show.start_time).all()
  
# setting data object for artist
  for show_list in past_shows_query:
      past_shows.append({
      "venue_id": show_list.artist_id,
      "venue_name": Venue.query.get(show_list.artist_id).name,
      "venue_image_link": Venue.query.get(show_list.artist_id).image_link,
      "start_time": show_list.start_time
 
  })
  get_upcoming_shows = Show.query.join(Artist, Show.artist_id == get_artist.id).filter(Show.start_time > datetime.isoformat(datetime.now())).all()
  upcoming_shows=[] #prepare list of upcoming shows
  for show_list in get_upcoming_shows:
      upcoming_shows.append({
      "venue_id": show_list.artist_id,
      "venue_name": Venue.query.get(show_list.artist_id).name,
      "venue_image_link": Venue.query.get(show_list.artist_id).image_link,
      "start_time": show_list.start_time
 
  })
  data = {
    "id": get_artist.id,
    "name": get_artist.name,
    "genres": get_artist.genres.split(", "),
    "city": get_artist.city,
    "state": get_artist.state,
    "phone": get_artist.phone,
    "website": get_artist.website,
    "facebook_link": get_artist.facebook_link,
    "seeking_venue": get_artist.seeking_venue,
    "seeking_description": get_artist.seeking_description,
    "image_link": get_artist.image_link,
    "past_shows":  past_shows,
    "upcoming_shows":   upcoming_shows,
    "past_shows_count":len(past_shows_query),
    "upcoming_shows_count":len(get_upcoming_shows) 
  }

  

  
  
  # set past_show data
  
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------


@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()
    get_artist = Artist.query.get(artist_id)
    form.name.data = get_artist.name
    form.genres.data = get_artist.genres
    form.city.data = get_artist.city
    form.state.data = get_artist.state
    form.phone.data = get_artist.phone
    form.website_link.data = get_artist.website
    form.facebook_link.data = get_artist.facebook_link
    form.seeking_venue.data = get_artist.seeking_venue
    form.seeking_description.data = get_artist.seeking_description
    form.image_link.data = get_artist.image_link
    
    # TODO: populate form with fields from artist with ID <artist_id>
    return render_template('forms/edit_artist.html', form=form, artist=get_artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    # TODO: take values from the form submitted, and update existing
    # artist record with ID <artist_id> using the new attributes
  try:
    query_data = Artist.query.get(artist_id)

    # using request.form.get is safer than accessing the value directly to handel null cases
    query_data.name = request.form.get('name')
    query_data.genres = ', '.join(request.form.getlist('genres'))
    query_data.city = request.form.get('city')
    query_data.state = request.form.get('state')
    query_data.phone = request.form.get('phone')
    query_data.facebook_link = request.form.get('facebook_link')
    query_data.image_link = request.form.get('image_link')
    query_data.website = request.form.get('website_link')
    query_data.seeking_venue = True if request.form.get('seeking_venue')!=None else False
    query_data.seeking_description = request.form.get('seeking_description')
    db.session.add(query_data)
    db.session.commit()
  except:
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  return redirect(url_for('show_artist', artist_id=artist_id))

#DELETE ARTIST

@app.route('/artists/<artist_id>/delete', methods=['GET'])
def delete_artist(artist_id):
    error = False
    try:
        Show.query.filter_by(artist_id=artist_id).delete()
        Artist.query.filter_by(id=artist_id).delete()
        db.session.commit()
    except:
        error = True
        db.session.rollback()
    finally:
        db.session.close()
    if not error:
        flash('Artist delete was successfully!')
        return render_template('pages/home.html'), 200
    else:
        flash('Delete was unsuccessfully!')
        abort(500)
        
        # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
        # clicking that button delete it from the db then redirect the user to the homepage
        # return None

#  Artists
#  ----------------------------------------------------------------


# EDIT

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  get_venue = Venue.query.get(venue_id)
 
  form.name.data = get_venue.name
  form.genres.data = get_venue.genres
  form.address.data = get_venue.address
  form.city.data = get_venue.city
  form.state.data = get_venue.state
  form.phone.data = get_venue.phone
  form.website_link.data = get_venue.website
  form.facebook_link.data = get_venue.facebook_link
  form.seeking_talent.data = get_venue.seeking_talent
  form.seeking_description.data = get_venue.seeking_description
  form.image_link.data = get_venue.image_link  
    # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=get_venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # TODO: take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes
    try:
      query_data = Venue.query.get(venue_id)
      query_data.name = request.form.get('name')
      query_data.genres = ', '.join(request.form.getlist('genres'))
      query_data.address = request.form.get('address')
      query_data.city = request.form.get('city')
      query_data.state = request.form.get('state')
      query_data.phone = request.form.get('phone')
      query_data.facebook_link = request.form.get('facebook_link')
      query_data.image_link = request.form.get('image_link')
      query_data.website = request.form.get('website_link')
      query_data.seeking_talent = True if request.form.get('seeking_talent')!= None else False
      query_data.seeking_description = request.form.get('seeking_description')
      db.session.add(query_data)
      db.session.commit()
    except:
      db.session.rollback()
      print(sys.exc_info())
    finally:
      db.session.close()
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
  error = False
  try:
    artists = Artist()
    artists.name = request.form.get('name')
    artists.genres = ', '.join(request.form.getlist('genres'))
    artists.city = request.form.get('city')
    artists.state = request.form.get('state')
    artists.phone = request.form.get('phone')
    artists.facebook_link = request.form.get('facebook_link')
    artists.image_link = request.form.get('image_link')
    artists.website = request.form.get('website_link')
    artists.seeking_venue = True if request.form.get('seeking_venue')!= None else False
    artists.seeking_description = request.form.get('seeking_description')
    db.session.add(artists)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  # on successful db insert, flash success
  if not error:
    flash('Artist ' + request.form.get('name') + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  else:
    flash('An error occurred. Artist ' + request.form.get('name') + ' could not be listed.')
    abort(500)
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    # displays list of shows at /shows
    # TODO: replace with real venues data.
    shows_data = []
    get_shows = db.session.query(Show).order_by(desc(Show.start_time)).all()
    for show in get_shows:
        artist = db.session.query(Artist.name, Artist.image_link).filter(Artist.id == show.artist_id).one()
        venue = db.session.query(Venue.name).filter(Venue.id == show.venue_id).one()
        shows_data.append({
          "venue_id": show.venue_id,
          "venue_name": venue.name,
          "artist_id": show.artist_id,
          "artist_name":artist.name,
          "artist_image_link": artist.image_link,
          "start_time": show.start_time.strftime('%m/%d/%Y')
        })
    return render_template('pages/shows.html', shows=shows_data)


@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    # called to create new shows in the db, upon submitting new show listing form
    # TODO: insert form data as a new Show record in the db, instead
  error=False
  try:
    show = Show()
    show.venue_id = request.form.get('venue_id')
    show.artist_id = request.form.get('artist_id')
    show.start_time = request.form.get('start_time')
    db.session.add(show)
    db.session.commit()
  except:
    error=True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  # on successful db insert, flash success
  if not error:
    flash('Show was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Show could not be listed.')
  else:
    flash('An error occurred. Show could not be listed.')
    abort(500)
    
    
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
        Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
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