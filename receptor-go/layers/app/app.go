package app

import "fmt"

func ShowMessage(text string, hasError bool, algorithm string, metadata map[string]int) {
	fmt.Println("\nRrepector")
	fmt.Printf("Algoritmo:          %s\n", algorithm)

	if len(metadata) > 0 {
		fmt.Printf("Metadata:           %v\n", metadata)
	}

	switch {
	case hasError && algorithm == "hamming":
		fmt.Println("Se detectaron y corrigieron errores de un bit en al menos un bloque.")
		fmt.Printf("Mensaje recibido:   %s\n", text)
	case hasError:
		fmt.Println("ERROR: se detectaron errores en la trama y no fue posible corregirlos.")
	default:
		fmt.Printf("Mensaje recibido:   %s\n", text)
	}
}
