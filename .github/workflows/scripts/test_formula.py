#!/usr/bin/env python3

def test_formula():
    print("Testing gold price calculation formula with different R4 values")
    print("Expected result: ~122.635 ERG per gram")
    print("\n")
    
    # Test with different R4 values
    test_values = [
        8154910.0,           # Original test value
        8154910000.0,        # Original * 1000
        8154910000000.0,     # Original * 1000000
        8154910.0 * (10**6), # Original * 10^6
        8154910.0 * (10**9), # Original * 10^9
        8154910.0 * (10**12) # Original * 10^12
    ]
    
    for r4_value in test_values:
        # Calculate gold price using the formula: 10^18 / R4_value
        gold_price_per_gram_erg = (10**18) / r4_value
        
        print(f"R4 value: {r4_value}")
        print(f"Formula: 10^18 / R4_value = 10^18 / {r4_value}")
        print(f"Result: {gold_price_per_gram_erg:.6f} ERG per gram")
        print("\n")
    
    # Try a reverse calculation - what R4 value would give us 122.635 ERG per gram?
    target_price = 122.635
    required_r4 = (10**18) / target_price
    
    print(f"Reverse calculation:")
    print(f"Target price: {target_price} ERG per gram")
    print(f"Required R4 value: {required_r4:.6f}")
    print(f"Formula check: 10^18 / {required_r4:.6f} = {(10**18) / required_r4:.6f} ERG per gram")

if __name__ == "__main__":
    test_formula()
