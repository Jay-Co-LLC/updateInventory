from ftplib import FTP_TLS
import os
import csv
import requests
import json
from threading import Thread

headers = {}
headers['Authorization'] = os.environ['ordoro_auth']
headers['Content-Type'] = 'application/json'

def updateItems(items):
	for each in items:
		sku = each[0]
		amt = each[1]
		r = requests.put(f'https://api.ordoro.com/product/{sku}/warehouse/{os.environ["ordoro_warehouse_id"]}/', data=json.dumps({"on_hand" : amt}), headers=headers)
		print(r.content)
		
def main(event, context):
	
	### RETRIEVE FILE FROM TAW ###
	
	# Set up connection to FTP server
	ftps = FTP_TLS()
	ftps.connect('ftp.tapww.com', 22, timeout=120)
	ftps.set_debuglevel(1)
	ftps.set_pasv(True)
	ftps.login(os.environ['taw_user'], os.environ['taw_pass'])
	ftps.prot_p()
	
	# Create local file to store contents of Inventory file
	f = open('/tmp/inv.txt', 'wb')
	
	# Retrieve the Inventory file contents and store locally
	ftps.retrbinary('RETR Inventory.txt', f.write)
	
	# Close local file
	f.close()
	
	# Close the connection
	ftps.quit()
	### END RETRIEVE FILE FROM TAW ###
	
	
	### READ INVENTORY FILE ###
	item_list = []
	with open('/tmp/inv.txt', newline='') as items:
		reader = csv.reader(items, delimiter='\t')
		item_list = [[item[2][:3] + '-' + item[2][3:], item[12]] for item in reader if item[2][:3] in ['BIL', 'EXP', 'FOX', 'RAN']]
		
	print(f"Items found: {len(item_list)}")
		
	# Divide list into chunks for threading
	chunks = []
	for i in range(0, len(item_list), 200):
		chunks.append(item_list[i:i+200])
		
	print(f"Number of chunks: {len(chunks)}")
		
	### END READ INVENTORY FILE ###
	
	
	### UPDATE ORDORO ###
	
	threads = []
	for each in chunks:
		t = Thread(target=updateItems, args=(each,))
		threads.append(t)
		
	print("Starting threads...")
		
	for t in threads:
		t.start()
		
	for t in threads:
		t.join()

	### END UPDATE ORDORO ###