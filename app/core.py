# -*- coding: utf-8 -*-
# MeeConf core: creates e-mail accounts for the Nokia N9 Mail app (Harmattan PR1.3).
# An account = one row in Accounts + settings rows in /home/user/.accounts/accounts.db
# (libaccounts, provider "email", service "genericemail"), the same keys the
# phone's own account wizard writes, plus one empty password entry in signond per
# protocol (imap4 / pop3 / smtp). With an empty entry the Mail app asks for the
# password on the first refresh, exactly as for an account created by hand.
# Python 2.6, no Qt here (testable on a PC).
# Designed and written by Claude (Anthropic) together with smyhu for Nokia N9. MIT licence.

import os
import re
import time
import shutil

ACC_DB = os.environ.get('MEECONF_ACC_DB', '/home/user/.accounts/accounts.db')
DOCS = os.environ.get('MEECONF_DOCS', '/home/user/MyDocs')
WORKDIR = os.path.join(DOCS, 'MeeConf')
SIGNON_NAMES = ('com.nokia.SingleSignOn', 'com.google.code.AccountsSSO.SingleSignOn')
SERVICE = 'genericemail'
PROTO = {'imap': 'imap4', 'pop': 'pop3'}
# QMF account status bit "preferred sender" (default account): 10236 vs 10204 on PR1.3
PREFERRED = 32

# default ports: (protocol, encryption) -> port; encryption 0 none, 1 SSL/TLS, 2 STARTTLS
PORTS = {('imap', 0): 143, ('imap', 1): 993, ('imap', 2): 143,
         ('pop', 0): 110, ('pop', 1): 995, ('pop', 2): 110,
         ('smtp', 0): 25, ('smtp', 1): 465, ('smtp', 2): 587}

# known providers: domain -> (incoming type, in server, in port, in enc, out server, out port, out enc)
PRESETS = {}
def _preset(domains, *v):
    for d in domains.split():
        PRESETS[d] = v
_preset('o2.pl tlen.pl go2.pl prokonto.pl', 'imap', 'poczta.o2.pl', 993, 1, 'poczta.o2.pl', 465, 1)
_preset('op.pl onet.pl onet.eu vp.pl poczta.onet.pl onet.com.pl spoko.pl autograf.pl buziaczek.pl',
        'imap', 'imap.poczta.onet.pl', 993, 1, 'smtp.poczta.onet.pl', 465, 1)
_preset('interia.pl interia.eu poczta.fm intmail.pl adresik.net vip.interia.pl pisz.to',
        'imap', 'poczta.interia.pl', 993, 1, 'poczta.interia.pl', 465, 1)
_preset('wp.pl', 'imap', 'imap.wp.pl', 993, 1, 'smtp.wp.pl', 465, 1)
_preset('gmail.com googlemail.com', 'imap', 'imap.gmail.com', 993, 1, 'smtp.gmail.com', 465, 1)
_preset('yahoo.com ymail.com', 'imap', 'imap.mail.yahoo.com', 993, 1, 'smtp.mail.yahoo.com', 465, 1)
_preset('icloud.com me.com mac.com', 'imap', 'imap.mail.me.com', 993, 1, 'smtp.mail.me.com', 587, 2)
_preset('gmx.net gmx.de', 'imap', 'imap.gmx.net', 993, 1, 'mail.gmx.net', 465, 1)
_preset('gmx.com', 'imap', 'imap.gmx.com', 993, 1, 'mail.gmx.com', 465, 1)
_preset('web.de', 'imap', 'imap.web.de', 993, 1, 'smtp.web.de', 587, 2)
_preset('aol.com', 'imap', 'imap.aol.com', 993, 1, 'smtp.aol.com', 465, 1)
_preset('zoho.com', 'imap', 'imap.zoho.com', 993, 1, 'smtp.zoho.com', 465, 1)
_preset('seznam.cz', 'imap', 'imap.seznam.cz', 993, 1, 'smtp.seznam.cz', 465, 1)
_preset('mail.ru inbox.ru list.ru bk.ru', 'imap', 'imap.mail.ru', 993, 1, 'smtp.mail.ru', 465, 1)
_preset('yandex.ru yandex.com', 'imap', 'imap.yandex.com', 993, 1, 'smtp.yandex.com', 465, 1)

ENC_WORDS = {'0': 0, 'none': 0, 'no': 0, 'off': 0, 'brak': 0, 'nie': 0, 'plain': 0,
             '1': 1, 'ssl': 1, 'tls/ssl': 1, 'ssl/tls': 1, 'yes': 1, 'tak': 1, 'on': 1,
             '2': 2, 'tls': 2, 'starttls': 2}
TYPE_WORDS = {'imap': 'imap', 'imap4': 'imap', 'pop': 'pop', 'pop3': 'pop'}


def u(x):
    if x is None:
        return u''
    if isinstance(x, buffer):
        x = str(x)
    if isinstance(x, str):
        return x.decode('utf-8', 'replace')
    return unicode(x)


def preset_for(email):
    dom = email.strip().lower().split('@')[-1] if '@' in email else ''
    v = PRESETS.get(dom)
    if not v:
        return None
    return {'in_type': v[0], 'in_server': v[1], 'in_port': v[2], 'in_ssl': v[3],
            'out_server': v[4], 'out_port': v[5], 'out_ssl': v[6], 'domain': dom}


def default_port(proto, enc):
    return PORTS.get((proto, int(enc)), 0)


# ------------------------------------------------------------------ database

def connect():
    import sqlite3
    if not os.path.exists(ACC_DB):
        raise IOError('missing ' + ACC_DB)
    con = sqlite3.connect(ACC_DB, timeout=10, isolation_level=None)
    con.text_factory = str
    return con


def service_id(con):
    r = con.execute("SELECT id FROM Services WHERE name=?", (SERVICE,)).fetchone()
    if not r:
        raise Exception('service %s not found in accounts.db' % SERVICE)
    return r[0]


def list_accounts():
    """All e-mail accounts of the native Mail app (provider email)."""
    con = connect()
    try:
        out = []
        for aid, name, enabled in con.execute(
                "SELECT id, name, enabled FROM Accounts WHERE provider='email' ORDER BY id").fetchall():
            s = {}
            for k, v in con.execute("SELECT key, value FROM Settings WHERE account=?", (aid,)):
                s[k] = u(v)
            t = 'pop' if s.get('incservertype', '').startswith('pop') else 'imap'
            p = PROTO[t]
            out.append({'id': aid, 'name': u(s.get('email/email_box_name') or name),
                        'email': s.get('emailaddress', u''), 'login': s.get(p + '/username', u''),
                        'in_type': t, 'in_server': s.get(p + '/server', u''),
                        'in_port': s.get(p + '/port', u''), 'in_ssl': s.get(p + '/encryption', u'0'),
                        'out_server': s.get('smtp/server', u''), 'out_port': s.get('smtp/port', u''),
                        'out_ssl': s.get('smtp/encryption', u'0'),
                        'out_login': s.get('smtp/username', u''),
                        'enabled': bool(enabled), 'password': (p + '/CredentialsId') in s,
                        'default': s.get('email/default', u'0') in (u'1', u'true')})
        return out
    finally:
        con.close()


def backup(con, tag):
    """Copy accounts.db (+ WAL files) while the caller holds the write lock."""
    bdir = os.path.join(WORKDIR, 'backup')
    if not os.path.isdir(bdir):
        os.makedirs(bdir)
    dst = os.path.join(bdir, 'accounts-%s-%s.db' % (tag, time.strftime('%Y%m%d-%H%M%S')))
    shutil.copyfile(ACC_DB, dst)
    for ext in ('-wal', '-shm'):
        if os.path.exists(ACC_DB + ext):
            shutil.copyfile(ACC_DB + ext, dst + ext)
    # keep the newest 10 backups
    olds = sorted([f for f in os.listdir(bdir) if f.endswith('.db')])
    for f in olds[:-10]:
        for ext in ('', '-wal', '-shm'):
            try:
                os.remove(os.path.join(bdir, f + ext))
            except OSError:
                pass
    return dst


# ------------------------------------------------------------------ validation

HOST_RE = re.compile(r'^[A-Za-z0-9]([A-Za-z0-9.-]*[A-Za-z0-9])?$')


def normalize(a):
    """Fills defaults and returns (account dict, error key or None)."""
    r = {}
    for k in ('name', 'email', 'login', 'in_server', 'out_server', 'out_login'):
        r[k] = u(a.get(k, u'')).strip()
    t = TYPE_WORDS.get(u(a.get('in_type', u'imap')).strip().lower() or 'imap')
    if not t:
        return r, 'errType'
    r['in_type'] = t
    for k, proto in (('in', t), ('out', 'smtp')):
        e = u(a.get(k + '_ssl', u'1')).strip().lower()
        if e == u'':
            e = u'1'
        if e not in ENC_WORDS:
            return r, 'errSsl'
        r[k + '_ssl'] = ENC_WORDS[e]
        p = u(a.get(k + '_port', u'')).strip()
        if p == u'':
            p = unicode(default_port(proto, r[k + '_ssl']))
        if not p.isdigit() or not 0 < int(p) < 65536:
            return r, 'errPort'
        r[k + '_port'] = int(p)
    r['default'] = u(a.get('default', u'')).strip().lower() in (u'1', u'yes', u'tak', u'true', u'x', u'*')
    if not r['email'] or '@' not in r['email']:
        return r, 'errEmail'
    pre = preset_for(r['email'])
    if pre and not r['in_server']:
        r['in_type'] = pre['in_type']
        r['in_server'], r['in_port'], r['in_ssl'] = pre['in_server'], pre['in_port'], pre['in_ssl']
    if pre and not r['out_server']:
        r['out_server'], r['out_port'], r['out_ssl'] = pre['out_server'], pre['out_port'], pre['out_ssl']
    if not r['login']:
        r['login'] = r['email']
    if not r['out_login']:
        r['out_login'] = r['login']
    if not r['name']:
        r['name'] = r['email']
    for k in ('in_server', 'out_server'):
        if not r[k]:
            return r, 'errServer'
        if not HOST_RE.match(r[k]):
            return r, 'errHost'
    # a port of another protocol makes Mail hang until timeout and ask for the
    # password again and again (IMAP on 995 gets a POP3 greeting)
    wrong_in = {'imap': (110, 995, 25, 465, 587), 'pop': (143, 993, 25, 465, 587)}
    if r['in_port'] in wrong_in[r['in_type']]:
        return r, 'errPortIn'
    if r['out_port'] in (110, 143, 993, 995):
        return r, 'errPortOut'
    return r, None


def exists(accounts, a):
    for x in accounts:
        if x['email'].lower() == a['email'].lower() and x['in_server'].lower() == a['in_server'].lower():
            return x
    return None


# ------------------------------------------------------------------ settings

def settings_for(a):
    """(service?, key, type, value) rows as written by the phone's wizard
    (taken from accounts created by hand on PR1.3)."""
    t = a['in_type']
    inp = PROTO[t]
    other = 'pop3' if inp == 'imap4' else 'imap4'
    G, S = 0, 1           # 0 = global settings, 1 = genericemail service
    rows = [
        (G, 'enabled', 'b', '1'),
        (G, 'name', 's', a['name']),
        (G, 'scheduler/schedule_enabled', 'b', '0'),
        (G, 'scheduler/schedule_off_peak', 'i', '-1'),
        (G, 'scheduler/schedule_peak', 'i', '60'),
        (G, 'scheduler/schedule_peak_days', 'i', '31'),
        (G, 'scheduler/schedule_peak_end_time', 'i', '1020'),
        (G, 'scheduler/schedule_peak_start_time', 'i', '540'),
        (G, 'username', 's', a['login']),
        (S, 'email/default', 'b', '1' if a.get('default') else '0'),
        (S, 'email/email_box_name', 's', a['name']),
        (S, 'emailaddress', 's', a['email']),
        (S, 'enabled', 'b', '1'),
        (S, 'fullName', 's', a['email']),
        (S, 'includeSignature', 'b', '1'),
        (S, 'incservertype', 's', t),
        (S, inp + '/autoDownload', 'i', '0' if t == 'imap' else '1'),
        (S, inp + '/encryption', 'i', str(a['in_ssl'])),
        (S, inp + '/maxSize', 'i', '0'),
        (S, inp + '/port', 's', str(a['in_port'])),
        (S, inp + '/server', 's', a['in_server']),
        (S, inp + '/servicetype', 's', 'source'),
        (S, inp + '/username', 's', a['login']),
        (S, other + '/autoDownload', 'i', '1'),
        (S, other + '/maxSize', 'i', '0'),
        (S, other + '/server', 's', a['in_server']),
        (S, other + '/servicetype', 's', ''),
        (S, other + '/username', 's', a['login']),
        (S, 'imap4/downloadAttachments', 'i', '0'),
        (S, 'imap4/version', 's', '100'),
        (S, 'qtopiamailfile/servicetype', 's', 'storage'),
        (S, 'qtopiamailfile/version', 's', '101'),
        (S, 'signature', 's', 'Sent from my N9'),
        (S, 'smtp/address', 's', a['email']),
        (S, 'smtp/authentication', 'i', '1'),
        (S, 'smtp/encryption', 'i', str(a['out_ssl'])),
        (S, 'smtp/port', 's', str(a['out_port'])),
        (S, 'smtp/server', 's', a['out_server']),
        (S, 'smtp/servicetype', 's', 'sink'),
        (S, 'smtp/smtpusername', 's', a['out_login']),
        (S, 'smtp/username', 's', a['out_login']),
        (S, 'smtp/version', 's', '100'),
        (S, 'status', 't', str((42972 if t == 'imap' else 10204) | (PREFERRED if a.get('default') else 0))),
        (S, 'type', 'i', '8'),
    ]
    return rows


# ------------------------------------------------------------------ signond

def _session_bus():
    import dbus
    if not os.environ.get('DBUS_SESSION_BUS_ADDRESS'):
        try:
            for line in open('/tmp/session_bus_address.user').read().splitlines():
                line = line.strip()
                if line.startswith('export '):
                    line = line[7:]
                if line.startswith('DBUS_SESSION_BUS_ADDRESS='):
                    os.environ['DBUS_SESSION_BUS_ADDRESS'] = line.split('=', 1)[1].strip("'\"")
        except IOError:
            pass
    return dbus.SessionBus()


class Signon(object):
    """Creates empty password entries, like the phone's wizard does."""

    def __init__(self):
        import dbus
        self.dbus = dbus
        self.bus = _session_bus()
        have = list(self.bus.list_names()) + list(self.bus.list_activatable_names())
        for n in SIGNON_NAMES:
            if n in have:
                path = '/com/nokia/SingleSignOn' if n == 'com.nokia.SingleSignOn' \
                    else '/com/google/code/AccountsSSO/SingleSignOn'
                self.name = n
                self.obj = self.bus.get_object(n, path)
                return
        raise Exception('signond not found')

    def new_identity(self, user):
        dbus = self.dbus
        path = self.obj.registerNewIdentity(dbus_interface=self.name + '.AuthService')
        if isinstance(path, tuple):
            path = path[0]
        ident = self.bus.get_object(self.name, path)
        info = dbus.Dictionary({
            'UserName': dbus.String(user),
            'Secret': dbus.String(''),
            'StoreSecret': dbus.Boolean(True),  # 'remember password', else lost on reboot
            'Caption': dbus.String('email'),
            'Realms': dbus.Array([], signature='s'),
            'AuthMethods': dbus.Dictionary(
                {'password': dbus.Array(['password'], signature='s', variant_level=1)}, signature='sv'),
            'ACL': dbus.Array([], signature='s'),
            'Type': dbus.Int32(0),
        }, signature='sv')
        nid = int(ident.store(info, dbus_interface=self.name + '.Identity'))
        if not nid:
            raise Exception('signond returned 0')
        return nid


# ------------------------------------------------------------------ create

def create(accounts, signon=None):
    """Creates the given (normalized) accounts. Returns a list of
    (account dict, new id or None, error text or None). One backup first."""
    results = []
    if not accounts:
        return results
    if signon is None:
        signon = Signon()
    con = connect()
    try:
        svc = service_id(con)
        con.execute('BEGIN IMMEDIATE')
        try:
            backup(con, 'meeconf')
        except Exception, e:
            con.execute('ROLLBACK')
            raise Exception('backup failed: %s' % e)
        con.execute('COMMIT')
        for a in accounts:
            try:
                creds = []
                for proto in (PROTO[a['in_type']], 'pop3' if a['in_type'] == 'imap' else 'imap4', 'smtp'):
                    user = a['out_login'] if proto == 'smtp' else a['login']
                    creds.append((proto, signon.new_identity(user)))
                con.execute('BEGIN IMMEDIATE')
                cur = con.execute("INSERT INTO Accounts (name, provider, enabled) VALUES (?, 'email', 1)",
                                  (a['name'],))
                aid = cur.lastrowid
                for g, key, typ, val in settings_for(a):
                    con.execute("INSERT INTO Settings (account, service, key, type, value) VALUES (?,?,?,?,?)",
                                (aid, svc if g else 0, key, typ, u(val)))
                for proto, nid in creds:
                    con.execute("INSERT INTO Settings (account, service, key, type, value) VALUES (?,?,?,?,?)",
                                (aid, svc, proto + '/CredentialsId', 'i', unicode(nid)))
                con.execute('COMMIT')
                results.append((a, aid, None))
            except Exception, e:
                try:
                    con.execute('ROLLBACK')
                except Exception:
                    pass
                results.append((a, None, u(str(e))))
    finally:
        con.close()
    # one default account: the one marked in the list, otherwise the first new
    # one when the phone has no default account at all (e.g. all were deleted)
    made = [(a, aid) for a, aid, err in results if aid]
    marked = [aid for a, aid in made if a.get('default')]
    try:
        if marked:
            set_default(marked[0])
        elif made and not has_default():
            set_default(made[0][1])
    except Exception:
        pass
    return results


def set_default(account_id):
    """Makes one account the default (preferred sender), clears the others."""
    con = connect()
    try:
        con.execute('BEGIN IMMEDIATE')
        try:
            backup(con, 'default')
            ids = [r[0] for r in con.execute("SELECT id FROM Accounts WHERE provider='email'")]
            if account_id not in ids:
                raise Exception('no such account')
            for aid in ids:
                on = aid == account_id
                con.execute("UPDATE Settings SET value=? WHERE account=? AND key='email/default'",
                            ('1' if on else '0', aid))
                r = con.execute("SELECT value FROM Settings WHERE account=? AND key='status'", (aid,)).fetchone()
                if r:
                    st = int(r[0])
                    st = (st | PREFERRED) if on else (st & ~PREFERRED)
                    con.execute("UPDATE Settings SET value=? WHERE account=? AND key='status'", (str(st), aid))
            con.execute('COMMIT')
        except Exception:
            con.execute('ROLLBACK')
            raise
    finally:
        con.close()


def has_default():
    return len([a for a in list_accounts() if a['default']]) > 0


# ------------------------------------------------------------------ CSV

CSV_ALIASES = {'template': None, 'name': 'name', 'account': 'name', 'email': 'email', 'address': 'email',
               'login': 'login', 'user': 'login', 'username': 'login',
               'type': 'in_type', 'in_type': 'in_type', 'protocol': 'in_type',
               'in_server': 'in_server', 'in_port': 'in_port', 'in_ssl': 'in_ssl',
               'out_server': 'out_server', 'out_port': 'out_port', 'out_ssl': 'out_ssl',
               'out_login': 'out_login', 'default': 'default'}
CSV_HEADER = 'name;email;login;in_type;in_server;in_port;in_ssl;out_server;out_port;out_ssl;out_login;default'


def csv_files():
    out = []
    for d in (DOCS, WORKDIR):
        try:
            names = os.listdir(d)
        except OSError:
            continue
        for f in sorted(names):
            if f.lower().endswith('.csv') and os.path.isfile(os.path.join(d, f)):
                out.append(os.path.join(d, f))
    return out


def parse_csv(path):
    """Returns (list of (line number, raw dict)), error key or None).
    UTF-8 or cp1250, separator ; or , (as Excel / OnlyOffice save it),
    lines whose first cell starts with # are comments."""
    import csv
    data = open(path, 'rb').read()
    if data.startswith('\xef\xbb\xbf'):
        data = data[3:]
    try:
        data.decode('utf-8')
    except UnicodeDecodeError:
        data = data.decode('cp1250').encode('utf-8')
    lines = data.replace('\r\n', '\n').replace('\r', '\n').split('\n')
    head_i = None
    for i, l in enumerate(lines):
        c = l.strip().lstrip('"').lower()
        if c.startswith('#') or not c:
            continue
        if c.startswith('name') or c.startswith('template') or c.startswith('email') or c.startswith('account'):
            head_i = i
        break
    if head_i is None:
        return [], 'errHeader'
    hl = lines[head_i]
    sep = ';' if hl.count(';') >= hl.count(',') else ','
    rows = []
    head = None
    for n, r in enumerate(csv.reader(lines[head_i:], delimiter=sep)):
        r = [c.strip() for c in r]
        if not r or not ''.join(r) or r[0].startswith('#'):
            continue
        if head is None:
            head = [CSV_ALIASES.get(c.lower(), '?' + c) for c in r]
            if 'email' not in head:
                return [], 'errHeader'
            continue
        d = {}
        for k, v in zip(head, r):
            if k and not k.startswith('?'):
                d[k] = v.decode('utf-8')
        rows.append((head_i + n + 1, d))
    return rows, None


def example_csv():
    """Writes MyDocs/MeeConf/accounts-example.csv once; returns its path."""
    p = os.path.join(WORKDIR, 'accounts-example.csv')
    if True:                      # always rewritten: the template follows the app version
        if not os.path.isdir(WORKDIR):
            os.makedirs(WORKDIR)
        f = open(p, 'w')
        f.write('# MeeConf - one line per e-mail account. Lines starting with # are skipped.\n'
                '# in_type: imap or pop; in_ssl / out_ssl: none, ssl (ports 993/995/465) or tls (STARTTLS, 143/110/587)\n'
                '# Empty cells: login = e-mail, ports from the encryption, servers of known providers filled in.\n'
                + CSV_HEADER + '\n'
                '# default: yes = the main account (shown first in Mail, used for sending); one account only.\n'
                'Work;john@example.com;john@example.com;imap;imap.example.com;993;ssl;smtp.example.com;465;ssl;;yes\n'
                'Private;someone@gmail.com;;;;;;;;;;\n')
        f.close()
    return p


ENC_NAMES = {0: 'none', 1: 'ssl', 2: 'tls'}


def export_csv():
    """Writes all Mail accounts (without passwords) to MyDocs/MeeConf/accounts-export-<date>.csv."""
    if not os.path.isdir(WORKDIR):
        os.makedirs(WORKDIR)
    p = os.path.join(WORKDIR, 'accounts-export-%s.csv' % time.strftime('%Y%m%d-%H%M%S'))
    rows = ['# MeeConf export %s - passwords are not exported' % time.strftime('%Y-%m-%d %H:%M'),
            CSV_HEADER]
    accs = list_accounts()
    for a in accs:
        def enc(v):
            try:
                return ENC_NAMES.get(int(v), 'ssl')
            except ValueError:
                return 'ssl'
        cells = [a['name'], a['email'], a['login'], a['in_type'], a['in_server'], a['in_port'],
                 enc(a['in_ssl']), a['out_server'], a['out_port'], enc(a['out_ssl']), a['out_login'],
                 'yes' if a['default'] else '']
        rows.append(u';'.join([u(c).replace(u';', u',') for c in cells]).encode('utf-8'))
    f = open(p, 'w')
    f.write('\xef\xbb\xbf' + '\n'.join([r if isinstance(r, str) else r.encode('utf-8') for r in rows]) + '\n')
    f.close()
    return p, len(accs)
