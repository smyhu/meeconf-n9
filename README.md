# MeeConf for Nokia N9

<img src="art/meeconf-n9.png" align="right" alt="MeeConf icon">

Bulk setup of e-mail accounts for the built-in **Mail** app of the Nokia N9
(MeeGo Harmattan PR1.3). Typing the server, port and user name of a dozen
mailboxes on the phone keyboard is tedious. MeeConf creates them for you, one by
one by hand or all at once from a CSV file made in Excel or OnlyOffice.

## Features

- **Account list** of the Mail app. Tap an account to see its servers; *Edit as new*
  opens the form pre-filled with that account.
- **New account by hand.** For known providers the servers are filled in from the
  e-mail address (o2, Onet/op.pl, Interia, WP, Gmail, Yahoo, iCloud, GMX, web.de,
  AOL, Zoho, Seznam, Mail.ru, Yandex).
- **Import from CSV** with a preview: what will be created and what is skipped and why
  (for example *this account already exists*).
- **Export to CSV** of the existing accounts (without passwords), to move them to
  another phone.
- **Default account** (shown first in Mail, used for sending): hold an account and
  choose *Make default*, tick it in the form, or put `yes` in the `default` column.
- A backup of the account database before every change
  (`MyDocs/MeeConf/backup`, last 10 kept).
- No root needed. Languages: English, Polish (follows the phone language).

## Passwords

MeeConf does not ask for or store passwords. Like the phone's own account wizard it
creates an empty password entry for each account, so **Mail asks for the password
on the first refresh**. Restart the phone after adding accounts.

## CSV format

UTF-8, separator `;` or `,`, lines starting with `#` are comments. Put the file in
`MyDocs` or `MyDocs/MeeConf` (a template, `accounts-example.csv`, is written there).

```
name;email;login;in_type;in_server;in_port;in_ssl;out_server;out_port;out_ssl;out_login;default
Work;john@example.com;john@example.com;imap;imap.example.com;993;ssl;smtp.example.com;465;ssl;;yes
Private;someone@gmail.com;;;;;;;;;;
```

| Column | Meaning | Empty cell |
|---|---|---|
| name | account name shown in Mail | the e-mail address |
| email | e-mail address (required) | – |
| login | user name | the e-mail address |
| in_type | `imap` or `pop` | `imap` (or the provider's) |
| in_server, out_server | incoming / SMTP server | known providers filled in |
| in_port, out_port | ports | from the encryption |
| in_ssl, out_ssl | `none`, `ssl` (993/995/465) or `tls` (STARTTLS, 143/110/587) | `ssl` |
| out_login | SMTP user name | same as login |
| default | `yes` for the main account | if the phone has no default account, the first new one |

The order of the lines is the order of the accounts in Mail (the N9 lists accounts
in the order they were created, the default one first).

## Install

Copy `dist/meeconf-n9_0.1.2_all.deb` to the phone and as root:

```
dpkg -i meeconf-n9_0.1.2_all.deb
```

Needs `python`, `python-pyside`, `python-dbus` and `qt-components` (all on a
standard PR1.3 phone). MeeConf is also part of
[MeeRevive](https://github.com/smyhu/meerevive-n9).

## How it works

Mail accounts live in `/home/user/.accounts/accounts.db` (libaccounts, provider
`email`, service `genericemail`). MeeConf writes the same settings the phone's
wizard writes, and creates empty password identities in signond over D-Bus
(`com.nokia.SingleSignOn`). See `app/core.py`.

## Credits

Designed and written by Claude (Anthropic) together with smyhu for the Nokia N9.

## License

MIT, see [LICENSE](LICENSE).
