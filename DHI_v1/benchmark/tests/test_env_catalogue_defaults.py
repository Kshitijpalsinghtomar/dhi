import unittest

from DHI_v1.environment.dhi_env import DEFAULT_TOOL_CATALOGUE


class TestEnvironmentCatalogueDefaults(unittest.TestCase):
    def test_boolean_tool_schema_defaults_are_python_booleans(self):
        for tool in DEFAULT_TOOL_CATALOGUE:
            properties = tool.get("input_schema", {}).get("properties", {})
            for name, specification in properties.items():
                if specification.get("type") == "boolean" and "default" in specification:
                    self.assertIs(type(specification["default"]), bool,
                                  f"{tool['tool_id']}.{name} default must be a Python bool")

    def test_tool_reversibility_metadata_is_boolean(self):
        for tool in DEFAULT_TOOL_CATALOGUE:
            self.assertIs(type(tool.get("reversible")), bool,
                          f"{tool['tool_id']}.reversible must be a Python bool")
