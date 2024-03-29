import os
import json
import base64
import urllib
from urllib.parse import urlparse
from urllib.parse import parse_qs
import requests
import boto3
from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import ClientError
from flask import Flask, redirect, url_for, current_app
from flask import request as r
from flask import Response as R
app = Flask(__name__)
def read_table_item(table_name, pk_name, pk_value):
    """
    Return item read by primary key.
    """
    dynamodb_resource = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb_resource.Table(table_name)
    response = table.get_item(Key={pk_name: pk_value})
    return response

def main():
    app.logger.info(r)
    app.logger.info("Function Executing")
    if r.method == 'GET':
        app.logger.info("GET request")
        return R(status=200)
    if r.method == 'POST':
        app.logger.info("POST request")
        fax_url = "http://nothing.net/?"+r.data
        parsed = urlparse(fax_url)
        qs = parse_qs(parsed.query)
        
        
        media_url = (qs['MediaUrl'])
        #print(media_url)
        #print(qs)
        print("Media URL: " + media_url[0])

        mailgun_api_key = os.environ['MAILGUN_API_KEY']
        sandbox = 'YOUR SANDBOX URL HERE'
        #recipient = os.environ['FAX_RECIPIENT']



        recipientfax = qs['To'][0]
        print("Faxnumber " + recipientfax)
        recipient=read_table_item('recipients', 'faxnumber', recipientfax)
        
        #print(recipient['Item']['emails'])



        #request_url = 'https://api.mailgun.net/v2/{0}/messages'.format(sandbox)
        request_url = 'https://api.mailgun.net/v2/out.faximatic.com/messages'
        request = requests.post(request_url, auth=('api', mailgun_api_key), data={
            'from': 'fax@in.faximatic.com',
            'to': recipient['Item']['emails'],
            'subject': 'New fax from '+qs['From'][0],
            'text': 'You have a new fax from '+qs['From'][0]+'. The PDF version of the fax is attached.'
        },
        files=[("attachment", ("fax.pdf", requests.get(media_url[0]).content))])

        print('Status: {0}'.format(request.status_code))
        print('Body:   {0}'.format(request.text))
        return R(status=200)
 

