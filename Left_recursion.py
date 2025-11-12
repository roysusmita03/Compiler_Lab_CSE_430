def eliminate_left_recursion(nonterminal, productions):
    
    alpha = []
    beta = []

    for prod in productions:
        if prod.startswith(nonterminal):  
            alpha.append(prod[len(nonterminal):])  
        else:
            beta.append(prod) 

    new_productions = {}
    if alpha:
        new_nt = nonterminal + "'"
       
        new_productions[nonterminal] = [b + new_nt for b in beta]
       
        new_productions[new_nt] = [a + new_nt for a in alpha] + ["ε"]
    else:
        new_productions[nonterminal] = productions

    return new_productions


if __name__ == "__main__":
    print("Enter grammar rules (format: A->Aa|b). Press Enter on empty line to finish:")

    grammar = {}
    while True:
        line = input().strip()
        if not line:
            break
        left, right = line.split("->")
        nonterminal = left.strip()
        productions = [r.strip() for r in right.split("|")]
        grammar[nonterminal] = productions

    print("\nOriginal Grammar:")
    for nt, rules in grammar.items():
        print(f"{nt} -> " + " | ".join(rules))

    print("\nAfter left recursion elimination:")
    new_grammar = {}
    for nt, rules in grammar.items():
        result = eliminate_left_recursion(nt, rules)
        new_grammar.update(result)

    for nt, rules in new_grammar.items():
        print(f"{nt} -> " + " | ".join(rules))
