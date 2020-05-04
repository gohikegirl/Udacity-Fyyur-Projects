from datetime import datetime
from flask_wtf import Form
from wtforms import StringField, SelectField, SelectMultipleField, DateTimeField
from wtforms.validators import DataRequired, AnyOf, URL, ValidationError, Optional, Regexp, regexp
from enums import Genre, State
import phonenumbers

#---------------------------------------------------------------
# Custom Validators
#---------------------------------------------------------------
def genre_validator(form, field):
    error = False
    message = 'Invalid entry, must be one of the following: %s ' %([choice.value for choice in Genre])
    genres = [choice.value for choice in Genre]
    for f in field.data:
        if f not in genres:
            raise ValidationError(message)

#---------------------------------------------------------------
# Forms
#---------------------------------------------------------------
class ShowForm(Form):
    artist_id = StringField(
        'artist_id'
    )
    venue_id = StringField(
        'venue_id'
    )
    start_time = DateTimeField(
        'start_time',
        validators=[DataRequired()],
        default= datetime.today()
    )

class VenueForm(Form):
    name = StringField(
        'name', validators=[DataRequired()]
    )
    city = StringField(
        'city', validators=[DataRequired()]
    )
    state = SelectField(
        'state', validators=[DataRequired(), AnyOf([choice.value for choice in State])],
        choices= State.state_choices()
    )
    address = StringField(
        'address', validators=[DataRequired()]
    )
    phone = StringField(
        'phone', validators=[Optional(), Regexp(r'^[0-9\-\+]+$')]
    )
    website = StringField(
        'website', validators=[URL(), Optional()]
    )
    image_link = StringField(
        'image_link', validators=[URL(), Optional()]
    )
    facebook_link = StringField(
        'facebook_link', validators=[URL(), Optional()]
    )
    genres = SelectMultipleField(
        ## TODO implement enum restriction
        'genres', validators=[DataRequired(), genre_validator],
        choices= Genre.g_choices()
    )
    seeking_talent = SelectField(
        'seeking_talent', validators=[DataRequired()],
        choices= [
        ('Yes', 'Yes'),
        ('No', 'No')
        ])
    seeking_description = StringField(
        'seeking_description', validators=[Optional()]
    )

class ArtistForm(Form):
    name = StringField(
        'name', validators=[DataRequired()]
    )
    city = StringField(
        'city', validators=[DataRequired()]
    )
    state = SelectField(
        'state', validators=[DataRequired(), AnyOf([choice.value for choice in State])],
        choices=State.state_choices()
    )
    ## TODO implement validation logic for state
    phone = StringField(
        'phone', validators=[Optional(),Regexp(r'^[0-9\-\+]+$')]
    )
    website = StringField(
        'facebook_link', validators=[URL(), Optional()]
    )
    image_link = StringField(
        'image_link', validators=[URL(), Optional()]
    )
    facebook_link = StringField(
        ## TODO implement enum restriction
        'facebook_link', validators=[URL(), Optional()]
    )
    genres = SelectMultipleField(
        ## TODO implement enum restriction
        'genres', validators=[DataRequired(), genre_validator],
        choices= Genre.g_choices()
    )
    seeking_venue = SelectField(
        'seeking_venue', validators=[DataRequired()],
        choices= [
        ('Yes', 'Yes'),
        ('No', 'No')
        ])
    seeking_description = StringField(
        'seeking_description', validators=[Optional()]
        )
# TODO IMPLEMENT NEW ARTIST FORM AND NEW SHOW FORM
