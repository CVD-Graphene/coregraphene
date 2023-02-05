#!/usr/bin/env python
import os
import sys
os.environ.setdefault('GRAPHENE_SETTINGS_MODULE', 'settings.raspberry')

from components.communication_methods import SerialAsciiCommunicationMethod


def main():
    from conf import settings

    settings1 = settings
    print("CORGY", settings1.CORGY)

    # obj = SerialAsciiCommunicationMethod()
    # obj._check_setup()


if __name__ == '__main__':
    main()
