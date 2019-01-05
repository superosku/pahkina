from main import Event


class TestEvent:
    def test_session_id_property(self):
        event = Event('track_end', 100, 'A', '101')
        assert event.session_id == ('A', '101')

    def test_repr(self):
        event = Event('track_end', 100, 'A', '101')
        assert (
            repr(event) ==
            "Event(event_type='track_end', " "timestamp=100, user_id='A', "
            "content_id='101')"
        )
