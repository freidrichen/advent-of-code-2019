from collections import Counter

def check_code_part1(code):
    digits = [int(d) for d in str(code)]
    double_digit = False
    for digit, last_digit in zip(digits[1:], digits[:-1]):
        if digit < last_digit:
            return False
        if digit == last_digit:
            double_digit = True
    return double_digit

min_ = 137683
max_ = 596253

count = 0
for i in range(min_, max_ + 1):
    count += check_code_part1(i)

print(f"Valid codes (part 1): {count}")


def check_code_part2(code):
    digits = [int(d) for d in str(code)]
    if not digits == sorted(digits):
        return False
    counts = Counter(digits)
    return 2 in counts.values()

count = 0
for i in range(min_, max_ + 1):
    count += check_code_part2(i)


print(f"Valid codes (part 2): {count}")
