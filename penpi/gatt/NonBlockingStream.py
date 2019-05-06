from threading import Thread
import queue


class NonBlockingStreamReader:
    def __init__(self, stream):
        """
        :param stream: the stream to read from.  Usually stdout or stderr.
        """
        self._s = stream
        self._q = queue.Queue()

        self.ready = False

        def _populate_queue(_stream, _queue, _parent):
            """Collect lines from 'stream' and put them in 'queue'"""
            while True:
                _char = _stream.read(1)
                _parent.ready = True

                if _char:
                    _queue.put(_char)
                else:
                    raise UnexpectedEndOfStream

        self._t = Thread(
            target=_populate_queue,
            args=(
                self._s,
                self._q,
                self
            )
        )
        self._t.daemon = True
        self._t.start() # Start collecting characters from the stream

    def readchar(self, timeout=None):
        try:
            _tmp = self._q.get(block=timeout is not None, timeout=timeout)
            return _tmp
        except queue.Empty:
            return None
    


class UnexpectedEndOfStream(Exception):
    pass
