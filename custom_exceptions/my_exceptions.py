class MissingColumnsError(Exception):
    """
    """

    def __init__(self, missing_columns, msg=""):
        self.missing_columns = missing_columns
        self.msg = msg
        super().__init__(f"{self.msg} is missing column(s) in: {self.missing_columns}")


class ColumnExistsError(Exception):
    """
    """

    def __init__(self, existing_columns, msg=""):
        self.missing_columns = existing_columns
        self.msg = msg
        super().__init__(f"{self.msg} already contains column(s): {self.existing_columns}")