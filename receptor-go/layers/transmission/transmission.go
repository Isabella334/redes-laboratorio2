package transmission

import (
	"bufio"
	"fmt"
	"net"
	"strconv"
	"strings"
)

type FrameHandler func(algorithm string, metadata map[string]int, frame string)

func parseMetadata(raw string) map[string]int {
	metadata := map[string]int{}

	if raw == "" {
		return metadata
	}

	for _, pair := range strings.Split(raw, ",") {
		kv := strings.SplitN(pair, "=", 2)
		if len(kv) != 2 {
			continue
		}

		value, err := strconv.Atoi(kv[1])
		if err != nil {
			continue
		}

		metadata[kv[0]] = value
	}

	return metadata
}

func handleConnection(conn net.Conn, handler FrameHandler) {
	defer conn.Close()

	line, err := bufio.NewReader(conn).ReadString('\n')
	if err != nil && line == "" {
		return
	}

	line = strings.TrimRight(line, "\n")

	parts := strings.SplitN(line, "|", 3)
	if len(parts) != 3 {
		fmt.Println("Trama con formato inválido, se descarta:", line)
		return
	}

	algorithm, metadataStr, frame := parts[0], parts[1], parts[2]
	handler(algorithm, parseMetadata(metadataStr), frame)
}

func ReceiveInformation(port int, handler FrameHandler) error {
	listener, err := net.Listen("tcp", fmt.Sprintf("0.0.0.0:%d", port))
	if err != nil {
		return fmt.Errorf("could not listen on port %d: %w", port, err)
	}
	defer listener.Close()

	fmt.Printf("Receptor escuchando en el puerto %d...\n", port)

	for {
		conn, err := listener.Accept()
		if err != nil {
			fmt.Println("Error aceptando conexión:", err)
			continue
		}

		handleConnection(conn, handler)
	}
}
