package main

import (
	"bufio"
	"fmt"
	"os"
	"strconv"
	"strings"

	"receptor-go/layers/app"
	"receptor-go/layers/link"
	"receptor-go/layers/presentation"
	"receptor-go/layers/transmission"
)

func requestPort() int {
	fmt.Println("Receptor")
	fmt.Print("\nPuerto en el que escuchar (Enter para usar 5000): ")

	reader := bufio.NewReader(os.Stdin)
	input, _ := reader.ReadString('\n')
	input = strings.TrimSpace(input)

	if input == "" {
		return 5000
	}

	port, err := strconv.Atoi(input)
	if err != nil {
		fmt.Println("Puerto inválido, usando 5000.")
		return 5000
	}

	return port
}

func handleFrame(algorithm string, metadata map[string]int, frame string) {
	data, hasError, err := link.VerifyIntegrity(frame, algorithm, metadata)
	if err != nil {
		fmt.Println("Error verificando integridad de la trama:", err)
		return
	}

	if hasError && algorithm == "crc32" {
		app.ShowMessage("", true, algorithm, metadata)
		return
	}

	text, err := presentation.DecodeMessage(data)
	if err != nil {
		fmt.Println("Error decodificando el mensaje:", err)
		return
	}

	app.ShowMessage(text, hasError, algorithm, metadata)
}

func main() {
	port := requestPort()

	if err := transmission.ReceiveInformation(port, handleFrame); err != nil {
		fmt.Println("Error iniciando el receptor:", err)
		os.Exit(1)
	}
}
