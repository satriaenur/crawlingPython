import urllib2, re, time, Queue, threading, lxml, __builtin__, httplib
from bs4 import BeautifulSoup as bs
from retry import retry

global urlopen_with_retry, listNovel, listPage

__builtin__.visited = []
__builtin__.totalKata = 0
__builtin__.totalWeb = 1

queue = Queue.Queue()

listNovel = [
	'http://www.bacanovelonline.com/novel-percy-jackson-olympians-lightning-thief/',
	'http://www.bacanovelonline.com/percy-jackson-olympians-sea-monsters/',
	'http://www.bacanovelonline.com/novel-percy-jackson-olympians-last-olympian/',
	'http://www.bacanovelonline.com/novel-the-da-vinci-code/',
	'http://www.bacanovelonline.com/novel-laskar-pelangi/',
	'http://www.bacanovelonline.com/novel-edensor/',
	'http://www.bacanovelonline.com/novel-sang-pemimpi/',
	'http://www.bacanovelonline.com/novel-padang-bulan/',
	'http://www.bacanovelonline.com/novel-cinta-di-dalam-gelas/',
	'http://www.bacanovelonline.com/maryamah-karpov-mimpi-mimpi-lintang/'
]

listPage = {
	'http://www.bacanovelonline.com/novel-percy-jackson-olympians-lightning-thief/': 75,
	'http://www.bacanovelonline.com/percy-jackson-olympians-sea-monsters/': 59,
	'http://www.bacanovelonline.com/novel-percy-jackson-olympians-last-olympian/': 78,
	'http://www.bacanovelonline.com/novel-the-da-vinci-code/': 119,
	'http://www.bacanovelonline.com/novel-laskar-pelangi/': 186,
	'http://www.bacanovelonline.com/novel-edensor/': 113,
	'http://www.bacanovelonline.com/novel-sang-pemimpi/': 95,
	'http://www.bacanovelonline.com/novel-padang-bulan/': 133,
	'http://www.bacanovelonline.com/novel-cinta-di-dalam-gelas/': 161,
	'http://www.bacanovelonline.com/maryamah-karpov-mimpi-mimpi-lintang/': 130
}

@retry(urllib2.URLError, tries=25, delay=3, backoff=2)
def urlopen_with_retry(url):
	try:
		hasil = urllib2.urlopen(url)
	except urllib2.HTTPError, e:
		raise
	else:
		return hasil

@retry(urllib2.URLError, tries=25, delay=3, backoff=2)
def read_retry(url):
	try:
		hasil = url.read()
	except urllib2.HTTPError, e:
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
		for halaman in range(1,listPage[hari]):
			urlIndex = hari + str(halaman)
			handle = urlopen_with_retry(urlIndex)
			html = read_retry(handle)
			soupIndex = bs(html, 'lxml')

			list_link = soupIndex.find_all("div", {"class":"textbox clearfix"})
			filetext = open("Corpus"+hari.rstrip().split('/')[-2]+".txt","a+")

			contentNovel = list_link[0].find_all("p")

			item = ""
			for x in contentNovel:
				item += x.text.encode('utf-8')
				item += " "

			__builtin__.totalKata += len(re.findall("[.?!] |[.?!]$",item))

			filetext.write(item)
			filetext.write('\n\n')

			__builtin__.totalWeb += 1

			filetext.close()

			print __builtin__.totalKata
		self.queue.task_done()

start = time.time()

def main():

	for i in range(len(listNovel)):
		t = CrawlingKompas(queue)
		t.setDaemon(True)
		t.start()

	for t in listNovel:
		queue.put(t)

	queue.join()

main()


# filetext.close()

# if totalKata >= 10**7:
# 	break

# print "Total kata saat ini : "+str(totalKata)

# print "Done"