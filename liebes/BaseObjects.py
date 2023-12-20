class BaseEquals:
    def __eq__(self, other):
        if type(self) is not type(other):
            return False
        return all(
            getattr(self, attr) == getattr(other, attr)
            for attr in self.__dict__
            if not attr.startswith('_')
        )
