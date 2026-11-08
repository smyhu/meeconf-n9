import QtQuick 1.1
import com.nokia.meego 1.0
import "strings.js" as S

// Step 1: choose a CSV file from MyDocs or MyDocs/MeeConf.
// Step 2: preview (what will be created, what is skipped and why), then import.
Page {
    id: page
    orientationLock: PageOrientation.LockPortrait
    property string file: ""
    property int count: 0
    property bool busy: false

    function loadFiles() {
        files.clear();
        var l = JSON.parse(backend.csvFiles());
        for (var i = 0; i < l.length; ++i)
            files.append({ "path": l[i].path, "name": l[i].name, "dir": l[i].dir });
    }
    function open(path, name) {
        rows.clear();
        var r = JSON.parse(backend.parseCsv(path));
        if (r.error) {
            appWindow.showBanner(name + ": " + S.err(uiLang, r.error));
            return;
        }
        for (var i = 0; i < r.rows.length; ++i)
            rows.append(r.rows[i]);
        page.count = r.count;
        page.file = name;
    }
    function doImport() {
        page.busy = true;
        var r = JSON.parse(backend.importPending());
        page.busy = false;
        var msg = S.a(uiLang, "imported", r.created);
        if (r.failed.length > 0) {
            var names = [];
            for (var i = 0; i < r.failed.length; ++i)
                names.push(r.failed[i].name + " (" + S.err(uiLang, r.failed[i].error) + ")");
            msg += "\n" + S.a(uiLang, "importFail", names.join(", "));
        }
        appWindow.showBanner(msg);
        if (r.created > 0)
            appWindow.accountsChanged();
        pageStack.pop();
    }
    Component.onCompleted: loadFiles()

    Image { source: "background.png"; y: -36; smooth: false }
    Header {
        id: header
        text: page.file == "" ? S.t(uiLang, "pickFile") : S.t(uiLang, "preview")
        subText: page.file == "" ? "" : page.file + " · " + S.a(uiLang, "toCreate", page.count)
    }
    ListModel { id: files }
    ListModel { id: rows }

    ListView {
        id: fileList
        visible: page.file == ""
        anchors { top: header.bottom; left: parent.left; right: parent.right; bottom: parent.bottom }
        clip: true
        model: files
        delegate: Item {
            width: fileList.width
            height: 88
            Rectangle { anchors.fill: parent; color: "#ffffff"; opacity: fm.pressed ? 0.12 : 0 }
            Column {
                anchors { left: parent.left; right: parent.right; leftMargin: 16; rightMargin: 16; verticalCenter: parent.verticalCenter }
                Label { width: parent.width; text: model.name; font.pixelSize: 26; elide: Text.ElideMiddle }
                Label { width: parent.width; text: "MyDocs/" + model.dir; font.pixelSize: 20; color: "#8c8c8c" }
            }
            Rectangle { anchors.bottom: parent.bottom; width: parent.width; height: 1; color: "#222222" }
            MouseArea { id: fm; anchors.fill: parent; onClicked: page.open(model.path, model.name) }
        }
    }
    Label {
        visible: page.file == "" && files.count == 0
        anchors { left: parent.left; right: parent.right; margins: 32; verticalCenter: parent.verticalCenter }
        horizontalAlignment: Text.AlignHCenter
        wrapMode: Text.WordWrap
        color: "#8c8c8c"
        font.pixelSize: 26
        text: S.t(uiLang, "noFiles")
    }

    ListView {
        id: rowList
        visible: page.file != ""
        anchors { top: header.bottom; left: parent.left; right: parent.right; bottom: parent.bottom }
        clip: true
        model: rows
        delegate: Item {
            width: rowList.width
            height: 124
            Column {
                anchors { left: parent.left; right: parent.right; leftMargin: 16; rightMargin: 16; verticalCenter: parent.verticalCenter }
                Label {
                    width: parent.width
                    text: model.name != "" ? model.name : "?"
                    font.pixelSize: 24
                    elide: Text.ElideRight
                }
                Label {
                    width: parent.width
                    text: model.email
                    font.pixelSize: 20
                    color: "#b0b0b0"
                    elide: Text.ElideMiddle
                }
                Label {
                    width: parent.width
                    text: (model.in_type == "pop" ? "POP3" : "IMAP") + " · " + model.in_server
                    font.pixelSize: 18
                    color: "#8c8c8c"
                    elide: Text.ElideRight
                }
                Label {
                    width: parent.width
                    text: S.a(uiLang, "line", model.line) + " · " + (model.state == "ok" ? S.t(uiLang, "stOk") : S.err(uiLang, model.state))
                    font.pixelSize: 20
                    color: model.state == "ok" ? appWindow.accent : appWindow.red
                    elide: Text.ElideRight
                }
            }
            Rectangle { anchors.bottom: parent.bottom; width: parent.width; height: 1; color: "#222222" }
        }
    }
    ScrollDecorator { flickableItem: page.file == "" ? fileList : rowList }

    BusyIndicator {
        anchors.centerIn: parent
        visible: page.busy
        running: page.busy
        platformStyle: BusyIndicatorStyle { size: "large" }
    }

    tools: ToolBarLayout {
        ToolIcon {
            iconId: "toolbar-back"
            onClicked: {
                if (page.file != "") { page.file = ""; rows.clear(); page.loadFiles(); }
                else pageStack.pop();
            }
        }
        ToolButton {
            visible: page.file != ""
            enabled: page.count > 0 && !page.busy
            text: S.a(uiLang, "importN", page.count)
            anchors.centerIn: parent
            onClicked: page.doImport()
        }
    }
}
