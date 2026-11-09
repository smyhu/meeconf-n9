#!/usr/bin/python
# -*- coding: utf-8 -*-
# MeeConf - bulk setup of e-mail accounts for the Nokia N9 Mail app
# (by hand or from a CSV file). Python 2.6 + PySide + QML.
# Designed and written by Claude (Anthropic) together with smyhu for Nokia N9. MIT licence.

import os
import sys
import json
import subprocess

from PySide.QtCore import QObject, QUrl, Slot
from PySide.QtGui import QApplication
from PySide.QtDeclarative import QDeclarativeView

APP_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, APP_DIR)
import core

APP_VERSION = '0.1.4'
BUS_NAME = 'com.github.smyhu.meeconf'
LANGUAGES = ('pl', 'en')


def session_env():
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


def phone_language():
    code = os.environ.get('MEECONF_LANG', '')
    if not code:
        session_env()
        try:
            p = subprocess.Popen(['gconftool-2', '-g', '/meegotouch/i18n/language'],
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            code = p.communicate()[0].strip()
        except OSError:
            pass
    code = (code or os.environ.get('LANG', ''))[:2].lower()
    return code if code in LANGUAGES else 'en'


def js(obj):
    return unicode(json.dumps(obj))


class Backend(QObject):
    """QML gets everything as JSON text (PySide 1.0.7 cannot pass Python
    dicts or signal arguments to QML)."""

    def __init__(self):
        QObject.__init__(self)
        self.pending = []
        self.signon = None

    def _signon(self):
        if self.signon is None:
            self.signon = core.Signon()
        return self.signon

    @Slot(result=unicode)
    def accounts(self):
        try:
            return js({'ok': True, 'items': core.list_accounts()})
        except Exception, e:
            return js({'ok': False, 'error': unicode(str(e), 'utf-8', 'replace')})

    @Slot(unicode, result=unicode)
    def preset(self, email):
        p = core.preset_for(email)
        return js(p) if p else u''

    @Slot(unicode, int, result=int)
    def defaultPort(self, proto, enc):
        return core.default_port(str(proto), enc)

    @Slot(unicode, result=unicode)
    def createOne(self, text):
        a, err = core.normalize(json.loads(text))
        if err:
            return js({'ok': False, 'error': err})
        try:
            if core.exists(core.list_accounts(), a):
                return js({'ok': False, 'error': 'errExists'})
            r = core.create([a], self._signon())[0]
        except Exception, e:
            return js({'ok': False, 'error': unicode(str(e), 'utf-8', 'replace')})
        if r[2]:
            return js({'ok': False, 'error': r[2]})
        return js({'ok': True, 'id': r[1], 'name': a['name']})

    @Slot(int, result=unicode)
    def setDefault(self, account_id):
        try:
            core.set_default(account_id)
            return js({'ok': True})
        except Exception, e:
            return js({'ok': False, 'error': unicode(str(e), 'utf-8', 'replace')})

    @Slot(result=unicode)
    def csvFiles(self):
        core.example_csv()
        out = []
        for p in core.csv_files():
            out.append({'path': p.decode('utf-8', 'replace'),
                        'name': os.path.basename(p).decode('utf-8', 'replace'),
                        'dir': p[len(core.DOCS):].rsplit('/', 1)[0].lstrip('/').decode('utf-8', 'replace')})
        return js(out)

    @Slot(unicode, result=unicode)
    def parseCsv(self, path):
        self.pending = []
        try:
            rows, err = core.parse_csv(path.encode('utf-8'))
            accs = core.list_accounts()
        except Exception, e:
            return js({'error': unicode(str(e), 'utf-8', 'replace'), 'rows': []})
        if err:
            return js({'error': err, 'rows': []})
        out = []
        seen = []
        for line, raw in rows:
            a, e = core.normalize(raw)
            st = 'ok'
            if e:
                st = e
            elif core.exists(accs, a) or core.exists(seen, a):
                st = 'errExists'
            else:
                self.pending.append(a)
                seen.append(a)
            out.append({'line': line, 'state': st, 'name': a.get('name', u''), 'email': a.get('email', u''),
                        'in_type': a.get('in_type', u''), 'in_server': a.get('in_server', u'')})
        return js({'error': None, 'rows': out, 'count': len(self.pending)})

    @Slot(result=unicode)
    def importPending(self):
        todo, self.pending = self.pending, []
        try:
            res = core.create(todo, self._signon())
        except Exception, e:
            return js({'created': 0, 'failed': [{'name': u'', 'error': unicode(str(e), 'utf-8', 'replace')}]})
        failed = [{'name': a['name'], 'error': err} for a, aid, err in res if err]
        return js({'created': len([1 for a, aid, err in res if not err]), 'failed': failed})

    @Slot(result=unicode)
    def exportCsv(self):
        try:
            p, n = core.export_csv()
            return js({'ok': True, 'path': p[len(core.DOCS) + 1:].decode('utf-8', 'replace'), 'count': n})
        except Exception, e:
            return js({'ok': False, 'error': unicode(str(e), 'utf-8', 'replace')})

    @Slot(result=unicode)
    def examplePath(self):
        try:
            return core.example_csv()[len(core.DOCS) + 1:].decode('utf-8', 'replace')
        except Exception, e:
            return u''


class Window(object):
    """Only one copy of the app; a second start brings the first to the front."""

    def __init__(self):
        self.view = None
        self.bus = None
        try:
            import dbus
            import dbus.service
            from dbus.mainloop.glib import DBusGMainLoop
        except ImportError, e:
            print 'meeconf: no D-Bus:', e
            return
        DBusGMainLoop(set_as_default=True)
        session_env()
        bus = dbus.SessionBus()
        if bus.request_name(BUS_NAME, dbus.bus.NAME_FLAG_DO_NOT_QUEUE) != dbus.bus.REQUEST_NAME_REPLY_PRIMARY_OWNER:
            self.bus = bus
            return
        owner = self

        class Service(dbus.service.Object):
            @dbus.service.method(BUS_NAME, in_signature='', out_signature='')
            def top(self):
                owner.top()

        self.service = Service(bus, '/')

    def running_elsewhere(self):
        if not self.bus:
            return False
        try:
            self.bus.get_object(BUS_NAME, '/').top(dbus_interface=BUS_NAME)
        except Exception, e:
            print 'meeconf: cannot reach the running copy:', e
        return True

    def top(self):
        if self.view:
            self.view.showFullScreen()
            self.view.raise_()
            self.view.activateWindow()


def main():
    os.environ.setdefault('DISPLAY', ':0')
    app = QApplication(sys.argv)
    app.setApplicationName('meeconf')
    app.setOrganizationName('meeconf')
    window = Window()
    if window.running_elsewhere():
        return
    view = QDeclarativeView()
    backend = Backend()
    ctx = view.rootContext()
    ctx.setContextProperty('uiLang', phone_language())
    ctx.setContextProperty('appVersion', APP_VERSION)
    ctx.setContextProperty('backend', backend)
    view.setResizeMode(QDeclarativeView.SizeRootObjectToView)
    view.setSource(QUrl.fromLocalFile(os.path.join(APP_DIR, 'qml', 'main.qml')))
    view.showFullScreen()
    window.view = view
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
