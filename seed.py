from model import *
from server import app
import geocoder
import pytz
from datetime import datetime
from json import loads


def load_users():
	"""Load carolyn & balloonicorn into database"""

	file = open('static/data/users.txt')

	for line in file:
		fname, lname, email, password, img_url,  = line.rstrip().split(",")

		user = User(fname=fname,
				   lname=lname,
				   email=email,
				   password=password,
				   img_url = img_url
				   )
		db.session.add(user)
	db.session.commit()
	# Add Carolyn's phone number to the DB
	User.query.get(1).phone = '6179973559'



def load_trips():
	"""Load carolyn's vacation into database"""

	file = open('static/data/trips.txt')

	for line in file:
		admin_id, title, start_raw, end_raw, destination = line.rstrip().split("|")

		admin_id = int(admin_id)
		tz_name = geocoder.timezone(destination).timeZoneId
		
		start_dt = datetime.strptime(start_raw, "%Y, %m, %d")
		start_local = declare_tz(start_dt, tz_name) # give it tzinfo=tz_name
		start_utc = convert_to_tz(start_local, 'utc') # convert that time to UTC

		end_dt = datetime.strptime(end_raw, "%Y, %m, %d")
		end_local = declare_tz(end_dt, tz_name)
		end_utc = convert_to_tz(end_local, 'utc')

		destination = geocoder.google(destination)
		address = destination.address
		lat = destination.lat
		lng = destination.lng
		city = destination.city
		country_code = destination.country

		trip = Trip(admin_id=admin_id,
					title=title,
					start=start_utc,
					end=end_utc,
					latitude=lat,
					longitude=lng,
					address=address,
					city=city,
					country_code=country_code,
					tz_name=tz_name
					)
		db.session.add(trip)
		db.session.commit()

		# Create admin permission
		perm = Permission(trip_id=trip.trip_id,
				  user_id=admin_id,
				  can_edit=True
				  )
		db.session.add(perm)
		trip.create_days()




def load_permissions():
	"""Load the permissions"""

	file = open("static/data/permissions.txt")

	for line in file:
		trip_id, user_id, can_edit = line.rstrip().split(",")

		can_edit = loads(can_edit.lower())

		perm = Permission(trip_id=trip_id,
					  user_id=user_id,
					  can_edit=can_edit
					  )
		db.session.add(perm)



def load_events():
	"""Load the events"""

	file = open('static/data/events.txt')

	for line in file:
		day_id, user_id, title, start_raw, end_raw, location = line.rstrip().split("|")

		tz_id = geocoder.timezone(location).timeZoneId
		tz = pytz.timezone(tz_id)

		location = geocoder.google(location)
		address = location.address
		city = location.city
		latitude = location.lat
		longitude = location.lng

		start = datetime.strptime(start_raw, "datetime(%Y, %m, %d, %H, %M)")

		end = datetime.strptime(end_raw, "datetime(%Y, %m, %d, %H, %M)")
		
		event = Event(day_id=day_id,
					  user_id=user_id,
					  title=title,
					  start=start,
					  end=end,
					  address=address,
					  city=city,
					  latitude=latitude,
					  longitude=longitude
					  )

		db.session.add(event)


def load_friendships():
	"""Load the friendships. Everyone is friends with everyone!"""

	db.session.commit()

	for user1 in User.query.all():
		for user2 in User.query.all():
			if user1.user_id != user2.user_id:
				friendship = Friendship(admin_id=user1.user_id,
										friend_id=user2.user_id
										)
				db.session.add(friendship)

#####################################################################
# Main Block

if __name__ == "__main__":
    connect_to_db(app)

    load_users()
    load_trips()
    load_permissions()
    load_events()
    load_friendships()
    db.session.commit()
    print "Database is populated."