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
from flask import request
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
    @app.route('/inboundfax', methods=['GET','POST'])
    def process_fax(request):
        print("Function Executing")
        if request.method == 'GET':
            print ("GET request")
        if request.method == 'POST':
            print ("POST request")

#    print("Event Passed to Handler: " + json.dumps(event))
#    emailbody = json.loads(event['body'])
#    print(emailbody.keys())
#
    app.logger.info(request)
#    print(event['body'])
    
    fax_url = "http://nothing.net/?"+event['body']
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



    response = {
  "isBase64Encoded" : "false",
  "statusCode": "200",
  "headers": {  },
  "body": json.dumps(event)
}
    return response

