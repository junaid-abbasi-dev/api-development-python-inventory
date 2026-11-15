from flask import Flask, jsonify, request
import requests

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
    new_id = max((item["id"] for item in inventory), default=0) + 1
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

def _product_fields(product, barcode):
    return {
        "product_name": product.get("product_name"),
        "brands": product.get("brands"),
        "ingredients_text": product.get("ingredients_text"),
        "barcode": barcode
    }

def _get_json(url, params=None):
    # None means the external request failed. A dict means OpenFoodFacts responded.
    headers = {"User-Agent": "FlatironInventoryLab/1.0 (student project)"}
    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException:
        return None

def fetch_product_by_barcode(barcode):
    url = f"https://world.openfoodfacts.org/api/v2/product/{barcode}.json"
    data = _get_json(url)
    if data is None:
        return None, "OpenFoodFacts request failed"
    if data.get("status") != 1:
        return None, None
    return _product_fields(data["product"], barcode), None

def fetch_product_by_name(name):
    url = "https://world.openfoodfacts.org/cgi/search.pl"
    data = _get_json(url, params={
        "search_terms": name,
        "search_simple": 1,
        "action": "process",
        "json": 1,
        "page_size": 1
    })
    if data is None:
        return None, "OpenFoodFacts request failed"
    products = data.get("products") or []
    if not products:
        return None, None
    product = products[0]
    return _product_fields(product, product.get("code")), None

@app.route("/lookup", methods=["GET"])
def lookup_product():
    barcode = request.args.get("barcode")
    name = request.args.get("name")
    if barcode:
        product, error = fetch_product_by_barcode(barcode)
    elif name:
        product, error = fetch_product_by_name(name)
    else:
        return jsonify({"message": "Provide a barcode or a name"}), 400
    if error:
        return jsonify({"message": error}), 502
    if product is None:
        return jsonify({"message": "Product not found"}), 404
    return jsonify(product)

@app.route("/inventory/from-barcode", methods=["POST"])
def add_from_barcode():
    data = request.get_json()
    product, error = fetch_product_by_barcode(data.get("barcode"))
    if error:
        return jsonify({"message": error}), 502
    if product is None:
        return jsonify({"message": "Product not found"}), 404
    new_id = max((item["id"] for item in inventory), default=0) + 1
    new_item = {
        "id": new_id,
        "product_name": product["product_name"],
        "brands": product["brands"],
        "ingredients_text": product["ingredients_text"],
        "barcode": product["barcode"],
        "price": data.get("price", 0),
        "quantity": data.get("quantity", 0)
    }
    inventory.append(new_item)
    return jsonify(new_item), 201

if __name__ == "__main__":
    app.run(port=5555, debug=True)