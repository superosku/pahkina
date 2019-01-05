import io
import json

from main import Sessionizer


class TestSessionizer:
    def _add_event(self, sessionizer, content_id, user_id, event_type, timestamp):
        sessionizer.handle_event({
            'content_id': content_id,
            'user_id': user_id,
            'event_type': event_type,
            'timestamp': timestamp
        })

    def test_get_dropped_session_keys(self):
        output_stream = io.StringIO()
        sessionizer = Sessionizer(output_stream=output_stream)

        self._add_event(sessionizer, '1', 'A', 'stream_start', 0)
        self._add_event(sessionizer, '2', 'B', 'stream_start', 10)
        self._add_event(sessionizer, '3', 'C', 'stream_start', 20)
        self._add_event(sessionizer, '4', 'A', 'stream_start', 30)

        assert sessionizer.get_dropped_session_keys(40) == []
        assert sessionizer.get_dropped_session_keys(60) == [('A', '1')]
        assert sessionizer.get_dropped_session_keys(100) == [
            ('A', '1'), ('B', '2'), ('C', '3'), ('A', '4')
        ]

    def test_handles_complex_case_properly(self):
        output_stream = io.StringIO()
        sessionizer = Sessionizer(output_stream=output_stream)

        self._add_event(sessionizer, '1', 'A', 'stream_start', 0)
        self._add_event(sessionizer, '1', 'A', 'ad_start', 1)
        self._add_event(sessionizer, '1', 'A', 'ad_end', 3)
        self._add_event(sessionizer, '1', 'A', 'ad_start', 4)
        self._add_event(sessionizer, '1', 'A', 'ad_end', 7)
        self._add_event(sessionizer, '1', 'A', 'track_start', 8)
        self._add_event(sessionizer, '1', 'A', 'track_heartbeat', 18)
        self._add_event(sessionizer, '1', 'A', 'track_heartbeat', 28)
        self._add_event(sessionizer, '1', 'A', 'track_heartbeat', 38)
        self._add_event(sessionizer, '1', 'A', 'pause', 41)
        self._add_event(sessionizer, '1', 'A', 'play', 49)
        self._add_event(sessionizer, '1', 'A', 'track_heartbeat', 59)
        self._add_event(sessionizer, '1', 'A', 'track_end', 63)
        self._add_event(sessionizer, '1', 'A', 'stream_end', 64)
        self._add_event(sessionizer, '1', 'A', 'stream_start', 100)
        self._add_event(sessionizer, '1', 'A', 'ad_start', 101)
        self._add_event(sessionizer, '1', 'A', 'ad_end', 106)
        self._add_event(sessionizer, '1', 'A', 'track_start', 107)
        self._add_event(sessionizer, '1', 'A', 'track_heartbeat', 117)
        self._add_event(sessionizer, '1', 'A', 'stream_start', 230)

        output_stream.seek(0)

        output_json = [
            json.loads(line)
            for line in output_stream.readlines()
        ]

        assert output_json == [
            {
                'user_id': 'A',
                'content_id': '1',
                'session_start': 0,
                'session_end': 64,
                'total_time': 64,
                'track_playtime': 47,
                'event_count': 14,
                'ad_count': 2
            },
            {
                'user_id': 'A',
                'content_id': '1',
                'session_start': 100,
                'session_end': 117,
                'total_time': 17,
                'track_playtime': 10,
                'event_count': 5,
                'ad_count': 1
            }
        ]
