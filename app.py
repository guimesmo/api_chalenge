from flask import Flask
from flask import request
from flask import jsonify

from serializers import UserSerializer, ValidationError
from models import db
from models import User

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'

with app.app_context():
    db.init_app(app)


@app.route('/api/user', methods=['GET', 'POST'])
@app.route('/api/user/<username>', methods=['PUT', 'DELETE'])
def user_actions(username=None):

    if request.method == "GET":
        users_list = User.query.all()
        output = [UserSerializer(instance=user).as_dict() for user in users_list]
        return jsonify(output)

    if request.method == "POST":
        if username:
            response = {
                "error": 1,
                "message": "POST is allowed only for new registers"
            }
            return jsonify(response), 400

        serializer = UserSerializer(data=request.json)
        try:
            serializer.validate(request.json)
        except ValidationError as e:
            response = jsonify({
                "error": 1,
                "message": str(e)
            })
            status_code = 400
        else:
            instance = serializer.create()
            response = UserSerializer(instance=instance).serialize()
            status_code = 200
        return response, status_code

    # Not GET or POST. Username is required
    if not username:
        return jsonify({
                   "error": 1,
                   "message": "The username is required"
               }), 400

    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({
            'error': 1,
            'message': "User not found"
        }), 404

    if request.method == "PUT":
        serializer = UserSerializer(instance=user, data=request.json)
        if serializer.validate(request.json):
            user = serializer.update()
            return UserSerializer(instance=user).serialize(), 200

    if request.method == "DELETE":
        db.session.delete(user)
        db.session.commit()
        return jsonify({
            'error': 0
        }), 200

    else:
        return "INVALID METHOD", 400


if __name__ == '__main__':
    app.run()
