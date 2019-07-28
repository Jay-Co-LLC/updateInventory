from ftplib import FTP_TLS
import os
import csv
import requests
import json
import boto3

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
	id = event['id']
	chunk = event['chunk']
	chunkNum = event['chunkNum']
	
	print(f"Processing chunk {chunkNum}...")
	updateItems(chunk)
	
	# When finished, send completion message to queue
	q = boto3.resource('sqs').get_queue_by_name(QueueName='q-updateInventory-TAW')
	q.send_message(MessageBody=f"{id}-{chunkNum}")