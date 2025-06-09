#!/usr/bin/env python3
import subprocess
import sys

def run_test():
    """Запуск одного теста для проверки"""
    cmd = [
        sys.executable, '-m', 'pytest', 
        'tests/generated_course_tests/test_strkum.py::test_strkum_Nayti_pervyy_simvol_stroki_10',
        '-v'
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    print("STDOUT:")
    print(result.stdout)
    print("STDERR:")
    print(result.stderr)
    print(f"Return code: {result.returncode}")

if __name__ == "__main__":
    run_test()
