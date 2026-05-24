# Appendix. Pythonのインストール

本書の3章以降で、Pythonを使ったプログラムを紹介します。そこで、Pythonのインストール方法を解説します。Pythonは、マルチプラットフォームで利用できるプログラミング言語で、Windows、macOS、Linuxなど、さまざまな環境で動作します。

Pythonのインストール方法は、利用するOSによって異なります。以下に、主要なOSごとのインストール方法を説明します。

## WindowsでのPythonのインストール

1. Pythonの[公式サイト](https://www.python.org/downloads/)にアクセスします。
2. 画面上方にある「Download Python install manager」を選んでダウンロードします。
3. ダウンロードしたインストーラーを実行します。すると、コマンドプロンプトが表示されます。そこで「Install CPython now?(CPythonをインストールしますか？)」と尋ねられるので、「y」を入力してEnterキーを押すと、インストールが開始されます。
4. PowerShellを開いて、次のコマンドを入力しましょう。

```sh
$ python --version
```

## macOSでのPythonのインストール

macOSには、Pythonがプリインストールされていますが、バージョンが古いことがあります。最新のPythonをインストールするには、Homebrewというパッケージマネージャーを利用する方法が一般的です。

1. Homebrewがインストールされていない場合は、[公式サイト](https://brew.sh/)の指示に従ってインストールします。
2. ターミナルを開いて、次のコマンドを入力してPythonをインストールします。

```sh
$ brew install python@3.14
```

3. インストールが完了したら、次のコマンドを入力してPythonのバージョンを確認します。

```sh
$ python3 --version
```

Pythonの公式サイトでは、macOS向けのインストーラーも提供されています。そちらを利用してインストールすることもできます。また、この後で紹介するpyenvを利用してインストールする方法もあります。

## LinuxでのPythonのインストール

Linuxディストリビューションによっては、Pythonがプリインストールされていることがありますが、最新のバージョンをインストールするには、パッケージマネージャーを利用する方法が一般的です。ここでは、Ubuntuを例に説明します。

1. ターミナルを開いて、次のコマンドを入力してPythonをインストールします。

```sh
$ sudo apt update
$ sudo apt install python3
```

2. インストールが完了したら、次のコマンドを入力してPythonのバージョンを確認します。

```sh
$ python3 --version
```

ただし、Linuxディストリビューションによっては、Pythonのバージョンが古いことがあります。その場合は、下記のpyenvを利用して、最新のPythonをインストールできます。本書が対象とするPythonのバージョンは、3.13以上です。

## pyenvを利用してPythonをインストールする方法

pyenvは、複数のPythonバージョンを管理できるツールです。macOSやLinuxでPythonをインストールする場合、pyenvを利用すると便利です。気軽に複数のバージョンを切り替えられるので、プロジェクトごとに異なるPythonバージョンを使いたい場合などに役立ちます。

ターミナルを起動して次のコマンドを実行します。

```sh
# pyenvのインストール
$ curl https://pyenv.run | bash
# Pythonをインストール
$ pyenv install 3.14
# インストールしたPythonをグローバルで使うように設定
$ pyenv global 3.14
```
