"""Authenticated, read-only SMB signing enforcement test for an authorized lab."""
import argparse
from getpass import getpass
from importlib.metadata import version

from impacket.smbconnection import SMBConnection, SessionError
from impacket.smb3structs import SMB2_DIALECT_21
from impacket.smb import FILE_READ_DATA, FILE_SHARE_READ, FILE_OPEN


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--server', required=True)
    parser.add_argument('--share', default='Confidential_Data')
    parser.add_argument('--file', default='SMB_SIGNING_TEST.txt')
    parser.add_argument('--user', default='student')
    parser.add_argument('--domain', default='')
    args = parser.parse_args()
    conn = None
    print('Impacket:', version('impacket'), '| Dialect: SMB 2.1')
    try:
        conn = SMBConnection(args.server, args.server, sess_port=445,
                             preferredDialect=SMB2_DIALECT_21, timeout=10)
        conn.login(args.user, getpass('Password: '), args.domain)
        smb = conn.getSMBServer()
        if not smb._Connection['RequireSigning']:
            raise RuntimeError('Server does not advertise required signing; check configuration.')
        smb._Session['SigningActivated'] = True
        tree_id = conn.connectTree(args.share)
        file_id = conn.openFile(tree_id, args.file, desiredAccess=FILE_READ_DATA,
                               shareMode=FILE_SHARE_READ, creationDisposition=FILE_OPEN)
        data = conn.readFile(tree_id, file_id, offset=0, bytesToRead=32)
        if not data:
            raise RuntimeError('Use a nonempty sample file for this test.')
        print('[1] Signed read succeeded:', len(data), 'bytes')
        input('Press Enter to send one unsigned Read Request...')
        smb._Session['SigningActivated'] = False
        try:
            data = conn.readFile(tree_id, file_id, offset=0, bytesToRead=32)
            print('[2] Unsigned read accepted:', len(data), 'bytes; inspect capture.')
        except SessionError as exc:
            print('[2] Server returned:', exc)
            print('Status:', hex(exc.getErrorCode()))
            if exc.getErrorCode() == 0xC0000022:
                print('ACCESS_DENIED observed; correlate with unsigned request in capture.')
        except Exception as exc:
            print('[2] Connection/client error:', type(exc).__name__, str(exc))
            print('Inconclusive without packet capture or server log.')
        finally:
            smb._Session['SigningActivated'] = True
    except Exception as exc:
        print('Setup/control read failed:', type(exc).__name__, str(exc))
        return 1
    finally:
        if conn is not None:
            try:
                conn.close()
            except Exception:
                pass
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
