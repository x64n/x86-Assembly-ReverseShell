@echo off
echo Compiling reverse_shell.asm...
nasm -f win32 reverse_shell.asm -o reverse_shell.obj
if errorlevel 1 goto error

echo Linking...
link /entry:Start /subsystem:console reverse_shell.obj kernel32.lib ws2_32.lib
if errorlevel 1 goto error

echo Compilation successful!
goto end

:error
echo Error during compilation/linking!
pause

:end
