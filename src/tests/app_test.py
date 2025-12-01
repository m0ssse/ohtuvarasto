"""Tests for the Flask web application."""
import unittest
from app import app, warehouses, clear_warehouses


class TestApp(unittest.TestCase):
    """Test cases for the Flask web application."""

    def setUp(self):
        """Set up test client and reset warehouses."""
        self.app = app.test_client()
        app.config["TESTING"] = True
        clear_warehouses()

    def test_index_page_loads(self):
        """Test that the index page loads successfully."""
        response = self.app.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Warehouse Management", response.data)

    def test_index_shows_no_warehouses_message(self):
        """Test that index shows message when no warehouses exist."""
        response = self.app.get("/")
        self.assertIn(b"No warehouses have been created yet", response.data)

    def test_create_page_loads(self):
        """Test that the create page loads successfully."""
        response = self.app.get("/create")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Create New Warehouse", response.data)

    def test_create_warehouse(self):
        """Test creating a new warehouse."""
        response = self.app.post("/create", data={
            "name": "Test Warehouse",
            "capacity": "100",
            "initial_balance": "50"
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Test Warehouse", response.data)
        self.assertIn("Test Warehouse", warehouses)
        self.assertAlmostEqual(warehouses["Test Warehouse"].tilavuus, 100)
        self.assertAlmostEqual(warehouses["Test Warehouse"].saldo, 50)

    def test_create_warehouse_without_name(self):
        """Test that creating warehouse without name shows error."""
        response = self.app.post("/create", data={
            "name": "",
            "capacity": "100",
            "initial_balance": "0"
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Name is required", response.data)

    def test_create_warehouse_duplicate_name(self):
        """Test that creating warehouse with duplicate name shows error."""
        self.app.post("/create", data={
            "name": "Duplicate",
            "capacity": "100",
            "initial_balance": "0"
        })
        response = self.app.post("/create", data={
            "name": "Duplicate",
            "capacity": "100",
            "initial_balance": "0"
        })
        self.assertIn(b"already exists", response.data)

    def test_create_warehouse_invalid_capacity(self):
        """Test that creating warehouse with invalid capacity shows error."""
        response = self.app.post("/create", data={
            "name": "Invalid",
            "capacity": "not a number",
            "initial_balance": "0"
        })
        self.assertIn(b"must be numbers", response.data)

    def test_view_warehouse(self):
        """Test viewing a warehouse."""
        self.app.post("/create", data={
            "name": "ViewTest",
            "capacity": "100",
            "initial_balance": "25"
        })
        response = self.app.get("/warehouse/ViewTest")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"ViewTest", response.data)
        self.assertIn(b"25", response.data)

    def test_view_nonexistent_warehouse_redirects(self):
        """Test that viewing nonexistent warehouse redirects to index."""
        response = self.app.get("/warehouse/NonExistent")
        self.assertEqual(response.status_code, 302)

    def test_modify_warehouse_page_loads(self):
        """Test that the modify page loads for existing warehouse."""
        self.app.post("/create", data={
            "name": "ModifyTest",
            "capacity": "100",
            "initial_balance": "0"
        })
        response = self.app.get("/warehouse/ModifyTest/modify")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Modify ModifyTest", response.data)

    def test_modify_warehouse_capacity(self):
        """Test modifying warehouse capacity."""
        self.app.post("/create", data={
            "name": "ModifyTest",
            "capacity": "100",
            "initial_balance": "50"
        })
        response = self.app.post("/warehouse/ModifyTest/modify", data={
            "capacity": "200"
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertAlmostEqual(warehouses["ModifyTest"].tilavuus, 200)
        self.assertAlmostEqual(warehouses["ModifyTest"].saldo, 50)

    def test_modify_warehouse_capacity_reduces_balance(self):
        """Test that reducing capacity reduces balance if needed."""
        self.app.post("/create", data={
            "name": "ReduceTest",
            "capacity": "100",
            "initial_balance": "80"
        })
        self.app.post("/warehouse/ReduceTest/modify", data={
            "capacity": "50"
        })
        self.assertAlmostEqual(warehouses["ReduceTest"].tilavuus, 50)
        self.assertAlmostEqual(warehouses["ReduceTest"].saldo, 50)

    def test_modify_warehouse_invalid_capacity(self):
        """Test that invalid capacity shows error."""
        self.app.post("/create", data={
            "name": "InvalidTest",
            "capacity": "100",
            "initial_balance": "0"
        })
        response = self.app.post("/warehouse/InvalidTest/modify", data={
            "capacity": "invalid"
        })
        self.assertIn(b"must be a number", response.data)

    def test_add_items_page_loads(self):
        """Test that the add items page loads."""
        self.app.post("/create", data={
            "name": "AddTest",
            "capacity": "100",
            "initial_balance": "0"
        })
        response = self.app.get("/warehouse/AddTest/add")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Add Items to AddTest", response.data)

    def test_add_items(self):
        """Test adding items to a warehouse."""
        self.app.post("/create", data={
            "name": "AddTest",
            "capacity": "100",
            "initial_balance": "10"
        })
        response = self.app.post("/warehouse/AddTest/add", data={
            "amount": "30"
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertAlmostEqual(warehouses["AddTest"].saldo, 40)

    def test_add_items_invalid_amount(self):
        """Test that invalid amount shows error."""
        self.app.post("/create", data={
            "name": "InvalidAdd",
            "capacity": "100",
            "initial_balance": "0"
        })
        response = self.app.post("/warehouse/InvalidAdd/add", data={
            "amount": "invalid"
        })
        self.assertIn(b"must be a number", response.data)

    def test_take_items_page_loads(self):
        """Test that the take items page loads."""
        self.app.post("/create", data={
            "name": "TakeTest",
            "capacity": "100",
            "initial_balance": "50"
        })
        response = self.app.get("/warehouse/TakeTest/take")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Take Items from TakeTest", response.data)

    def test_take_items(self):
        """Test taking items from a warehouse."""
        self.app.post("/create", data={
            "name": "TakeTest",
            "capacity": "100",
            "initial_balance": "50"
        })
        response = self.app.post("/warehouse/TakeTest/take", data={
            "amount": "20"
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Took 20", response.data)
        self.assertAlmostEqual(warehouses["TakeTest"].saldo, 30)

    def test_take_items_invalid_amount(self):
        """Test that invalid amount shows error."""
        self.app.post("/create", data={
            "name": "InvalidTake",
            "capacity": "100",
            "initial_balance": "50"
        })
        response = self.app.post("/warehouse/InvalidTake/take", data={
            "amount": "invalid"
        })
        self.assertIn(b"must be a number", response.data)

    def test_nonexistent_warehouse_modify_redirects(self):
        """Test that modifying nonexistent warehouse redirects."""
        response = self.app.get("/warehouse/NonExistent/modify")
        self.assertEqual(response.status_code, 302)

    def test_nonexistent_warehouse_add_redirects(self):
        """Test that add items for nonexistent warehouse redirects."""
        response = self.app.get("/warehouse/NonExistent/add")
        self.assertEqual(response.status_code, 302)

    def test_nonexistent_warehouse_take_redirects(self):
        """Test that take items for nonexistent warehouse redirects."""
        response = self.app.get("/warehouse/NonExistent/take")
        self.assertEqual(response.status_code, 302)

    def test_index_displays_created_warehouses(self):
        """Test that created warehouses are displayed on index."""
        self.app.post("/create", data={
            "name": "First",
            "capacity": "100",
            "initial_balance": "10"
        })
        self.app.post("/create", data={
            "name": "Second",
            "capacity": "200",
            "initial_balance": "50"
        })
        response = self.app.get("/")
        self.assertIn(b"First", response.data)
        self.assertIn(b"Second", response.data)

    def test_search_page_loads(self):
        """Test that the search page loads successfully."""
        response = self.app.get("/search")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Search Results", response.data)

    def test_search_with_empty_query(self):
        """Test search with empty query shows appropriate message."""
        response = self.app.get("/search?q=")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Please enter a search term", response.data)

    def test_search_finds_matching_warehouses(self):
        """Test that search finds warehouses containing the search string."""
        self.app.post("/create", data={
            "name": "Main Warehouse",
            "capacity": "100",
            "initial_balance": "50"
        })
        self.app.post("/create", data={
            "name": "Secondary Storage",
            "capacity": "200",
            "initial_balance": "30"
        })
        response = self.app.get("/search?q=Warehouse")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Main Warehouse", response.data)
        self.assertNotIn(b"Secondary Storage", response.data)

    def test_search_is_case_insensitive(self):
        """Test that search is case insensitive."""
        self.app.post("/create", data={
            "name": "Big Warehouse",
            "capacity": "100",
            "initial_balance": "0"
        })
        response = self.app.get("/search?q=warehouse")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Big Warehouse", response.data)

    def test_search_no_results(self):
        """Test search with no matching results."""
        self.app.post("/create", data={
            "name": "Test Storage",
            "capacity": "100",
            "initial_balance": "0"
        })
        response = self.app.get("/search?q=nonexistent")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"No warehouses found", response.data)

    def test_search_results_show_warehouse_details(self):
        """Test that search results display warehouse details like front page."""
        self.app.post("/create", data={
            "name": "Detail Warehouse",
            "capacity": "100",
            "initial_balance": "25"
        })
        response = self.app.get("/search?q=Detail")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Detail Warehouse", response.data)
        self.assertIn(b"Balance", response.data)
        self.assertIn(b"Capacity", response.data)
        self.assertIn(b"Available Space", response.data)
        self.assertIn(b"View Details", response.data)

    def test_search_partial_match(self):
        """Test that search finds partial matches."""
        self.app.post("/create", data={
            "name": "Warehouse Alpha",
            "capacity": "100",
            "initial_balance": "0"
        })
        self.app.post("/create", data={
            "name": "Warehouse Beta",
            "capacity": "100",
            "initial_balance": "0"
        })
        response = self.app.get("/search?q=house")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Warehouse Alpha", response.data)
        self.assertIn(b"Warehouse Beta", response.data)
