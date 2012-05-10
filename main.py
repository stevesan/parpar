from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from datetime import datetime, timedelta

import md5

import config

class MyRequestHandler( webapp.RequestHandler ):
	def output(self,s): self.response.out.write(s)

class ScoreEntry( db.Model ):
	player = db.StringProperty( multiline=False )
	song = db.StringProperty( multiline=False )
	value = db.IntegerProperty()
	timestamp = db.DateTimeProperty( auto_now_add=True )
	# Store this separately for efficient equality daily queries
	date = db.DateProperty( auto_now_add=True )

	def get_value(self): return self.value

class SaveScore( MyRequestHandler ):
	def get(self):
		self.response.headers['Content-Type'] = 'text/html'
		req = self.request
		if req.get('song') != '' \
			and req.get('player') != '' \
			and req.get('value') != '':
			songName = self.request.get('song')
			playerName = self.request.get('player')
			value = int(self.request.get('value'))
			given_hexdigest = self.request.get('hexdigest')

			# check the digest
			expected_hexdigest = md5.new('%s%s%d%s' % (songName, playerName, value, config.SecretMD5Salt)).hexdigest()
			if expected_hexdigest != given_hexdigest:
				self.output('bad MD5 hexdigest given. Score not saved. Given = '+given_hexdigest)
			else:
				entry = ScoreEntry()
				entry.song = songName
				entry.player = playerName
				entry.value = value
				entry.put()
				self.output('score = %d saved!' % value)
	
class GetScores( MyRequestHandler ):
	def get(self):
		self.response.headers['Content-Type'] = 'text/plain'
		song = self.request.get('song')
		limit = int(self.request.get('limit'))
		justtoday = int(self.request.get('justtoday'))

		results = None

		if justtoday == 1:
			# enforce time limit
			results = db.GqlQuery('SELECT player, value FROM ScoreEntry '
				'WHERE song = :1 AND date = :2 '
				'ORDER BY value DESC LIMIT %d' % limit,\
				song, datetime.today().date() )
		else:
			# all time
			results = db.GqlQuery('SELECT player, value FROM ScoreEntry '
				'WHERE song = :1 '
				'ORDER BY value DESC LIMIT %d' % limit,\
				song )

		if song != '':
			for result in results:
				self.output( '%s,%d|' % (result.player, result.value ) )
		else:
			self.output('no song name given')

application = webapp.WSGIApplication( \
	[('/SaveScore', SaveScore), \
	('/GetScores', GetScores), \
	], debug=True )

def main():
	run_wsgi_app( application )

if __name__=='__main__':
	main()