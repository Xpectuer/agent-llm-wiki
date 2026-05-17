import json

import pytest

from wiki_cli.convert import _parse_json


def test_plain_json_object():
    assert _parse_json('{"a": 1}') == {"a": 1}


def test_plain_json_array():
    assert _parse_json("[1, 2, 3]") == [1, 2, 3]


def test_json_in_fence():
    assert _parse_json('```json\n{"a": 1}\n```') == {"a": 1}


def test_json_in_fence_no_lang():
    assert _parse_json('```\n{"a": 1}\n```') == {"a": 1}


def test_json_buried_in_prose():
    text = 'Some reasoning text before.\n{"concepts": [{"name": "test"}], "ambiguities": []}\nMore text after.'
    result = _parse_json(text)
    assert result == {"concepts": [{"name": "test"}], "ambiguities": []}


def test_nested_objects():
    assert _parse_json('{"outer": {"inner": {"key": "value"}}}') == {
        "outer": {"inner": {"key": "value"}}
    }


def test_nested_arrays():
    assert _parse_json('{"items": [1, [2, 3], 4]}') == {"items": [1, [2, 3], 4]}


def test_array_with_nested_objects():
    assert _parse_json('[{"id": 1}, {"id": 2}]') == [{"id": 1}, {"id": 2}]


def test_empty_object():
    assert _parse_json("{}") == {}


def test_empty_array():
    assert _parse_json("[]") == []


def test_escaped_quotes():
    assert _parse_json('{"key": "value with \\"quotes\\""}') == {"key": 'value with "quotes"'}


def test_unicode_json():
    assert _parse_json('{"摘要": "Chinese value"}') == {"摘要": "Chinese value"}


def test_empty_string_raises_valueerror():
    with pytest.raises(ValueError, match="Empty response from LLM"):
        _parse_json("")


def test_invalid_no_json_raises():
    with pytest.raises(json.JSONDecodeError):
        _parse_json("This is just text, no JSON at all.")


def test_malformed_json_raises():
    with pytest.raises(json.JSONDecodeError):
        _parse_json('{"unclosed": ')


def test_truncated_json_raises():
    with pytest.raises(json.JSONDecodeError):
        _parse_json('{"key": "value')


def test_bracket_in_string_no_false_match():
    text = 'The result is: { "items": [1, 2, 3] }'
    assert _parse_json(text) == {"items": [1, 2, 3]}


def test_deepseek_style_output():
    text = '思考：需要提取概念。\n```json\n{"concepts": [{"name": "rlhf", "action": "create", "summary": "强化学习人类反馈"}], "ambiguities": []}\n```\n以上是提取结果。'
    result = _parse_json(text)
    assert result["concepts"][0]["name"] == "rlhf"


def test_realistic_concept_extract_response():
    text = (
        "我已经搜索了现有的wiki页面，以下是分析结果。\n\n"
        '{"concepts": [\n'
        '  {"name": "transformer", "action": "merge", "target_page": "transformer-architecture", "summary": "Transformer模型基础"},\n'
        '  {"name": "attention-mechanism", "action": "create", "target_page": null, "summary": "注意力机制详解"}\n'
        '], "ambiguities": [{"concept": "attention", "conflict": "多个页面已涉及attention", "resolution": "创建独立页面详细讲解"}]}'
    )
    result = _parse_json(text)
    assert len(result["concepts"]) == 2
    assert result["concepts"][0]["action"] == "merge"
    assert result["concepts"][1]["action"] == "create"
    assert len(result["ambiguities"]) == 1
