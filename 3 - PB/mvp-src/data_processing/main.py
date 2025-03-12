import connection_db
import create_table
import data_saving

def main():
    # Call functions from your scripts here
    connection_db.setup_connection()
    create_table.create_tables()
    data_saving.write_products_in_DB('data/product_file.json')

if __name__ == "__main__":
    main()