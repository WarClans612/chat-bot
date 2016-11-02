class Keywords:
    def __init__(self, words):
        self.words = list(words)

    def dict(self):
        return self.__dict__

    def similarity(self, other):
        if isinstance(other, self.__class__):
            count = 0
            for word in other.words:
                if word in self.words:
                    count += 1
            return count
        else:
            return 0.0

    def __str__(self):
        return '{}'.format(self.words)

    def __eq__(self, other):
        """Override the default Equals behavior"""
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        return False

    def __ne__(self, other):
        """Define a non-equality test"""
        return not self.__eq__(other)

    def __hash__(self):
        """Override the default hash behavior (that returns the id or the object)"""
        return hash(tuple(sorted(self.__dict__.items())))