"""Flask web application for warehouse management."""
from flask import Flask, render_template, request, redirect, url_for
from varasto import Varasto


app = Flask(__name__)

# In-memory storage for warehouses
# key: warehouse name, value: Varasto instance
warehouses = {}


def clear_warehouses():
    """Clear all warehouses. Used for testing."""
    warehouses.clear()


def _parse_floats(capacity_str, balance_str):
    """Parse capacity and balance strings to floats."""
    return float(capacity_str), float(balance_str)


def _validate_create_input(name, capacity_str, balance_str):
    """Validate create warehouse input. Returns error message or None."""
    try:
        _parse_floats(capacity_str, balance_str)
    except ValueError:
        return "Capacity and initial balance must be numbers"
    if not name:
        return "Name is required"
    if name in warehouses:
        return "A warehouse with this name already exists"
    return None


@app.route("/")
def index():
    """Display the main page with list of all warehouses."""
    return render_template("index.html", warehouses=warehouses)


@app.route("/create", methods=["GET", "POST"])
def create_warehouse():
    """Create a new warehouse."""
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        capacity_str = request.form.get("capacity", "0")
        balance_str = request.form.get("initial_balance", "0")

        error = _validate_create_input(name, capacity_str, balance_str)
        if error:
            return render_template("create.html", error=error)

        capacity, initial_balance = _parse_floats(capacity_str, balance_str)
        warehouses[name] = Varasto(capacity, initial_balance)
        return redirect(url_for("index"))

    return render_template("create.html")


@app.route("/warehouse/<name>")
def view_warehouse(name):
    """Display details of a specific warehouse."""
    if name not in warehouses:
        return redirect(url_for("index"))
    return render_template("view.html", name=name, warehouse=warehouses[name])


def _update_warehouse_capacity(warehouse, new_capacity):
    """Update warehouse capacity using the Varasto class method."""
    warehouse.aseta_tilavuus(new_capacity)


@app.route("/warehouse/<name>/modify", methods=["GET", "POST"])
def modify_warehouse(name):
    """Modify an existing warehouse's capacity."""
    if name not in warehouses:
        return redirect(url_for("index"))

    warehouse = warehouses[name]

    if request.method == "POST":
        try:
            new_capacity = float(request.form.get("capacity", "0"))
        except ValueError:
            return render_template(
                "modify.html", name=name, warehouse=warehouse,
                error="Capacity must be a number"
            )
        _update_warehouse_capacity(warehouse, new_capacity)
        return redirect(url_for("view_warehouse", name=name))

    return render_template("modify.html", name=name, warehouse=warehouse)


@app.route("/warehouse/<name>/add", methods=["GET", "POST"])
def add_items(name):
    """Add items to a warehouse."""
    if name not in warehouses:
        return redirect(url_for("index"))

    warehouse = warehouses[name]

    if request.method == "POST":
        try:
            amount = float(request.form.get("amount", "0"))
        except ValueError:
            return render_template(
                "add.html", name=name, warehouse=warehouse,
                error="Amount must be a number"
            )
        warehouse.lisaa_varastoon(amount)
        return redirect(url_for("view_warehouse", name=name))

    return render_template("add.html", name=name, warehouse=warehouse)


@app.route("/warehouse/<name>/take", methods=["GET", "POST"])
def take_items(name):
    """Take items from a warehouse."""
    if name not in warehouses:
        return redirect(url_for("index"))

    warehouse = warehouses[name]

    if request.method == "POST":
        try:
            amount = float(request.form.get("amount", "0"))
        except ValueError:
            return render_template(
                "take.html", name=name, warehouse=warehouse,
                error="Amount must be a number"
            )
        taken = warehouse.ota_varastosta(amount)
        return render_template(
            "take.html", name=name, warehouse=warehouse,
            message=f"Took {taken} items from the warehouse"
        )

    return render_template("take.html", name=name, warehouse=warehouse)


if __name__ == "__main__":
    app.run()
