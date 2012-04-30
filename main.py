from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from datetime import datetime, timedelta

class MyRequestHandler( webapp.RequestHandler ):
	def output(self,s): self.response.out.write(s)

class ScoreEntry( db.Model ):
	player = db.StringProperty( multiline=False )
	song = db.StringProperty( multiline=False )
	value = db.IntegerProperty()
	when = db.DateTimeProperty(auto_now_add=True)

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
		daysago = int(self.request.get('days'))

		dateClause = ''
		results = None
		if daysago > 0:
			# enforce time limit
			dt = timedelta(1)
			now = datetime.today()
			minWhen = now-dt
			results = db.GqlQuery('SELECT player, value FROM ScoreEntry '
				'WHERE song = :1 AND when >= :2 '
				'ORDER BY when DESC LIMIT %d' % limit,\
				song, minWhen )
			# NOTE: Why don't we order by score value here? Because GQL doesn't allow it..yeah. It's OK - we don't expect more than 10 results, so we'll manually sort them later
		else:
			# all time
			results = db.GqlQuery('SELECT player, value FROM ScoreEntry '
				'WHERE song = :1 '
				'ORDER BY when DESC LIMIT %d' % limit,\
				song )

		if song != '':
			# sort them by score value
			entries = sorted( results, key=ScoreEntry.get_value, reverse=True )
			for entry in entries:
				self.output( '%s,%d|' % (entry.player, entry.value) )
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