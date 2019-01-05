from main import Session, Event


class TestSession:
    def test_session_id_comes_from_first_event(self):
        session = Session()
        session.add_event(Event('track_end', 100, 'A', '101'))
        session.add_event(Event('track_end', 100, 'B', '101'))

        assert session.session_id == ('A', '101')

    def test_start_time_comes_from_first_event(self):
        session = Session()
        session.add_event(Event('track_end', 100, 'A', '101'))
        session.add_event(Event('track_end', 50, 'A', '101'))
        session.add_event(Event('track_end', 150, 'A', '101'))

        assert session.start_time == 100

    def test_last_time_comes_from_last_event(self):
        session = Session()
        session.add_event(Event('track_end', 50, 'A', '101'))
        session.add_event(Event('track_end', 150, 'A', '101'))
        session.add_event(Event('track_end', 100, 'A', '101'))

        assert session.last_time == 100

    def test_duration_is_time_between_last_and_first_event(self):
        session = Session()
        session.add_event(Event('track_end', 50, 'A', '101'))
        session.add_event(Event('track_end', 150, 'A', '101'))
        session.add_event(Event('track_end', 100, 'A', '101'))

        assert session.duration == 50

    def test_track_playtime_counts_time_between_track_start_and_track_end(
        self
    ):
        session = Session()
        session.add_event(Event('track_start', 50, 'A', '101'))
        session.add_event(Event('track_end', 100, 'A', '101'))

        assert session.track_playtime == 50

    def test_track_playtime_works_without_track_end(self):
        session = Session()
        session.add_event(Event('track_start', 50, 'A', '101'))
        session.add_event(Event('track_heartbeat', 60, 'A', '101'))

        assert session.track_playtime == 10

    def test_track_playtime_supports_pauses(self):
        session = Session()
        session.add_event(Event('track_start', 50, 'A', '101'))
        session.add_event(Event('pause', 60, 'A', '101'))
        session.add_event(Event('play', 70, 'A', '101'))
        session.add_event(Event('track_end', 100, 'A', '101'))

        assert session.track_playtime == 40

    def test_track_playtime_supports_paused_heartbeated_unfinished_sessions(self):
        session = Session()
        session.add_event(Event('track_start', 50, 'A', '101'))
        session.add_event(Event('pause', 60, 'A', '101'))
        session.add_event(Event('track_heartbeat', 70, 'A', '101'))

        assert session.track_playtime == 10

    def test_ad_count_counts_number_of_ad_starts(self):
        session = Session()
        session.add_event(Event('ad_start', 50, 'A', '101'))
        session.add_event(Event('ad_start', 50, 'A', '101'))
        session.add_event(Event('ad_end', 50, 'A', '101'))
        session.add_event(Event('ad_start', 50, 'A', '101'))

        assert session.ad_count == 3

    def test_is_expired_is_false_59_seconds_after_last_event(self):
        session = Session()
        session.add_event(Event('ad_start', 50, 'A', '101'))

        assert not session.is_expired(50 + 59)

    def test_is_expired_is_true_60_seconds_after_last_event(self):
        session = Session()
        session.add_event(Event('ad_start', 50, 'A', '101'))

        assert session.is_expired(50 + 60)

    def test_get_formatted_output_returns_in_correct_format(self):
        session = Session()
        session.add_event(Event('stream_start', 50, 'A', '101'))
        session.add_event(Event('ad_start', 60, 'A', '101'))
        session.add_event(Event('ad_end', 70, 'A', '101'))
        session.add_event(Event('track_start', 80, 'A', '101'))
        session.add_event(Event('track_heartbeat', 90, 'A', '101'))

        assert session.get_formatted_output() == {
            'user_id': 'A',
            'content_id': '101',
            'session_start': 50,
            'session_end': 90,
            'total_time': 40,
            'track_playtime': 10,
            'event_count': 5,
            'ad_count': 1
        }

