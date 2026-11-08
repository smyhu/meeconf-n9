.pragma library
// UI texts (pl, en). The language comes from the phone setting (uiLang, main.py).
// A missing entry falls back to English.

var texts = {
    "subtitle":    { "pl": "Konta pocztowe: %1", "en": "E-mail accounts: %1" },
    "empty":       { "pl": "Brak kont pocztowych.\nDodaj konto przyciskiem + albo zaimportuj plik CSV.",
                     "en": "No e-mail accounts.\nAdd one with + or import a CSV file." },
    "readError":   { "pl": "Nie udało się odczytać kont", "en": "Could not read the accounts" },
    "importCsv":   { "pl": "Import CSV", "en": "Import CSV" },
    "exportCsv":   { "pl": "Eksport do CSV", "en": "Export to CSV" },
    "exported":    { "pl": "Zapisano %1", "en": "Saved %1" },
    "csvHelp":     { "pl": "Wzór pliku CSV", "en": "CSV file template" },
    "csvHelpText": { "pl": "Wzór jest w MyDocs/%1. Jeden wiersz = jedno konto. Kolumny: name, email, login, in_type (imap/pop), in_server, in_port, in_ssl, out_server, out_port, out_ssl (none/ssl/tls), out_login, default (yes = konto domyślne). Kolejność wierszy = kolejność w Poczcie. Puste pola: login = adres, porty według szyfrowania, serwery znanych dostawców uzupełniane same. Plik z Excela lub OnlyOffice (UTF-8, średnik lub przecinek) wrzuć do MyDocs albo MyDocs/MeeConf.",
                     "en": "The template is in MyDocs/%1. One line = one account. Columns: name, email, login, in_type (imap/pop), in_server, in_port, in_ssl, out_server, out_port, out_ssl (none/ssl/tls), out_login, default (yes = default account). Row order = order in Mail. Empty cells: login = address, ports from the encryption, servers of known providers filled in. Put a file saved from Excel or OnlyOffice (UTF-8, semicolon or comma) into MyDocs or MyDocs/MeeConf." },
    "about":       { "pl": "O programie", "en": "About" },
    "aboutText":   { "pl": "Hurtowe zakładanie kont pocztowych dla aplikacji Poczta: ręcznie albo z pliku CSV. Hasła wpisujesz w Poczcie przy pierwszym odświeżeniu.",
                     "en": "Bulk setup of e-mail accounts for the Mail app: by hand or from a CSV file. You enter the passwords in Mail on the first refresh." },
    "credit":      { "pl": "Zaprojektowany i napisany przez Claude (Anthropic) wspólnie ze smyhu dla Nokii N9.",
                     "en": "Designed and written by Claude (Anthropic) together with smyhu for the Nokia N9." },
    "version":     { "pl": "Wersja %1", "en": "Version %1" },
    "close":       { "pl": "Zamknij", "en": "Close" },
    "restart":     { "pl": "Uruchom telefon ponownie, aby Poczta zobaczyła nowe konta.",
                     "en": "Restart the phone so that Mail sees the new accounts." },
    "useAsBase":   { "pl": "Edytuj jako nowe", "en": "Edit as new" },
    "isDefault":   { "pl": "domyślne", "en": "default" },
    "makeDefault": { "pl": "Ustaw jako domyślne", "en": "Make default" },
    "defaultSet":  { "pl": "%1 jest teraz kontem domyślnym", "en": "%1 is now the default account" },
    "defaultBox":  { "pl": "Konto domyślne (na górze w Poczcie, do wysyłki)", "en": "Default account (first in Mail, used for sending)" },
    "noPassword":  { "pl": "bez wpisu hasła", "en": "no password entry" },

    "newAccount":  { "pl": "Nowe konto", "en": "New account" },
    "create":      { "pl": "Utwórz", "en": "Create" },
    "accName":     { "pl": "Nazwa konta (widoczna w Poczcie)", "en": "Account name (shown in Mail)" },
    "email":       { "pl": "Adres e-mail", "en": "E-mail address" },
    "login":       { "pl": "Login (puste = adres e-mail)", "en": "User name (empty = e-mail address)" },
    "incoming":    { "pl": "Poczta przychodząca", "en": "Incoming mail" },
    "outgoing":    { "pl": "Poczta wychodząca (SMTP)", "en": "Outgoing mail (SMTP)" },
    "server":      { "pl": "Serwer", "en": "Server" },
    "port":        { "pl": "Port", "en": "Port" },
    "security":    { "pl": "Szyfrowanie", "en": "Encryption" },
    "encNone":     { "pl": "Brak", "en": "None" },
    "outLogin":    { "pl": "Login SMTP (puste = jak wyżej)", "en": "SMTP user name (empty = same)" },
    "presetUsed":  { "pl": "Wpisano serwery dla %1", "en": "Servers for %1 filled in" },
    "created":     { "pl": "Utworzono konto %1", "en": "Account %1 created" },
    "passLater":   { "pl": "Hasło wpiszesz w Poczcie przy pierwszym odświeżeniu.",
                     "en": "You will enter the password in Mail on the first refresh." },

    "pickFile":    { "pl": "Wybierz plik CSV", "en": "Choose a CSV file" },
    "noFiles":     { "pl": "Brak plików CSV w MyDocs i MyDocs/MeeConf.", "en": "No CSV files in MyDocs and MyDocs/MeeConf." },
    "preview":     { "pl": "Podgląd importu", "en": "Import preview" },
    "importN":     { "pl": "Importuj (%1)", "en": "Import (%1)" },
    "toCreate":    { "pl": "Do utworzenia: %1", "en": "To create: %1" },
    "imported":    { "pl": "Utworzono kont: %1", "en": "Accounts created: %1" },
    "importFail":  { "pl": "Nie udało się: %1", "en": "Failed: %1" },
    "line":        { "pl": "wiersz %1", "en": "line %1" },
    "stOk":        { "pl": "zostanie utworzone", "en": "will be created" },

    "errEmail":    { "pl": "brak poprawnego adresu e-mail", "en": "no valid e-mail address" },
    "errServer":   { "pl": "brak serwera (nieznany dostawca)", "en": "server missing (unknown provider)" },
    "errHost":     { "pl": "błędna nazwa serwera", "en": "invalid server name" },
    "errPort":     { "pl": "błędny port", "en": "invalid port" },
    "errSsl":      { "pl": "szyfrowanie: none, ssl albo tls", "en": "encryption: none, ssl or tls" },
    "errType":     { "pl": "typ: imap albo pop", "en": "type: imap or pop" },
    "errExists":   { "pl": "takie konto już jest", "en": "this account already exists" },
    "errHeader":   { "pl": "brak wiersza nagłówka z kolumną email", "en": "no header line with an email column" }
};

function t(lang, key) {
    var e = texts[key];
    if (!e)
        return key;
    return e[lang] !== undefined ? e[lang] : (e["en"] !== undefined ? e["en"] : key);
}

function a(lang, key, arg) {
    return t(lang, key).replace("%1", arg);
}

// error keys from the backend are translated, other texts are shown as they are
function err(lang, e) {
    return texts[e] ? t(lang, e) : e;
}
