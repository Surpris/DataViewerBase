DataViewerBase
=====

__DataViewerBase__ パッケージはリアルタイムで測定された画像を確認するためのGUIやツールを提供します。   
SPring-8内のSACLAにてカメラで測定されたデータを積算し、それらを確認するために作成されました。   

## システム要件
DataViewerBase を使用するには以下のパッケージおよびバージョンが必要です。   
これらのうち`olpy`および`stpy`はSACLAのHPC上で利用されるモジュールです。   
動作確認をするだけであれば必要ありません。   

* Python >= 3
* PyQt4 (pyqt >= 4.11)
* pyqtgraph >= 0.10.0
* pyzmq >= 16.0
* olpy
* dbpy

## 使用方法
1. ターミナル（コマンドプロンプト）を２つ開きます。便宜上、これらを A, B と呼ぶことにします。
1. ターミナルAで`DataViewerBase`ディレクトリ（フォルダ）に移動します。
    + これによってデータベースからのデータの取得が開始されます。
1. `python getDatawithOLPY.py`を実行します。
1. ターミナルBで`DataViewerBase`ディレクトリ（フォルダ）に移動します。
1. `python main.py`を実行します。
    + これによってGUIが起動します。

### DataViewerBaseの機能
* `Start`ボタンを押すことでデータの積算・表示が開始されます。
* `Clear`ボタンを押すことでデータをクリアします。
* `Save`ボタンを押すことでその時点でのデータを保存します。
* `Window`ボタンを押すことで、別のウィンドウでデータを確認できます。
    + &#8251;2017/10/15 時点では特に必要のない機能です。

## 構成
DataViewerBaseパッケージの構成は次図の通りです。   
SACLAのデータベースからデータを取得する機能は`getDatawithOLPY.py`スクリプトによって行われます。   
データの表示は`DataViewerBase`クラス（GUI）によって行われます。   

```
DataViewerBase/
    - anatools/ : analysis tools for VMI
    - core/ : core modules
        + decorator.py
            Some decorators.
        + GetDataClass.py
            Classes used to get data from the database.
        + Worker.py
            Worker classes.
            currently GetDataWorker3 is used.
        + ZeroMQ.py
            Publisher/listener classes using ZeroMQ.
    - gui/ : GUI classes
        + AnalyzeWindow.py
            Window class for analysis.
            (under construction)
        + DataViewerBase.py
            The main class of this package.
        + PlotWindow.py
            GUI class for showing a data image and some graphs.
    + getDatawithOLPY.py
        a script which starts to get and send data.
    + main.py
        a script which starts DataViewerBase.
```   

## データフロー
SACLAのサーバに蓄積された測定データを`getDatawithOLPY.py`によって取得します。   
それらをシグナルとバックグラウンド、などに分類して積算し、指定されたポートにデータを送ります。   
それらのポートに DataViewerBase がアクセスしてデータを取得し、さらに DataViewerBase の内部で積算したものをGUI上に表示します。   
