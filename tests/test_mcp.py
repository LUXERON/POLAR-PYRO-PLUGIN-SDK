from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from polar_pyro_plugin_sdk.mcp import McpStdioDescriptor, require_tool_subset
from polar_pyro_plugin_sdk.models import ContractError


class McpTests(unittest.TestCase):
    def test_command_is_argument_vector(self):
        descriptor = McpStdioDescriptor("obscura-mcp", ("--stdio",))
        self.assertEqual(descriptor.command(), ("obscura-mcp", "--stdio"))

    def test_newline_argument_rejected(self):
        with self.assertRaises(ContractError):
            McpStdioDescriptor("tool", ("safe\nunsafe",)).command()

    def test_undeclared_runtime_tool_rejected(self):
        with self.assertRaisesRegex(ContractError, "undeclared tools"):
            require_tool_subset(["browser.snapshot", "filesystem.erase"], ["browser.snapshot"])


if __name__ == "__main__":
    unittest.main()
