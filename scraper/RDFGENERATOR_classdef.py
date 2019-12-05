# RDF Generator for Coding Da Vinci data

import rdflib as rdf
from django.utils.html import escape

class rdfGenerator:

    #setup for URIs
    __graph__ = rdf.Graph()
    __prefix__= 'http://codingdavinci.de/lod/'
    __superior__ = rdf.URIRef(__prefix__ + 'superior/')

    __event__ = rdf.URIRef(__prefix__ + 'event/')
    __data__ = rdf.URIRef(__prefix__ + 'data/')
    __project__ = rdf.URIRef(__prefix__ + 'project/')
    __article__ = rdf.URIRef(__prefix__ + 'article/')
    __tweet__ = rdf.URIRef(__prefix__ + 'tweet/')
    __award__ = rdf.URIRef(__prefix__ + 'award/')

    __title__ = rdf.URIRef(__prefix__ + 'title/')
    __description__ = rdf.URIRef(__prefix__ + 'description/')
    __format__ = rdf.URIRef(__prefix__ + 'format/')
    __license__ = rdf.URIRef(__prefix__ + 'license/')

    __url__ = rdf.URIRef(__prefix__ + 'url/')
    __thumbnailUrl__ = rdf.URIRef(__prefix__ + 'thumbnailUrl/')

    __date__ = rdf.URIRef(__prefix__ + 'date/')
    __year__ = rdf.URIRef(__prefix__ + 'year/')
    __duration__ = rdf.URIRef(__prefix__ + 'duration/')

    __person__ = rdf.URIRef(__prefix__ + 'person/')
    #__twitter_account__ = rdf.URIRef(__prefix__ + 'twitter/')
    #__mail_address__ = rdf.URIRef(__prefix__ + 'mail/')
    __institution__ = rdf.URIRef(__prefix__ + 'institution/')
    __location__ = rdf.URIRef(__prefix__ + 'location/')

    __articleType__ = rdf.URIRef(__prefix__ + 'articleType/')
    __magazine__ = rdf.URIRef(__prefix__ + 'magazine/')



    #save the made graph
    def saveRdf(self,path):
        #as turtle rdf
        for sub,pred,ob in self.__graph__:
            ob = ob.replace('"', '\'').encode("unicode_escape").decode("utf-8")
        self.__graph__.serialize(path,format='nt')
        #as d3.js compatible js file
        with open("rdf/rdf.js", "a") as f:
            rdfjs = "var triples = ["
            for sub,pred,ob in self.__graph__:
                #descriptions shouldnt be visualized, take up too much space
                if (str(pred) != "http://codingdavinci.de/lod/description/"):
                    rdfjs += '{subject:"' + sub.replace("http://codingdavinci.de/lod/", "") + '",predicate:"' + pred.replace("http://codingdavinci.de/lod/", "") + '",object:"' + ob.replace('"', '\'').encode("unicode_escape").decode("utf-8").replace("http://codingdavinci.de/lod/", "") + '"},\n'
            rdfjs += "];"
            f.write(rdfjs)
            f.close()

    #create one new node
    def createNode(self,id,title):
        newNode = rdf.URIRef(self.__prefix__ + str(id))
        self.__graph__.add((newNode, self.__title__, rdf.Literal(title)))

        print("created Node")
        return newNode

    #create cdv events
    def createEvent(self,id,title,locations,year,duration,url,thumbnailUrl):
        #id | id for the node, is the shortform of the title (e.g. cdv_ost) (string)
        #title | title of the event (string)
        #locations | locations of the event (array)
        #year | year of the event (int)
        #duration | duration of the event, e.g. 01.01.-16.02.2019 (string)
        #url | url to the events homepage (string)
        #thumbnailUrl | url to a thumbnail (string)

        #setup node and link to metanode
        event = self.createNode(id,title)
        self.__graph__.add((event,self.__superior__,rdf.URIRef(self.eventNode)))
        #add all locations
        for location in locations:
            self.__graph__.add((event,self.__location__,rdf.Literal(location)))
        #add all other properties
        self.__graph__.add((event,self.__year__,rdf.Literal(year)))
        self.__graph__.add((event,self.__duration__,rdf.Literal(duration)))
        self.__graph__.add((event,self.__url__,rdf.Literal(url)))
        self.__graph__.add((event,self.__thumbnailUrl__,rdf.Literal(thumbnailUrl)))
        #return node
        return event

    #create cdv awards
    def createAward(self,id,title):
        #id | id for the node, is the shortform of the title (e.g. cdv_ost) (string)
        #title | title of the event (string)

        #setup node and link to metanode
        award = self.createNode(id,title)
        self.__graph__.add((award,self.__superior__,rdf.URIRef(self.awardNode)))
        return award

    #create one new dataset
    def createDataset(self,id,title,description,producer,formats,licenses,events,urls,thumbnailUrl):
        #id | id for the node, generated in DATA_SCRAPER_CLASSDEF.py (string)
        #title | title of the dataset (string)
        #description | description of dataset (string)
        #producer | corporation that made the dataset available (string)
        #formats | format(s) of the dataset (array)
        #licenses | license(s) of the dataset (array)
        #events | cdv-event(s) in which the dataset was published (array)
        #urls | url(s) to obtain the dataset (dict)
        #thumbnailUrl | url to a thumbnail (string)

        #counter for url node ids
        i = 1
        #setup node and link to metanode
        dataset = self.createNode(id,title)
        self.__graph__.add((dataset,self.__superior__,rdf.URIRef(self.datasetNode)))
        #add properties
        self.__graph__.add((dataset,self.__description__,rdf.Literal(description)))
        self.__graph__.add((dataset,self.__institution__,rdf.Literal(producer)))
        for format in formats:
            self.__graph__.add((dataset,self.__format__,rdf.Literal(format)))
        for license in licenses:
            self.__graph__.add((dataset,self.__license__,rdf.Literal(license)))
        for event in events:
            self.__graph__.add((dataset,self.__event__,rdf.URIRef(self.__prefix__ + event)))
        for res,url in urls.items():
            url_id = id + "_" + str(i)
            i += 1
            url_node = self.createNode(url_id,url)
            self.__graph__.add((dataset,self.__url__,rdf.URIRef(url_node)))
            self.__graph__.add((url_node,self.__title__,rdf.Literal(res)))
        self.__graph__.add((dataset,self.__url__,rdf.URIRef(thumbnailUrl)))
        #return node
        print("created Dataset")
        return dataset

    #create one new project
    def createProject(self,id,title,description,authors,event,urls,data,thumbnailUrl):
        #id | id for the node, generated in DATA_SCRAPER_CLASSDEF.py (string)
        #title | title of the project (string)
        #description | description of project (string)
        #authors | authors and contributors of project (array)
        #event | cdv-event at which the project was developed
        #urls | url(s) to obtain the project (dict)
        #data | dataset(s) used for the project (array)
        #thumbnailUrl | url to a thumbnail (string)

        #counter for url node ids
        i = 1
        #counter for author node ids
        k = 1
        #setup node and link to metanode
        project = self.createNode(id,title)
        self.__graph__.add((project,self.__superior__,rdf.URIRef(self.projectNode)))
        #add all authors
        for name,contacts in authors.items():
            #new node
            aut_id = "author_" + id + "_" + str(k)
            k += 1
            aut_node = self.createNode(aut_id,name)
            self.__graph__.add((project,self.__person__,rdf.URIRef(aut_node)))
            for contact in contacts:
                if (contact != ("Keine eMail" or "Kein Twitter-Account")):
                    self.__graph__.add((aut_node,self.__url__,rdf.Literal(contact)))
        #add all datasets
        for set in data:
            self.__graph__.add((project,self.__data__,rdf.Literal(set)))
        #add all links
        for res,url in urls.items():
            #new node
            url_id = id + "_" + str(i)
            i += 1
            url_node = self.createNode(url_id,url)
            self.__graph__.add((project,self.__title__,rdf.URIRef(url_node)))
            self.__graph__.add((url_node,self.__url__,rdf.Literal(res)))
        #add all other properties
        self.__graph__.add((project,self.__description__,rdf.Literal(description)))
        self.__graph__.add((project,self.__event__,rdf.URIRef(self.__prefix__ + event)))
        self.__graph__.add((project,self.__thumbnailUrl__,rdf.Literal(thumbnailUrl)))
        #return node
        return project

    #create new "article" about cdv
    def createArticle(self, id, magazine = "Unbekanntes Magazin", type = "Artikel", event = "Coding Da Vinci", date = "Unbekanntes Datum", url = "http://codingdavinci.de"):
        #id | id for the node, generated in DATA_SCRAPER_CLASSDEF.py (string)
        #magazine | name of the publishing magazine (string)
        #type | type of the article (blogpost,hörbeitrag etc.) (string)
        #event | cdv-event this article is about (string)
        #date | date of the publishing (string)
        #url | url to the article (string)

        #setup node and link to metanode
        title = str(type) + " " + str(magazine)
        article = self.createNode(id,title)
        self.__graph__.add((article,self.__superior__,rdf.URIRef(self.articleNode)))
        #add properties
        #link to eventNode property
        if (event == "cdv_rheinmain & cdv_ost"):
           self.__graph__.add((article,self.__event__,rdf.URIRef(self.__prefix__ + "cdv_rheinmain")))
           self.__graph__.add((article,self.__event__,rdf.URIRef(self.__prefix__ + "cdv_ost")))
        else:
           self.__graph__.add((article,self.__event__,rdf.URIRef(self.__prefix__ + event)))
        #add other properties
        self.__graph__.add((article,self.__magazine__,rdf.Literal(magazine)))
        self.__graph__.add((article,self.__articleType__,rdf.Literal(type)))
        self.__graph__.add((article,self.__date__,rdf.Literal(date)))
        self.__graph__.add((article,self.__url__,rdf.Literal(url)))
        #return node
        return article

    #create new tweet about cdv
    def createTweet(self,author,authorLink,event,date,text,url):
        #author | name of the tweeter (string)
        #authorLink | link to authors profile (string)
        #event | cdv-event this article is about (string)
        #date | date of tweet (string)
        #text | text of tweet (string)
        #url | url to the tweet (string)
        print("created Tweet")

    #setup metanodes
    def createMeta(self):
        self.eventNode = self.createNode("event","Event")
        self.tweetNode = self.createNode("tweet","Tweet")
        self.projectNode = self.createNode("project","Projekt")
        self.articleNode = self.createNode("article","Artikel")
        self.datasetNode = self.createNode("dataset","Datenset")
        self.awardNode = self.createNode("award","Preis")
