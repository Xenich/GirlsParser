import Bridesbay
import gc
import time
from threading import Thread

'''
def gc_cb(phase, info):
	if not info['collected'] and not info['uncollectable']:
		return
	print("{0}:\t{1[generation]}\t{1[collected]}\t{1[uncollectable]}".format(phase, info))
	print (gc.get_objects())	  

gc.callbacks.append(gc_cb)
	'''
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0'}
b = Bridesbay.Bridesbay(20, 5, headers)
Thread(target=b.StartParse).start()
time.sleep(30)
b.StopParse()