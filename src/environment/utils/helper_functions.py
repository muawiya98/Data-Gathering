def generate_random_positions():
    """
    typically used for generating sensors position with uniform random distribution
    """

    import random

    random_numbers = [(random.randint(0, 999), random.randint(0, 999), random.randint(0, 999)) for _ in range(200)]

    formatted_list = "\n".join([f"{x},{y},{z}" for x, y, z in random_numbers])

    output_file_path = "random_numbers.txt"
    with open(output_file_path, "w") as file:
        file.write(formatted_list)
