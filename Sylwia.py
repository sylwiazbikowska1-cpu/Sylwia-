streamlit
supabase import json
from typing import List, Optional
from pydantic import BaseModel, Field

# 1. Define Pydantic models for Category and Product
# These models help define the structure and can be easily serialized/deserialized.
# Pydantic is excellent for data validation and schema definition.
class Product(BaseModel):
    id: int = Field(..., description="Unique identifier for the product")
    name: str = Field(..., description="Name of the product")
    description: Optional[str] = Field(None, description="Optional description of the product")
    price: float = Field(..., gt=0, description="Price of the product, must be greater than 0")
    category_id: int = Field(..., description="Foreign key to the Category table")

class Category(BaseModel):
    id: int = Field(..., description="Unique identifier for the category")
    name: str = Field(..., description="Name of the category")
    description: Optional[str] = Field(None, description="Optional description of the category")
    # The 'products' field will be used for nested data in Python, but not directly in SQL DDL
    products: List[Product] = Field([], description="List of products belonging to this category")

class DatabaseSchema(BaseModel):
    categories: List[Category]

# 2. Create some sample data
# This demonstrates how to populate the models with example categories and products.
product_1 = Product(id=1, name="Laptop Pro", description="High-performance laptop", price=1200.00, category_id=1)
product_2 = Product(id=2, name="Gaming Mouse", description="Ergonomic gaming mouse", price=75.50, category_id=2)
product_3 = Product(id=3, name="Mechanical Keyboard", description="RGB mechanical keyboard", price=150.00, category_id=2)
product_4 = Product(id=4, name="Smartphone X", description="Latest model smartphone", price=800.00, category_id=1)
product_5 = Product(id=5, name="Coffee Maker", description="Automatic coffee maker", price=100.00, category_id=3)

category_1 = Category(id=1, name="Electronics", description="Devices like phones, computers", products=[product_1, product_4])
category_2 = Category(id=2, name="Peripherals", description="Computer accessories", products=[product_2, product_3])
category_3 = Category(id=3, name="Home Appliances", description="Appliances for home use", products=[product_5])

# Assemble the full database schema with sample data
db_data = DatabaseSchema(categories=[category_1, category_2, category_3])

# 3. Display the data (e.g., as JSON for easy inspection or transfer)
print("--- Sample Data in JSON Format ---")
print(db_data.model_dump_json(indent=2))

# 4. Generate SQL DDL for Supabase (PostgreSQL compatible)
# This function converts the Pydantic models into SQL CREATE TABLE statements and INSERT statements.
def generate_supabase_sql_ddl(db_schema: DatabaseSchema) -> str:
    sql_statements = []

    # Categories Table DDL
    sql_statements.append("""CREATE TABLE IF NOT EXISTS categories (
    id INT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT
);
""")

    # Products Table DDL
    sql_statements.append("""CREATE TABLE IF NOT EXISTS products (
    id INT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    price DECIMAL(10, 2) NOT NULL,
    category_id INT NOT NULL,
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE CASCADE
);
""")

    # Insert sample data into Categories table
    sql_statements.append("\n-- Insert sample data into categories\n")
    for category in db_schema.categories:
        # Sanitize string inputs for SQL to prevent issues with single quotes
        cat_name = category.name.replace("'", "''")
        cat_desc = (category.description or 'NULL').replace("'", "''")
        sql_statements.append(f"INSERT INTO categories (id, name, description) VALUES ({category.id}, '{cat_name}', '{cat_desc}');")

    # Insert sample data into Products table
    sql_statements.append("\n-- Insert sample data into products\n")
    # Collect all products from all categories to insert them into the products table
    all_products = []
    for category in db_schema.categories:
        all_products.extend(category.products)
    
    for product in all_products:
        # Sanitize string inputs for SQL
        prod_name = product.name.replace("'", "''")
        prod_desc = (product.description or 'NULL').replace("'", "''")
        sql_statements.append(f"INSERT INTO products (id, name, description, price, category_id) VALUES ({product.id}, '{prod_name}', '{prod_desc}', {product.price}, {product.category_id});")

    return "\n".join(sql_statements)

# Generate and print the SQL DDL
print("\n--- SQL DDL for Supabase (PostgreSQL) ---")
supabase_sql = generate_supabase_sql_ddl(db_data)
print(supabase_sql)
