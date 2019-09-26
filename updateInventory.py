from ftplib import FTP_TLS
import os
import csv
import requests
import json
import boto3

headers = {}
headers['Authorization'] = os.environ['ordoro_auth']
headers['Content-Type'] = 'application/json'

url = "https://api.ordoro.com"
warehouse_id = os.environ["ordoro_warehouse_id"]

def updateItems(items):
	for each in items:
		supplier_sku = each[0]
		amt = each[1]
		params = {"search" : supplier_sku}
		
		# Get ordoro sku by searching via supplier_sku
		r = requests.get(f'{url}/product/', params=params, headers=headers)
		rob = r.json()
		
		if (rob['count'] == 0):
			print(f"{rob['count']} found with Supplier SKU {supplier_sku}")
			continue
		
		product = rob['product'][0]
		ordoro_sku = product['sku']
		
		# Update the product in ordoro
		r = requests.put(f'{url}/product/{ordoro_sku}/warehouse/{warehouse_id}/', data=json.dumps({"on_hand" : amt}), headers=headers)
		rob = r.json()
		
		if (r.status_code == 200):
			print(f"{rob['sku']} on-hand amount updated to {amt}.")
		else:
			print(f"{rob['error_message']}")
		
def main(event, context):
	id = event['id']
	chunk = event['chunk']
	chunkNum = event['chunkNum']
	
	print(f"Processing chunk {chunkNum}...")
	updateItems(chunk)
	
	# When finished, send completion message to queue
	q = boto3.resource('sqs').get_queue_by_name(QueueName='q-updateInventory-TAW')
	q.send_message(MessageBody=f"{id}-{chunkNum}")