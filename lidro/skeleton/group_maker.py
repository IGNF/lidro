class GroupMaker:
    """
    From a list of elements, GroupMaker is used to
    put together groups of elements, according to single
    element from each group. For example:
    At the beginning, we have {A}, {B}, {C}, {D}, {E}
    put_together(A, B) -> {A, B}, {C}, {D}, {E}
    put_together(C, D) -> {A, B}, {C, D}, {E}
    put_together(A, D) -> {A, B, C, D}, {E}
    """
    def __init__(self, element_list):
        self.element_set_list = [{element} for element in element_list]

    def find_index(self, element) -> int:
        for index, element_set in enumerate(self.element_set_list):
            if element in element_set:
                return index

    def are_together(self, element_a, element_b) -> bool:
        """return true if 2 elements are already together"""
        index = self.find_index(element_a)
        return element_b in self.element_set_list[index]

    def put_together(self, element_a, element_b):
        """put the set of a and b together if they aren't"""
        if self.are_together(element_a, element_b):
            return
        index_a = self.find_index(element_a)
        set_a = self.element_set_list.pop(index_a)
        index_b = self.find_index(element_b)
        self.element_set_list[index_b] = self.element_set_list[index_b].union(set_a)
