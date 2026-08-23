package algorithms

import (
	"fmt"
	"strconv"
	"strings"
)

func CalculateM(r int) (int, error) {
	if r < 1 {
		return 0, fmt.Errorf("r must be a positive integer")
	}

	m := (1 << r) - r - 1

	if m < 1 {
		return 0, fmt.Errorf("r=%d is too small: there is no space left for data bits", r)
	}

	return m, nil
}

func isPowerOfTwo(pos int) bool {
	return pos&(pos-1) == 0
}

func decode(codeword string, r int) (string, bool) {
	n := len(codeword)
	block := make([]int, n+1)

	for i, c := range codeword {
		if c == '1' {
			block[i+1] = 1
		}
	}

	syndrome := 0
	for i := range r {
		parityPos := 1 << i
		parity := 0

		for pos := 1; pos <= n; pos++ {
			if pos&parityPos != 0 {
				parity ^= block[pos]
			}
		}

		if parity != 0 {
			syndrome += parityPos
		}
	}

	hasError := syndrome != 0
	if hasError && syndrome <= n {
		block[syndrome] ^= 1
	}

	var sb strings.Builder

	for pos := 1; pos <= n; pos++ {
		if !isPowerOfTwo(pos) {
			sb.WriteString(strconv.Itoa(block[pos]))
		}
	}

	return sb.String(), hasError
}

func CorrectMessage(frame string, r int, padding int) (string, bool, error) {
	m, err := CalculateM(r)
	if err != nil {
		return "", false, err
	}

	n := m + r

	if n == 0 || len(frame)%n != 0 {
		return "", false, fmt.Errorf(
			"the received frame (%d bits) is not a multiple of the expected block size (n=%d for r=%d)",
			len(frame), n, r,
		)
	}

	var dataBlocks []string
	hasError := false

	for i := 0; i < len(frame); i += n {
		blockData, blockError := decode(frame[i:i+n], r)
		dataBlocks = append(dataBlocks, blockData)
		hasError = hasError || blockError
	}

	data := strings.Join(dataBlocks, "")

	if padding > 0 && padding <= len(data) {
		data = data[:len(data)-padding]
	}

	return data, hasError, nil
}
