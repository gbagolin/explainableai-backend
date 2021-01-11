class OperandError(Exception):
    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = None

    def __str__(self):
        if self.message:
            return 'Operator given as input: {}'.format(self.message)
        else:
            return 'Operand error has been raised'
