from collections import defaultdict

EPS = 'ε'  
EPS_ALIASES = {'e', 'eps', 'epsilon', EPS}

def normalize_token(tok: str):
    tok = tok.strip()
    if tok.lower() in EPS_ALIASES:
        return EPS
    return tok

def parse_grammar_from_input():
    grammar = defaultdict(list)
    n = int(input("Enter number of productions: ").strip())
    print("Enter productions (e.g. E -> T E'):")
    for _ in range(n):
        line = input().strip()
        if not line:
            continue
        if '->' not in line:
            raise ValueError("Production must contain '->' (e.g. S -> A B C)")
        lhs, rhs = line.split('->', 1)
        lhs = lhs.strip()
      
        for alt in rhs.split('|'):
            alt = alt.strip()
            if alt == '':
               grammar[lhs].append([EPS])
            else:
                tokens = [normalize_token(t) for t in alt.split() if t != '']
                if not tokens:
                    tokens = [EPS]
                grammar[lhs].append(tokens)
    return grammar

def compute_first(grammar):
    nonterminals = set(grammar.keys())
    symbols_in_prods = set(sym for prods in grammar.values() for prod in prods for sym in prod)
    terminals = {s for s in symbols_in_prods if s not in nonterminals and s != EPS}

    FIRST = {sym: set() for sym in nonterminals.union(terminals)}
    for t in terminals:
        FIRST[t].add(t)
    FIRST[EPS] = {EPS}

    changed = True
    while changed:
        changed = False
        for A in nonterminals:
            for prod in grammar[A]:
                if len(prod) == 1 and prod[0] == EPS:
                    if EPS not in FIRST[A]:
                        FIRST[A].add(EPS)
                        changed = True
                    continue

                add_eps = True
                for Xi in prod:
                    Xi_first = FIRST.get(Xi, set())
                    before = len(FIRST[A])
                    to_add = Xi_first - {EPS}
                    if to_add - FIRST[A]:
                        FIRST[A].update(to_add)
                        changed = True
                    if EPS in Xi_first:
                        add_eps = True
                        continue
                    else:
                        add_eps = False
                        break
                if add_eps:
                    if EPS not in FIRST[A]:
                        FIRST[A].add(EPS)
                        changed = True
    return FIRST

def compute_follow(grammar, FIRST, start_symbol):
    nonterminals = set(grammar.keys())
    FOLLOW = {A: set() for A in nonterminals}
    FOLLOW[start_symbol].add('$')

    changed = True
    while changed:
        changed = False
        for A in nonterminals:
            for prod in grammar[A]:
                trailer = FOLLOW[A].copy()
                for Xi in reversed(prod):
                    if Xi in nonterminals:
                        before = len(FOLLOW[Xi])
                        if not trailer.issubset(FOLLOW[Xi]):
                            FOLLOW[Xi].update(trailer)
                            changed = True
                        if EPS in FIRST[Xi]:
                            trailer = trailer.union(FIRST[Xi] - {EPS})
                        else:
                            trailer = FIRST[Xi].copy()
                    else:
                        trailer = FIRST.get(Xi, set()).copy()
    return FOLLOW

def format_set(s):
   
    if not s:
        return "set()"
    items = sorted(s, key=lambda x: (str(x)))
    return "{" + ", ".join(repr(x) for x in items) + "}"

def main():
    grammar = parse_grammar_from_input()
    if not grammar:
        print("No productions provided.")
        return

    start_symbol = next(iter(grammar.keys()))
    FIRST = compute_first(grammar)
    FOLLOW = compute_follow(grammar, FIRST, start_symbol)

    print("\nFIRST sets:")
    for nt in grammar.keys():
        print(f"FIRST({nt}) = {format_set(FIRST.get(nt, set()))}")

    print("\nFOLLOW sets:")
    for nt in grammar.keys():
        print(f"FOLLOW({nt}) = {format_set(FOLLOW.get(nt, set()))}")

if __name__ == "__main__":
    main()
