class Record:
    """
        Record in grid.
    """

    def __init__(self, id, path, cells):
        self.id = id
        self.path = path
        self.cells = cells

    def __str__(self):
        return self.id


class Cell:
    """
        Cell in record.
    """

    def __init__(self, id, value):
        self.columnId = id
        self.value = value

    def __str__(self):
        return self.columnId


class Page:
    """
            Paging in grid.
    """

    def __init__(self, limit=100, offset=0):
        self.limit = limit
        self.offset = offset

    def __str__(self):
        return f'limit: {self.limit} - offset: {self.offset}'

