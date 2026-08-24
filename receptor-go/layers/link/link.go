package link

import (
	"fmt"
	"receptor-go/algorithms"
)

func VerifyIntegrity(frame string, algorithm string, metadata map[string]int) (string, bool, error) {
	switch algorithm {
	case "hamming":
		r, ok := metadata["r"]
		if !ok {
			return "", false, fmt.Errorf("missing 'r' in metadata for hamming")
		}

		padding := metadata["padding"]

		return algorithms.CorrectMessage(frame, r, padding)

	case "crc32":
		return algorithms.VerifyIntegrity(frame)

	default:
		return "", false, fmt.Errorf("unknown algorithm: %s", algorithm)
	}
}
