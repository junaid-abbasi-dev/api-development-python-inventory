# Inventory API

A small Flask inventory API for a retail store. Employees can list, add, update, and delete products. The API can also look up a real product on [OpenFoodFacts](https://world.openfoodfacts.org/) by barcode or name and store it in the inventory list.

Inventory is kept in a Python list in `app.py`. Restarting the server clears any products you added.

## Setup

Python 3.8 or newer is required.

```bash
python3 -m pip install -r requirements.txt
```

Start the API:

```bash
python3 app.py
```

The server runs at `http://127.0.0.1:5555`.

In a second terminal, start the menu:

```bash
python3 cli.py
```

Run the tests:

```bash
python3 -m pytest
```

## API

| Method | Path | What it does |
|---|---|---|
| GET | `/inventory` | Return every item |
| GET | `/inventory/<id>` | Return one item, or 404 |
| POST | `/inventory` | Add an item. The server assigns the id. Returns 201 |
| PATCH | `/inventory/<id>` | Change `price`, `quantity`, or both. Returns 404 if the id is missing |
| DELETE | `/inventory/<id>` | Remove an item. Returns 204, or 404 |
| GET | `/lookup?barcode=` | Fetch a product from OpenFoodFacts by barcode |
| GET | `/lookup?name=` | Fetch the first OpenFoodFacts match for a name |
| POST | `/inventory/from-barcode` | Look up a barcode and store it with your `price` and `quantity` |

A stored item looks like this:

```json
{
  "id": 1,
  "product_name": "Organic Almond Milk",
  "brands": "Silk",
  "ingredients_text": "Filtered water, almonds, cane sugar",
  "barcode": "025293001234",
  "price": 3.99,
  "quantity": 12
}
```

Add an item:

```bash
curl -X POST http://127.0.0.1:5555/inventory \
  -H "Content-Type: application/json" \
  -d '{"product_name":"Orange Juice","brands":"Tropicana","ingredients_text":"Oranges","barcode":"048500012345","price":3.29,"quantity":15}'
```

Change a price:

```bash
curl -X PATCH http://127.0.0.1:5555/inventory/1 \
  -H "Content-Type: application/json" \
  -d '{"price": 5.25}'
```

Look up a barcode without saving it:

```bash
curl "http://127.0.0.1:5555/lookup?barcode=3017620422003"
```

Save that product in the inventory:

```bash
curl -X POST http://127.0.0.1:5555/inventory/from-barcode \
  -H "Content-Type: application/json" \
  -d '{"barcode":"3017620422003","price":4.99,"quantity":6}'
```

Search by name:

```bash
curl "http://127.0.0.1:5555/lookup?name=nutella"
```

If OpenFoodFacts cannot be reached, lookup routes return `502`. An unknown barcode or name returns `404`.

## CLI

`cli.py` sends requests to the running API. Leave `python3 app.py` running while you use it.

```text
1. List inventory
2. View one item
3. Add an item
4. Update price or quantity
5. Delete an item
6. Find a product on OpenFoodFacts
7. Find a product and add it to inventory
8. Quit
```

Option 4 leaves a field unchanged when you press Enter on it. Option 6 asks for a barcode, and a blank barcode lets you search by name. Option 7 asks for a barcode, a price, and a quantity, then stores the OpenFoodFacts result.

Example: list the inventory, then quit.

```text
Choose an option: 1
1: Organic Almond Milk - $3.99 (12 in stock)
2: Peanut Butter - $4.49 (8 in stock)
3: Whole Wheat Bread - $2.79 (20 in stock)
Choose an option: 8
```
