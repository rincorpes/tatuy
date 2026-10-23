from tatuy.events.bus import EventBus


def test_event_bus_emits_to_subscribers_and_clear_removes_them():
    bus = EventBus()
    bus.clear()
    calls = []

    bus.on("damage", lambda **kwargs: calls.append(kwargs))
    bus.emit("damage", amount=3)

    assert calls == [{"amount": 3}]

    bus.clear()
    bus.emit("damage", amount=5)

    assert calls == [{"amount": 3}]
