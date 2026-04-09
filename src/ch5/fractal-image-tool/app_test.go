package main

import (
	"os"
	"path/filepath"
	"strings"
	"testing"
)

func TestGenerateAndSaveImage(t *testing.T) {
	a := NewApp()
	out := filepath.Join(t.TempDir(), "mandelbrot.png")

	b64, err := a.GenImage(-0.5, 0, 1, 200)
	if err != nil {
		t.Fatalf("GenareteImage failed: %v", err)
	}
	if !strings.HasPrefix(b64, "data:image/png;base64,") {
		t.Fatalf("unexpected image prefix: %s", b64[:24])
	}

	err = a.SaveB64Image(b64, out)
	if err != nil {
		t.Fatalf("SaveB64Image failed: %v", err)
	}

	info, err := os.Stat(out)
	if err != nil {
		t.Fatalf("output file was not created: %v", err)
	}
	if info.Size() == 0 {
		t.Fatal("output file is empty")
	}
}
