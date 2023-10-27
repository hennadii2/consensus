import web.chat_gpt_plugin.app.endpoints.search.util as util


def test_make_details_url() -> None:
    actual = util.make_details_url(claim_id="1234", url_slug="test-slug")
    assert actual == "https://consensus.app/details/test-slug/1234/?utm_source=chatgpt"
