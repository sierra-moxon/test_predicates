from src.treats import treats


def test_treats():
    treats.fetch_treats_examples()


def test_get_id_prefixes():
    treats.get_id_prefixes()


def test_query_endpoint():
    treats.query_endpoint()
