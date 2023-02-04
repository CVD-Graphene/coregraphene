#!/usr/bin/env python
import os
import sys


def main():
    os.environ.setdefault('GRAPHENE_SETTINGS_MODULE', 'settings.raspberry')
    from conf import settings

    print("CORGY", settings.CORGY)


if __name__ == '__main__':
    main()
