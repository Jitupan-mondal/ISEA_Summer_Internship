#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <netinet/ip.h>
#include <netinet/ip_icmp.h>
#include <arpa/inet.h>

#define PACKET_COUNT 20
#define BUFFER_SIZE  65536

int main() {
    int sock;
    unsigned char buffer[BUFFER_SIZE];
    struct sockaddr saddr;
    socklen_t saddr_len = sizeof(saddr);
    int packet_no = 0;

    printf("ROLL_NO=EEB24023\n");
    printf("ASSIGNED_PROTOCOL=ICMP\n\n");

    sock = socket(AF_INET, SOCK_RAW, IPPROTO_ICMP);
    if (sock < 0) {
        perror("socket() failed. Are you running as root?");
        return 1;
    }

    printf("Listening for ICMP packets...\n\n");

    while (packet_no < PACKET_COUNT) {
        int data_size = recvfrom(sock, buffer, BUFFER_SIZE, 0, &saddr, &saddr_len);
        if (data_size < 0) {
            perror("recvfrom() failed");
            close(sock);
            return 1;
        }

        struct iphdr *ip_header = (struct iphdr *)buffer;
        struct icmphdr *icmp_header = (struct icmphdr *)(buffer + ip_header->ihl * 4);

        struct in_addr src_addr, dst_addr;
        src_addr.s_addr = ip_header->saddr;
        dst_addr.s_addr = ip_header->daddr;

        packet_no++;

        printf("PACKET_NO=%d\n", packet_no);
        printf("SRC_IP=%s\n",      inet_ntoa(src_addr));
        printf("DST_IP=%s\n",      inet_ntoa(dst_addr));
        printf("PROTOCOL=ICMP\n");
        printf("PROTOCOL_NO=%d\n", ip_header->protocol);
        printf("TTL=%d\n",         ip_header->ttl);
        printf("PACKET_SIZE=%d\n", data_size);
        printf("HEADER_LENGTH=%d bytes\n", ip_header->ihl * 4);
        printf("ICMP_TYPE=%d\n",   icmp_header->type);
        printf("ICMP_CODE=%d\n",   icmp_header->code);
        printf("\n");
    }

    close(sock);
    printf("Done. Captured %d packets.\n", PACKET_COUNT);
    return 0;
}