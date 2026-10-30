"""Command-line tic-tac-toe game where the human plays X and the computer plays O."""


def display(board):
    """Print the board using positions for empty cells."""
    print()
    for row in range(3):
        cells = [board[row * 3 + col] or str(row * 3 + col + 1) for col in range(3)]
        print(" " + " | ".join(cells))
        if row < 2:
            print("---+---+---")
    print()


def winner(board):
    """Return the winning mark, or None if there is no winner."""
    lines = (
        (0, 1, 2), (3, 4, 5), (6, 7, 8),
        (0, 3, 6), (1, 4, 7), (2, 5, 8),
        (0, 4, 8), (2, 4, 6),
    )
    for a, b, c in lines:
        if board[a] and board[a] == board[b] == board[c]:
            return board[a]
    return None


def computer_move(board):
    """Choose a move for the computer as O using a simple strategy."""
    lines = (
        (0, 1, 2), (3, 4, 5), (6, 7, 8),
        (0, 3, 6), (1, 4, 7), (2, 5, 8),
        (0, 4, 8), (2, 4, 6),
    )

    for mark in ("O", "X"):
        for a, b, c in lines:
            if board[a] == mark and board[b] == mark and not board[c]:
                return c
            if board[a] == mark and board[c] == mark and not board[b]:
                return b
            if board[b] == mark and board[c] == mark and not board[a]:
                return a

    for position in (4, 0, 2, 6, 8, 1, 3, 5, 7):
        if not board[position]:
            return position

    return None


def play():
    board = [""] * 9
    print("Tic-Tac-Toe (enter q to quit)")

    while True:
        display(board)
        choice = input("Player X, choose a square (1-9): ").strip().lower()
        if choice in {"q", "quit"}:
            print("Goodbye!")
            return
        if not choice.isdigit() or not 1 <= int(choice) <= 9:
            print("Please enter a number from 1 to 9.")
            continue
        position = int(choice) - 1
        if board[position]:
            print("That square is already taken.")
            continue

        board[position] = "X"
        game_winner = winner(board)
        if game_winner:
            display(board)
            print(f"Player {game_winner} wins!")
            return
        if all(board):
            display(board)
            print("It's a draw!")
            return

        computer_choice = computer_move(board)
        if computer_choice is None:
            display(board)
            print("It's a draw!")
            return

        board[computer_choice] = "O"
        print(f"Computer chooses square {computer_choice + 1}.")
        game_winner = winner(board)
        if game_winner:
            display(board)
            print(f"Player {game_winner} wins!")
            return
        if all(board):
            display(board)
            print("It's a draw!")
            return


if __name__ == "__main__":
    play()
