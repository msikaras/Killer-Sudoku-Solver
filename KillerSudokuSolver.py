import random
import numpy as np
import matplotlib.pyplot as plt
import time


def generate_sudoku_grid():
    def is_valid(grid, row, col, num):
        for i in range(9):
            if grid[row][i] == num or grid[i][col] == num:
                return False
        subgrid_row, subgrid_col = 3 * (row // 3), 3 * (col // 3)
        for i in range(subgrid_row, subgrid_row + 3):
            for j in range(subgrid_col, subgrid_col + 3):
                if grid[i][j] == num:
                    return False
        return True

    def solve(grid):
        for row in range(9):
            for col in range(9):
                if grid[row][col] == 0:
                    random.shuffle(numbers)
                    for num in numbers:
                        if is_valid(grid, row, col, num):
                            grid[row][col] = num
                            if solve(grid):
                                return True
                            grid[row][col] = 0
                    return False
        return True

    grid = [[0] * 9 for _ in range(9)]
    numbers = list(range(1, 10))
    solve(grid)
    return grid


def generate_killer_sudoku_cages(grid, max_cage_size=4, min_cages=10):
    def get_random_starting_cell(available_cells):
        return random.choice(available_cells)

    def get_neighbors(cell, available_cells):
        neighbors = []
        row, col = cell
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            neighbor = (row + dr, col + dc)
            if neighbor in available_cells:
                neighbors.append(neighbor)
        return neighbors

    available_cells = [(r, c) for r in range(9) for c in range(9)]
    cages = []

    while available_cells and len(cages) < min_cages:
        starting_cell = get_random_starting_cell(available_cells)
        cage_cells = [starting_cell]
        available_cells.remove(starting_cell)

        cage_size = random.randint(2, max_cage_size)

        while len(cage_cells) < cage_size and available_cells:
            neighbors = []
            for cell in cage_cells:
                neighbors.extend(get_neighbors(cell, available_cells))
            if not neighbors:
                break
            new_cell = random.choice(neighbors)
            cage_cells.append(new_cell)
            available_cells.remove(new_cell)

        cage_sum = sum(grid[r][c] for r, c in cage_cells)
        cages.append({"cells": cage_cells, "sum": cage_sum})

    return cages


def generate_starting_board(solution_grid, num_prefilled=20):
    starting_board = np.zeros((9, 9), dtype=int)
    filled_positions = set()
    while len(filled_positions) < num_prefilled:
        row = random.randint(0, 8)
        col = random.randint(0, 8)
        if (row, col) not in filled_positions:
            starting_board[row][col] = solution_grid[row][col]
            filled_positions.add((row, col))
    return starting_board


def optimized_backtracking_solver(grid, cages):
    def is_valid_killer(grid, row, col, num, cages):
        for i in range(9):
            if grid[row][i] == num or grid[i][col] == num:
                return False

        subgrid_row, subgrid_col = 3 * (row // 3), 3 * (col // 3)
        for i in range(subgrid_row, subgrid_row + 3):
            for j in range(subgrid_col, subgrid_col + 3):
                if grid[i][j] == num:
                    return False

        for cage in cages:
            if (row, col) in cage["cells"]:
                cage_values = [grid[r][c] for r, c in cage["cells"] if grid[r][c] != 0]
                if num in cage_values:
                    return False
                if sum(cage_values) + num > cage["sum"]:
                    return False
                break
        return True

    def forward_checking(grid, domains):
        for r in range(9):
            for c in range(9):
                if grid[r][c] != 0:
                    domains[r][c] = {grid[r][c]}
                else:
                    possible_values = {v for v in range(1, 10) if is_valid_killer(grid, r, c, v, cages)}
                    domains[r][c] = possible_values

    def select_unassigned_variable(domains):
        min_domain = 10
        selected_cell = None
        for r in range(9):
            for c in range(9):
                if len(domains[r][c]) > 1 and len(domains[r][c]) < min_domain:
                    min_domain = len(domains[r][c])
                    selected_cell = (r, c)
        return selected_cell

    def backtrack(grid, domains):
        forward_checking(grid, domains)
        cell = select_unassigned_variable(domains)
        if cell is None:
            return True

        row, col = cell
        for num in sorted(domains[row][col]):
            if is_valid_killer(grid, row, col, num, cages):
                grid[row][col] = num
                if backtrack(grid, domains):
                    return True
                grid[row][col] = 0
        return False

    puzzle = np.copy(grid)
    domains = [[set(range(1, 10)) for _ in range(9)] for _ in range(9)]
    forward_checking(puzzle, domains)
    if backtrack(puzzle, domains):
        return puzzle
    else:
        raise ValueError("No solution exists for the given puzzle.")


def solve_multiple_boards(num_boards):
    solving_times = []
    start_time_total = time.time()

    for _ in range(num_boards):
        sudoku_grid = generate_sudoku_grid()
        cages = generate_killer_sudoku_cages(sudoku_grid, max_cage_size=4, min_cages=10)
        initial_grid = generate_starting_board(sudoku_grid, num_prefilled=20)

        start_time = time.time()
        try:
            optimized_backtracking_solver(np.copy(initial_grid), cages)
        except ValueError:
            pass
        solving_times.append(time.time() - start_time)
        
    total_duration = time.time() - start_time_total

    # Plot results
    plt.figure(figsize=(10, 6))
    plt.plot(range(1, num_boards + 1), solving_times, label="Backtracking Solver")
    plt.xlabel("Board Number")
    plt.ylabel("Time (s)")
    plt.title("Backtracking Solver Performance Across Multiple Boards")
    plt.legend()
    plt.show()
    
    print(f"\nTotal Time to Solve {num_boards} Boards: {total_duration:.2f} seconds")
    print(f"Average Time Per Board: {total_duration / num_boards:.2f} seconds")


if __name__ == "__main__":
    while True:
        print("\nOptions:")
        print("1. Generate a Killer Sudoku Board")
        print("2. Solve a Board with Backtracking Solver")
        print("3. Solve Multiple Boards with Backtracking Solver and Plot Results")
        print("4. Exit")

        choice = input("Enter your choice: ").strip()
        if choice == "1":
            sudoku_grid = generate_sudoku_grid()
            cages = generate_killer_sudoku_cages(sudoku_grid, max_cage_size=4, min_cages=10)
            initial_grid = generate_starting_board(sudoku_grid, num_prefilled=20)
            print("Initial Grid:")
            print(initial_grid)
            print("Cages:")
            for cage in cages:
                print(cage)
        elif choice == "2":
            sudoku_grid = generate_sudoku_grid()
            cages = generate_killer_sudoku_cages(sudoku_grid, max_cage_size=4, min_cages=10)
            initial_grid = generate_starting_board(sudoku_grid, num_prefilled=20)
            print("Initial Grid:")
            print(initial_grid)
            print("Cages:")
            for cage in cages:
                print(cage)
            try:
                solved_grid = optimized_backtracking_solver(np.copy(initial_grid), cages)
                print("Backtracking Solved Grid:")
                print(solved_grid)
            except ValueError as e:
                print("Error:", e)
        elif choice == "3":
            num_boards = int(input("Enter the number of boards to solve: ").strip())
            solve_multiple_boards(num_boards)
        elif choice == "4":
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please try again.")
