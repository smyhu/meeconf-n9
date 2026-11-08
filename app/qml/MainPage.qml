import QtQuick 1.1
import com.nokia.meego 1.0
import "strings.js" as S

// List of the Mail app's accounts. Tap = details, with "new account with these servers".
Page {
    id: page
    orientationLock: PageOrientation.LockPortrait
    property int total: 0
    property bool failed: false
    property variant current

    function encName(v) {
        return v == "1" ? "SSL" : (v == "2" ? "STARTTLS" : S.t(uiLang, "encNone"));
    }
    function reload() {
        model.clear();
        var r = JSON.parse(backend.accounts());
        page.failed = !r.ok;
        if (!r.ok) {
            errorText.text = S.t(uiLang, "readError") + "\n" + r.error;
            page.total = 0;
            return;
        }
        for (var i = 0; i < r.items.length; ++i)
            model.append({ "json": JSON.stringify(r.items[i]), "name": r.items[i].name,
                           "email": r.items[i].email, "kind": r.items[i].in_type == "pop" ? "POP3" : "IMAP",
                           "server": r.items[i].in_server, "password": r.items[i].password,
                           "isDefault": r.items[i]["default"], "accId": r.items[i].id });
        page.total = r.items.length;
    }
    Component.onCompleted: reload()

    Image { source: "background.png"; y: -36; smooth: false }
    Header {
        id: header
        text: "MeeConf"
        subText: S.a(uiLang, "subtitle", page.total)
    }
    ListModel { id: model }

    Rectangle {
        id: restartBar
        visible: appWindow.restartNeeded
        anchors { top: header.bottom; left: parent.left; right: parent.right }
        height: visible ? restartLabel.height + 24 : 0
        color: "#2a3a1c"
        Label {
            id: restartLabel
            anchors { left: parent.left; right: parent.right; margins: 16; verticalCenter: parent.verticalCenter }
            text: S.t(uiLang, "restart")
            color: appWindow.accent
            font.pixelSize: 22
            wrapMode: Text.WordWrap
        }
    }

    ListView {
        id: list
        anchors { top: restartBar.bottom; left: parent.left; right: parent.right; bottom: parent.bottom }
        clip: true
        model: model
        delegate: Item {
            width: list.width
            height: 96
            Rectangle {
                anchors.fill: parent
                color: "#ffffff"
                opacity: mouse.pressed ? 0.12 : 0
            }
            Column {
                anchors { left: parent.left; right: parent.right; leftMargin: 16; rightMargin: 16; verticalCenter: parent.verticalCenter }
                Label {
                    width: parent.width
                    text: model.name + (model.isDefault ? "  <font color=\"#cfeca0\">★ " + S.t(uiLang, "isDefault") + "</font>" : "")
                    font.pixelSize: 26
                    font.bold: true
                    elide: Text.ElideRight
                }
                Label {
                    width: parent.width
                    text: model.email
                    font.pixelSize: 22
                    color: "#d0d0d0"
                    elide: Text.ElideRight
                }
                Label {
                    width: parent.width
                    text: model.kind + " · " + model.server + (model.password ? "" : " · " + S.t(uiLang, "noPassword"))
                    font.pixelSize: 18
                    color: "#8c8c8c"
                    elide: Text.ElideRight
                }
            }
            Rectangle { anchors.bottom: parent.bottom; width: parent.width; height: 1; color: "#222222" }
            MouseArea {
                id: mouse
                anchors.fill: parent
                onClicked: {
                    page.current = JSON.parse(model.json);
                    var a = page.current;
                    details.titleText = a.name;
                    details.message = a.email + "\n\n"
                        + (a.in_type == "pop" ? "POP3" : "IMAP") + ": " + a.in_server + ":" + a.in_port + " · " + page.encName(a.in_ssl)
                        + "\n" + S.t(uiLang, "login").split(" (")[0] + ": " + a.login
                        + "\n\nSMTP: " + a.out_server + ":" + a.out_port + " · " + page.encName(a.out_ssl)
                        + "\n" + S.t(uiLang, "login").split(" (")[0] + ": " + a.out_login;
                    details.open();
                }
                onPressAndHold: {
                    page.current = JSON.parse(model.json);
                    ctx.open();
                }
            }
        }
    }
    ScrollDecorator { flickableItem: list }

    Label {
        id: errorText
        visible: page.total == 0
        anchors { left: parent.left; right: parent.right; margins: 32; verticalCenter: parent.verticalCenter }
        horizontalAlignment: Text.AlignHCenter
        wrapMode: Text.WordWrap
        color: "#8c8c8c"
        font.pixelSize: 26
        text: S.t(uiLang, "empty")
    }

    QueryDialog {
        id: details
        acceptButtonText: S.t(uiLang, "useAsBase")
        rejectButtonText: S.t(uiLang, "close")
        onAccepted: {
            var a = page.current;
            pageStack.push(Qt.resolvedUrl("EditPage.qml"), { initial: {
                "name": a.name, "email": a.email, "login": a.login == a.email ? "" : a.login,
                "out_login": a.out_login == a.login ? "" : a.out_login,
                "in_type": a.in_type, "in_server": a.in_server, "in_port": a.in_port, "in_ssl": a.in_ssl,
                "out_server": a.out_server, "out_port": a.out_port, "out_ssl": a.out_ssl } });
        }
    }

    ContextMenu {
        id: ctx
        MenuLayout {
            MenuItem {
                text: S.t(uiLang, "makeDefault")
                onClicked: {
                    var r = JSON.parse(backend.setDefault(page.current.id));
                    if (r.ok) {
                        appWindow.showBanner(S.a(uiLang, "defaultSet", page.current.name));
                        appWindow.accountsChanged();
                    } else {
                        appWindow.showBanner(r.error);
                    }
                }
            }
        }
    }

    QueryDialog {
        id: about
        titleText: "MeeConf"
        message: S.a(uiLang, "version", appVersion) + "<br><br>" + S.t(uiLang, "aboutText") + "<br><br>"
                 + S.t(uiLang, "credit") + "<br><br><a href=\"https://github.com/smyhu/meeconf-n9\">github.com/smyhu/meeconf-n9</a>"
        acceptButtonText: S.t(uiLang, "close")
        onLinkActivated: Qt.openUrlExternally(link)
    }

    QueryDialog {
        id: help
        titleText: S.t(uiLang, "csvHelp")
        acceptButtonText: S.t(uiLang, "close")
    }

    Menu {
        id: menu
        MenuLayout {
            MenuItem {
                text: S.t(uiLang, "exportCsv")
                onClicked: {
                    var r = JSON.parse(backend.exportCsv());
                    appWindow.showBanner(r.ok ? S.a(uiLang, "exported", "MyDocs/" + r.path) : r.error);
                }
            }
            MenuItem {
                text: S.t(uiLang, "csvHelp")
                onClicked: {
                    help.message = S.a(uiLang, "csvHelpText", backend.examplePath());
                    help.open();
                }
            }
            MenuItem { text: S.t(uiLang, "about"); onClicked: about.open() }
        }
    }

    tools: ToolBarLayout {
        ToolIcon {
            iconId: "toolbar-add"
            onClicked: pageStack.push(Qt.resolvedUrl("EditPage.qml"))
        }
        ToolButton {
            text: S.t(uiLang, "importCsv")
            anchors.centerIn: parent
            onClicked: pageStack.push(Qt.resolvedUrl("ImportPage.qml"))
        }
        ToolIcon {
            iconId: "toolbar-view-menu"
            onClicked: menu.status == DialogStatus.Closed ? menu.open() : menu.close()
        }
    }
}
