import tmdb
import json
import gspread
import urllib
import config
from urllib.request import urlopen
from urllib.parse import quote
from bs4 import BeautifulSoup
from oauth2client.service_account import ServiceAccountCredentials

def next_available_row(sheet):
	str_list = list(filter(None, sheet.col_values(1)))  # fastest
	return len(str_list)

def add_strings(sheet, rowNum, movieRes):
	rateAddr = gspread.utils.rowcol_to_a1(i, 4)
	ws.update_acell(rateAddr, movieResult['vote_average'])
	dateAddr = gspread.utils.rowcol_to_a1(i, 3)
	ws.update_acell(dateAddr, movieResult['release_date'])
	genreAddr = gspread.utils.rowcol_to_a1(i, 2)
	genreString = ""
	for genresNames in movieResult['genres']:
		genreString = genreString + ", "+ genresNames['name']
	ws.update_acell(genreAddr, genreString[2:])
	runtimeAddr = gspread.utils.rowcol_to_a1(i, 5)
	ws.update_acell(runtimeAddr, movieResult['runtime'])
	posterAddr = gspread.utils.rowcol_to_a1(i, 6)
	ws.update_acell(posterAddr, "http://image.tmdb.org/t/p/original//" + movieResult['poster_path'])
	bgAddr = gspread.utils.rowcol_to_a1(i, 7)
	ws.update_acell(bgAddr, "http://image.tmdb.org/t/p/original//" + movieResult['backdrop_path'])
	overviewAddr = gspread.utils.rowcol_to_a1(i, 8)
	ws.update_acell(overviewAddr, movieResult['overview'])
	taglineAddr = gspread.utils.rowcol_to_a1(i, 9)
	ws.update_acell(taglineAddr, movieResult['tagline'])

def add_trailer(sheet, rowNum):
	textToSearch = ws.acell(titleAddr).value + " trailer"
	query = quote(textToSearch)
	url = "https://www.youtube.com/results?search_query=" + query
	response = urlopen(url)
	html = response.read()
	soup = BeautifulSoup(html)
	vid = soup.findAll(attrs={'class':'yt-uix-tile-link'})
	try:
		print ('https://www.youtube.com' + vid[0]['href'])
		trailerAddr = gspread.utils.rowcol_to_a1(i, 10)
		ws.update_acell(trailerAddr, 'https://www.youtube.com' + vid[0]['href'].replace("watch?v=", "embed/"))
	except Exception as uh:
		print(uh) 
		print("Unable to find trailer for " + ws.acell(titleAddr))

scope = ['https://spreadsheets.google.com/feeds']

credentials = ServiceAccountCredentials.from_json_keyfile_name('creds.json', scope)
print(credentials.service_account_email)
gc = gspread.authorize(credentials)

wks = gc.open_by_url(config.spreadsheet_link)

ws = wks.get_worksheet(0)
api = tmdb.API(config.tmdb_key)

end = next_available_row(sheet=ws)
print("Length: " + str(end))
for i in range (end, 2, -1):
	titleAddr = gspread.utils.rowcol_to_a1(i, 1)
	print(titleAddr + ": " + ws.acell(titleAddr).value)
	try:
		movieResult = api.movie(api.search_movie(query=ws.acell(titleAddr).value)['results'][0]['id'])
		add_strings(sheet=ws, rowNum=i, movieRes=movieResult)
	except Exception as ahh:
		print (ahh)
		print ("Movie search unable to generate result for " + ws.acell(titleAddr))	
	add_trailer(sheet=ws, rowNum=i)
