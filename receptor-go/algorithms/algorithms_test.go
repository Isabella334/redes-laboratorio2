package algorithms

import (
	"strings"
	"testing"
)

func flipBit(bits string, pos int) string {
	b := []byte(bits)
	if b[pos] == '0' {
		b[pos] = '1'
	} else {
		b[pos] = '0'
	}
	return string(b)
}

func TestHammingCorrectsSingleBitError(t *testing.T) {
	bits := "01001000"
	r := 4

	m, err := CalculateM(r)
	if err != nil {
		t.Fatalf("CalculateM: %v", err)
	}

	padding := (m - len(bits)%m) % m
	padded := bits + strings.Repeat("0", padding)

	n := m + r
	block := make([]int, n+1)
	dataIter := 0
	for pos := 1; pos <= n; pos++ {
		if pos&(pos-1) != 0 {
			block[pos] = int(padded[dataIter] - '0')
			dataIter++
		}
	}
	for i := range r {
		parityPos := 1 << i
		parity := 0
		for pos := 1; pos <= n; pos++ {
			if pos&parityPos != 0 {
				parity ^= block[pos]
			}
		}
		block[parityPos] = parity
	}
	codeword := ""
	for pos := 1; pos <= n; pos++ {
		codeword += string(rune('0' + block[pos]))
	}

	noisy := flipBit(codeword, 2)

	data, hasError, err := CorrectMessage(noisy, r, padding)
	if err != nil {
		t.Fatalf("CorrectMessage: %v", err)
	}
	if !hasError {
		t.Errorf("expected hasError=true, got false")
	}
	if data != bits {
		t.Errorf("expected recovered data %q, got %q", bits, data)
	}
}

func TestCRC32DetectsError(t *testing.T) {
	bits := "0100100001101001" // "Hi"
	frame := bits + calculateRemainder(bits)

	if _, hasError, err := VerifyIntegrity(frame); err != nil || hasError {
		t.Errorf("expected no error on clean frame, got hasError=%v err=%v", hasError, err)
	}

	noisy := flipBit(frame, 5)
	if _, hasError, err := VerifyIntegrity(noisy); err != nil || !hasError {
		t.Errorf("expected detected error on noisy frame, got hasError=%v err=%v", hasError, err)
	}
}
