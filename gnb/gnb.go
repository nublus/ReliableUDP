package gnb

import (
	"fmt"
	"net"
)

const (
	IP_ADD      = "8.137.79.215"
	SERVER_PORT = 12138
	CLIENT_PORT = 12140
	BUFFER_SIZE = 1024
)

type Packet struct {
	SeqNum int
	Data   string
}

type GBNClient struct {
	conn *net.UDPConn
}

type GBNServer struct {
	conn *net.UDPConn
}

func (c *GBNClient) sendData(data string) {
	packet := Packet{
		SeqNum: 0,
		Data:   data,
	}
	packetBytes := encodePacket(packet)
	c.conn.Write(packetBytes)
}

func (s *GBNServer) receiveData() string {
	buffer := make([]byte, BUFFER_SIZE)
	n, _ := s.conn.Read(buffer)
	return string(buffer[:n])
}

func encodePacket(packet Packet) []byte {
	// Encode packet into bytes here
	return []byte(fmt.Sprintf("%d %s", packet.SeqNum, packet.Data))
}

func decodePacket(data []byte) Packet {
	// Decode bytes into packet here
	var packet Packet
	fmt.Sscanf(string(data), "%d %s", &packet.SeqNum, &packet.Data)
	return packet
}

func run() {
	serverAddr := fmt.Sprintf(":%d", SERVER_PORT)
	clientAddr := fmt.Sprintf(":%d", CLIENT_PORT)
	fmt.Println(serverAddr)
	fmt.Println(clientAddr)

	// Start server
	serverConn, _ := net.ListenUDP("udp", &net.UDPAddr{IP: net.ParseIP(IP_ADD), Port: SERVER_PORT})
	server := GBNServer{conn: serverConn}
	defer serverConn.Close()

	// Start client
	clientConn, _ := net.DialUDP("udp", nil, &net.UDPAddr{IP: net.ParseIP(IP_ADD), Port: SERVER_PORT})
	client := GBNClient{conn: clientConn}
	defer clientConn.Close()

	// Send data from client to server
	client.sendData("Hello, UDP GBN!")

	// Receive data at server
	receivedData := server.receiveData()
	fmt.Println("Received:", receivedData)
}
