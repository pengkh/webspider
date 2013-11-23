import bs4
import gevent
import requests
import urllib2
import urlparse
import re

from gevent.queue import Queue
from gevent import monkey

monkey.patch_all()


class Spider:
    def __init__(self, url='', depth=1, threads=4):
	self.url = url
	self.depth = depth
	self.threads = threads
	self.tasks = Queue()
	self.bucket = []
	
    def run(self):
	self.tasks.put(Task(self.url, self.depth))
	threds = [ 
		gevent.spawn(self.worker)
		for i in range(self.threads)
		]
	gevent.joinall(threds)

    def worker(self, worker_id=''):
	while not self.tasks.empty():
	    task = self.tasks.get()
	    if task.url in self.bucket:
		# here have a bug
		continue
	    self.bucket.append(task.url)
	    task.run()
	    subtasks = task.subtasks
	    for t in subtasks:
		self.tasks.put_nowait(t)

class Task:
    def __init__(self, url, depth):
	self.url = url
	self.depth = depth
	self.subtasks = []

    def run(self):
	p = Page(self.url, self.depth)
	p.do_request()

	if self.depth > 0:
	    # if self.depth > 0, so we need go to next level
	    # should do the parse content
	    # otherwise, do nothing
	    p.parse_content()
	    for href in p.hrefs:
		t = Task(href, self.depth-1)
		self.subtasks.append(t)

    def __get_subtasks(self):
	return self.subtasks
    subtasks = property(__get_subtasks)

    def __get_url(self):
	return self.url
    url = property(__get_url)


class Page:
    def __init__(self, url='', depth=''):
	self.url = url
	self.depth = depth
	self.hrefs = []
	self.content = ''
	self.baseurl = self.get_baseurl(url)

    def get_baseurl(self, url):
	u = urlparse.urlparse(url)
	if u.scheme and u.netloc:
	    return u.scheme + '://' + u.netloc + '/'.join(u.path.split('/')[:-1])
	elif u.path:
	    return '/'.join(u.path.split('/')[:-1])
	else:
	    return None
    
    def do_request(self):
	if not self.url:
	    return None
	print 'do request to: %s, depth: %s' % (self.url, self.depth)
	# maybe need do some exception resolve and timeout
	# and if this is in class Page ?
	# or in other part ?
	req = requests.get(url)
	self.content = req.content

    def parse_content(self):
	if not self.content:
	    return None
	sp = bs4.BeautifulSoup(self.content)
	for a in sp.find_all('a'):
	    href = a.attrs.get('href')
	    if href and href[0] != '#':
		# if not has protocol scheme or is a relative url
		# should use the absolute and standard presentation style
		u = urlparse.urlparse(href)
		if not u.scheme:
		    href = self.baseurl + href
		self.hrefs.append(href)
    
    def __get_href(self):
	# remove repetition
	new_hrefs = set(self.hrefs)
	return list(new_hrefs)
    hrefs = property(__get_href)


if __name__ == '__main__':
    url = 'http://www.python.org'
    #url = 'http://www.hao123.com'
    spider = Spider(url=url, depth=10)
    spider.run()
