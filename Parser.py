import gc
import time
from threading import Thread
from Bridesbay import Bridesbay


'''
def gc_cb(phase, info):
	if not info['collected'] and not info['uncollectable']:
		return
	print("{0}:\t{1[generation]}\t{1[collected]}\t{1[uncollectable]}".format(phase, info))
	print (gc.get_objects())	  

gc.callbacks.append(gc_cb)
	'''
h1={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0'}
h2={'User-Agent': 'Mozilla/5.0 (X11; CrOS x86_64 8172.45.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.64 Safari/537.36'}
headers = [h1, h2]

proxy=[]

proxy = () 		# множество
b = Bridesbay(20, 5, headers, proxy)
#b.AddGirl(,)
Thread(target=b.StartParse).start()
time.sleep(30)
b.StopParse()