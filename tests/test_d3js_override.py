import io
import inspect
import unittest
from unittest import mock

import pandas as pd

import tskit_arg_visualizer
from tskit_arg_visualizer import D3ARG, draw_D3


class TestD3JsOverride(unittest.TestCase):
    def _displayed_html(self, call):
        return call.args[0].data

    def _minimal_arg_json(self):
        return {
            "data": {"nodes": [], "edges": [], "mutations": [], "breakpoints": []},
            "width": 100,
            "height": 100,
            "y_axis": {"include_labels": True},
            "edges": {"type": "line"},
            "condense_mutations": False,
            "label_mutations": False,
            "tree_highlighting": True,
            "title": "None",
            "rotate_tip_labels": False,
            "plot_type": "full",
        }

    def _minimal_d3arg(self):
        return D3ARG(
            nodes=pd.DataFrame(columns=["id", "time"]),
            edges=pd.DataFrame(columns=["source", "target", "bounds"]),
            mutations=pd.DataFrame(columns=["position_01"]),
            breakpoints=pd.DataFrame(
                [
                    {"start": 0.0, "stop": 1.0, "x_pos_01": 0.0, "width_01": 1.0, "fill": "#053e4e"}
                ]
            ),
            num_samples=0,
            sample_order=[],
            default_node_style={},
        )

    def test_draw_D3_default_uses_default_url(self):
        with mock.patch.object(tskit_arg_visualizer, "display") as display_mock:
            draw_D3(self._minimal_arg_json(), force_notebook=True)
        html = self._displayed_html(display_mock.call_args)
        self.assertIn("https://d3js.org/d3.v7.min", html)

    def test_public_draw_apis_accept_d3js_parameter(self):
        self.assertIn("d3js", inspect.signature(D3ARG.draw).parameters)
        self.assertIn("d3js", inspect.signature(D3ARG.draw_node).parameters)
        self.assertIn("d3js", inspect.signature(D3ARG.draw_nodes).parameters)
        self.assertIn("d3js", inspect.signature(D3ARG.draw_genome_bar).parameters)

    def test_draw_D3_uses_url_override(self):
        custom_url = "https://example.org/custom/d3.min"
        with mock.patch.object(tskit_arg_visualizer, "display") as display_mock:
            draw_D3(self._minimal_arg_json(), force_notebook=True, d3js=custom_url)
        html = self._displayed_html(display_mock.call_args)
        self.assertIn(custom_url, html)
        self.assertNotIn("https://d3js.org/d3.v7.min", html)

    def test_draw_D3_inlines_file_like_content(self):
        inline_js = b"window.d3 = {version: 'inline'};"
        with mock.patch.object(tskit_arg_visualizer, "display") as display_mock:
            draw_D3(self._minimal_arg_json(), force_notebook=True, d3js=io.BytesIO(inline_js))
        html = self._displayed_html(display_mock.call_args)
        self.assertIn("<script>window.d3 = {version: 'inline'};</script>", html)

    def test_draw_genome_bar_uses_d3js_override(self):
        d3arg = self._minimal_d3arg()
        custom_url = "https://example.org/alt/d3.min"
        with mock.patch.object(tskit_arg_visualizer, "display") as display_mock:
            d3arg.draw_genome_bar(force_notebook=True, d3js=custom_url)
        html = self._displayed_html(display_mock.call_args)
        self.assertIn(custom_url, html)

    def test_draw_genome_bar_inlines_file_like_content(self):
        d3arg = self._minimal_d3arg()
        with mock.patch.object(tskit_arg_visualizer, "display") as display_mock:
            d3arg.draw_genome_bar(force_notebook=True, d3js=io.StringIO("window.d3 = {};"))
        html = self._displayed_html(display_mock.call_args)
        self.assertIn("<script>window.d3 = {};</script>", html)

    def test_draw_genome_bar_default_uses_default_url(self):
        d3arg = self._minimal_d3arg()
        with mock.patch.object(tskit_arg_visualizer, "display") as display_mock:
            d3arg.draw_genome_bar(force_notebook=True)
        html = self._displayed_html(display_mock.call_args)
        self.assertIn("https://d3js.org/d3.v7.min", html)


if __name__ == "__main__":
    unittest.main()
