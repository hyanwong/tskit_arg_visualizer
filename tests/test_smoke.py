import msprime
import pytest

import tskit_arg_visualizer as argviz


def _example_d3arg():
    ts = msprime.sim_ancestry(
        samples=4,
        sequence_length=100,
        recombination_rate=1e-2,
        record_full_arg=True,
        ploidy=1,
        random_seed=123,
    )
    return ts, argviz.D3ARG.from_ts(ts)


class TestRenderingSmoke:
    def test_draw_returns_drawinfo_without_opening_browser(self, monkeypatch):
        _, d3arg = _example_d3arg()

        # Keep test non-interactive while still exercising HTML generation path.
        monkeypatch.setattr(argviz, "display", lambda *_args, **_kwargs: None)

        info = d3arg.draw(
            width=320,
            height=240,
            tree_highlighting=False,
            show_mutations=False,
            is_notebook=True,
        )

        assert isinstance(info, argviz.DrawInfo)
        # Width/height may be adjusted internally (e.g., axis/title spacing),
        # so only assert broad sanity constraints here.
        assert float(info.width) >= 320
        assert float(info.height) >= 240
        assert info.uid.startswith("arg_")

        included_nodes = info.included.nodes
        assert isinstance(included_nodes, list)
        assert len(included_nodes) > 0
        assert set(included_nodes).issubset(set(d3arg.nodes["id"]))

    def test_draw_nodes_returns_drawinfo_without_opening_browser(self, monkeypatch):
        _, d3arg = _example_d3arg()

        monkeypatch.setattr(argviz, "display", lambda *_args, **_kwargs: None)

        info = d3arg.draw_nodes(
            seed_nodes=[d3arg.sample_order[0]],
            depth=1,
            width=320,
            height=240,
            tree_highlighting=False,
            show_mutations=False,
            is_notebook=True,
        )

        assert isinstance(info, argviz.DrawInfo)
        assert float(info.width) >= 320
        assert float(info.height) >= 240
        assert info.uid.startswith("arg_")

        included_nodes = info.included.nodes
        assert isinstance(included_nodes, list)
        assert len(included_nodes) > 0
        assert set(included_nodes).issubset(set(d3arg.nodes["id"]))

    def test_draw_genome_bar_smoke_notebook_mode(self, monkeypatch):
        _, d3arg = _example_d3arg()

        monkeypatch.setattr(argviz, "display", lambda *_args, **_kwargs: None)

        result = d3arg.draw_genome_bar(
            width=320,
            show_mutations=True,
            is_notebook=True,
        )
        assert result is None


class TestGraphSubsetSmoke:
    def test_from_ts_and_subset_graph_smoke(self):
        ts, d3arg = _example_d3arg()

        assert d3arg.num_samples == ts.num_samples
        assert not d3arg.nodes.empty
        assert not d3arg.edges.empty

        subset = d3arg.subset_graph(seed_nodes=[d3arg.sample_order[0]], depth=1)
        assert not subset.nodes.empty
        assert not subset.edges.empty

        node_ids = set(subset.nodes["id"].tolist())
        assert set(subset.edges["source"]).issubset(node_ids)
        assert set(subset.edges["target"]).issubset(node_ids)
        assert set(subset.mutations["edge"]).issubset(set(subset.edges["id"]))


class TestSecondaryPositionUtilities:
    def test_extract_x_positions_from_json_smoke(self):
        arg_no_labels = {
            "width": 500,
            "y_axis": {"include_labels": False},
            "data": {
                "nodes": [
                    {"id": 1, "x": 50},
                    {"id": 2, "x": 450},
                ]
            },
        }
        pos_no_labels = argviz.extract_x_positions_from_json(arg_no_labels)
        assert pos_no_labels[1] == pytest.approx(0.0)
        assert pos_no_labels[2] == pytest.approx(1.0)

        arg_with_labels = {
            "width": 500,
            "y_axis": {"include_labels": True},
            "data": {
                "nodes": [
                    {"id": 1, "x": 150},
                    {"id": 2, "x": 450},
                ]
            },
        }
        pos_with_labels = argviz.extract_x_positions_from_json(arg_with_labels)
        assert pos_with_labels[1] == pytest.approx(0.0)
        assert pos_with_labels[2] == pytest.approx(1.0)

    def test_calculate_evenly_distributed_positions_smoke(self):
        positions = argviz.calculate_evenly_distributed_positions(
            num_elements=5, start=0, end=1, round_to=3
        )
        assert len(positions) == 5
        assert positions[0] == 0
        assert positions[-1] == 1
        assert positions == sorted(positions)

        midpoint = argviz.calculate_evenly_distributed_positions(
            num_elements=1, start=10, end=20, round_to=3
        )
        assert midpoint == [15.0]

    def test_convert_time_to_position_monotonic_in_time_scale(self):
        y_shift = 7
        height = 200
        y_for_recent = argviz.convert_time_to_position(
            t=0,
            min_time=0,
            max_time=10,
            scale="time",
            unique_times=[0, 5, 10],
            h_spacing=0.5,
            height=height,
            y_shift=y_shift,
        )
        y_for_ancient = argviz.convert_time_to_position(
            t=10,
            min_time=0,
            max_time=10,
            scale="time",
            unique_times=[0, 5, 10],
            h_spacing=0.5,
            height=height,
            y_shift=y_shift,
        )
        assert y_for_ancient < y_for_recent

    def test_convert_time_to_position_rank_requires_known_time(self):
        with pytest.raises(RuntimeError):
            argviz.convert_time_to_position(
                t=3,
                min_time=0,
                max_time=10,
                scale="rank",
                unique_times=[0, 1, 2],
                h_spacing=0.5,
                height=100,
                y_shift=0,
            )
