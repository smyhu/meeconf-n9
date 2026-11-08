import QtQuick 1.1
import com.nokia.meego 1.0
import "strings.js" as S

// New account by hand. Known providers fill in the servers from the e-mail address.
Page {
    id: page
    orientationLock: PageOrientation.LockPortrait
    property variant initial
    property string inType: "imap"
    property int inSsl: 1
    property int outSsl: 1
    property bool serversTouched: false

    function setInSsl(v) { inSsl = v; inPort.text = backend.defaultPort(inType, v); }
    function setOutSsl(v) { outSsl = v; outPort.text = backend.defaultPort("smtp", v); }
    function setType(t) { inType = t; inPort.text = backend.defaultPort(t, inSsl); }

    function applyPreset() {
        if (page.serversTouched)
            return;
        var t = backend.preset(email.text);
        if (t == "")
            return;
        var p = JSON.parse(t);
        page.inType = p.in_type; inServer.text = p.in_server; inPort.text = p.in_port; page.inSsl = p.in_ssl;
        outServer.text = p.out_server; outPort.text = p.out_port; page.outSsl = p.out_ssl;
        appWindow.showBanner(S.a(uiLang, "presetUsed", p.domain));
        page.serversTouched = true;
    }

    function create() {
        var a = { "name": name.text, "email": email.text, "login": login.text, "in_type": page.inType,
                  "in_server": inServer.text, "in_port": inPort.text, "in_ssl": "" + page.inSsl,
                  "out_server": outServer.text, "out_port": outPort.text, "out_ssl": "" + page.outSsl,
                  "out_login": outLogin.text, "default": isDefault.checked ? "yes" : "" };
        var r = JSON.parse(backend.createOne(JSON.stringify(a)));
        if (!r.ok) {
            appWindow.showBanner(S.err(uiLang, r.error));
            return;
        }
        appWindow.showBanner(S.a(uiLang, "created", r.name) + " " + S.t(uiLang, "passLater"));
        appWindow.accountsChanged();
        pageStack.pop();
    }

    Component.onCompleted: {
        if (page.initial) {
            var i = page.initial;
            if (i.email) { email.text = i.email; name.text = i.name; login.text = i.login; outLogin.text = i.out_login; }
            page.inType = i.in_type; inServer.text = i.in_server; inPort.text = i.in_port; page.inSsl = parseInt(i.in_ssl);
            outServer.text = i.out_server; outPort.text = i.out_port; page.outSsl = parseInt(i.out_ssl);
            page.serversTouched = true;
        } else {
            inPort.text = backend.defaultPort("imap", 1);
            outPort.text = backend.defaultPort("smtp", 1);
        }
    }

    Image { source: "background.png"; y: -36; smooth: false }
    Header { id: header; text: S.t(uiLang, "newAccount") }

    Flickable {
        id: flick
        anchors { top: header.bottom; left: parent.left; right: parent.right; bottom: parent.bottom }
        contentHeight: col.height + 40
        clip: true
        Column {
            id: col
            anchors { left: parent.left; right: parent.right; margins: 16 }
            y: 8
            spacing: 8

            Label { text: S.t(uiLang, "email"); color: "#b0b0b0"; font.pixelSize: 22 }
            TextField {
                id: email
                width: parent.width
                inputMethodHints: Qt.ImhEmailCharactersOnly | Qt.ImhNoPredictiveText | Qt.ImhNoAutoUppercase
                onActiveFocusChanged: if (!activeFocus) page.applyPreset()
            }
            Label { text: S.t(uiLang, "accName"); color: "#b0b0b0"; font.pixelSize: 22 }
            TextField {
                id: name
                width: parent.width
                placeholderText: email.text
                inputMethodHints: Qt.ImhNoPredictiveText
            }
            Label { text: S.t(uiLang, "login"); color: "#b0b0b0"; font.pixelSize: 22 }
            TextField {
                id: login
                width: parent.width
                placeholderText: email.text
                inputMethodHints: Qt.ImhNoPredictiveText | Qt.ImhNoAutoUppercase
            }

            Row {
                width: parent.width
                spacing: 16
                CheckBox { id: isDefault }
                Label {
                    width: parent.width - isDefault.width - 16
                    anchors.verticalCenter: isDefault.verticalCenter
                    text: S.t(uiLang, "defaultBox")
                    wrapMode: Text.WordWrap
                    MouseArea { anchors.fill: parent; onClicked: isDefault.checked = !isDefault.checked }
                }
            }

            SectionLabel { text: S.t(uiLang, "incoming") }
            ButtonRow {
                width: parent.width
                Button { text: "IMAP"; checked: page.inType == "imap"; onClicked: page.setType("imap") }
                Button { text: "POP3"; checked: page.inType == "pop"; onClicked: page.setType("pop") }
            }
            Label { text: S.t(uiLang, "server"); color: "#b0b0b0"; font.pixelSize: 22 }
            TextField {
                id: inServer
                width: parent.width
                inputMethodHints: Qt.ImhUrlCharactersOnly | Qt.ImhNoPredictiveText | Qt.ImhNoAutoUppercase
                onTextChanged: if (activeFocus) page.serversTouched = true
            }
            Label { text: S.t(uiLang, "security"); color: "#b0b0b0"; font.pixelSize: 22 }
            ButtonRow {
                width: parent.width
                Button { text: S.t(uiLang, "encNone"); checked: page.inSsl == 0; onClicked: page.setInSsl(0) }
                Button { text: "SSL"; checked: page.inSsl == 1; onClicked: page.setInSsl(1) }
                Button { text: "STARTTLS"; checked: page.inSsl == 2; onClicked: page.setInSsl(2) }
            }
            Label { text: S.t(uiLang, "port"); color: "#b0b0b0"; font.pixelSize: 22 }
            TextField {
                id: inPort
                width: 160
                inputMethodHints: Qt.ImhDigitsOnly
            }

            SectionLabel { text: S.t(uiLang, "outgoing") }
            Label { text: S.t(uiLang, "server"); color: "#b0b0b0"; font.pixelSize: 22 }
            TextField {
                id: outServer
                width: parent.width
                inputMethodHints: Qt.ImhUrlCharactersOnly | Qt.ImhNoPredictiveText | Qt.ImhNoAutoUppercase
                onTextChanged: if (activeFocus) page.serversTouched = true
            }
            Label { text: S.t(uiLang, "security"); color: "#b0b0b0"; font.pixelSize: 22 }
            ButtonRow {
                width: parent.width
                Button { text: S.t(uiLang, "encNone"); checked: page.outSsl == 0; onClicked: page.setOutSsl(0) }
                Button { text: "SSL"; checked: page.outSsl == 1; onClicked: page.setOutSsl(1) }
                Button { text: "STARTTLS"; checked: page.outSsl == 2; onClicked: page.setOutSsl(2) }
            }
            Label { text: S.t(uiLang, "port"); color: "#b0b0b0"; font.pixelSize: 22 }
            TextField {
                id: outPort
                width: 160
                inputMethodHints: Qt.ImhDigitsOnly
            }
            Label { text: S.t(uiLang, "outLogin"); color: "#b0b0b0"; font.pixelSize: 22 }
            TextField {
                id: outLogin
                width: parent.width
                placeholderText: login.text != "" ? login.text : email.text
                inputMethodHints: Qt.ImhNoPredictiveText | Qt.ImhNoAutoUppercase
            }
        }
    }
    ScrollDecorator { flickableItem: flick }

    tools: ToolBarLayout {
        ToolIcon { iconId: "toolbar-back"; onClicked: pageStack.pop() }
        ToolButton {
            text: S.t(uiLang, "create")
            anchors.centerIn: parent
            onClicked: page.create()
        }
    }
}
