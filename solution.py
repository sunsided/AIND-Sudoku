from functools import lru_cache as cache
from typing import List, Set, Dict, Union

Box = str
Values = str
Unit = List[Box]
SudokuDict = Dict[Box, Values]
MaybeSolution = Union[SudokuDict, bool]

assignments = []

# noinspection SpellCheckingInspection
rows = 'ABCDEFGHI'
cols = '123456789'
digits = '123456789'


def assign_value(values, box, value):
    """
    Please use this function to update your values dictionary!
    Assigns a value to a given box. If it updates the board record it.
    """

    # Don't waste memory appending actions that don't actually change any values
    if values[box] == value:
        return values

    values[box] = value
    if len(value) == 1:
        assignments.append(values.copy())
    return values


def naked_twins(values):
    """Eliminate values using the naked twins strategy.
    Args:
        values(dict): a dictionary of the form {'box_name': '123456789', ...}

    Returns:
        the values dictionary with the naked twins eliminated from peers.
    """

    # Find all instances of naked twins
    # Eliminate the naked twins as possibilities for their peers


def cross(a: str, b: str) -> List[str]:
    """
    Cross product of elements in a and elements in b.
    
    Parameters
    ----------
    a : str  
        The string from which to select the first character.
    b : str  
        The string from which to select the second character.
        
    Returns
    -------
    List[str]
        The combinatorial values.
    """
    return [s+t for s in a for t in b]


@cache(maxsize=None)
def boxes() -> List[Box]:
    """Returns the list of all boxes."""
    bs = cross(rows, cols)
    assert len(bs) == 81
    return bs


@cache(maxsize=None)
def row_units() -> List[Unit]:
    """Returns the list of row-wise units."""
    return [cross(r, cols) for r in rows]


@cache(maxsize=None)
def column_units() -> List[Unit]:
    """Returns the list of column-wise units."""
    return [cross(rows, c) for c in cols]


@cache(maxsize=None)
def square_units() -> List[Unit]:
    """Returns the list of square units."""
    return [cross(rs, cs)
            for rs in ('ABC', 'DEF', 'GHI')
            for cs in ('123', '456', '789')]


@cache(maxsize=None)
def unit_list() -> List[Unit]:
    """Returns the list of square units."""
    return row_units() + column_units() + square_units()


@cache(maxsize=None)
def unit_dict() -> Dict[Box, List[Unit]]:
    """Returns the dictionary of all units a given box is in."""
    return dict((s, [u for u in unit_list() if s in u])
                for s in boxes())


@cache(maxsize=None)
def peer_dict() -> Dict[Box, Set[Box]]:
    """Returns the dictionary of all peers a given box has."""
    units = unit_dict()
    return dict((s, set(sum(units[s], [])) - {s})
                for s in boxes())


def grid_values(grid: str) -> SudokuDict:
    """
    Convert grid into a dict of {square: char} with '123456789' for empties.
    
    Args:
        grid(string)
            A grid in string form.
    Returns:
        A grid in dictionary form
            Keys: The boxes, e.g., 'A1'
            Values: The value in each box, e.g., '8'. If the box has no value, then the value will be '123456789'.
    """
    chars = [c if c != '.' else digits
             for c in grid
             if c in digits or c == '.']
    assert len(chars) == 81
    return dict(zip(boxes(), chars))


def display(values: SudokuDict) -> None:
    """
    Display the values as a 2-D grid.
    
    Parameters
    ----------
    values : SudokuDict  
             The sudoku in dictionary form
    """
    # This code is taken straight from the online quizzes.
    width = 1+max(len(values[s]) for s in boxes())
    line = '+'.join(['-'*(width*3)]*3)
    for r in rows:
        print(''.join(values[r+c].center(width)+('|' if c in '36' else '')
                      for c in cols))
        if r in 'CF':
            print(line)


def eliminate(values: SudokuDict) -> SudokuDict:
    """
    Goes through all the boxes, and whenever there is a box with a value, 
    eliminates this value from the values of all its peers.

    Parameters
    ----------
    values : SudokuDict  
        The sudoku in dictionary form
        
    Returns
    -------
    SudokuDict
        The resulting sudoku in dictionary form.
    """
    peers = peer_dict()
    solved_values = [box for box in values.keys() if len(values[box]) == 1]
    for box in solved_values:
        digit = values[box]
        for peer in peers[box]:
            values[peer] = values[peer].replace(digit, '')
    return values


def only_choice(values: SudokuDict) -> SudokuDict:
    """
    Go through all the units, and whenever there is a unit with a value that only fits in one box, 
    assign the value to this box.
    
    Parameters
    ----------
    values : SudokuDict  
        The sudoku in dictionary form
        
    Returns
    -------
    solution : SudokuDict
        The resulting sudoku in dictionary form.
    """
    # Since a digit has to appear once in each unit belonging to a box,
    # we have to check these units individually.
    for unit in unit_list():
        for digit in digits:
            candidates = [box for box in unit
                          if digit in values[box]]
            if len(candidates) == 1:
                values[candidates[0]] = digit
    return values


def reduce_puzzle(values: SudokuDict) -> MaybeSolution:
    """
    Iterate eliminate() and only_choice(). If at some point, there is a box with no available values, return False.
    If the sudoku is solved, return the sudoku.
    If after an iteration of both functions, the sudoku remains the same, return the sudoku.
    
    Parameters
    ----------
    values : SudokuDict  
        The sudoku in dictionary form
        
    Returns
    -------
    SudokuDict
        The resulting sudoku in dictionary form.
    False
        No solution could be found.
    """
    stalled = False
    while not stalled:
        solved_values_before = n_solved(values)
        values = eliminate(values)
        values = only_choice(values)

        stalled = solved_values_before == n_solved(values)
        if len([box for box in values if len(values[box]) == 0]):
            # TODO: When does this ever happen?
            return False
    return values


def n_solved(values: SudokuDict) -> int:
    """
    Determines how many fields of the grid have been solved.
    
    Parameters
    ----------
    values : SudokuDict  
        The sudoku in dictionary form
    
    Returns
    -------
    int
        The number of boxes in the grid that have a solution.
    """
    return len([box for box in values
                if len(values[box]) == 1])


def is_solved(values: SudokuDict) -> bool:
    """
    Determines if a Sudoku grid is solved.
    
    Parameters
    ----------
    values : SudokuDict  
        The sudoku in dictionary form
    
    Returns
    -------
    bool
        A boolean indicating if all boxes have a solution.
    """
    assert not isinstance(values, bool)
    return all(len(values[s]) == 1 for s in boxes())


def search(values: SudokuDict) -> MaybeSolution:
    """
    Using depth-first search and propagation, try all possible values.
        
    Parameters
    ----------
    values : SudokuDict  
        The sudoku in dictionary form
    
    Returns
    -------
    SudokuDict
        The resulting sudoku in dictionary form.
    False
        No solution could be found.
    """
    # First, reduce the puzzle using the previous function
    values = reduce_puzzle(values)
    if values is False:
        return False
    if is_solved(values):
        return values

    # Choose one of the unfilled squares with the fewest possibilities
    n, s = min((len(values[s]), s) for s in boxes() if len(values[s]) > 1)

    # Recursively try to solve each one of the resulting sudokus.
    for value in values[s]:
        branch = dict(values)
        branch[s] = value
        attempt = search(branch)
        if attempt:
            return attempt


def solve(grid: str) -> MaybeSolution:
    """
    Find the solution to a Sudoku grid.
    
    Parameters
    ----------
    grid : string 
        A string representing a sudoku grid.
        
        Example: ``2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3``
    
    Returns
    -------
    SudokuDict
        The resulting sudoku in dictionary form.
    False
        No solution could be found.
    """
    values = grid_values(grid)
    return search(values)


if __name__ == '__main__':
    diag_sudoku_grid = '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    display(solve(diag_sudoku_grid))
    exit(1)

    try:
        from visualize import visualize_assignments

        visualize_assignments(assignments)

    except SystemExit:
        pass
    except:
        print('We could not visualize your board due to a pygame issue. Not a problem! It is not a requirement.')
