package main

import (
	"context"
	"fmt"
	"os"

	"github.com/wailsapp/wails/v2/pkg/runtime"
)

// Wailsの核となるApp構造体を定義 --- (※1)
type App struct {
	ctx context.Context
}

// Appを生成するコンストラクタを定義 --- (※2)
func NewApp() *App {
	return &App{}
}

// アプリ起動時に呼び出されるメソッドを定義 --- (※3)
func (a *App) startup(ctx context.Context) {
	a.ctx = ctx
}

// ファイルの保存機能を定義 --- (※4)
func (a *App) Save(text string) (string, error) {
	// ファイルダイアログを表示
	filename, err := runtime.SaveFileDialog(a.ctx, runtime.SaveDialogOptions{})
	if err != nil {
		return "", fmt.Errorf("ファイルの保存に失敗: %v", err)
	}
	// ファイルに書き込む
	err = os.WriteFile(filename, []byte(text), 0644)
	if err != nil {
		return "", fmt.Errorf("ファイルの書き込みに失敗: %v", err)
	}
	return filename, nil
}

// ファイルの読み込み機能を定義 --- (※5)
func (a *App) Load() (string, error) {
	// ファイルダイアログを表示
	filename, err := runtime.OpenFileDialog(a.ctx, runtime.OpenDialogOptions{})
	if err != nil {
		return "", fmt.Errorf("ファイルの読み込みに失敗: %v", err)
	}
	// テキストファイルを読む
	data, err := os.ReadFile(filename)
	if err != nil {
		return "", fmt.Errorf("ファイルの読み込みに失敗: %v", err)
	}
	return string(data), nil
}
