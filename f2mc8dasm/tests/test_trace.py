import unittest
from f2mc8dasm.trace import TraceQueue

class TraceQueueTests(unittest.TestCase):
    # __init__

    def test_ctor(self):
        queue = TraceQueue()
        self.assertEqual(queue.traced_addresses, set())
        self.assertEqual(queue.untraced_addresses, set())

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

    def test_push_doesnt_add_address_if_already_traced(self):
        queue = TraceQueue()
        queue.push(0x0005)
        self.assertEqual(len(queue), 1)
        queue.pop()
        queue.push(0x0005)
        self.assertEqual(len(queue), 0)

    # pop

    def test_pop_raises_if_no_more_addresses(self):
        queue = TraceQueue()
        try:
            queue.pop()
            self.fail()
        except KeyError as exc:
            self.assertEqual(exc.args[0], 'pop from empty trace queue')

    def test_pop_removes_from_untraced_and_adds_to_traced(self):
        queue = TraceQueue()
        queue.push(0x0005)
        self.assertEqual(queue.untraced_addresses, set([0x0005]))
        address = queue.pop()
        self.assertEqual(address, 0x0005)
        self.assertEqual(queue.untraced_addresses, set())
        self.assertEqual(queue.traced_addresses, set([0x0005]))
