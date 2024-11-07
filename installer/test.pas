program tttt;
uses sysutils;

{ Use -MANSISTRINGS compiler option in Free Pascal: https://www.freepascal.org/docs-html/user/usersu16.html }

function IsPathInList(Path: string; Paths: string): boolean;
var
    X, Tail: string;
    P: integer;
begin
    IsPathInList := false;

    Tail := Paths;
    while Length(Tail) > 0 do
    begin
        P := Pos(';', Tail);

        if P < 1 then
        begin
            X := Tail;
            Tail := '';
        end
        else
        begin
            X := Copy(Tail, 1, P-1);
            Tail := Copy(Tail, P+1, Length(Tail)-P);
        end;

        if SameStr(X, Path) then
        begin
            IsPathInList := true;
            break;
        end;
    end;
end;


begin

writeln('These lines must return TRUE (do not forget to enable ANSISTRINGS).');

writeln(IsPathInList('C:\Program Files (x86)\Nmap', 'C:\WINDOWS\system32;C:\WINDOWS;C:\WINDOWS\System32\Wbem;'+
        'C:\WINDOWS\System32\WindowsPowerShell\v1.0\;C:\WINDOWS\System32\OpenSSH\;C:\Program Files\Git\cmd;'+
        'C:\Program Files\TortoiseGit\bin;C:\Strawberry\c\bin;C:\Strawberry\perl\site\bin;C:\Strawberry\perl\bin;'+
        'C:\Program Files\Meld\;C:\FPC\3.2.2\bin\i386-Win32;C:\Ruby27-x64\bin;'+
        'C:\Users\1\AppData\Local\Microsoft\WindowsApps;C:\Strawberry\perl\bin;C:\Ruby27-x64\msys64\mingw64\bin;'+
        'C:\Program Files\jdk-21.0.1\bin;C:\texlive\2023\bin\windows;C:\Program Files\ffmpeg-6.0-full_build\bin;'+
        'C:\Program Files (x86)\Nmap;'));

writeln(IsPathInList('C:\WINDOWS\system32', 'C:\WINDOWS\system32;C:\WINDOWS;C:\WINDOWS\System32\Wbem;'+
        'C:\WINDOWS\System32\WindowsPowerShell\v1.0\;C:\WINDOWS\System32\OpenSSH\;C:\Program Files\Git\cmd;'+
        'C:\Program Files\TortoiseGit\bin;C:\Strawberry\c\bin;C:\Strawberry\perl\site\bin;C:\Strawberry\perl\bin;'+
        'C:\Program Files\Meld\;C:\FPC\3.2.2\bin\i386-Win32;C:\Ruby27-x64\bin;'+
        'C:\Users\1\AppData\Local\Microsoft\WindowsApps;C:\Strawberry\perl\bin;C:\Ruby27-x64\msys64\mingw64\bin;'+
        'C:\Program Files\jdk-21.0.1\bin;C:\texlive\2023\bin\windows;C:\Program Files\ffmpeg-6.0-full_build\bin;'+
        'C:\Program Files (x86)\Nmap;'));

writeln(IsPathInList('C:\Program Files\TortoiseGit\bin', 'C:\WINDOWS\system32;C:\WINDOWS;C:\WINDOWS\System32\Wbem;'+
        'C:\WINDOWS\System32\WindowsPowerShell\v1.0\;C:\WINDOWS\System32\OpenSSH\;C:\Program Files\Git\cmd;'+
        'C:\Program Files\TortoiseGit\bin;C:\Strawberry\c\bin;C:\Strawberry\perl\site\bin;C:\Strawberry\perl\bin;'+
        'C:\Program Files\Meld\;C:\FPC\3.2.2\bin\i386-Win32;C:\Ruby27-x64\bin;'+
        'C:\Users\1\AppData\Local\Microsoft\WindowsApps;C:\Strawberry\perl\bin;C:\Ruby27-x64\msys64\mingw64\bin;'+
        'C:\Program Files\jdk-21.0.1\bin;C:\texlive\2023\bin\windows;C:\Program Files\ffmpeg-6.0-full_build\bin;'+
        'C:\Program Files (x86)\Nmap;'));

writeln(IsPathInList('C:\WINDOWS', 'C:\WINDOWS\system32;C:\WINDOWS;C:\WINDOWS\System32\Wbem;'+
        'C:\WINDOWS\System32\WindowsPowerShell\v1.0\;C:\WINDOWS\System32\OpenSSH\;C:\Program Files\Git\cmd;'+
        'C:\Program Files\TortoiseGit\bin;C:\Strawberry\c\bin;C:\Strawberry\perl\site\bin;C:\Strawberry\perl\bin;'+
        'C:\Program Files\Meld\;C:\FPC\3.2.2\bin\i386-Win32;C:\Ruby27-x64\bin;'+
        'C:\Users\1\AppData\Local\Microsoft\WindowsApps;C:\Strawberry\perl\bin;C:\Ruby27-x64\msys64\mingw64\bin;'+
        'C:\Program Files\jdk-21.0.1\bin;C:\texlive\2023\bin\windows;C:\Program Files\ffmpeg-6.0-full_build\bin;'+
        'C:\Program Files (x86)\Nmap;'));

writeln(IsPathInList('C:\Program Files\ffmpeg-6.0-full_build\bin', 'C:\WINDOWS\system32;C:\WINDOWS;C:\WINDOWS\System32\Wbem;'+
        'C:\WINDOWS\System32\WindowsPowerShell\v1.0\;C:\WINDOWS\System32\OpenSSH\;C:\Program Files\Git\cmd;'+
        'C:\Program Files\TortoiseGit\bin;C:\Strawberry\c\bin;C:\Strawberry\perl\site\bin;C:\Strawberry\perl\bin;'+
        'C:\Program Files\Meld\;C:\FPC\3.2.2\bin\i386-Win32;C:\Ruby27-x64\bin;'+
        'C:\Users\1\AppData\Local\Microsoft\WindowsApps;C:\Strawberry\perl\bin;C:\Ruby27-x64\msys64\mingw64\bin;'+
        'C:\Program Files\jdk-21.0.1\bin;C:\texlive\2023\bin\windows;C:\Program Files\ffmpeg-6.0-full_build\bin;'+
        'C:\Program Files (x86)\Nmap;'));


{ Short string in the second argument. }
{ This returns TRUE even if you forgot to add -MANSISTRINGS option. }
writeln();
writeln('Short string (must work even without ANSISTRINGS):');
writeln(IsPathInList('C:\Program Files (x86)\Nmap', ''+
        'C:\Users\1\AppData\Local\Microsoft\WindowsApps;C:\Strawberry\perl\bin;C:\Ruby27-x64\msys64\mingw64\bin;'+
        'C:\Program Files\jdk-21.0.1\bin;C:\texlive\2023\bin\windows;C:\Program Files\ffmpeg-6.0-full_build\bin;'+
        'C:\Program Files (x86)\Nmap;'));


writeln();
writeln('Without semicolon at the end.');

writeln(IsPathInList('C:\Program Files (x86)\Nmap', 'C:\WINDOWS\system32;C:\WINDOWS;C:\WINDOWS\System32\Wbem;'+
        'C:\WINDOWS\System32\WindowsPowerShell\v1.0\;C:\WINDOWS\System32\OpenSSH\;C:\Program Files\Git\cmd;'+
        'C:\Program Files\TortoiseGit\bin;C:\Strawberry\c\bin;C:\Strawberry\perl\site\bin;C:\Strawberry\perl\bin;'+
        'C:\Program Files\Meld\;C:\FPC\3.2.2\bin\i386-Win32;C:\Ruby27-x64\bin;'+
        'C:\Users\1\AppData\Local\Microsoft\WindowsApps;C:\Strawberry\perl\bin;C:\Ruby27-x64\msys64\mingw64\bin;'+
        'C:\Program Files\jdk-21.0.1\bin;C:\texlive\2023\bin\windows;C:\Program Files\ffmpeg-6.0-full_build\bin;'+
        'C:\Program Files (x86)\Nmap'));

writeln(IsPathInList('C:\WINDOWS\system32', 'C:\WINDOWS\system32;C:\WINDOWS;C:\WINDOWS\System32\Wbem;'+
        'C:\WINDOWS\System32\WindowsPowerShell\v1.0\;C:\WINDOWS\System32\OpenSSH\;C:\Program Files\Git\cmd;'+
        'C:\Program Files\TortoiseGit\bin;C:\Strawberry\c\bin;C:\Strawberry\perl\site\bin;C:\Strawberry\perl\bin;'+
        'C:\Program Files\Meld\;C:\FPC\3.2.2\bin\i386-Win32;C:\Ruby27-x64\bin;'+
        'C:\Users\1\AppData\Local\Microsoft\WindowsApps;C:\Strawberry\perl\bin;C:\Ruby27-x64\msys64\mingw64\bin;'+
        'C:\Program Files\jdk-21.0.1\bin;C:\texlive\2023\bin\windows;C:\Program Files\ffmpeg-6.0-full_build\bin;'+
        'C:\Program Files (x86)\Nmap'));

writeln(IsPathInList('C:\Program Files\TortoiseGit\bin', 'C:\WINDOWS\system32;C:\WINDOWS;C:\WINDOWS\System32\Wbem;'+
        'C:\WINDOWS\System32\WindowsPowerShell\v1.0\;C:\WINDOWS\System32\OpenSSH\;C:\Program Files\Git\cmd;'+
        'C:\Program Files\TortoiseGit\bin;C:\Strawberry\c\bin;C:\Strawberry\perl\site\bin;C:\Strawberry\perl\bin;'+
        'C:\Program Files\Meld\;C:\FPC\3.2.2\bin\i386-Win32;C:\Ruby27-x64\bin;'+
        'C:\Users\1\AppData\Local\Microsoft\WindowsApps;C:\Strawberry\perl\bin;C:\Ruby27-x64\msys64\mingw64\bin;'+
        'C:\Program Files\jdk-21.0.1\bin;C:\texlive\2023\bin\windows;C:\Program Files\ffmpeg-6.0-full_build\bin;'+
        'C:\Program Files (x86)\Nmap'));

writeln(IsPathInList('C:\WINDOWS', 'C:\WINDOWS\system32;C:\WINDOWS;C:\WINDOWS\System32\Wbem;'+
        'C:\WINDOWS\System32\WindowsPowerShell\v1.0\;C:\WINDOWS\System32\OpenSSH\;C:\Program Files\Git\cmd;'+
        'C:\Program Files\TortoiseGit\bin;C:\Strawberry\c\bin;C:\Strawberry\perl\site\bin;C:\Strawberry\perl\bin;'+
        'C:\Program Files\Meld\;C:\FPC\3.2.2\bin\i386-Win32;C:\Ruby27-x64\bin;'+
        'C:\Users\1\AppData\Local\Microsoft\WindowsApps;C:\Strawberry\perl\bin;C:\Ruby27-x64\msys64\mingw64\bin;'+
        'C:\Program Files\jdk-21.0.1\bin;C:\texlive\2023\bin\windows;C:\Program Files\ffmpeg-6.0-full_build\bin;'+
        'C:\Program Files (x86)\Nmap'));

writeln(IsPathInList('C:\Program Files\ffmpeg-6.0-full_build\bin', 'C:\WINDOWS\system32;C:\WINDOWS;C:\WINDOWS\System32\Wbem;'+
        'C:\WINDOWS\System32\WindowsPowerShell\v1.0\;C:\WINDOWS\System32\OpenSSH\;C:\Program Files\Git\cmd;'+
        'C:\Program Files\TortoiseGit\bin;C:\Strawberry\c\bin;C:\Strawberry\perl\site\bin;C:\Strawberry\perl\bin;'+
        'C:\Program Files\Meld\;C:\FPC\3.2.2\bin\i386-Win32;C:\Ruby27-x64\bin;'+
        'C:\Users\1\AppData\Local\Microsoft\WindowsApps;C:\Strawberry\perl\bin;C:\Ruby27-x64\msys64\mingw64\bin;'+
        'C:\Program Files\jdk-21.0.1\bin;C:\texlive\2023\bin\windows;C:\Program Files\ffmpeg-6.0-full_build\bin;'+
        'C:\Program Files (x86)\Nmap'));


writeln();
writeln('With semicolon at the beginning.');

writeln(IsPathInList('C:\Program Files (x86)\Nmap', ';C:\WINDOWS\system32;C:\WINDOWS;C:\WINDOWS\System32\Wbem;'+
        'C:\WINDOWS\System32\WindowsPowerShell\v1.0\;C:\WINDOWS\System32\OpenSSH\;C:\Program Files\Git\cmd;'+
        'C:\Program Files\TortoiseGit\bin;C:\Strawberry\c\bin;C:\Strawberry\perl\site\bin;C:\Strawberry\perl\bin;'+
        'C:\Program Files\Meld\;C:\FPC\3.2.2\bin\i386-Win32;C:\Ruby27-x64\bin;'+
        'C:\Users\1\AppData\Local\Microsoft\WindowsApps;C:\Strawberry\perl\bin;C:\Ruby27-x64\msys64\mingw64\bin;'+
        'C:\Program Files\jdk-21.0.1\bin;C:\texlive\2023\bin\windows;C:\Program Files\ffmpeg-6.0-full_build\bin;'+
        'C:\Program Files (x86)\Nmap;'));

writeln(IsPathInList('C:\WINDOWS\system32', ';C:\WINDOWS\system32;C:\WINDOWS;C:\WINDOWS\System32\Wbem;'+
        'C:\WINDOWS\System32\WindowsPowerShell\v1.0\;C:\WINDOWS\System32\OpenSSH\;C:\Program Files\Git\cmd;'+
        'C:\Program Files\TortoiseGit\bin;C:\Strawberry\c\bin;C:\Strawberry\perl\site\bin;C:\Strawberry\perl\bin;'+
        'C:\Program Files\Meld\;C:\FPC\3.2.2\bin\i386-Win32;C:\Ruby27-x64\bin;'+
        'C:\Users\1\AppData\Local\Microsoft\WindowsApps;C:\Strawberry\perl\bin;C:\Ruby27-x64\msys64\mingw64\bin;'+
        'C:\Program Files\jdk-21.0.1\bin;C:\texlive\2023\bin\windows;C:\Program Files\ffmpeg-6.0-full_build\bin;'+
        'C:\Program Files (x86)\Nmap;'));

writeln(IsPathInList('C:\Program Files\TortoiseGit\bin', ';C:\WINDOWS\system32;C:\WINDOWS;C:\WINDOWS\System32\Wbem;'+
        'C:\WINDOWS\System32\WindowsPowerShell\v1.0\;C:\WINDOWS\System32\OpenSSH\;C:\Program Files\Git\cmd;'+
        'C:\Program Files\TortoiseGit\bin;C:\Strawberry\c\bin;C:\Strawberry\perl\site\bin;C:\Strawberry\perl\bin;'+
        'C:\Program Files\Meld\;C:\FPC\3.2.2\bin\i386-Win32;C:\Ruby27-x64\bin;'+
        'C:\Users\1\AppData\Local\Microsoft\WindowsApps;C:\Strawberry\perl\bin;C:\Ruby27-x64\msys64\mingw64\bin;'+
        'C:\Program Files\jdk-21.0.1\bin;C:\texlive\2023\bin\windows;C:\Program Files\ffmpeg-6.0-full_build\bin;'+
        'C:\Program Files (x86)\Nmap;'));

writeln(IsPathInList('C:\WINDOWS', ';C:\WINDOWS\system32;C:\WINDOWS;C:\WINDOWS\System32\Wbem;'+
        'C:\WINDOWS\System32\WindowsPowerShell\v1.0\;C:\WINDOWS\System32\OpenSSH\;C:\Program Files\Git\cmd;'+
        'C:\Program Files\TortoiseGit\bin;C:\Strawberry\c\bin;C:\Strawberry\perl\site\bin;C:\Strawberry\perl\bin;'+
        'C:\Program Files\Meld\;C:\FPC\3.2.2\bin\i386-Win32;C:\Ruby27-x64\bin;'+
        'C:\Users\1\AppData\Local\Microsoft\WindowsApps;C:\Strawberry\perl\bin;C:\Ruby27-x64\msys64\mingw64\bin;'+
        'C:\Program Files\jdk-21.0.1\bin;C:\texlive\2023\bin\windows;C:\Program Files\ffmpeg-6.0-full_build\bin;'+
        'C:\Program Files (x86)\Nmap;'));

writeln(IsPathInList('C:\Program Files\ffmpeg-6.0-full_build\bin', ';C:\WINDOWS\system32;C:\WINDOWS;C:\WINDOWS\System32\Wbem;'+
        'C:\WINDOWS\System32\WindowsPowerShell\v1.0\;C:\WINDOWS\System32\OpenSSH\;C:\Program Files\Git\cmd;'+
        'C:\Program Files\TortoiseGit\bin;C:\Strawberry\c\bin;C:\Strawberry\perl\site\bin;C:\Strawberry\perl\bin;'+
        'C:\Program Files\Meld\;C:\FPC\3.2.2\bin\i386-Win32;C:\Ruby27-x64\bin;'+
        'C:\Users\1\AppData\Local\Microsoft\WindowsApps;C:\Strawberry\perl\bin;C:\Ruby27-x64\msys64\mingw64\bin;'+
        'C:\Program Files\jdk-21.0.1\bin;C:\texlive\2023\bin\windows;C:\Program Files\ffmpeg-6.0-full_build\bin;'+
        'C:\Program Files (x86)\Nmap;'));


writeln();
writeln('With two semicolons at the beginning.');

writeln(IsPathInList('C:\Program Files (x86)\Nmap', ';;C:\WINDOWS\system32;C:\WINDOWS;C:\WINDOWS\System32\Wbem;'+
        'C:\WINDOWS\System32\WindowsPowerShell\v1.0\;C:\WINDOWS\System32\OpenSSH\;C:\Program Files\Git\cmd;'+
        'C:\Program Files\TortoiseGit\bin;C:\Strawberry\c\bin;C:\Strawberry\perl\site\bin;C:\Strawberry\perl\bin;'+
        'C:\Program Files\Meld\;C:\FPC\3.2.2\bin\i386-Win32;C:\Ruby27-x64\bin;'+
        'C:\Users\1\AppData\Local\Microsoft\WindowsApps;C:\Strawberry\perl\bin;C:\Ruby27-x64\msys64\mingw64\bin;'+
        'C:\Program Files\jdk-21.0.1\bin;C:\texlive\2023\bin\windows;C:\Program Files\ffmpeg-6.0-full_build\bin;'+
        'C:\Program Files (x86)\Nmap;'));

writeln(IsPathInList('C:\WINDOWS\system32', ';;C:\WINDOWS\system32;C:\WINDOWS;C:\WINDOWS\System32\Wbem;'+
        'C:\WINDOWS\System32\WindowsPowerShell\v1.0\;C:\WINDOWS\System32\OpenSSH\;C:\Program Files\Git\cmd;'+
        'C:\Program Files\TortoiseGit\bin;C:\Strawberry\c\bin;C:\Strawberry\perl\site\bin;C:\Strawberry\perl\bin;'+
        'C:\Program Files\Meld\;C:\FPC\3.2.2\bin\i386-Win32;C:\Ruby27-x64\bin;'+
        'C:\Users\1\AppData\Local\Microsoft\WindowsApps;C:\Strawberry\perl\bin;C:\Ruby27-x64\msys64\mingw64\bin;'+
        'C:\Program Files\jdk-21.0.1\bin;C:\texlive\2023\bin\windows;C:\Program Files\ffmpeg-6.0-full_build\bin;'+
        'C:\Program Files (x86)\Nmap;'));

writeln(IsPathInList('C:\Program Files\TortoiseGit\bin', ';;C:\WINDOWS\system32;C:\WINDOWS;C:\WINDOWS\System32\Wbem;'+
        'C:\WINDOWS\System32\WindowsPowerShell\v1.0\;C:\WINDOWS\System32\OpenSSH\;C:\Program Files\Git\cmd;'+
        'C:\Program Files\TortoiseGit\bin;C:\Strawberry\c\bin;C:\Strawberry\perl\site\bin;C:\Strawberry\perl\bin;'+
        'C:\Program Files\Meld\;C:\FPC\3.2.2\bin\i386-Win32;C:\Ruby27-x64\bin;'+
        'C:\Users\1\AppData\Local\Microsoft\WindowsApps;C:\Strawberry\perl\bin;C:\Ruby27-x64\msys64\mingw64\bin;'+
        'C:\Program Files\jdk-21.0.1\bin;C:\texlive\2023\bin\windows;C:\Program Files\ffmpeg-6.0-full_build\bin;'+
        'C:\Program Files (x86)\Nmap;'));

writeln(IsPathInList('C:\WINDOWS', ';;C:\WINDOWS\system32;C:\WINDOWS;C:\WINDOWS\System32\Wbem;'+
        'C:\WINDOWS\System32\WindowsPowerShell\v1.0\;C:\WINDOWS\System32\OpenSSH\;C:\Program Files\Git\cmd;'+
        'C:\Program Files\TortoiseGit\bin;C:\Strawberry\c\bin;C:\Strawberry\perl\site\bin;C:\Strawberry\perl\bin;'+
        'C:\Program Files\Meld\;C:\FPC\3.2.2\bin\i386-Win32;C:\Ruby27-x64\bin;'+
        'C:\Users\1\AppData\Local\Microsoft\WindowsApps;C:\Strawberry\perl\bin;C:\Ruby27-x64\msys64\mingw64\bin;'+
        'C:\Program Files\jdk-21.0.1\bin;C:\texlive\2023\bin\windows;C:\Program Files\ffmpeg-6.0-full_build\bin;'+
        'C:\Program Files (x86)\Nmap;'));

writeln(IsPathInList('C:\Program Files\ffmpeg-6.0-full_build\bin', ';;C:\WINDOWS\system32;C:\WINDOWS;C:\WINDOWS\System32\Wbem;'+
        'C:\WINDOWS\System32\WindowsPowerShell\v1.0\;C:\WINDOWS\System32\OpenSSH\;C:\Program Files\Git\cmd;'+
        'C:\Program Files\TortoiseGit\bin;C:\Strawberry\c\bin;C:\Strawberry\perl\site\bin;C:\Strawberry\perl\bin;'+
        'C:\Program Files\Meld\;C:\FPC\3.2.2\bin\i386-Win32;C:\Ruby27-x64\bin;'+
        'C:\Users\1\AppData\Local\Microsoft\WindowsApps;C:\Strawberry\perl\bin;C:\Ruby27-x64\msys64\mingw64\bin;'+
        'C:\Program Files\jdk-21.0.1\bin;C:\texlive\2023\bin\windows;C:\Program Files\ffmpeg-6.0-full_build\bin;'+
        'C:\Program Files (x86)\Nmap;'));


writeln();
writeln('With three semicolons in the middle.');

writeln(IsPathInList('C:\Program Files (x86)\Nmap', 'C:\WINDOWS\system32;C:\WINDOWS;C:\WINDOWS\System32\Wbem;'+
        'C:\WINDOWS\System32\WindowsPowerShell\v1.0\;C:\WINDOWS\System32\OpenSSH\;C:\Program Files\Git\cmd;'+
        'C:\Program Files\TortoiseGit\bin;C:\Strawberry\c\bin;;;C:\Strawberry\perl\site\bin;C:\Strawberry\perl\bin;'+
        'C:\Program Files\Meld\;C:\FPC\3.2.2\bin\i386-Win32;C:\Ruby27-x64\bin;'+
        'C:\Users\1\AppData\Local\Microsoft\WindowsApps;C:\Strawberry\perl\bin;C:\Ruby27-x64\msys64\mingw64\bin;'+
        'C:\Program Files\jdk-21.0.1\bin;C:\texlive\2023\bin\windows;C:\Program Files\ffmpeg-6.0-full_build\bin;'+
        'C:\Program Files (x86)\Nmap;'));

writeln(IsPathInList('C:\WINDOWS\system32', 'C:\WINDOWS\system32;C:\WINDOWS;C:\WINDOWS\System32\Wbem;'+
        'C:\WINDOWS\System32\WindowsPowerShell\v1.0\;C:\WINDOWS\System32\OpenSSH\;C:\Program Files\Git\cmd;'+
        'C:\Program Files\TortoiseGit\bin;C:\Strawberry\c\bin;;;C:\Strawberry\perl\site\bin;C:\Strawberry\perl\bin;'+
        'C:\Program Files\Meld\;C:\FPC\3.2.2\bin\i386-Win32;C:\Ruby27-x64\bin;'+
        'C:\Users\1\AppData\Local\Microsoft\WindowsApps;C:\Strawberry\perl\bin;C:\Ruby27-x64\msys64\mingw64\bin;'+
        'C:\Program Files\jdk-21.0.1\bin;C:\texlive\2023\bin\windows;C:\Program Files\ffmpeg-6.0-full_build\bin;'+
        'C:\Program Files (x86)\Nmap;'));

writeln(IsPathInList('C:\Program Files\TortoiseGit\bin', 'C:\WINDOWS\system32;C:\WINDOWS;C:\WINDOWS\System32\Wbem;'+
        'C:\WINDOWS\System32\WindowsPowerShell\v1.0\;C:\WINDOWS\System32\OpenSSH\;C:\Program Files\Git\cmd;'+
        'C:\Program Files\TortoiseGit\bin;C:\Strawberry\c\bin;;;C:\Strawberry\perl\site\bin;C:\Strawberry\perl\bin;'+
        'C:\Program Files\Meld\;C:\FPC\3.2.2\bin\i386-Win32;C:\Ruby27-x64\bin;'+
        'C:\Users\1\AppData\Local\Microsoft\WindowsApps;C:\Strawberry\perl\bin;C:\Ruby27-x64\msys64\mingw64\bin;'+
        'C:\Program Files\jdk-21.0.1\bin;C:\texlive\2023\bin\windows;C:\Program Files\ffmpeg-6.0-full_build\bin;'+
        'C:\Program Files (x86)\Nmap;'));

writeln(IsPathInList('C:\WINDOWS', 'C:\WINDOWS\system32;C:\WINDOWS;C:\WINDOWS\System32\Wbem;'+
        'C:\WINDOWS\System32\WindowsPowerShell\v1.0\;C:\WINDOWS\System32\OpenSSH\;C:\Program Files\Git\cmd;'+
        'C:\Program Files\TortoiseGit\bin;C:\Strawberry\c\bin;;;C:\Strawberry\perl\site\bin;C:\Strawberry\perl\bin;'+
        'C:\Program Files\Meld\;C:\FPC\3.2.2\bin\i386-Win32;C:\Ruby27-x64\bin;'+
        'C:\Users\1\AppData\Local\Microsoft\WindowsApps;C:\Strawberry\perl\bin;C:\Ruby27-x64\msys64\mingw64\bin;'+
        'C:\Program Files\jdk-21.0.1\bin;C:\texlive\2023\bin\windows;C:\Program Files\ffmpeg-6.0-full_build\bin;'+
        'C:\Program Files (x86)\Nmap;'));

writeln(IsPathInList('C:\Program Files\ffmpeg-6.0-full_build\bin', 'C:\WINDOWS\system32;C:\WINDOWS;C:\WINDOWS\System32\Wbem;'+
        'C:\WINDOWS\System32\WindowsPowerShell\v1.0\;C:\WINDOWS\System32\OpenSSH\;C:\Program Files\Git\cmd;'+
        'C:\Program Files\TortoiseGit\bin;C:\Strawberry\c\bin;;;C:\Strawberry\perl\site\bin;C:\Strawberry\perl\bin;'+
        'C:\Program Files\Meld\;C:\FPC\3.2.2\bin\i386-Win32;C:\Ruby27-x64\bin;'+
        'C:\Users\1\AppData\Local\Microsoft\WindowsApps;C:\Strawberry\perl\bin;C:\Ruby27-x64\msys64\mingw64\bin;'+
        'C:\Program Files\jdk-21.0.1\bin;C:\texlive\2023\bin\windows;C:\Program Files\ffmpeg-6.0-full_build\bin;'+
        'C:\Program Files (x86)\Nmap;'));


writeln(); writeln();
writeln('-----------');
writeln();

writeln('These lines must return FALSE.');

writeln(IsPathInList('C:\Program', 'C:\WINDOWS\system32;C:\WINDOWS;C:\WINDOWS\System32\Wbem;'+
        'C:\WINDOWS\System32\WindowsPowerShell\v1.0\;C:\WINDOWS\System32\OpenSSH\;C:\Program Files\Git\cmd;'+
        'C:\Program Files\TortoiseGit\bin;C:\Strawberry\c\bin;C:\Strawberry\perl\site\bin;C:\Strawberry\perl\bin;'+
        'C:\Program Files\Meld\;C:\FPC\3.2.2\bin\i386-Win32;C:\Ruby27-x64\bin;'+
        'C:\Users\1\AppData\Local\Microsoft\WindowsApps;C:\Strawberry\perl\bin;C:\Ruby27-x64\msys64\mingw64\bin;'+
        'C:\Program Files\jdk-21.0.1\bin;C:\texlive\2023\bin\windows;C:\Program Files\ffmpeg-6.0-full_build\bin;'+
        'C:\Program Files (x86)\Nmap;'));

writeln(IsPathInList(';', 'C:\WINDOWS\system32;C:\WINDOWS;C:\WINDOWS\System32\Wbem;'+
        'C:\WINDOWS\System32\WindowsPowerShell\v1.0\;C:\WINDOWS\System32\OpenSSH\;C:\Program Files\Git\cmd;'+
        'C:\Program Files\TortoiseGit\bin;C:\Strawberry\c\bin;C:\Strawberry\perl\site\bin;C:\Strawberry\perl\bin;'+
        'C:\Program Files\Meld\;C:\FPC\3.2.2\bin\i386-Win32;C:\Ruby27-x64\bin;'+
        'C:\Users\1\AppData\Local\Microsoft\WindowsApps;C:\Strawberry\perl\bin;C:\Ruby27-x64\msys64\mingw64\bin;'+
        'C:\Program Files\jdk-21.0.1\bin;C:\texlive\2023\bin\windows;C:\Program Files\ffmpeg-6.0-full_build\bin;'+
        'C:\Program Files (x86)\Nmap;'));

writeln(IsPathInList(';', 'C:\WINDOWS\system32;C:\WINDOWS;C:\WINDOWS\System32\Wbem;'+
        'C:\WINDOWS\System32\WindowsPowerShell\v1.0\;C:\WINDOWS\System32\OpenSSH\;C:\Program Files\Git\cmd;'+
        'C:\Program Files\TortoiseGit\bin;C:\Strawberry\c\bin;C:\Strawberry\perl\site\bin;C:\Strawberry\perl\bin;'+
        'C:\Program Files\Meld\;C:\FPC\3.2.2\bin\i386-Win32;C:\Ruby27-x64\bin;'+
        'C:\Users\1\AppData\Local\Microsoft\WindowsApps;C:\Strawberry\perl\bin;C:\Ruby27-x64\msys64\mingw64\bin;'+
        'C:\Program Files\jdk-21.0.1\bin;C:\texlive\2023\bin\windows;C:\Program Files\ffmpeg-6.0-full_build\bin;'+
        'C:\Program Files (x86)\Nmap;'));

writeln(IsPathInList('zxczxczx', 'C:\WINDOWS\system32;C:\WINDOWS;C:\WINDOWS\System32\Wbem;'+
        'C:\WINDOWS\System32\WindowsPowerShell\v1.0\;C:\WINDOWS\System32\OpenSSH\;C:\Program Files\Git\cmd;'+
        'C:\Program Files\TortoiseGit\bin;C:\Strawberry\c\bin;C:\Strawberry\perl\site\bin;C:\Strawberry\perl\bin;'+
        'C:\Program Files\Meld\;C:\FPC\3.2.2\bin\i386-Win32;C:\Ruby27-x64\bin;'+
        'C:\Users\1\AppData\Local\Microsoft\WindowsApps;C:\Strawberry\perl\bin;C:\Ruby27-x64\msys64\mingw64\bin;'+
        'C:\Program Files\jdk-21.0.1\bin;C:\texlive\2023\bin\windows;C:\Program Files\ffmpeg-6.0-full_build\bin;'+
        'C:\Program Files (x86)\Nmap;'));

writeln(IsPathInList('C:\', 'C:\WINDOWS\system32;C:\WINDOWS;C:\WINDOWS\System32\Wbem;'+
        'C:\WINDOWS\System32\WindowsPowerShell\v1.0\;C:\WINDOWS\System32\OpenSSH\;C:\Program Files\Git\cmd;'+
        'C:\Program Files\TortoiseGit\bin;C:\Strawberry\c\bin;C:\Strawberry\perl\site\bin;C:\Strawberry\perl\bin;'+
        'C:\Program Files\Meld\;C:\FPC\3.2.2\bin\i386-Win32;C:\Ruby27-x64\bin;'+
        'C:\Users\1\AppData\Local\Microsoft\WindowsApps;C:\Strawberry\perl\bin;C:\Ruby27-x64\msys64\mingw64\bin;'+
        'C:\Program Files\jdk-21.0.1\bin;C:\texlive\2023\bin\windows;C:\Program Files\ffmpeg-6.0-full_build\bin;'+
        'C:\Program Files (x86)\Nmap;'));

writeln(IsPathInList('Nmap', 'C:\WINDOWS\system32;C:\WINDOWS;C:\WINDOWS\System32\Wbem;'+
        'C:\WINDOWS\System32\WindowsPowerShell\v1.0\;C:\WINDOWS\System32\OpenSSH\;C:\Program Files\Git\cmd;'+
        'C:\Program Files\TortoiseGit\bin;C:\Strawberry\c\bin;C:\Strawberry\perl\site\bin;C:\Strawberry\perl\bin;'+
        'C:\Program Files\Meld\;C:\FPC\3.2.2\bin\i386-Win32;C:\Ruby27-x64\bin;'+
        'C:\Users\1\AppData\Local\Microsoft\WindowsApps;C:\Strawberry\perl\bin;C:\Ruby27-x64\msys64\mingw64\bin;'+
        'C:\Program Files\jdk-21.0.1\bin;C:\texlive\2023\bin\windows;C:\Program Files\ffmpeg-6.0-full_build\bin;'+
        'C:\Program Files (x86)\Nmap;'));

writeln(IsPathInList('', 'C:\WINDOWS\system32;C:\WINDOWS;C:\WINDOWS\System32\Wbem;'+
        'C:\WINDOWS\System32\WindowsPowerShell\v1.0\;C:\WINDOWS\System32\OpenSSH\;C:\Program Files\Git\cmd;'+
        'C:\Program Files\TortoiseGit\bin;C:\Strawberry\c\bin;C:\Strawberry\perl\site\bin;C:\Strawberry\perl\bin;'+
        'C:\Program Files\Meld\;C:\FPC\3.2.2\bin\i386-Win32;C:\Ruby27-x64\bin;'+
        'C:\Users\1\AppData\Local\Microsoft\WindowsApps;C:\Strawberry\perl\bin;C:\Ruby27-x64\msys64\mingw64\bin;'+
        'C:\Program Files\jdk-21.0.1\bin;C:\texlive\2023\bin\windows;C:\Program Files\ffmpeg-6.0-full_build\bin;'+
        'C:\Program Files (x86)\Nmap;'));

end.
