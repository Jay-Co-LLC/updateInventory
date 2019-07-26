from ftplib import FTP_TLS
import os
import csv
import requests
import json

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
	chunk = event['chunk']
	chunkNum = event['chunkNum']
	
	print(f"Processing chunk {chunkNum}...")
	updateItems(chunk)