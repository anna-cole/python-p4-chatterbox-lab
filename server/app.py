from flask import Flask, request, make_response, jsonify
from flask_cors import CORS
from flask_migrate import Migrate
from models import db, Message

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

CORS(app)
migrate = Migrate(app, db)

db.init_app(app)

@app.route('/')
def home():
    return '<h1>Chatterbox GET-POST-PATCH-DELETE API</h1>'

@app.route('/messages', methods=['GET', 'POST'])
def messages():
    if request.method == 'GET':
        messages = [message.to_dict() for message in Message.query.order_by('created_at').all()]
        return make_response(messages, 200)
    
    elif request.method == 'POST':
        # breakpoint()
        # The below will capture input data from the client (frontend) request.form or request.get_json() and will create a new object (instance) with it. Then it will add it to the database. Then it will convert the object to dictionary and send as a response to the client. When it is sent, it is automatically converted to json. So, get data as json, convert to obj, add to db then convert back to json and send it to client.  
        new_message = Message( 
            body = request.get_json().get("body"), # retrieve the input data as a dictionary
            username = request.get_json().get("username")
        ) 
        db.session.add(new_message)
        db.session.commit()
        message_serialized = new_message.to_dict() 
        return make_response(message_serialized, 201)

@app.route('/messages/<int:id>', methods=['GET', 'PATCH', 'DELETE'])
def messages_by_id(id):
    message = Message.query.filter_by(id=id).first()

    if message == None:
        message_body = {"message": "This record does not exist in our database. Please try again."}
        return make_response(message_body, 404)
    
    elif request.method == 'GET':
        message_dict = message.to_dict()
        return make_response(message_dict, 200)
    
    elif request.method == 'DELETE':
        db.session.delete(message)
        db.session.commit()
        response_body = {"delete_successful": True, "message": "Message deleted."}
        return make_response(response_body, 200)
    
    elif request.method == 'PATCH':
        for attr in request.get_json():
            setattr(message, attr, request.get_json().get(attr))
        db.session.add(message)
        db.session.commit()
        message_serialized = message.to_dict() 
        return make_response(message_serialized, 200)

if __name__ == '__main__':
    app.run(port=5555)
