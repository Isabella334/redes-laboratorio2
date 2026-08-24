package algorithms

import "fmt"

const CRC32Polynomial = "100000100110000010001110110110111"
const CRCSize = 32

func calculateRemainder(bits string) string {
	polyLen := len(CRC32Polynomial)
	dividend := make([]byte, len(bits)+CRCSize)
	copy(dividend, bits)

	for i := len(bits); i < len(dividend); i++ {
		dividend[i] = '0'
	}

	for i := 0; i < len(bits); i++ {
		if dividend[i] == '1' {
			for j := range polyLen {
				dividend[i+j] = xorBit(dividend[i+j], CRC32Polynomial[j])
			}
		}
	}

	return string(dividend[len(bits):])
}

func xorBit(a, b byte) byte {
	if a == b {
		return '0'
	}
	return '1'
}

func VerifyIntegrity(frame string) (string, bool, error) {
	if len(frame) <= CRCSize {
		return "", false, fmt.Errorf("the frame is too short to contain a valid CRC-32")
	}

	data := frame[:len(frame)-CRCSize]
	receivedCRC := frame[len(frame)-CRCSize:]
	calculatedCRC := calculateRemainder(data)

	hasError := calculatedCRC != receivedCRC

	return data, hasError, nil
}
