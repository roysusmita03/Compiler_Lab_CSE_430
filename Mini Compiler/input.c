int main() {
    int x = 10;
    float y = 5.5;
    int result;
    
    if (x > 5) {
        result = x + y;
    } 
    else {
        result = x - y;
    }
    
    while (x > 0) {
        x = x - 1;
    }
    
    for (i = 0; i < 5; i = i + 1) {
        result = result + i;
    }
    
    return result;
}


float calculate(int a, float b) {
    return a * b + 2.0;
}

