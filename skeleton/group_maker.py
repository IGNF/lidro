class GroupMaker:
    def __init__(self, element_list):
        self.element_set_list = []
        for element in element_list:
            self.element_set_list.append({element})

    def find_index(self, element) -> int:
        for index, element_set in enumerate(self.element_set_list):
            if element in element_set:
                return index

    def are_together(self, element_a, element_b) -> bool:
        """return true if 2 elements are already together"""
        index = self.find_index(element_a)
        return element_b in self.element_set_list[index]

    def put_together(self, element_a, element_b):
        """put the set of a and b together"""
        index_a = self.find_index(element_a)
        set_a = self.element_set_list.pop(index_a)
        index_b = self.find_index(element_b)
        self.element_set_list[index_b] = self.element_set_list[index_b].union(set_a)