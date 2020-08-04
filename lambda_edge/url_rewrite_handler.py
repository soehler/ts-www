import json
import re

def lambda_handler(event,context):
    
    request = event['Records'][0]['cf']['request']

    # Function to handle URL rewriting in cloudfront
    # HUGO server does URL rewiting to default object (CloudFront does not), 
    #             i.e. rewrites /posts/ to /posts/index.html 

    if request.uri.length() > 0 and request.uri.endswith("/"):
        request.uri+= "index.html"
    elif not not re.search("[.](css|md|gif|ico|jpg|jpeg|js|png|txt|svg|woff|ttf|map|json|html|htm)$", request.uri):
        request.uri+= "/index.html"
    
    return request    
