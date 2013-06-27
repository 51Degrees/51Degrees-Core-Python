# -*- coding: utf-8 -*-

'''
:copyright: (c) 2013 by 51Degrees.mobi, see README.rst for more details.
:license: MPL2, see LICENSE.txt for more details.
'''

from __future__ import absolute_import
import os
import sys
import subprocess


def settings(args, help):
    import inspect
    from fiftyone_degrees.mobile_detector.conf import default
    sys.stdout.write(inspect.getsource(default))


def match(args, help):
    if len(args) == 1:
        from fiftyone_degrees import mobile_detector
        device = mobile_detector.match(args[0])
        for name, value in device.properties.iteritems():
            sys.stdout.write('%s: %s\n' % (name, unicode(value),))
    else:
        sys.stderr.write(help)
        sys.exit(1)


def update_premium_pattern_wrapper(args, help):
    import tempfile
    import urllib2
    from fiftyone_degrees.mobile_detector.conf import settings

    if settings.LICENSE:
        # Build source URL.
        url = 'https://51degrees.mobi/Products/Downloads/Premium.aspx?LicenseKeys=%s&Type=Python&Download=True' % (
            settings.LICENSE
        )

        # Download & install package.
        with tempfile.NamedTemporaryFile(
                suffix='.tar.gz',
                prefix='51Degrees-premium-pattern-wrapper-',
                delete=False) as fh:
            delete = True
            try:
                # Fetch URL (no verification of the server's certificate here).
                uh = urllib2.urlopen(url, timeout=120)
                meta = uh.info()

                # Check server response.
                if meta.getheader('Content-Disposition') is not None:
                    # Download the package.
                    file_size = int(meta.getheader('Content-Length'))
                    sys.stdout.write('=> Downloading %s bytes... ' % file_size)
                    downloaded = 0
                    while True:
                        buffer = uh.read(8192)
                        if buffer:
                            downloaded += len(buffer)
                            fh.write(buffer)
                            status = r'%3.2f%%' % (downloaded * 100.0 / file_size)
                            status = status + chr(8) * (len(status) + 1)
                            print status,
                        else:
                            break
                    fh.close()

                    # Try to update the package.
                    sys.stdout.write('\n=> Updating the package...\n')
                    updated = False
                    try:
                        updated = (subprocess.call('pip install "%s" --upgrade' % fh.name, shell=True) == 0)
                    except:
                        pass
                    finally:
                        if updated:
                            sys.stdout.write('=> The package has  been successfully updated!\n')
                        else:
                            delete = False
                            sys.stderr.write(
                                'Failed to update the package. The downloaded package has been stored in %s.\n' % fh.name)
                else:
                    sys.stderr.write('Failed to download the package: is your license key expired?\n')
            except Exception as e:
                sys.stderr.write('Failed to download the package: %s.\n' % unicode(e))
            finally:
                # Delete temporary file.
                if delete:
                    try:
                        os.remove(fh.name)
                    except:
                        pass
    else:
        sys.stderr.write('Failed to download the package: you need a license key. Please, check you settings.\n')


def main():
    # Build help message.
    help = '''Usage:

  %(cmd)s settings:
      Dumps sample settings file.

  %(cmd)s match <user agent>
      Fetches device properties based on the input user agent string.

  %(cmd)s update-premium-pattern-wrapper
      Downloads and installs latest premium pattern wrapper package available
      at 51Degrees.mobi website (a valid license key is required).

''' % {
        'cmd': os.path.basename(sys.argv[0])
    }

    # Check base arguments.
    if len(sys.argv) > 1:
        command = sys.argv[1].replace('-', '_')
        if command in ('settings', 'match', 'update_premium_pattern_wrapper'):
            getattr(sys.modules[__name__], command)(sys.argv[2:], help)
        else:
            sys.stderr.write(help)
            sys.exit(1)
    else:
        sys.stderr.write(help)
        sys.exit(1)


if __name__ == '__main__':
    main()
