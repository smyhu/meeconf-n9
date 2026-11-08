import QtQuick 1.1
import com.nokia.meego 1.0
import com.nokia.extras 1.1
import "strings.js" as S

PageStackWindow {
    id: appWindow
    showStatusBar: true
    initialPage: MainPage { id: mainPage }

    property color accent: "#cfeca0"
    property color tintBorder: "#5f7f45"
    property color red: "#ff7a6a"
    property bool restartNeeded: false

    function showBanner(text) {
        banner.text = text;
        banner.show();
    }
    function accountsChanged() {
        restartNeeded = true;
        mainPage.reload();
    }

    InfoBanner { id: banner; y: 36 + 8 }

    Component.onCompleted: theme.inverted = true
}
