from holocore.commands import get_command


def test_global_graph_is_a_write_scoped_command():
    command = get_command("global-graph")
    assert command.write is True
    assert "global-graph" in command.invocation
