import sys

from django.core.management.base import BaseCommand, CommandError

from ietf.submit.mail import process_response_email

import debug                            # pyflakes:ignore

class Command(BaseCommand):
    help = (u"Process incoming manual post email responses")

    def add_arguments(self, parser):
        parser.add_argument('--email-file', dest='email', help='File containing email (default: stdin)')

    def handle(self, *args, **options):
        email = options.get('email', None)
        msg = None

        if not email:
            msg = sys.stdin.read()
        else:
            msg = open(email, "r").read()

        try:
            process_response_email(msg)
        except ValueError as e:
            raise CommandError(e)
