import bs4
import requests
import urlparse
import threading

class Req(threading.Thread):
    def __init__(self, task, ContentQueue):
        threading.Thread.__init__(self)
        self.url = 
        self.ContentQueue = ContentQueue
