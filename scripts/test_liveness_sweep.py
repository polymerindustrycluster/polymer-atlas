"""No-network unit tests for scripts/liveness_sweep.py."""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import liveness_sweep as ls  # noqa: E402


class NormalizeTests(unittest.TestCase):
    def test_clean_forms(self):
        for raw in ("https://www.Example.com/about?x=1", "example.com", "http://example.com:8080/",
                    "WWW.EXAMPLE.COM/", "https://example.com."):
            self.assertEqual(ls.normalize_website(raw), ("example.com", "ok"), raw)

    def test_empty(self):
        self.assertEqual(ls.normalize_website(""), (None, "empty"))
        self.assertEqual(ls.normalize_website("   "), (None, "empty"))
        self.assertEqual(ls.normalize_website(None), (None, "empty"))

    def test_polluted(self):
        for raw in ("odm.com (parked - see notes)", "https://nissha.medical ; https://nissha.com",
                    "none found", "A2LA scope document", "https://hammillmedical.com;/",
                    "a.com, b.com"):
            self.assertEqual(ls.normalize_website(raw)[1], "polluted", raw)

    def test_invalid(self):
        for raw in ("none_found", "localhost", "https://-bad-.com/x", "1.2.3.4"):
            self.assertEqual(ls.normalize_website(raw)[1], "invalid", raw)

    def test_nfkc_ligature_and_idna(self):
        self.assertEqual(ls.normalize_website("polyﬁlinc.com")[0], "polyfilinc.com")
        self.assertEqual(ls.normalize_website("https://münchen.de/")[0], "xn--mnchen-3ya.de")

    def test_registered_domain(self):
        self.assertEqual(ls.registered_domain("a.b.example.com"), "example.com")
        self.assertEqual(ls.registered_domain("www.foo.co.uk"), "foo.co.uk")
        self.assertEqual(ls.registered_domain("example.com"), "example.com")

    def test_cross_domain(self):
        self.assertFalse(ls.is_cross_domain("example.com", "https://www.example.com/en/"))
        self.assertFalse(ls.is_cross_domain("example.com", "https://shop.example.com/"))
        self.assertTrue(ls.is_cross_domain("example.com", "https://newbrand.com/"))
        self.assertFalse(ls.is_cross_domain("example.com", ""))


class HeuristicTests(unittest.TestCase):
    def test_parked_phrases(self):
        self.assertTrue(ls.parked_markers("<h1>This domain is for sale</h1>"))
        self.assertTrue(ls.parked_markers("Buy this domain today"))
        self.assertTrue(ls.parked_markers("<a href='https://hugedomains.com/x'>"))
        self.assertTrue(ls.parked_markers("x", "https://sedoparking.com/frmpark"))

    def test_suspended_hosting(self):
        self.assertTrue(ls.parked_markers("<title>Account Suspended</title>"))
        self.assertTrue(ls.parked_markers("", "https://x.com/cgi-sys/suspendedpage.cgi"))
        self.assertTrue(ls.parked_markers("<title>ConnectYourDomain Error | Wix.com</title>"))

    def test_godaddy_only_for_short_lander(self):
        self.assertTrue(ls.parked_markers("<html>godaddy - this domain is parked"))
        big = "godaddy hosting footer " + ("lorem ipsum coming soon " * 2000)
        self.assertEqual(ls.parked_markers(big), [])

    def test_normal_page_not_parked(self):
        self.assertEqual(ls.parked_markers("<title>Acme Molding</title> injection molding since 1972"), [])

    def test_title_extraction(self):
        self.assertEqual(ls.extract_title("<TITLE>\n Acme &amp; Sons \n</title>"), "Acme & Sons")
        self.assertEqual(ls.extract_title("<p>none</p>"), "")

    def test_meta_refresh(self):
        h = '<meta http-equiv="refresh" content="0; url=https://new.example.org/">'
        self.assertEqual(ls.meta_refresh_target(h), "https://new.example.org/")
        self.assertIsNone(ls.meta_refresh_target("<p>x</p>"))

    def test_bot_markers(self):
        self.assertTrue(ls.bot_wall_markers(200, "Just a moment...", ""))
        self.assertTrue(ls.bot_wall_markers(503, "", "<div class='g-recaptcha'>"))
        self.assertEqual(ls.bot_wall_markers(200, "Acme", "<p>hi</p>"), [])


class ClassifyTests(unittest.TestCase):
    def base(self, **kw):
        r = {"dns": "ok", "error": None, "http_status": 200, "domain": "acme.com",
             "final_url": "https://www.acme.com/", "title": "Acme", "html": "<p>Acme</p>",
             "body_complete": True}
        r.update(kw)
        return r

    def test_ok(self):
        self.assertEqual(ls.classify(self.base()), "OK")

    def test_nxdomain(self):
        self.assertEqual(ls.classify(self.base(dns="nxdomain", http_status=None)), "NXDOMAIN")

    def test_cross_domain(self):
        self.assertEqual(ls.classify(self.base(final_url="https://other.com/")), "REDIRECT_CROSS_DOMAIN")

    def test_parked_beats_redirect(self):
        r = self.base(final_url="https://sedoparking.com/x", html="<p>x</p>")
        self.assertEqual(ls.classify(r), "PARKED_SUSPECT")

    def test_parked_on_404_body(self):
        self.assertEqual(ls.classify(self.base(http_status=404, html="This domain is for sale")), "PARKED_SUSPECT")

    def test_http_classes(self):
        self.assertEqual(ls.classify(self.base(http_status=404)), "HTTP_4XX")
        self.assertEqual(ls.classify(self.base(http_status=410)), "HTTP_4XX")
        self.assertEqual(ls.classify(self.base(http_status=500)), "HTTP_5XX")
        self.assertEqual(ls.classify(self.base(http_status=503, html="down")), "HTTP_5XX")

    def test_bot_wall(self):
        self.assertEqual(ls.classify(self.base(http_status=403)), "BOT_WALL_SUSPECT")
        self.assertEqual(ls.classify(self.base(http_status=429)), "BOT_WALL_SUSPECT")
        self.assertEqual(ls.classify(self.base(http_status=200, title="Just a moment...")), "BOT_WALL_SUSPECT")
        self.assertEqual(ls.classify(self.base(http_status=503, html="cf-challenge")), "BOT_WALL_SUSPECT")

    def test_errors(self):
        self.assertEqual(ls.classify(self.base(error="timeout", http_status=None)), "TIMEOUT")
        self.assertEqual(ls.classify(self.base(error="tls", http_status=None)), "TLS_ERROR")
        self.assertEqual(ls.classify(self.base(error="proxy", http_status=None)), "OTHER_ERROR")
        self.assertEqual(ls.classify(self.base(error="other", http_status=None)), "OTHER_ERROR")
        self.assertEqual(ls.classify(self.base(http_status=None)), "OTHER_ERROR")


class ErrKindTests(unittest.TestCase):
    def test_kinds(self):
        import socket
        import ssl
        import urllib.error as ue
        self.assertEqual(ls._err_kind(ue.URLError(socket.timeout("timed out")))[0], "timeout")
        self.assertEqual(ls._err_kind(ue.URLError(ssl.SSLError("CERTIFICATE_VERIFY_FAILED")))[0], "tls")
        self.assertEqual(ls._err_kind(ue.URLError(OSError("Tunnel connection failed: 502 Bad Gateway"))),
                         ("proxy", "proxy_tunnel_502"))
        self.assertEqual(ls._err_kind(ue.URLError(ConnectionRefusedError("refused")))[0], "other")


class TargetTests(unittest.TestCase):
    def row(self, i, status, web):
        return {"org_id": i, "legal_name": "N" + i, "shard": "OH", "status": status, "tier": "U", "website": web}

    def test_build_targets(self):
        rows = [self.row("1", "active", "https://www.a.com/x"), self.row("2", "unknown", "a.com"),
                self.row("3", "closed", "b.com"), self.row("4", "active", "none found"),
                self.row("5", "active", "none_found"), self.row("6", "active", ""),
                self.row("7", "active", "https://thomasnet.com/profile/x")]
        t, h, s = ls.build_targets(rows)
        self.assertEqual(list(t), ["a.com"])
        self.assertEqual(len(t["a.com"]), 2)
        self.assertEqual(len(h["polluted"]), 1)
        self.assertEqual(len(h["invalid"]), 1)
        self.assertEqual(len(h["shared_platform"]), 1)
        self.assertEqual(s["rows_skipped_status"], 1)
        self.assertEqual(s["rows_no_website"], 1)

    def test_sample_is_deterministic(self):
        doms = [f"d{i}.com" for i in range(100)]
        a = ls.deterministic_sample(doms, 10)
        self.assertEqual(a, ls.deterministic_sample(list(reversed(doms)), 10))
        self.assertEqual(len(a), 10)

    def test_user_agent_is_honest(self):
        self.assertTrue(ls.USER_AGENT.startswith("polymer-atlas-liveness/"))
        self.assertNotIn("Mozilla", ls.USER_AGENT)


if __name__ == "__main__":
    unittest.main()
