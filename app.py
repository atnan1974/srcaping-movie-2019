from flask import Flask, render_template
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from bs4 import BeautifulSoup 
import requests

#don't change this
matplotlib.use('Agg')
app = Flask(__name__) #do not change this

#insert the scrapping here
url_get = requests.get('https://www.imdb.com/search/title/?release_date=2019-01-01,2019-12-31?')
soup = BeautifulSoup(url_get.content,"html.parser")

sourceData = soup.find("div",attrs={"class":"lister-list"})
table_list = sourceData.find_all("div" ,attrs={"class":"lister-item mode-advanced"})


temp = [] #initiating a tuple

for i in range(0, len(table_list)):                                      
    condrat1 = len(sourceData.find_all("div",attrs={"class":"ratings-bar"}))
    condrat2 = len(sourceData.find_all("div",attrs={"class":"lister-item-content"})[i])
    title = sourceData.find_all("h3",attrs={"class":"lister-item-header"})[i]
    rating = sourceData.find_all("div",attrs={"class":"lister-item-content"})[i]
    if condrat2 <= 9:
        dataTittle = title.find_all("a")[0].text
        dataTittle = dataTittle.strip()
        temp.append((dataTittle,0,0,0))
    else:
        dataTittle = title.find_all("a")[0].text
        dataTittle = dataTittle.strip()
        dataRating = rating.find("strong").text
        dataRating = dataRating.strip()
        condmet = sourceData.find_all("div",attrs={"class":"lister-item-content"})[i]
        condmetLength=(len(condmet.find_all("span",attrs={"class":"metascore favorable"})))
        dataVotes = rating.find_all("p",attrs={"class":"sort-num_votes-visible"})[0].text
        dataVotes = dataVotes.replace("\n","")
        dataVotes = dataVotes.replace("Votes:","")
        dataVotes = dataVotes.replace("| Gross:$858.37M","")
        dataVotes = dataVotes.replace("| Gross:$53.80M","")
        dataVotes = dataVotes.replace(",",".")
        if condmetLength == 0:                
            temp.append((dataTittle,dataRating,0,dataVotes))
        else :
            temp.append(
                (dataTittle,
                 dataRating,
                 condmet.find("span",attrs={"class":"metascore favorable"}).text.strip(),dataVotes) 
            )
temp



#change into dataframe
dataIMDB = pd.DataFrame(temp, columns = ("Title","Rating","Meta Score","Votes"))


#insert data wrangling here

dataIMDB[["Rating","Meta Score","Votes"]]=dataIMDB[["Rating","Meta Score","Votes"]].astype('float64')
BestSevenMovies = dataIMDB.sort_values(by='Votes', ascending=False).head(7)
BestSevenMovies = BestSevenMovies.set_index('Title')
BestSevenMovies.dtypes


print(BestSevenMovies)


#end of data wranggling 

@app.route("/")
def index(): 
	
	card_data = f'BestSevenMovies in 2019 {BestSevenMovies.max().round(2)}'

	# generate plot
	ax = BestSevenMovies[["Meta Score","Rating"]].sort_values("Meta Score").plot.barh(figsize = (20,9),title='Best Meta Score 2019')

	
	# Rendering plot
	# Do not change this
	figfile = BytesIO()
	plt.savefig(figfile, format='png', transparent=True)
	figfile.seek(0)
	figdata_png = base64.b64encode(figfile.getvalue())
	plot_result = str(figdata_png)[2:-1]


	# render to html
	return render_template('index.html',
		card_data = card_data, 
		plot_result=plot_result
		)


if __name__ == "__main__": 
    app.run(debug=True)
