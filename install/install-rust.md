# Appendix. Rustのインストール

本書の5章では、Rustを利用したプログラムを紹介します。そこで、Rustのインストール方法について解説します。OSごとにインストール方法が異なるので、Windows、macOS、Linuxそれぞれの方法を解説します。

## Windowsの場合

WindowsにRustをインストールするには、次の手順を実行してください。

1. Rustの[公式サイト](https://www.rust-lang.org/tools/install)にアクセスします。
2. 利用中のOSに合ったバージョンのボタンをクリックしてインストーラーをダウンロードします。一般的には「DOWNLOAD RUSTUP-INIT.EXE(X64)」のボタンをクリックします。
3. ダウンロードしたインストーラーを実行します。
4. インストーラーの指示に従って、インストールを完了します。
5. インストールの途中で、Visual Studio Build Toolsのインストールを求められることがあります。Rustは、C++のビルドツールを必要とするため、Visual Studio Build Toolsもインストールしてください。

```text
Windows用 Build Tools for C++:
[URL] https://visualstudio.microsoft.com/ja/visual-cpp-build-tools/
```

6. インストールが完了したら、コマンドプロンプトを開いて、次のコマンドを実行してRustが正しくインストールされたか確認します。

```sh
$ rustc --version
```

## macOS/Linuxの場合

macOS/LinuxにRustをインストールするには、次の手順を実行してください。

1. ターミナルを開きます。
2. 次のコマンドを実行して、Rustのインストーラーであるrustupをインストールします。

```sh
$ curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
```

3. インストーラーの指示に従って、インストールを完了します。
4. インストールが完了したら、次のコマンドを実行してRustが正しくインストールされたか確認します。

```sh
$ rustc --version
```

正しくインストールされていれば、バージョン情報が表示されます。
