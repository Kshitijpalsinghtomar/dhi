from DHI_v1.environment.dhi_env import DEFAULT_TOOL_CATALOGUE


def test_boolean_tool_schema_defaults_are_python_booleans():
    for tool in DEFAULT_TOOL_CATALOGUE:
        properties = tool.get("input_schema", {}).get("properties", {})
        for name, specification in properties.items():
            if specification.get("type") == "boolean" and "default" in specification:
                assert type(specification["default"]) is bool, (
                    f"{tool['tool_id']}.{name} default must be a Python bool"
                )


def test_tool_reversibility_metadata_is_boolean():
    for tool in DEFAULT_TOOL_CATALOGUE:
        assert type(tool.get("reversible")) is bool, (
            f"{tool['tool_id']}.reversible must be a Python bool"
        )
