def lambda_handler(event, context):


    response = {
  "isBase64Encoded" : "false",
  "statusCode": "200",
  "headers": { "Content-Type": "text/xml" },
  "body": """ 
        <Response>
            <Receive action="/prod/inboundfax"/>
        </Response>
          """
   }
    return response

