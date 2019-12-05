# Scraper for Coding Da Vinci data

import re
import markdown as md

from os import walk
from lxml import html
from RDFGENERATOR_classdef import rdfGenerator

class cdvScraper:

    #setup new rdf generator
    rdfGen = rdfGenerator()
    #create meta nodes
    rdfGen.createMeta()
    #dict for events
    eventYears = {
        "Undefiniertes Event" : "cdv",
        "2014" : "cdv_2014",
        "2015" : "cdv_2015",
        "Nord 2016" : "cdv_nord",
        "Berlin 2017" : "cdv_berlin",
        "Rhein-Main 2018" : "cdv_rheinmain",
        "Ost 2018" : "cdv_ost",
        "Süd 2019" : "cdv_sued",
        "Westfalen-Ruhrgebiet 2019" : "cdv_west"
    }

    #start scraping
    def start(self):
        #scrape cdv events
        self.scrapeEvents()
        #scrape cdv articles
        self.scrapeArticles()
        #scrape cdv datasets
        self.scrapeData()
        #scrape cdv projects
        self.scrapeProjects()
        #scrape cdv awards
        self.scrapeAwards()
        #save output
        self.rdfGen.saveRdf("./rdf/rdf.nt")

    #scrape cdv events
    def scrapeEvents(self):
        #scrape every event available
        #first one is placeholder for resources that can not be connected to any event
        events = [
            ["cdv", "Coding Da Vinci", ["Berlin", "Berlin"], 9999, "99.99.9999-99.99.9999", "https://codingdavinci.de", "https://codingdavinci.de/img/nord/header_logo_cdvnord.png"],
            ["cdv_nord", "Coding Da Vinci Nord", ["Hamburg", "Hamburg"], 2016, "17.09.2016-06.11.2016","https://codingdavinci.de/events/nord/","https://codingdavinci.de/img/nord/header_logo_cdvnord.png"],
            ["cdv_berlin", "Coding Da Vinci Berlin", ["Berlin", "Berlin"], 2017, "21.10.2017-02.12.2017", "https://codingdavinci.de/events/berlin/", "https://codingdavinci.de/img/berlin/header_logo_2017.png"],
            ["cdv_ost", "Coding Da Vinci Ost", ["Leipzig", "Leipzig"], 2018, "14.04.2018-16.06.2018", "https://codingdavinci.de/events/ost/", "https://codingdavinci.de/img/ost/header_logo_2018.png"],
            ["cdv_rheinmain", "Coding Da Vinci Rhein-Main", ["Mainz", "Mainz"], 2018, "27.10.2018-01.12.2018", "https://codingdavinci.de/events/rheinmain/", "https://codingdavinci.de/img/rheinmain/header_logo_rheinmain.png"],
            ["cdv_sued", "Coding Da Vinci Süd", ["München", "Nürnberg"], 2019, "06.04.2019-18.05.2019", "https://codingdavinci.de/events/sued/", "https://codingdavinci.de/img/sued/header_sued.jpg"],
            ["cdv_west", "Coding Da Vinci Westfalen-Ruhrgebiet", ["Dortmund", "Dortmund"], 2019, "12.10.2019-06.12.2019", "https://codingdavinci.de/events/westfalen-ruhrgebiet/", "https://codingdavinci.de/img/westruhr/header.png"]
        ]
        for event in events:
            #add the event as rdf node
            self.rdfGen.createEvent(event[0], event[1], event[2], event[3], event[4], event[5], event[6])

    #scrape cdv awards
    def scrapeAwards(self):
        #scrape every award available
        awards = [
            ["award_useful","Most useful"],
            ["award_tech", "Most technical"],
            ["award_design", "Best design"],
            ["award_funny", "Funniest hack"],
            ["award_innovative", "Most innovative"],
            ["award_performing", "Most performing"],
            ["award_show", "Best of show"],
            ["award_unusual", "Unusual use of data"],
            ["award_competition", "Out of competition"],
            ["award_darling", "Everybody's darling"]
        ]
        for award in awards:
            #add the award as rdf node
            self.rdfGen.createAward(award[0], award[1])

    #scrape cdv datasets
    def scrapeData(self):
        #scrape every dataset available
        data = html.fromstring(html.tostring(html.parse("../daten/index.html")))
        datasets = data.cssselect("div.data-entry")
        i = 1 #counter for ids
        #for every single dataset
        for dataset in datasets:
            #get id and count up
            id = "dataset_" + str(i)
            i += 1
            #get title
            try:
                title = dataset.cssselect("div.data-content h4")[0].text
            except:
                title = "Datenset"
            #get description
            description = ""
            try:
                descriptions = dataset.cssselect("div.data-content p")
                for descr in descriptions:
                    description += descr.text + " "
            except:
                description = "Keine Beschreibung"
            #get producer
            try:
                producer = dataset.cssselect("div.data-interlude h3")[0].text
            except:
                producer = "Bereitsteller"
            #get formats
            formats = []
            formats_text = dataset.cssselect("div.data-meta dd.data-type span")
            for format in formats_text:
                if (format.text == ("" or None)):
                    formats.append("Undefiniertes Format")
                else:
                    formats.append(format.text)
            if (len(formats_text) == 0 or formats_text == None):
                formats.append("Undefiniertes Format")
            #get licenses
            licenses = []
            licenses_text = dataset.cssselect("div.data-meta dd.data-license span")
            for license in licenses_text:
                if (license.text == ("" or None)):
                    licenses.append("Undefinierte_Lizenz")
                else:
                    licenses.append(format.text)
            if (len(licenses_text) == 0 or licenses_text == None):
                licenses.append("Undefinierte_Lizenz")
            #get & formalize events
            years = []
            years_text = dataset.cssselect("div.data-meta dd.data-year span")
            for year in years_text:
                if (year.text == ("" or None)):
                    years.append(self.eventYears["Undefiniertes Event"])
                else:
                    years.append(self.eventYears[year.text])
            if (len(years_text) == 0 or years_text == None):
                years.append(self.eventYears["Undefiniertes Event"])
            #get & name urls
            links = {}
            links_text = dataset.cssselect("div.data-meta a")
            for link in links_text:
                if (link.text == ("" or None) or link.get("href") == ("" or None)):
                    links["Undefinierter_Link"] = "http://codingdavinci.de"
                else:
                    links[link.text] = link.get("href")
            if (len(links_text) == 0 or links_text == None):
                links["Undefinierter_Link"] = "http://codingdavinci.de"
            #get thumbnailUrl
            #left out at the moment (mostly no real pictures)
            #add the dataset as rdf node
            self.rdfGen.createDataset(id,title,description,producer,formats,licenses,years,links,"https://codingdavinci.de/img/logos/ddb.png")

    #scrape cdv projects
    def scrapeProjects(self):
        #scrape every project available
        path = "../_projects"
        #counter variables for id
        i = 0
        k = 0
        #for all project folders
        for (dirpath, dirnames, filenames) in walk(path):
            #for all folders
            for dirname in dirnames:
                #set counter
                i += 1
                #for all projects inside those folders
                extended_path = path + "/" + dirname
                for (dirpath_lower, dirnames_lower, filenames_lower) in walk(extended_path):
                    #all the files
                    for filename in filenames_lower:
                        #set counter
                        k += 1
                        #skip the template file
                        if (filename != "_template.md"):
                            #read the project file
                            input_file = open(extended_path + "/" + filename, mode="r", encoding="utf-8")
                            project_text = input_file.read().split("---")
                            #get id
                            id = "project_" + str(i) + "_" + str(k)
                            #get title
                            try:
                                title = re.sub("\"", "", re.split("\"?name\"?:\s", project_text[1])[1].splitlines()[0])
                            except:
                                title = filename.split(".md")[0]
                            #get description
                            description = project_text[2]
                            #get authors
                            authors = {}
                            try:
                                all_authors = re.split("-\s", re.split("\"?team\"?:", project_text[1])[1])
                            except:
                                all_authors = ["",""]
                            author_iter = iter(all_authors)
                            next(author_iter)
                            for author in author_iter:
                                try:
                                    #author name
                                    try:
                                        author_name = re.sub("\"", "", re.split("\"?name\"?:\s", author)[1].splitlines()[0])
                                    except:
                                        author_name = "Kein/e Autor/in"
                                    #author mail
                                    try:
                                        author_mail = re.sub("\"", "", re.split("\"?mail\"?:\s", author)[1].splitlines()[0])
                                    except:
                                        author_mail = "Keine eMail"
                                    #author twitter
                                    try:
                                        author_twitter = re.sub("\"", "", re.split("\"?twitter\"?:\s", author)[1].splitlines()[0])
                                    except:
                                        author_twitter = "Kein Twitter-Account"
                                except:
                                    continue

                                authors[author_name] = [author_mail,author_twitter]
                            #get & formalize events
                            try:
                                event = self.eventYears[re.split("\"?year\"?:\s", project_text[1])[1].splitlines()[0]]
                            except:
                                event = self.eventYears["Undefiniertes Event"]
                            #get & name urls
                            urls = {}
                            all_urls = re.split("\"?links\"?:", project_text[1])[1].split("-")
                            for url in all_urls:
                                try:
                                    link = re.sub("\"", "", re.split("\"?link\"?:\s", url)[1].splitlines()[0])
                                    link_name = re.sub("\"", "", re.split("\"?text\"?:\s", url)[1].splitlines()[0])
                                    urls[link_name] = link
                                except:
                                    continue

                            #get (& formalize?) datasets (link them)
                            datasets = []
                            all_sets = re.split("\"?data\"?:", project_text[1])[1].split("-")
                            for set in all_sets:
                                set = set.splitlines()[0]
                                try:
                                    if (set != ""):
                                        datasets.append(re.sub("\"", "", set))
                                except:
                                    datasets.append("Keine Angabe")

                            #get thumbnailUrl
                            try:
                                thumbnailUrl = "https://codingdavinci.de" + re.sub("\"", "", re.split("\"?tile_active\"?:\s", project_text[1])[1].splitlines()[0])
                            except:
                                thumbnailUrl = "https://codingdavinci.de/img/logos/ddb.png"

                            #add the project as rdf node
                            self.rdfGen.createProject(id,title,description,authors,event,urls,datasets,thumbnailUrl)

    #scrape cdv projects
    def scrapeArticles(self):
        #known article types and follow-up words for regex
        articleTypes = "Frühpodcast|Podcast|Meldung|Blogbeitrag|Journalbeitrag|Nachricht|Ankündigung|Hörbeitrag|Blogpost|Beitrag|Artikel|Zeitungsartikel"
        articleCons = "auf|in|im|bei|durch|der|des|von|vom"
        #array that links different article collections to cdv events (resembles order on website)
        articleEvents = ["cdv_west", "cdv_sued", "cdv_rheinmain & cdv_ost", "cdv_berlin", "cdv_nord"]

        #read html with articles
        press = html.fromstring(html.tostring(html.parse("../presse/index.html")))
        articleYears = press.cssselect("ul.list-unstyled")
        #for every single year
        for i in range(len(articleYears)-2): ##### !! ÜBERPRÜFEN !! #####
            #for every single article
            articles = articleYears[i].cssselect("li")
            #counter variable
            k = 1
            for article in articles:
                #set id
                id = "article" + "_" + str(i) + "_" + str(k)
                #if there is a link included, select it
                try:
                    articleLinked = article.cssselect("a")[0]
                #if not, proceed with already selected
                except:
                    articleLinked = article
                #get magazine
                magazine = re.sub('(' + articleTypes + ')\s?(' + articleCons + ')?\s?', "", articleLinked.text)
                #get type of article
                type = re.search('(' + articleTypes + ')?', articleLinked.text)
                #if no type, set to standard
                if (type.group() == "" or type.group() == None):
                    type = "Artikel"
                #if there is a type, select it
                else:
                    type = type.group()
                #get & formalize event
                event = articleEvents[i]
                #get date
                date = re.search('\d{0,2}\.?\s*(Januar|Februar|März|April|Mai|Juni|Juli|August|September|Oktober|November|Dezember)?\s+20\d{2}', article.text)
                #get url
                #if articleLinked is not set to article (=> "a"-tag found!)
                if (articleLinked.text != article.text):
                    url = articleLinked.get("href")
                #if no "a"-tag found, set to standard
                else:
                    url = "http://codingdavinci.de"
                #add the project as rdf node
                self.rdfGen.createArticle(id,magazine,type,event,date.group(),url)
                #count up
                k = k+1

    #scrape cdv projects
    def scrapeTweets(self):
        #relevant hashtags
        cdvHashtags = ["cdv", "codingdavinci", "cdvsued", "cdvwest", "", ""]
        cdvHashEvents = {"CodingDaVinciSued" : ["cdvsued", "cdv19", "cdvsued19"], "":""}
        #scrape every tweet with hashtags
            #get author
            #get authorLink
            #authorLink = "http://twitter.com/" + str(author)
            #get & formalize event
            #get date
            #get text
            #get url
        #add the project as rdf node
        self.rdfGen.createTweet("author")
