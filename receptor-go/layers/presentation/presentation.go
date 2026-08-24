package presentation

import (
	"fmt"
	"strconv"
	"strings"
)

func DecodeMessage(bits string) (string, error) {
	if len(bits)%8 != 0 {
		return "", fmt.Errorf("bit length %d is not a multiple of 8", len(bits))
	}

	var sb strings.Builder

	for i := 0; i < len(bits); i += 8 {
		chunk := bits[i : i+8]

		value, err := strconv.ParseUint(chunk, 2, 8)
		if err != nil {
			return "", fmt.Errorf("invalid ASCII binary chunk %q: %w", chunk, err)
		}

		sb.WriteByte(byte(value))
	}

	return sb.String(), nil
}
