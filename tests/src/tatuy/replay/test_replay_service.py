"""Replay capability remains independent from media capture."""

from pathlib import Path

from tatuy.capture.replay_header import ReplayHeader
from tatuy.capture.settings import ReplaySettings
from tatuy.input.frame import InputFrame
from tatuy.replay.null import NullReplayService
from tatuy.replay.service import ReplayService


def test_replay_service_records_and_plays_without_capture(tmp_path: Path) -> None:
    service = ReplayService(
        ReplaySettings(root_dir=str(tmp_path), replays_dir="replays")
    )
    header = ReplayHeader(
        game_id="demo",
        initial_scene="main",
        virtual_w=800,
        virtual_h=600,
    )
    frame = InputFrame()

    service.start_record(filename="session.jsonl", header=header)
    service.record_input(frame, 1 / 60)
    service.stop_record()

    replay_path = tmp_path / "replays" / "session.jsonl"
    assert replay_path.exists()

    loaded = service.start_play("session.jsonl")
    recorded = service.next_frame()

    assert loaded == header
    assert recorded is not None
    assert recorded.index == 0
    assert recorded.dt == 1 / 60
    assert recorded.input_frame == frame
    assert service.next_frame() is None
    assert service.playing is True

    service.stop_play()
    assert service.playing is False
    assert service.header is None


def test_null_replay_service_is_inert() -> None:
    service = NullReplayService()

    assert service.enabled is False
    assert service.recording is False
    assert service.playing is False
    assert service.header is None
    assert service.next_frame() is None
