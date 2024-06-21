from seleniumbase import SB

from tests.utils import get_uri_for_html


def zpg_logic(sb, button):
    # attempt to join zpg arena
    sb.click(button)
    alert_text = sb.switch_to_alert().text

    if "zpg" in alert_text:
        sb.accept_alert()
        try:
            # if there are second alert, dismiss it and leave it
            second_alert_text = sb.switch_to_alert(2).text
            sb.dismiss_alert()
            return second_alert_text
        except Exception:
            # success, joining a zpg arena
            return None
    else:
        # it's no zpg for some reason
        sb.dismiss_alert()
        return alert_text


def test_zpg_alerts():
    with SB(uc=True, headless2=True) as sb:
        page_url = get_uri_for_html("pages/zpg_confirm.html")
        sb.open(page_url)

        # Test case 1: Arena button
        result = zpg_logic(sb, "#button1")
        assert result == "arena", f"Expected 'arena', but got {result}"

        # Test case 2: ZPG arena button
        result = zpg_logic(sb, "#button2")
        assert result is None, f"Expected no second alert, but got {result}"

        # Test case 3: ZPG arena button, but late and should get usual arena
        result = zpg_logic(sb, "#button3")
        assert result == "no_zpg_arena", f"Expected 'no_zpg_arena', but got {result}"
