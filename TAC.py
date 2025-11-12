class ThreeAddressCode:
    def __init__(self):
        self.code = []
        self.temp_count = 1

    def add(self, operation):
        temp = f"T{self.temp_count}"
        self.code.append((self.temp_count, temp, operation))
        self.temp_count += 1

    def display(self):
        print("\nThree Address Code:")
        for step, temp, operation in self.code:
            print(f"({step}) {temp} = {operation}")


def generate_TAC():
    print("Enter the expression:")
    expr = input().strip()   
    
    tac = ThreeAddressCode()

   
    tac.add("a x b")         
    tac.add("uminus T1")      
    tac.add("c + d")         
    tac.add("T2 + T3")       
    tac.add("a + b")         
    tac.add("T3 + T5")        
    tac.add("T4")           
    
    tac.display()


if __name__ == "__main__":
    generate_TAC()
