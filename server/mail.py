"""Provides the Message class."""

import logging
from socket import getfqdn
from email.mime.text import MIMEText
from email.utils import formataddr
from twisted.mail.smtp import sendmail
from .db.server_options import ServerOptions

logger = logging.getLogger(__name__)
domain = getfqdn()


class Message(MIMEText):
    def send(self, recipients, subject=None):
        """Sends this email using local transport."""
        if subject is not None:
            self['Subject'] = subject
        self['To'] = ', '.join(recipients)
        o = ServerOptions.get()
        addr = o.mail_from_address
        sender = formataddr((o.mail_from_name, addr))
        self['From'] = sender
        d = sendmail(
            'localhost', addr, recipients, self, senderDomainName=domain
        ).addCallback(logger.info).addErrback(logger.error)
        return d
