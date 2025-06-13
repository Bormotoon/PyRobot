"""
Task 11: arr_fill_natural

Original: Заполнить натуральными числами (цел N, рез целтаб A[1:N])
Init: Целочисленный массив A[1:N]
Todo: Заполнить массив первыми N натуральными числами, начиная с 1.

Kumir code:
нач цел i нц для i от 1 до N A[i]:=i кц кон
"""

def arr_fill_natural(N: int, A: list):
    """Python solution for the task."""
    for i in range(N):
        A[i] = i + 1
    return A


def test_solution():
    """Test the solution."""
    N = 5
    A = [0] * N
    result = arr_fill_natural(N, A.copy())
    print(f"Result: {result}")
    return result


if __name__ == "__main__":
    test_solution()