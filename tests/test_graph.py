from agent.graph import build_graph


def test_graph_builds_without_error():
    graph = build_graph()
    assert graph is not None


def test_graph_has_invoke_method():
    graph = build_graph()
    assert callable(graph.invoke)


def test_graph_has_stream_method():
    graph = build_graph()
    assert callable(graph.stream)
