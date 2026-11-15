import requests

BASE_URL = "http://127.0.0.1:5555"


def print_item(item):
    print(f"{item['id']}: {item['product_name']} ({item['brands']})")
    print(f"  Barcode: {item['barcode']}")
    print(f"  Price: ${item['price']}  Quantity: {item['quantity']}")
    print(f"  Ingredients: {item['ingredients_text']}")


def request_failed(response):
    try:
        message = response.json().get("message", "Request failed")
    except ValueError:
        message = "Request failed"
    print(f"{response.status_code}: {message}")


def list_inventory():
    response = requests.get(f"{BASE_URL}/inventory")
    if response.status_code != 200:
        request_failed(response)
        return
    items = response.json()
    if not items:
        print("Inventory is empty.")
        return
    for item in items:
        print(f"{item['id']}: {item['product_name']} - ${item['price']} ({item['quantity']} in stock)")


def view_item():
    item_id = input("Item id: ")
    response = requests.get(f"{BASE_URL}/inventory/{item_id}")
    if response.status_code != 200:
        request_failed(response)
        return
    print_item(response.json())


def add_item():
    payload = {
        "product_name": input("Product name: "),
        "brands": input("Brand: "),
        "ingredients_text": input("Ingredients: "),
        "barcode": input("Barcode: "),
    }
    try:
        payload["price"] = float(input("Price: "))
        payload["quantity"] = int(input("Quantity: "))
    except ValueError:
        print("Price must be a number and quantity must be a whole number.")
        return
    response = requests.post(f"{BASE_URL}/inventory", json=payload)
    if response.status_code != 201:
        request_failed(response)
        return
    item = response.json()
    print(f"Added {item['product_name']} as id {item['id']}")


def update_item():
    item_id = input("Item id: ")
    print("Leave a field blank to keep its current value.")
    price_text = input("New price: ")
    quantity_text = input("New quantity: ")
    payload = {}
    try:
        if price_text.strip():
            payload["price"] = float(price_text)
        if quantity_text.strip():
            payload["quantity"] = int(quantity_text)
    except ValueError:
        print("Price must be a number and quantity must be a whole number.")
        return
    if not payload:
        print("Nothing to update.")
        return
    response = requests.patch(f"{BASE_URL}/inventory/{item_id}", json=payload)
    if response.status_code != 200:
        request_failed(response)
        return
    item = response.json()
    print(f"Updated {item['product_name']}: ${item['price']}, {item['quantity']} in stock")


def delete_item():
    item_id = input("Item id to delete: ")
    response = requests.delete(f"{BASE_URL}/inventory/{item_id}")
    if response.status_code == 204:
        print(f"Deleted item {item_id}")
        return
    request_failed(response)


def find_on_api():
    barcode = input("Barcode: ").strip()
    if not barcode:
        print("Enter a barcode.")
        return
    response = requests.get(f"{BASE_URL}/lookup", params={"barcode": barcode})
    if response.status_code != 200:
        request_failed(response)
        return
    product = response.json()
    print(f"{product['product_name']} ({product['brands']})")
    print(f"  Barcode: {product['barcode']}")
    print(f"  Ingredients: {product['ingredients_text']}")


def add_from_barcode():
    barcode = input("Barcode: ").strip()
    if not barcode:
        print("Enter a barcode.")
        return
    try:
        price = float(input("Price: "))
        quantity = int(input("Quantity: "))
    except ValueError:
        print("Price must be a number and quantity must be a whole number.")
        return
    response = requests.post(
        f"{BASE_URL}/inventory/from-barcode",
        json={"barcode": barcode, "price": price, "quantity": quantity},
    )
    if response.status_code != 201:
        request_failed(response)
        return
    item = response.json()
    print(f"Added {item['product_name']} as id {item['id']}")


def main():
    actions = {
        "1": list_inventory,
        "2": view_item,
        "3": add_item,
        "4": update_item,
        "5": delete_item,
        "6": find_on_api,
        "7": add_from_barcode,
    }
    while True:
        print("\n1. List inventory")
        print("2. View one item")
        print("3. Add an item")
        print("4. Update price or quantity")
        print("5. Delete an item")
        print("6. Find a product on OpenFoodFacts")
        print("7. Find a product and add it to inventory")
        print("8. Quit")
        choice = input("Choose an option: ").strip()
        if choice == "8":
            break
        action = actions.get(choice)
        if action is None:
            print("Choose a number from 1 to 8.")
            continue
        try:
            action()
        except requests.RequestException:
            print("Could not reach the API. Start the server with: python3 app.py")


if __name__ == "__main__":
    main()
