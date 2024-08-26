from lidro.skeleton.group_maker import GroupMaker


def test_group_maker():
    A = 'A'
    B = 'B'
    C = 'C'
    element_list = [A, B, C]
    group_maker = GroupMaker(element_list)
    group_maker.put_together(A, B)
    assert group_maker.are_together(A, B)
    assert not group_maker.are_together(A, C)
