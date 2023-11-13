def handler(event, content):
    print(event)
    return{
        'statusCode': 200,
        'body': 'Success!'
    }