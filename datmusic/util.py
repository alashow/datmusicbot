from constants import DATMUSIC_BASE_URL
from prettyIntegers import encode

def generateAudioUrl(oid, aid):
	return "{server}{oid}:{aid}".format(server=DATMUSIC_BASE_URL, oid=encode(oid), aid=encode(aid))