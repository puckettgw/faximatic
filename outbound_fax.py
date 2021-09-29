import os
import json
import base64
import urllib
import boto3
import uuid
from requests_toolbelt.multipart import decoder
from requests import Request, Session
import requests
from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import ClientError
import re



from twilio.rest import Client

def read_table_item(table_name, pk_name, pk_value):
    """
    Return item read by primary key.
    """
    dynamodb_resource = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb_resource.Table(table_name)
    response = table.get_item(Key={pk_name: pk_value})

    return response

def print_function(word):
    return word

def process_fax(fax_target,pdf_data,txn_uuid):
    print("Faxing PDF to " + fax_target)
    s3 = boto3.resource("s3")
    s3.Bucket("faxtests").put_object(Key=txn_uuid+".pdf", Body=pdf_data)
    s3c = boto3.client('s3')
    url = s3c.generate_presigned_url(
        ClientMethod='get_object',
        Params={
            'Bucket': 'faxtests',
            'Key': txn_uuid + '.pdf'
        }
    )

    print(url)
    account_sid=os.environ["TWILIO_ACC_SID"]
    auth_token=os.environ["TWILIO_AUTH_TOKEN"]
    client = Client(account_sid, auth_token)

    stripped = re.sub("[^0-9]", "", fax_target)

    fax = client.fax.faxes \
        .create(
             from_='+17207101078',
             to="+"+stripped,
             media_url=url
         )

    print(fax.sid)
    
def check_auth(fromaddr, faxnumber):
    fromaddr_morph = re.search('<(.*)>', fromaddr)
    if fromaddr_morph:
        found = fromaddr_morph.group(1)
    else:
        return False
    print("Fromaddr")
    faxnumber_plus = "+" + faxnumber
    print(found)
    dynamocheck = read_table_item("senders", "emailaddress", found)
    if 'Item' in dynamocheck:
        #if dynamocheck['Item']['faxnumber'] == faxnumber_plus:
        return True
        #else: return False
    else:
        return False
    

def lambda_handler(event, context):
    fax_target = event["queryStringParameters"]['faxtgt']
    print('Function Executing')


    string = event['body']
    encoded_string = string.encode("utf-8")

    req = Request('POST', 'https://8mehskfwze.execute-api.us-east-1.amazonaws.com/prod/outboundfax', data=event['body'], headers=event['headers'])
    prepped = req.prepare()
    
    print(prepped.headers)
    mpdecoder = decoder.MultipartDecoder(base64.b64decode(prepped.body),str(prepped.headers['Content-Type']))
    for part in mpdecoder.parts:
        print(part.headers)
        headers = dict((k.decode('utf-8'), v.decode('utf-8')) for k, v in part.headers.items())
        if 'Content-Disposition' in headers:
            if headers['Content-Disposition'] == 'form-data; name="From"':
                fromaddr = part.content
                if check_auth(fromaddr,fax_target) == False:
                    response = {
                  "isBase64Encoded" : "false",
                  "statusCode": "200",
                  "headers": {  },
                  "body": "Unauthorized sending address" 
                  }
                    return response
                   
        if 'Content-Type' in headers:
            content_type = headers['Content-Type'] 
            if content_type == "application/pdf":
                txn_uuid = str(uuid.uuid4())
                process_fax(fax_target,part.content,txn_uuid) 
            else:
                print("Not a PDF: " + content_type)
        
                
            

    response = {
  "isBase64Encoded" : "false",
  "statusCode": "200",
  "headers": {  },
  "body": "Success" 
   }
    return response

