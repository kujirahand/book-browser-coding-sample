package main

// 利用するライブラリのインポート宣言
import (
	"bytes"
	"context"
	"encoding/base64"
	"image"
	"image/color"
	"image/png"
	"math"
	"os"

	"github.com/lucasb-eyer/go-colorful"
	wails "github.com/wailsapp/wails/v2/pkg/runtime"
)

// Wailsアプリの構造体を定義 --- (*1)
type App struct {
	ctx context.Context
}

func NewApp() *App { // アプリの構造体を初期化
	return &App{}
}

func (a *App) startup(ctx context.Context) { // 起動時に呼び出される関数
	a.ctx = ctx
}

// 保存先をダイアログで選択する関数 --- (*2)
func (a *App) OpenSaveDialog() (string, error) {
	// 保存ダイアログのオプションを設定 --- (*3)
	saveDialogOptions := wails.SaveDialogOptions{
		DefaultFilename: "mandelbrot.png",
		Filters: []wails.FileFilter{
			{DisplayName: "PNG画像", Pattern: "*.png"},
			{DisplayName: "全てのファイル", Pattern: "*.*"},
		},
	}
	// ダイアログを表示して保存先のファイル名を取得 --- (*4)
	filename, err := wails.SaveFileDialog(a.ctx, saveDialogOptions)
	if err != nil {
		return "", err
	}
	return filename, nil
}

// Base64エンコードされたPNGデータをファイルに保存する関数 --- (*5)
func (a *App) SaveB64Image(dataURL, filename string) error {
	// "data:image/png;base64," プレフィックスを削除
	prefix := "data:image/png;base64,"
	if !bytes.HasPrefix([]byte(dataURL), []byte(prefix)) {
		return os.ErrInvalid
	}
	base64Data := dataURL[len(prefix):]

	// Base64デコード
	imgData, err := base64.StdEncoding.DecodeString(base64Data)
	if err != nil {
		return err
	}

	// デコードされたデータをファイルに保存
	return os.WriteFile(filename, imgData, 0644)
}

// マンデルブロ集合の画像を生成してPNGデータを文字列で返す --- (*6)
func (a *App) GenImage(cx, cy, zoom float64, maxIter int) (string, error) {
	// 画像を生成
	img := genImage(600, 600, cx, cy, zoom, maxIter)
	// PNG形式で画像をエンコードしてバッファに書き込む
	var buf bytes.Buffer
	if err := png.Encode(&buf, img); err != nil {
		return "", err
	}
	// Base64エンコードされたPNGデータを生成
	encoded := base64.StdEncoding.EncodeToString(buf.Bytes())
	return "data:image/png;base64," + encoded, nil
}

// 実際にマンデル集合の画像を生成する関数 --- (*7)
func genImage(w, h int, cx, cy, zoom float64, maxIter int) image.Image {
	// 空のRGBA画像を作成
	img := image.NewRGBA(image.Rect(0, 0, w, h))
	// 各ピクセルに対してマンデルブロ集合の計算を行って色を設定
	for y := range h {
		for x := range w {
			rx, ry := pxToComplex(x, y, w, h, cx, cy, zoom)
			iter, zx, zy := iterMandelbrot(rx, ry, maxIter)
			img.Set(x, y, pixelColor(iter, maxIter, zx, zy))
		}
	}

	return img
}

// ピクセル座標を複素数平面の座標に変換する関数 --- (*8)
func pxToComplex(x, y, w, h int, cx, cy, zoom float64) (float64, float64) {
	rx := (float64(x)-float64(w)/2)/(0.5*zoom*float64(w)) + cx
	ry := (float64(y)-float64(h)/2)/(0.5*zoom*float64(h)) + cy
	return rx, ry
}

// マンデルブロ集合の計算を行う関数 --- (*9)
func iterMandelbrot(rx, ry float64, maxIter int) (int, float64, float64) {
	zx, zy := 0.0, 0.0
	iter := 0
	for zx*zx+zy*zy <= 4 && iter < maxIter {
		zx, zy = zx*zx-zy*zy+rx, 2*zx*zy+ry
		iter++
	}
	return iter, zx, zy
}

// ピクセルの色を決定する関数 --- (*10)
func pixelColor(iter, maxIter int, zx, zy float64) color.Color {
	if iter == maxIter {
		return color.RGBA{R: 8, G: 8, B: 24, A: 255}
	}
	// スムーズカラーリングでバンディングを減らし、色相を循環させる。
	mod2 := zx*zx + zy*zy
	mu := float64(iter) + 1 - math.Log(math.Log(math.Sqrt(mod2)))/math.Log(2)
	t := mu / float64(maxIter)
	h := math.Mod(360*3*t+220, 360)
	col := colorful.Hsv(h, 0.9, 1.0)
	r, g, b := col.RGB255()
	return color.RGBA{R: r, G: g, B: b, A: 255}
}
