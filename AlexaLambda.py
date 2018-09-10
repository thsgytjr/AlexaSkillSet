import boto3

access_key = "AKIAJUNVKY76Z6S4QZ5A"
access_secret = "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"
region = "us-east-1"
queue_url = "https://sqs.us-east-1.amazonaws.com/858717887305/AlexaScripts"

def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {
            'type': 'Simple',
            'title': "SessionSpeechlet - " + title,
            'content': "SessionSpeechlet - " + output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }

def build_response(session_attributes, speechlet_response):
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }

def post_message(client, message_body, url):
    print("Posting message")
    response = client.send_message(QueueUrl = url, MessageBody= message_body)
    
def lambda_handler(event, context):
    client = boto3.client('sqs', aws_access_key_id = access_key, aws_secret_access_key = access_secret, region_name = region)
    intent_name = event['request']['intent']['name']
    if intent_name == "EnterpriseDashboardOn":
        post_message(client, 'EnterpriseDashboardOn', queue_url)
        message = "Turning on Enterprise Dashboard Service"
    elif intent_name == "PortalOn":
        post_message(client, 'PortalOn', queue_url)
        message = "Turning on Portal Service"
    elif intent_name == "EnterpriseDashboardOff":
        post_message(client, 'EnterpriseDashboardOff', queue_url)
        message = "Turning off Enterprise Dashboard Service"
    else:
        message = "I was not able to start requested service"
        
    speechlet = build_speechlet_response("Service Status", message, "", "true")
    return build_response({}, speechlet)