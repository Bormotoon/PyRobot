"""
Task 30: arr_find_max

Original: цел Максимум (цел N, аргрез целтаб A[1:N])
Init: Целочисленный массив A[1:N]
Todo: Найти максимальный элемент массива и записать его в переменную Max.

Kumir code:
нач цел Max цел i Max:=A[1] нц для i от 1 до N если A[i] > Max то Max:=A[i] все кц знач:=Max кон
"""

def arr_find_max(N: int, A: list):
    """Python solution for the task."""
    max_val = A[0]
    for i in range(N):
        if A[i] > max_val:
            max_val = A[i]
    return max_val


def test_solution():
    """Test the solution."""
    N = 5
    A = [0] * N
    result = arr_find_max(N, A.copy())
    print(f"Result: {result}")
    return result


if __name__ == "__main__":
    test_solution()