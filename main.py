from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

class ScoreEntry( db.Model ):
	player = db.StringProperty( multiline=False )
	song = db.StringProperty( multiline=False )
	value = db.IntegerProperty()
	when = db.DateTimeProperty(auto_now_add=True)

class SaveScore( webapp.RequestHandler ):
	def output(self,s): self.response.out.write(s)

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
	
class GetScores( webapp.RequestHandler ):
	def output(self,s): self.response.out.write(s)
	def get(self):
		self.response.headers['Content-Type'] = 'text/plain'
		song = self.request.get('song')
		if song != '':
			prevPlayer = ''
			for entry in db.GqlQuery('SELECT player, value FROM ScoreEntry '
				'WHERE song = :1 ORDER BY value DESC', song ):
				# only show each player's highest score
				if prevPlayer != entry.player:
					self.output( '%s,%d|' % (entry.player, entry.value) )
				prevPlayer = entry.player
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