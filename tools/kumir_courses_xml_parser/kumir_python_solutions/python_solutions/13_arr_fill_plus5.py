"""
Task 13: arr_fill_plus5

Original: Заполнить плюс 5 (цел N, рез целтаб A[1:N], арг цел X)
Init: Целочисленный массив A[1:N]
Todo: Заполнить массив натуральными числами, так что первый элемент массива должен быть равен X, а каждый следующий элемент должен быть на 5 больше предыдущего.

Kumir code:
нач цел i A[1]:=X нц для i от 2 до N A[i]:=A[i-1] + 5 кц кон
"""

def arr_fill_plus5(N: int, A: list, X: int):
    """Python solution for the task."""
    A[0] = X
    for i in range(1, N):
        A[i] = A[i-1] + 5
    return A


def test_solution():
    """Test the solution."""
    N = 5
    A = [0] * N
    X = 10
    result = arr_fill_plus5(N, A.copy(), X)
    print(f"Result: {result}")
    return result


if __name__ == "__main__":
    test_solution()