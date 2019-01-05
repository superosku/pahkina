import json

import sys


class Event:
    def __init__(self, event_type, timestamp, user_id, content_id):
        self.event_type = event_type
        self.timestamp = timestamp
        self.user_id = user_id
        self.content_id = content_id

    @property
    def session_id(self):
        return (self.user_id, self.content_id)

    def __repr__(self):
        return (
            f'Event(event_type={self.event_type!r}, '
            f'timestamp={self.timestamp!r}, '
            f'user_id={self.user_id!r}, '
            f'content_id={self.content_id!r})'
        )


class Session:
    def __init__(self):
        self.events = []

    def add_event(self, event):
        self.events.append(event)

    @property
    def session_id(self):
        return self.events[0].session_id

    @property
    def start_time(self):
        return self.events[0].timestamp

    @property
    def last_time(self):
        return self.events[-1].timestamp

    @property
    def duration(self):
        return self.last_time - self.start_time

    @property
    def track_playtime(self):
        playing = False
        play_start = None
        total_time = 0
        for event in self.events:
            if not playing and event.event_type in ['track_start', 'play']:
                playing = True
                play_start = event.timestamp
            if playing and event.event_type in [
                'track_end', 'stream_end', 'pause'
            ]:
                playing = False
                total_time += event.timestamp - play_start
        if playing:
            total_time += event.timestamp - play_start
        return total_time

    @property
    def ad_count(self):
        return len(
            [event for event in self.events if event.event_type == 'ad_start']
        )

    def is_expired(self, current_timestamp):
        return current_timestamp - self.last_time >= 60

    def get_formatted_output(self):
        return {
            'user_id': self.events[0].user_id,
            'content_id': self.events[0].content_id,
            'session_start': self.start_time,
            'session_end': self.last_time,
            'total_time': self.duration,
            'track_playtime': self.track_playtime,
            'event_count': len(self.events),
            'ad_count': self.ad_count
        }


class Sessionizer:
    def __init__(self, output_stream):
        self.output_stream = output_stream
        self.sessions = {}

    def handle_session_end(self, session_id):
        session = self.sessions[session_id]
        output = session.get_formatted_output()
        self.output_stream.write(json.dumps(output))
        self.output_stream.write('\n')
        self.sessions.pop(session_id)

    def get_dropped_session_keys(self, time_now):
        return [
            session_key
            for session_key, session in self.sessions.items()
            if session.is_expired(time_now)
        ]

    def handle_event(self, data):
        event = Event(
            content_id=data['content_id'],
            user_id=data['user_id'],
            event_type=data['event_type'],
            timestamp=data['timestamp'],
        )
        time_now = event.timestamp
        session_id = event.session_id

        # Session timeouted and new started but 60s not yet done.
        # We need to terminate old session before starting new.
        if session_id in self.sessions and event.event_type == 'stream_start':
            self.handle_session_end(session_id)

        if session_id not in self.sessions:
            self.sessions[session_id] = Session()
        session = self.sessions[session_id]
        session.add_event(event)

        ended_session_keys = self.get_dropped_session_keys(time_now)
        if event.event_type == 'stream_end':
            ended_session_keys.append(session_id)
        for ended_session_id in ended_session_keys:
            self.handle_session_end(ended_session_id)

    def handle_all_unfinished_events(self):
        unfinished_session_keys = list(self.sessions.keys())
        for session_id in unfinished_session_keys:
            self.handle_session_end(session_id)


def main(input_stream=sys.stdin, output_stream=sys.stdout):
    sessionizer = Sessionizer(output_stream)

    for line in input_stream:
        if not line.strip():
            break

        line_data = json.loads(line)
        sessionizer.handle_event(line_data)
    sessionizer.handle_all_unfinished_events()


if __name__ == '__main__':
    main()

