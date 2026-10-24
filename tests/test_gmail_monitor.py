"""Offline regression tests for the IMAP TLS connection."""

import imaplib
import ssl
import unittest
from configparser import ConfigParser
from unittest.mock import Mock, patch

from gmail_monitor import GmailMonitor


class GmailMonitorTLSTests(unittest.TestCase):
    def setUp(self):
        config = ConfigParser()
        config.read_dict(
            {"Gmail": {"email": "offline@example.invalid", "password": "dummy pass"}}
        )
        self.monitor = GmailMonitor(config)
        # A regression must never make a network connection during these tests.
        network = patch(
            "socket.create_connection", side_effect=AssertionError("Network forbidden")
        )
        network.start()
        self.addCleanup(network.stop)

    def assert_secure_context(self, context):
        self.assertIsInstance(context, ssl.SSLContext)
        self.assertEqual(context.verify_mode, ssl.CERT_REQUIRED)
        self.assertTrue(context.check_hostname)

    def test_connect_verifies_server_before_login(self):
        with patch("gmail_monitor.imaplib.IMAP4_SSL") as client:
            self.assertTrue(self.monitor.connect())

        client.assert_called_once()
        self.assertEqual(client.call_args.args, ("imap.gmail.com", 993))
        self.assert_secure_context(client.call_args.kwargs["ssl_context"])
        client.return_value.login.assert_called_once_with(
            "offline@example.invalid", "dummypass"
        )
        self.assertIs(self.monitor.imap, client.return_value)

    def test_tls_rejection_prevents_login_and_insecure_retry(self):
        # Exercise real imaplib TLS setup with a mocked socket and handshake.
        # No real certificate, server, mailbox, or network connection is used.
        for reason in ("untrusted issuer", "hostname mismatch"):
            with self.subTest(reason=reason):
                fake_socket = Mock()
                error = ssl.SSLCertVerificationError(1, reason)
                with (
                    patch.object(
                        imaplib.IMAP4, "_create_socket", return_value=fake_socket
                    ) as create_socket,
                    patch.object(
                        ssl.SSLContext, "wrap_socket", autospec=True, side_effect=error
                    ) as handshake,
                    patch.object(imaplib.IMAP4, "login") as login,
                    self.assertLogs("gmail_monitor", level="ERROR"),
                ):
                    with self.assertRaisesRegex(Exception, reason):
                        self.monitor.connect()

                create_socket.assert_called_once()
                handshake.assert_called_once()
                self.assert_secure_context(handshake.call_args.args[0])
                self.assertIs(handshake.call_args.args[1], fake_socket)
                self.assertEqual(
                    handshake.call_args.kwargs["server_hostname"], "imap.gmail.com"
                )
                login.assert_not_called()
                self.assertIsNone(self.monitor.imap)

    def test_context_failure_does_not_connect(self):
        with (
            patch(
                "gmail_monitor.ssl.create_default_context",
                side_effect=ssl.SSLError("Unable to load trusted certificates"),
            ),
            patch("gmail_monitor.imaplib.IMAP4_SSL") as client,
            self.assertLogs("gmail_monitor", level="ERROR"),
        ):
            with self.assertRaisesRegex(
                Exception, "Unable to load trusted certificates"
            ):
                self.monitor.connect()

        client.assert_not_called()
        self.assertIsNone(self.monitor.imap)


if __name__ == "__main__":
    unittest.main()
