class SymbolInfo:
    def __init__(self, name, typ, size, dimension, line, address, bucket):
        self.name = name
        self.typ = typ
        self.size = size
        self.dimension = dimension
        self.line = line
        self.address = address
        self.bucket = bucket  

    def __str__(self):
        return (f"[Bucket: {self.bucket}, {self.name}, {self.typ}, {self.size}, {self.dimension}, "
                f"Line: {self.line}, Addr: {self.address}]")

class SymbolTable:
    def __init__(self, table_size=10):
        self.table = {}
        self.table_size = table_size  

   
    def simple_hash(self, name):
        total = 0
        for ch in name:
            total += ord(ch)  
        return total % self.table_size

    def insert(self, name, typ, size, dimension, line, address):
        if name in self.table:
            print(f"Error: '{name}' already exists in the table.")
        else:
            bucket = self.simple_hash(name)  
            self.table[name] = SymbolInfo(name, typ, size, dimension, line, address, bucket)
            print(f"Inserted: {self.table[name]}")

    def search(self, name):
        if name in self.table:
            print(f"Found: {self.table[name]}")
            return self.table[name]
        else:
            print(f"'{name}' not found in symbol table.")
            return None

    def delete(self, name):
        if name in self.table:
            print(f"Deleted: {self.table[name]}")
            del self.table[name]
        else:
            print(f"Cannot delete: '{name}' not found.")

    def update(self, name, new_typ=None, new_size=None, new_dimension=None, new_line=None, new_address=None):
        if name in self.table:
            symbol = self.table[name]
            symbol.typ = new_typ or symbol.typ
            symbol.size = new_size or symbol.size
            symbol.dimension = new_dimension or symbol.dimension
            symbol.line = new_line or symbol.line
            symbol.address = new_address or symbol.address
            symbol.bucket = self.simple_hash(symbol.name)  
            print(f"Updated: {symbol}")
        else:
            print(f"Cannot update: '{name}' not found.")

    def show(self):
        if not self.table:
            print("Symbol Table is empty.")
        else:
            print("\n Symbol Table Contents:")
            for symbol in self.table.values():
                print(f"   {symbol}")
            print()

def menu():
    sym_table = SymbolTable(table_size=10)  
    
    while True:
        print("\n====== SYMBOL TABLE MENU ======")
        print("1. Insert")
        print("2. Search")
        print("3. Update")
        print("4. Delete")
        print("5. Show Table")
        print("6. Exit")
        choice = input("Enter your choice (1-6): ")

        if choice == '1':
            name = input("Enter NAME: ")
            typ = input("Enter TYPE: ")
            size = input("Enter SIZE: ")
            dim = input("Enter DIMENSION: ")
            line = input("Enter LINE number: ")
            addr = input("Enter ADDRESS: ")
            sym_table.insert(name, typ, size, dim, line, addr)

        elif choice == '2':
            name = input("Enter NAME to Search: ")
            sym_table.search(name)

        elif choice == '3':
            name = input("Enter NAME to Update: ")
            print("Enter new values (leave blank to keep unchanged):")
            new_typ = input("New TYPE: ")
            new_size = input("New SIZE: ")
            new_dim = input("New DIMENSION: ")
            new_line = input("New LINE: ")
            new_addr = input("New ADDRESS: ")
            sym_table.update(
                name,
                new_typ or None,
                new_size or None,
                new_dim or None,
                new_line or None,
                new_addr or None
            )

        elif choice == '4':
            name = input("Enter NAME to Delete: ")
            sym_table.delete(name)

        elif choice == '5':
            sym_table.show()

        elif choice == '6':
            print("Exiting Symbol Table Program.")
            break

        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    menu()
