from wiki_cli.convert import slugify


def test_simple_english():
    assert slugify("Hello World") == "hello-world"


def test_underscore_to_hyphen():
    assert slugify("hello_world") == "hello-world"


def test_chinese_characters():
    assert slugify("神经网络") == "神经网络"


def test_mixed_cn_en():
    assert slugify("Transformer 架构") == "transformer-架构"


def test_special_characters_stripped():
    assert slugify("hello!!!world") == "hello-world"


def test_multiple_spaces():
    assert slugify("hello   world") == "hello-world"


def test_leading_trailing_hyphens():
    assert slugify("-hello-") == "hello"


def test_empty_string():
    assert slugify("") == ""


def test_only_special_chars():
    assert slugify("!@#$%") == ""


def test_numbers_preserved():
    assert slugify("gpt-4-turbo") == "gpt-4-turbo"


def test_camel_case_to_lower():
    assert slugify("HelloWorld") == "helloworld"
