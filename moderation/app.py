from flask import Flask, request
from flask_restful import Resource, Api
import requests
import os

app = Flask(__name__)
api = Api(app)

class Events(Resource):
    def post(self):
        req_data = request.get_json(force=True)  # Add force=True to ensure parsing JSON data even if the client doesn't set the Content-Type header
        type = req_data['type']
        data = req_data['data']

        API_KEY = os.getenv("API_KEY")


        if type == 'CommentCreated':
            text = data['content']
            api_key = 'X-Api-Key'
            headers = {api_key: API_KEY}

            try:
                response = requests.get(f'https://api.api-ninjas.com/v1/profanityfilter?text={text}', headers=headers)
                content = response.json()['censored']
            except Exception as err:
                print(err)

            try:
                requests.post('http://event-bus-srv:4005/events', json={
                    'type': 'CommentModerated',
                    'data': {
                        'id': data['id'],
                        'postId': data['postId'],
                        'status': 'approved',
                        'content': content
                    }
                })
            except Exception as err:
                print(err)

        return {}, 200

api.add_resource(Events, '/events')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4003, debug=False)
