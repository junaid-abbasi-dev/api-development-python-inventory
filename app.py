from flask import Flask, jsonify, request

app = Flask(__name__)

inventory = [
    {
        "id": 1,
        "product_name": "Organic Almond Milk",
        "brands": "Silk",
        "ingredients_text": "Filtered water, almonds, cane sugar",
        "barcode": "025293001234",
        "price": 3.99,
        "quantity": 12
    },
    {
        "id": 2,
        "product_name": "Peanut Butter",
        "brands": "Jif",
        "ingredients_text": "Roasted peanuts, sugar, salt",
        "barcode": "051500255161",
        "price": 4.49,
        "quantity": 8
    },
    {
        "id": 3,
        "product_name": "Whole Wheat Bread",
        "brands": "Nature's Own",
        "ingredients_text": "Whole wheat flour, water, yeast, salt",
        "barcode": "072250037015",
        "price": 2.79,
        "quantity": 20
    }
]
# GET inventory and return status code 200
@app.route("/inventory", methods=["GET"])
def get_products():
    return jsonify(inventory)

# return by id and handle invalid id
@app.route("/inventory/<int:id>")
def get_product_by_id(id):
    for product in inventory:
        if product["id"] == id:
            return jsonify(product), 200
    return jsonify({"message": "Product not found"}), 404

# POST products in inventory
@app.route("/inventory", methods=["POST"])
def create_products():
    data = request.get_json()
    new_id = max(item["id"] for item in inventory) + 1
    new_item = {
        "id": new_id,
        "product_name": data["product_name"],
        "brands": data["brands"],
        "ingredients_text": data["ingredients_text"],
        "barcode": data["barcode"],
        "price": data["price"],
        "quantity": data["quantity"]
    }
    inventory.append(new_item)
    return jsonify(new_item), 201

@app.route("/inventory/<int:id>", methods=["PATCH"])
def update_products(id):
    data = request.get_json()
    for product in inventory:
        if product["id"] == id:
            if "price" in data:
                product["price"] = data["price"]
            if "quantity" in data:
                product["quantity"] = data["quantity"]
            return jsonify(product)
    return jsonify({"message": "Product not found"}), 404

@app.route("/inventory/<int:id>", methods=["DELETE"])
def delete_product(id):
    for product in inventory:
        if product["id"] == id:
            inventory.remove(product)
            return "", 204
    return jsonify({"message": "Product not found"}), 404

if __name__ == "__main__":
    app.run(port=5555, debug=True)