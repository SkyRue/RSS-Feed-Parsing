

import feedparser
import string
import time
import threading
from project_util import translate_html
from tkinter import *
from datetime import datetime
import pytz
import traceback

###############################################################
###############################################################

"""
retrieving and parsing Google and Yahoo News feeds
"""

def process(url):
    """
    Fetches news items from the rss url and parses them.
    Returns a list of NewsStory-s.
    """
    feed = feedparser.parse(url)
    entries = feed.entries
    ret = []
    for entry in entries:
        guid = entry.guid
        title = translate_html(entry.title)
        link = entry.link
        description = translate_html(entry.description)
        pubdate = translate_html(entry.published)

        try:
            pubdate = datetime.strptime(pubdate, "%a, %d %b %Y %H:%M:%S %Z")
        except ValueError:
            pubdate = datetime.strptime(pubdate, "%a, %d %b %Y %H:%M:%S %z")

        # assume the news we get is in GMT
        pubdate = pubdate.replace(tzinfo=pytz.timezone("GMT"))
        # convert to EST
        pubdate = pubdate.astimezone(pytz.timezone('EST'))
        # remove timezone information for simplicity
        pubdate = pubdate.replace(tzinfo=None)

        newsStory = NewsStory(guid, title, description, link, pubdate)
        ret.append(newsStory)
    return ret






# TODO: NewsStory
"""
Create a class, NewsStory, with the following 
attributes and getter methods: 

Attributes:
    guid - a string
    title - a string
    description - a string
    link - a string
    pubdate - a datetime

Getter methods:
    get_guid(self)
    get_title(self)
    get_description(self)
    get_link(self)
    get_pubdate(self)
"""

class NewsStory(object):
    def __init__(self, guid, title, description, link, pubdate):
        self.guid = guid
        self.title = title
        self.description = description
        self.link = link
        self.pubdate = pubdate
    
    def get_guid(self):
        return self.guid
    
    def get_title(self):
        return self.title
    
    def get_description(self):
        return self.description
    
    def get_link(self):
        return self.link
    
    def get_pubdate(self):
        return self.pubdate



###############################################################
########################  Triggers  ###########################
###############################################################

class Trigger(object):    #abstract class
    def evaluate(self, story):
        """
        Returns True if an alert should be generated
        for the given news item, or False otherwise.
        """
        # DO NOT CHANGE THIS!
        raise NotImplementedError

#=============================================================
#                       PHRASE TRIGGERS
#=============================================================


# TODO: PhraseTrigger
"""
PhraseTrigger,a subclass of Trigger.

Attribute:
    phrase - a string

Method:
    is_phrase_in - takes in one string argument text. 
        It returns True if the whole phrase phrase is present, 
        False otherwise, as described in the above examples.
        NOT case-sensitive. Implement this method. 


"""

class PhraseTrigger(Trigger):
    def __init__(self, phrase):
        self.phrase = phrase
    
    
    
    def is_phrase_in(self, text):
        #lowercase entire phrase, replace all punctuation with spaces
        phrase = self.phrase.lower()
        punct_list = list(string.punctuation)
        for char in phrase:
            if char in punct_list:
                phrase = phrase.replace(char, " ")
        #deletes extra spaces in list of phrase characters so that every word in phrase is only seperated by 1 space  
        #results in a list of characters, all of which are letters or spaces, and the letters are seperated by a max 1 space   
        phrase_list = list(phrase)
        phrase_list_copy = phrase_list[:]
        for i in range (len(phrase_list_copy) - 1):     
            if (phrase_list_copy[i] == " ") and (phrase_list_copy[i+1] == " "):
                del(phrase_list[i+1])
        phrase = ''.join(phrase_list) 
            
        
        #lowercase entire text, replace all punctuation with spaces
        text = text.lower() 
        for char in text:
            if char in punct_list:
                text = text.replace(char, " ")
        #deletes extra spaces in list of text characters so that every word in text is only seperated by 1 space  
        #results in a list of characters, all of which are letters or spaces, and the letters are seperated by a max 1 space     
        text_list = list(text)
        length = len(text_list) 
        for i in range(length - 2, -1, -1):  #iterate backwards so we can delete elements while we iterate
            if (text_list[i] == " ") and (text_list[i+1] == " "):
                del(text_list[i+1])
        text = ''.join(text_list) #text string, with no punctuation, all words seperated by max 1 space
        
        text_word_list = text.split() #list of words in the text
        phrase_word_list = phrase.split() #list of words in phrase
        num_phrase_words = len(phrase_word_list) #num of words in phrase
        temp_string = '' #used to hold every set of num_phrase_words (for ex, 3 if there are 3 words in the phrase) words in text
        phrase = phrase + " "
        #compares the phrase string to every consecutive string of 3 words in text
        #returns true if the phrase matches any one of these strings
        for i in range(len(text_word_list) - num_phrase_words + 1):
            for w in range(num_phrase_words):
                temp_string += text_word_list[i + w] + " "
            if phrase == temp_string:
                return True
            temp_string = ''
        
        return False
                
    
                
        

        
        

        

# TODO: TitleTrigger
"""
TitleTrigger, a subclass of PhraseTrigger.

Fires when a news item's title contains a given phrase.


"""
class TitleTrigger(PhraseTrigger):
    def __init__(self, phrase):
        PhraseTrigger.__init__(self, phrase)
    
    def evaluate(self, story):
        title = story.get_title()
        return self.is_phrase_in(title)


# TODO: DescriptionTrigger
"""
DescriptionTrigger, subclass of PhraseTrigger.

Fires when a news item's description contains a given phrase.

"""


class DescriptionTrigger(PhraseTrigger):
    def __init__(self, phrase):
        PhraseTrigger.__init__(self, phrase)
    
    def evaluate(self, story):
        description = story.get_description()
        return self.is_phrase_in(description)



#============================================================
#                         TIME TRIGGERS
#============================================================

class TimeTrigger(Trigger):   #abstract class
    def __init__(self, time):
        """
        Input: Time has to be in EST and in the format of "%d %b %Y %H:%M:%S".
        Converts time from string to a datetime before saving it as a time attribute
        """
        time = datetime.strptime(time, "%d %b %Y %H:%M:%S")
        self.time = time
        

# TODO: BeforeTrigger and AfterTrigger
"""
BeforeTrigger and AfterTrigger are subclasses of TimeTrigger.

BeforeTrigger fires when a story is published before the 
trigger's time.

AfterTrigger fires when a story is published after 

"""
class BeforeTrigger(TimeTrigger):
    def __init__(self, time):
        TimeTrigger.__init__(self, time)
    
    def evaluate(self, story):
        if story.get_pubdate() < self.time:
            return True
        return False

class AfterTrigger(TimeTrigger):
    def __init__(self, time):
        TimeTrigger.__init__(self, time)
    
    def evaluate(self, story):
        if story.get_pubdate() > self.time:
            return True
        return False


#============================================================
#                         COMPOSITE TRIGGERS
#============================================================



# TODO: NotTrigger
"""

Take in as input a trigger and returns its opposite value.


"""
class NotTrigger(Trigger):
    def __init__(self, trigger):
        self.trigger = trigger
    
    def evaluate(self, story):
        not_trigger = not self.trigger.evaluate(story)
        return not_trigger
        



# TODO: AndTrigger
"""


takes two triggers as arguments 
to its constructor, and fires on a news story 
if both of the inputted triggers would fire.


"""

class AndTrigger(Trigger):
    map_trigger_str = {"TITLE": TitleTrigger, "DESCRIPTION": DescriptionTrigger, "AFTER": AfterTrigger, "BEFORE": BeforeTrigger, "NOT": NotTrigger }
    def __init__(self, trigger1, trigger2):
        
        self.trigger1 = trigger1
        self.trigger2 = trigger2
    
    def evaluate(self, story):
        return self.trigger1.evaluate(story) and self.trigger2.evaluate(story)
            


# TODO: OrTrigger
"""


takes two triggers as arguments 
to its constructor, and fires if either one (or both) 
of its inputted triggers would fire 

"""

class OrTrigger(Trigger):
    def __init__(self, trigger1, trigger2):
        self.trigger1 = trigger1
        self.trigger2 = trigger2
    
    def evaluate(self, story):
        return self.trigger1.evaluate(story) or self.trigger2.evaluate(story)

###############################################################
########################  Filtering  ##########################
###############################################################


# TODO: FilterStories
def filter_stories(stories, triggerlist):
    """
    takes in list of NewsStory instances

    Returns: a list of only the stories for which a trigger in 
    triggerlist fires.
    """
    relevant_stories = []
    for trigger in triggerlist:
        for story in stories:
            if trigger.evaluate(story):
                relevant_stories.append(story)

    return relevant_stories




# TODO: ReadTriggerConfig

def create_trigger_dict(lines):
    """
    lines: list of string elements that needs to be parsed
    
    Returns: dict of config file trigger names mapped with their corresponding instantiated trigger objects 
    """
    
    #maps trigger string names to class trigger names
    map_trigger_str = {"TITLE": TitleTrigger, "DESCRIPTION": DescriptionTrigger, "AFTER": AfterTrigger, "BEFORE": BeforeTrigger, "NOT": NotTrigger, "AND": AndTrigger, "OR": OrTrigger  }
    trigger_dict = {}
    
    #instantiates all trigger objects (that arent AND or OR) in the config file based on their trigger type
    for line in lines:
        line_list = line.split(",")
        trigger_obj = line_list[0]
    
        if not(line_list[0] == "ADD") and not(line_list[1] == "AND") and not(line_list[1] == "OR"): 
            trigger_name = line_list[0]
            trigger_obj = map_trigger_str[line_list[1]](line_list[2] )    
            trigger_dict[trigger_name] = trigger_obj
    
    #now that all non AND and OR trigger objects exist in the dict, we can add ADD and OR triggers (which are other trigger objects that we had to put in the dict first )
    for line in lines:
        line_list = line.split(",")
        trigger_obj = line_list[0]
        trigger_name = line_list[0]
        
        if line_list[1] == "AND" or line_list[1] == "OR":
            arg_1 = trigger_dict[line_list[2]]
            arg_2 = trigger_dict[line_list[3]]
            trigger_obj = map_trigger_str[line_list[1]](arg_1, arg_2)
            trigger_dict[trigger_name] = trigger_obj
    
    
    return trigger_dict


        
            
                


def read_trigger_config(filename):
    """
    filename: the name of a trigger configuration file

    Returns: a list of trigger objects specified by the trigger configuration
        file.
    """
    
    trigger_file = open(filename, 'r')
    lines = []
    for line in trigger_file:
        line = line.rstrip()
        if not (len(line) == 0 or line.startswith('//')):
            lines.append(line)

    
    # line is the list of lines that you need to parse and for which you need
    # to build triggers
    # this should return a list of triggers specified by the configuration file
    
    avail_triggs = create_trigger_dict(lines)
    trigger_objs = []
    #adds trigger objects to a list that were specified by the config file
    for line in lines:
        line_list = line.split(",")
        if line_list[0] == "ADD":
            del(line_list[0])
            for i in range(0, len(line_list)):
                trigger_objs.append(avail_triggs[line_list[i]])
        
    
    return trigger_objs
            
            
        
        
    
    


SLEEPTIME = 120 #seconds (how often polling happens)

def main_thread(master):
    try:
        t1 = TitleTrigger("a")
        t2 = DescriptionTrigger("a")
        t3 = DescriptionTrigger("a")
        t4 = AndTrigger(t2, t3)
        triggerlist = [t1, t4]
 
        triggerlist = read_trigger_config('triggers.txt')

        #print("triggers:", triggerlist)
        
      
        # creates popup window that displays the filtered stories
        # retrieves and filters the stories from the RSS feeds
        frame = Frame(master)
        frame.pack(side=BOTTOM)
        scrollbar = Scrollbar(master)
        scrollbar.pack(side=RIGHT,fill=Y)

        t = "Google & Yahoo Top News"
        title = StringVar()
        title.set(t)
        ttl = Label(master, textvariable=title, font=("Helvetica", 18))
        ttl.pack(side=TOP)
        cont = Text(master, font=("Helvetica",14), yscrollcommand=scrollbar.set)
        cont.pack(side=BOTTOM)
        cont.tag_config("title", justify='center')
        button = Button(frame, text="Exit", command=root.destroy)
        button.pack(side=BOTTOM)
        guidShown = []
        def get_cont(newstory):
            if newstory.get_guid() not in guidShown:
                cont.insert(END, newstory.get_title()+"\n", "title")
                cont.insert(END, "\n---------------------------------------------------------------\n", "title")
                cont.insert(END, newstory.get_description())
                cont.insert(END, "\n*********************************************************************\n", "title")
                guidShown.append(newstory.get_guid())

        while True:

            print("Polling!", end=' ')
            # gets stories from Google's Top Stories RSS news feed
            stories = process("http://news.google.com/news?output=rss")

            # get stories from Yahoo's Top Stories RSS news feed
            stories.extend(process("http://news.yahoo.com/rss/topstories"))

            stories = filter_stories(stories, triggerlist)

            list(map(get_cont, stories))
            scrollbar.config(command=cont.yview)


            print("Sleeping")
            time.sleep(SLEEPTIME)

    except Exception as e:
        traceback.print_exc()
        print(e)


if __name__ == '__main__':
    root = Tk()
    root.title("RSS parser")
    t = threading.Thread(target=main_thread, args=(root,))
    t.start()
    root.mainloop()

