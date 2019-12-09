import numpy as np


input_file = "../input.txt"
with open(input_file, 'r') as f:
    input_text = f.read()
image_data = np.array([int(i) for i in input_text.strip()]).reshape((-1, 6, 25))
# image_data = np.array([int(i) for i in "123456789012"]).reshape((-1, 2, 3))

fewest_zeros = np.argmin([np.count_nonzero(layer == 0) for layer in image_data])
print(fewest_zeros, image_data[fewest_zeros])
number_of_ones = np.count_nonzero(image_data[fewest_zeros] == 1)
number_of_twos = np.count_nonzero(image_data[fewest_zeros] == 2)

print("Part 1:", number_of_ones*number_of_twos)
