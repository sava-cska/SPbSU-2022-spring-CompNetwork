from flask import Flask, jsonify, abort, request
import uuid

class Item(object):
    def __init__(self, name, description, picture_file):
        self.id = str(uuid.uuid4())
        self.name = name
        self.description = description
        self.picture_file = picture_file

    def toJSON(self):
        return self.__dict__

shop_list = [Item('Ball', 'Round', 'product_images/ball.jpg'), 
             Item('Table', 'Big', 'product_images/table.jpg')]

def list_to_JSON(shop_list):
    return [item.toJSON() for item in shop_list]

app = Flask(__name__)

@app.route('/shop', methods=['GET'])
def get_list_item():
    return jsonify({'shop_list': list_to_JSON(shop_list)}), 200

@app.route('/shop/<string:item_id>', methods=['GET'])
def get_item(item_id):
    for item in shop_list:
        if item.id == item_id:
            return jsonify({'item': item.toJSON()}), 200
    abort(404)

@app.route('/shop', methods=['POST'])
def add_item():
    request_data = request.form
    image = request.files
    if request_data is None or 'name' not in request_data or 'description' not in request_data \
    or image is None or 'picture' not in image:
        abort(400)
    new_item = Item(request_data['name'], request_data['description'], image['picture'].filename)
    new_item.picture_file = 'product_images/' + new_item.id + '__' + new_item.picture_file
    image['picture'].save(new_item.picture_file)
    shop_list.append(new_item)
    return jsonify({'shop_list': list_to_JSON(shop_list)}), 201

@app.route('/shop/<string:item_id>', methods=['PUT'])
def update_item(item_id):
    request_data = request.form
    image = request.files
    if request_data is None:
        abort(400)
    for item in shop_list:
        if item.id == item_id:
            if 'name' in request_data:
                item.name = request_data['name']
            if 'description' in request_data:
                item.description = request_data['description']
            if image is not None and 'picture' in image:
                item.picture_file = 'product_images/' + item.id + '__' + image['picture'].filename
                image['picture'].save(item.picture_file)
            return jsonify({'item': item.toJSON()}), 200
    abort(400)

@app.route('/shop/<string:item_id>', methods=['DELETE'])
def delete_item(item_id):
    for item in shop_list:
        if item.id == item_id:
            shop_list.remove(item)
            return jsonify({'shop_list': list_to_JSON(shop_list)}), 200
    abort(400)

app.run(debug=True)