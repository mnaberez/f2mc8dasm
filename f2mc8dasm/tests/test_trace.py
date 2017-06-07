import unittest
from f2mc8dasm.trace import TraceQueue, SortedSet

class TraceQueueTests(unittest.TestCase):
    # __init__

    def test_ctor(self):
        queue = TraceQueue()
        self.assertEqual(queue.traced_addresses, set())
        self.assertEqual(queue.untraced_addresses, SortedSet())

    # __len__

    def test_len_returns_untraced_length(self):
        queue = TraceQueue()
        queue.push(0x0001)
        queue.push(0x0002)
        self.assertEqual(len(queue), 2)

    # push

    def test_push_adds_address_to_untraced(self):
        queue = TraceQueue()
        queue.push(0x0005)
        self.assertEqual(queue.untraced_addresses, set([0x0005]))
        queue.push(0x0006)
        self.assertEqual(queue.untraced_addresses, set([0x0005, 0x0006]))

    def test_push_doesnt_add_address_if_already_in_traced(self):
        queue = TraceQueue()
        queue.push(0x0005)
        self.assertEqual(len(queue), 1)
        queue.pop()
        queue.push(0x0005)
        self.assertEqual(len(queue), 0)

    def test_push_doesnt_add_address_if_already_in_untraced(self):
        queue = TraceQueue()
        queue.push(0x0005)
        self.assertEqual(len(queue), 1)
        queue.push(0x0005)
        self.assertEqual(len(queue), 1)

    # pop

    def test_pop_raises_if_no_more_addresses(self):
        queue = TraceQueue()
        try:
            queue.pop()
            self.fail()
        except KeyError as exc:
            self.assertEqual(exc.args[0], 'pop from empty trace queue')

    def test_pop_removes_address_from_untraced_and_adds_to_traced(self):
        queue = TraceQueue()
        queue.push(0x0005)
        self.assertEqual(queue.untraced_addresses, set([0x0005]))
        address = queue.pop()
        self.assertEqual(address, 0x0005)
        self.assertEqual(queue.untraced_addresses, set())
        self.assertEqual(queue.traced_addresses, set([0x0005]))

    def test_pop_returns_addresses_in_sorted_order(self):
        queue = TraceQueue()
        queue.push(0x0003)
        queue.push(0x0001)
        queue.push(0x0002)
        self.assertEqual(queue.pop(), 0x0001)
        self.assertEqual(queue.pop(), 0x0002)
        self.assertEqual(queue.pop(), 0x0003)


class SortedSetTests(unittest.TestCase):
    # __init__

    def test_ctor(self):
        s = SortedSet([1, 2])
        self.assertTrue(1 in s)
        self.assertTrue(2 in s)

    # __len__

    def test_len_initially_0(self):
        s = SortedSet()
        self.assertEqual(len(s), 0)

    def test_len(self):
        s = SortedSet([1, 2])
        s.add(3)
        self.assertEqual(len(s), 3)

    # __contains__

    def test_contains(self):
        s = SortedSet([1])
        s.add(2)
        self.assertTrue(1 in s)
        self.assertTrue(2 in s)
        self.assertFalse(3 in s)

    # __iter__

    def test_iter(self):
        s = SortedSet([2,1,3])
        s.add(5)
        s.add(4)
        self.assertEqual(list(s), [1,2,3,4,5])

    # __eq__

    def test_eq_set(self):
        s = SortedSet([1, 2])
        self.assertTrue(s == set([1, 2]))
        self.assertFalse(s == set([1, 2, 3]))

    def test_eq_SortedSet(self):
        s = SortedSet([1, 2])
        self.assertTrue(s == SortedSet([1, 2]))
        self.assertFalse(s == SortedSet([1, 2, 3]))

    # add

    def test_add_new_item(self):
        s = SortedSet()
        s.add(1)
        self.assertEqual(s, set([1]))

    def test_add_existing_item(self):
        s = SortedSet()
        s.add(1)
        s.add(1)
        s.add(1)
        self.assertEqual(s, set([1]))
        self.assertEqual(list(s), [1])

    # remove

    def test_remove(self):
        s = SortedSet([1, 2, 3])
        s.remove(2)
        self.assertEqual(s, set([1, 3]))
        self.assertEqual(list(s), [1, 3])

    def test_remove_nonexistent_item(self):
        s = SortedSet()
        self.assertRaises(KeyError, s.remove, 1)

    # pop

    def test_pop(self):
        s = SortedSet([3,1,4])
        s.add(2)
        self.assertEqual(s.pop(), 1)
        self.assertEqual(s.pop(), 2)
        self.assertEqual(s.pop(), 3)
        self.assertEqual(s.pop(), 4)

    def test_pop_empty(self):
        s = SortedSet()
        self.assertRaises(KeyError, s.pop)
