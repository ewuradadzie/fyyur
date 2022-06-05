#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

from enum import unique
import json
from tracemalloc import start
import re
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from models import *

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db.init_app(app)
migrate = Migrate(app, db)


#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#


def format_datetime(value, format='medium'):
    if type(value) == str:
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
    print("back to index")
    recent_venues = Venue.query.order_by(db.desc(Venue.created_at)).limit(10).all()
    recent_artists = Artist.query.order_by(db.desc(Artist.created_at)).limit(10).all()
    return render_template('pages/home.html', venues=recent_venues, artists=recent_artists)

#  Venues
#  ----------------------------------------------------------------


@app.route('/venues')
def venues():
    areas = Venue.query.with_entities(
        func.count(Venue.id),
        Venue.city,
        Venue.state
    ).group_by(
        Venue.city,
        Venue.state
    ).all()
    data = []
    for area in areas:
        venues = Venue.query.filter_by(city=area[1], state=area[2])
        area_venues = {
            "city": area[1],
            "state": area[2],
            "venues": venues
        }
        data.append(area_venues)
    return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    search_term = request.form.get('search_term')
    data = []
    matches = Venue.query.filter(Venue.name.ilike(f'%{search_term}%')).all()
    for venue in matches:
        upcoming_shows = Show.query.join(Venue).filter_by(id=venue.id).all()
        result = {
            "id": venue.id,
            "name": venue.name,
            "num_upcoming_shows": len(upcoming_shows)
        }
        data.append(result)

    response = {
        "count": len(matches),
        "data": data
    }
    return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):

    venue = Venue.query.filter_by(id=venue_id).one()
    shows = Show.query.filter_by(venue_id=venue_id).join(Artist).all()
    current_time = datetime.now()
    past_shows = []
    upcoming_shows = []

    for show in shows:
        obj = {
            "artist_id": show.artist.id,
            "artist_name": show.artist.name,
            "artist_image_link": show.artist.image_link,
            "start_time": show.start_time
        }
        if show.start_time > current_time:
            upcoming_shows.append(obj)
        else:
            past_shows.append(obj)

    data = {
        "id": venue.id,
        "name": venue.name,
        "genres": venue.genres,
        "address": venue.address,
        "city": venue.city,
        "state": venue.state,
        "phone": venue.phone,
        "website": venue.website_link,
        "facebook_link": venue.facebook_link,
        "seeking_talent": venue.seeking_talent,
        "seeking_description": venue.seeking_description,
        "image_link": venue.image_link,
        "past_shows": past_shows,
        "upcoming_shows": upcoming_shows,
        "past_shows_count": len(past_shows),
        "upcoming_shows_count": len(upcoming_shows)
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

    venue = Venue(
        name=request.form.get('name'),
        city=request.form.get('city'),
        state=request.form.get('state'),
        address=request.form.get('address'),
        phone=request.form.get('phone'),
        genres=request.form.getlist('genres'),
        facebook_link=request.form.get('facebook_link'),
        image_link=request.form.get('image_link'),
        website_link=request.form.get('website_link'),
        seeking_talent=request.form.get('seeking_talent') == 'y',
        seeking_description=request.form.get('seeking_description')
    )

    db.session.add(venue)
    try:
        db.session.commit()
        flash('Venue ' + venue.name + ' was successfully listed!')
    except:
        flash('An error occurred. Venue ' + venue.name +
              ' could not be listed.', 'error')
        db.session.rollback()
    finally:
        db.session.close()
    return render_template('pages/home.html')


#  Update Venue
#  ----------------------------------------------------------------

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()
    selected_venue = Venue.query.get(venue_id)
    venue = {
        "id": selected_venue.id,
        "name": selected_venue.name,
        "genres": selected_venue.genres,
        "address": selected_venue.address,
        "city": selected_venue.city,
        "state": selected_venue.state,
        "phone": selected_venue.phone,
        "website": selected_venue.website_link,
        "facebook_link": selected_venue.facebook_link,
        "seeking_talent": selected_venue.seeking_talent == 'y',
        "seeking_description": selected_venue.seeking_description,
        "image_link": selected_venue.image_link
    }
    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    venue = Venue.query.get(venue_id)

    venue.name = request.form.get('name')
    venue.city = request.form.get('city')
    venue.state = request.form.get('state')
    venue.address = request.form.get('address')
    venue.phone = request.form.get('phone')
    venue.genres = request.form.getlist('genres')
    venue.facebook_link = request.form.get('facebook_link')
    venue.image_link = request.form.get('image_link')
    venue.website_link = request.form.get('website_link')
    venue.seeking_talent = request.form.get('seeking_talent') == 'y'
    venue.seeking_description = request.form.get('seeking_description')
    try:
        db.session.commit()
        flash('Venue ' + venue.name + ' was successfully updated!')
    except:
        flash('An error occurred. Venue ' +
              venue.name + ' could not be updated.', 'error')
        db.session.rollback()
    finally:
        db.session.close()
    return redirect(url_for('show_venue', venue_id=venue_id))


#  Delete Venue
#  ----------------------------------------------------------------

@app.route('/venues/<int:venue_id>/delete', methods=['GET'])
def delete_venue(venue_id):
    venue = Venue.query.get(venue_id)
    print("venue", venue)
    db.session.delete(venue)
    try:
        db.session.commit()
        flash('Venue ' + venue.name + ' was successfully deleted!')
    except:
        flash('An error occurred. Venue ' + venue.name +
              ' could not be deleted.', 'error')
        db.session.rollback()
    finally:
        db.session.close()

    return redirect(url_for('index'))


#  Artists
#  ----------------------------------------------------------------


@app.route('/artists')
def artists():
    data = Artist.query.all()
    return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    search_term = request.form.get('search_term')
    data = []
    matches = Artist.query.filter(Artist.name.ilike(f'%{search_term}%')).all()
    for artist in matches:
        upcoming_shows = Show.query.join(Artist).filter_by(id=artist.id).all()
        result = {
            "id": artist.id,
            "name": artist.name,
            "num_upcoming_shows": len(upcoming_shows)
        }
        data.append(result)

    response = {
        "count": len(matches),
        "data": data
    }
    return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    artist = Artist.query.filter_by(id=artist_id).one()
    shows = Show.query.filter_by(artist_id=artist_id).join(Venue).all()
    current_time = datetime.now()
    past_shows = []
    upcoming_shows = []

    for show in shows:
        info = {
            "venue_id": show.venue.id,
            "venue_name": show.venue.name,
            "venue_image_link": show.venue.image_link,
            "start_time": show.start_time
        }
        if show.start_time > current_time:
            upcoming_shows.append(info)
        else:
            past_shows.append(info)

    data = {
        "id": artist.id,
        "name": artist.name,
        "genres": artist.genres,
        "city": artist.city,
        "state": artist.state,
        "phone": artist.phone,
        "website": artist.website_link,
        "facebook_link": artist.facebook_link,
        "seeking_venue": artist.seeking_venue,
        "seeking_description": artist.seeking_description,
        "image_link": artist.image_link,
        "past_shows": past_shows,
        "upcoming_shows": upcoming_shows,
        "past_shows_count": len(past_shows),
        "upcoming_shows_count": len(upcoming_shows)
    }

    return render_template('pages/show_artist.html', artist=data)

#  Create Artist
#  ----------------------------------------------------------------


@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():

    artist = Artist(
        name=request.form.get('name'),
        city=request.form.get('city'),
        state=request.form.get('state'),
        phone=request.form.get('phone'),
        genres=request.form.getlist('genres'),
        facebook_link=request.form.get('facebook_link'),
        image_link=request.form.get('image_link'),
        website_link=request.form.get('website_link'),
        seeking_venue=request.form.get('seeking_venue') == 'y',
        seeking_description=request.form.get('seeking_description')
    )
    db.session.add(artist)

    try:
        db.session.commit()
        flash('Artist ' + artist.name + ' was successfully listed!')
    except:
        flash('An error occurred. Artist ' +
              artist.name + ' could not be listed.', 'error')
        db.session.rollback()
    finally:
        db.session.close()
    return redirect(url_for('index'))

#  Update Artist
#  ----------------------------------------------------------------


@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()
    selected_artist = Artist.query.get(artist_id)

    artist = {
        "id": selected_artist.id,
        "name": selected_artist.name,
        "genres": selected_artist.genres,
        "city": selected_artist.city,
        "state": selected_artist.state,
        "phone": selected_artist.phone,
        "website": selected_artist.website_link,
        "facebook_link": selected_artist.facebook_link,
        "seeking_venue": selected_artist.seeking_venue,
        "seeking_description": selected_artist.seeking_description,
        "image_link": selected_artist.image_link
    }
    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    artist = Artist.query.get(artist_id)

    artist.name = request.form.get('name')
    artist.city = request.form.get('city')
    artist.state = request.form.get('state')
    artist.phone = request.form.get('phone')
    artist.genres = request.form.getlist('genres')
    artist.facebook_link = request.form.get('facebook_link')
    artist.image_link = request.form.get('image_link')
    artist.website_link = request.form.get('website_link')
    artist.seeking_venue = request.form.get('seeking_venue') == 'y'
    artist.seeking_description = request.form.get('seeking_description')
    try:
        db.session.commit()
        flash('Artist ' + artist.name + ' was successfully updated!')
    except:
        flash('An error occurred. Artist ' +
              artist.name + ' could not be updated.', 'error')
        db.session.rollback()
    finally:
        db.session.close()
    return redirect(url_for('show_artist', artist_id=artist_id))

#  Delete Artist
#  ----------------------------------------------------------------

@app.route('/artists/<int:artist_id>/delete', methods=['GET'])
def delete_artist(artist_id):
    artist = Artist.query.get(artist_id)
    db.session.delete(artist)
    try:
        db.session.commit()
        flash('Artist ' + artist.name + ' was successfully deleted!')
    except:
        flash('An error occurred. Artist ' + artist.name +
              ' could not be deleted.', 'error')
        db.session.rollback()
    finally:
        db.session.close()

    return redirect(url_for('index'))


#  Shows
#  ----------------------------------------------------------------


@app.route('/shows')
def shows():
    shows = Show.query.join(Artist).join(Venue).all()
    data = []
    for show in shows:
        info = {
            "venue_id": show.venue.id,
            "venue_name": show.venue.name,
            "artist_id": show.artist.id,
            "artist_name": show.artist.name,
            "artist_image_link": show.artist.image_link,
            "start_time": show.start_time
        }
        data.append(info)
    return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():

    show = Show(
        artist_id=request.form.get('artist_id'),
        venue_id=request.form.get('venue_id'),
        start_time=request.form.get('start_time')
    )
    db.session.add(show)
    try:
        db.session.commit()
    # on successful db insert, flash success
        flash('Show was successfully listed!')
    except:
        flash('An error occurred. Show could not be listed.', 'error')
        db.session.rollback()
    finally:
        db.session.close()
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
