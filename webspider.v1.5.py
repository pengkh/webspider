import bs4
import gevent
import requests
import urllib2
import urlparse
import re

from gevent.queue import Queue

class Spider:
    def __init__(self, url='', depth=1):
	self.tasks = Queue()
	self.tasks.put(url)
	self.init_url = url or ''
	self.depth = depth or ''
	
    def run(self):
	threds = [
		gevent.spawn(self.work),
		gevent.spawn(self.work),
		gevent.spawn(self.work),
		gevent.spawn(self.work)
		]
	gevent.joinall(threds)

    def work(self):
	while not self.tasks.empty():
	    task = self.tasks.get()
	    task.run()
	    subtasks = task.subtasks
	    for t in subtasks:
		self.tasks.put_nowait(t)

class Task:
    def __init__(self, url, depth):
	self.url = url
	self.depth = depth
	self.hrefs = []
	self.subtasks = []

    def run(self):
	p = Page(self.url, self.depth)
	p.do_request()
	p.parse_content()
	if self.depth > 0:
	    self.hrefs = p.hrefs
	    for href in self.hrefs:
		t = Task(href, self.depth-1)
		self.subtasks.append(t)

    def __get_subtasks(self):
	return self.subtasks
    subtasks = property(__get_subtasks)





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
	print 'do request to: %s' % self.url

	if not self.url:
	    return None
	# maybe need do some exception and timeout
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
    spider = Spider(url=url, depth=1)
    spider.run()
