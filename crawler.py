import urllib2, re, time, Queue, threading, lxml, __builtin__, httplib
from bs4 import BeautifulSoup as bs
from decorators import retry

global urlopen_with_retry, tanggal

__builtin__.visited = []
__builtin__.totalKata = 0
__builtin__.totalWeb = 1

queue = Queue.Queue()

tanggal = [k for k in range(1,26)]

@retry(urllib2.URLError, tries=25, delay=3, backoff=2)
def urlopen_with_retry(url):
	try:
		hasil = urllib2.urlopen(url)
	except urllib2.HTTPError, e:
		if e.code == 404 or e.code == 400 or e.code == 403:
			return None
		print e.code,url
		raise
	else:
		return hasil

@retry(urllib2.URLError, tries=25, delay=3, backoff=2)
def read_retry(url):
	try:
		hasil = url.read()
	except urllib2.HTTPError, e:
		if e.code == 404 or e.code == 400 or e.code == 403:
			return None
		raise
	except httplib.IncompleteRead:
		return None
	else:
		return hasil

class CrawlingKompas(threading.Thread):
	def __init__(self, queue):
		threading.Thread.__init__(self)
		self.queue = queue

	def run(self):
		k = 0
		hari = self.queue.get()
		idx = 1
		urlIndex = 'http://indeks.kompas.com/indeks?tanggal='+str(tanggal[k])+'&bulan='+str(hari[0])+'&tahun='+str(hari[1])+'&pos=indeks&p='+str(idx)
		while True:
			handle = urlopen_with_retry(urlIndex)
			if handle != None:
				html = read_retry(handle)
				soupIndex = bs(html, 'lxml')

				list_link = soupIndex.find_all("div", {"class":"kcm-main-list"})

				if len(list_link) > 0:
					list_link = list_link[0].find_all('li')

					filetext = open("Corpus"+str(hari[0])+"-"+str(hari[1])+".txt","a+")

					if len(list_link) > 0:
						if list_link[0].a != None:
							for z in list_link:
								urlNews = z.a['href']
								if urlNews not in __builtin__.visited:
									__builtin__.visited.append(urlNews)
									if len(__builtin__.visited) > 20:
										__builtin__.visited.pop(0)
									handleNews = urlopen_with_retry(urlNews)
									if handleNews == None:
										continue
									htmlNews = read_retry(handleNews)
									soupNews = bs(htmlNews, 'lxml')
									contentNews = soupNews.find_all("div", {"class":"kcm-read-text"})

									if len(contentNews) > 0:
										contentNews = contentNews[0].find_all("p")

										item = ""
										for x in contentNews:
											item += x.text.encode('utf-8')
											item += " "

										__builtin__.totalKata += len(re.findall("[A-Za-z,;'\"\\s]+[.?!]",item))

										filetext.write(item)
										filetext.write('\n\n')

									__builtin__.totalWeb += 1

					filetext.close()

				print __builtin__.totalKata

				paginasi = soupIndex.find_all("ul",{"class":"paginasi"})
				if len(paginasi) > 0:
					paginasi = paginasi[0].find_all("li")
					urlIndex = paginasi[-1].a['href']
					if urlIndex=='javascript:void(0)':
						if k+1 == len(tanggal):
							self.queue.task_done()
							break
						else:
							k += 1
							idx = 1
					else:
						idx += 1
				else:
					if k+1 == len(tanggal):
						self.queue.task_done()
						break
					else:
						k += 1
						idx = 1
			else:
				if k+1 == len(tanggal):
					self.queue.task_done()
					break
				else:
					k += 1
					idx = 1
			
			urlIndex = 'http://indeks.kompas.com/indeks?tanggal='+str(tanggal[k])+'&bulan='+str(hari[0])+'&tahun='+str(hari[1])+'&pos=indeks&p='+str(idx)

			if totalKata >= 10**7:
				self.queue.task_done()
				break


start = time.time()

def main():

	hari = [[j,i] for j in range(1,13) for i in range(2008,2018) if not(j>1 and i==2017)]
	for i in range(len(hari)):
		t = CrawlingKompas(queue)
		t.setDaemon(True)
		t.start()

	for t in hari:
		queue.put(t)

	queue.join()

main()


# filetext.close()

# if totalKata >= 10**7:
# 	break

# print "Total kata saat ini : "+str(totalKata)

# print "Done"