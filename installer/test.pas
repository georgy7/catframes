program tttt;
uses sysutils;

{ Use -MANSISTRINGS compiler option in Free Pascal: https://www.freepascal.org/docs-html/user/usersu16.html }

function IsPathInList(Path: string; Paths: string): boolean;
var
    X, Tail: string;
    P: integer;
begin
    Result := false;

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

        if SameStr(Uppercase(X), Uppercase(Path)) then
        begin
            Result := true;
            break;
        end;
    end;
end;


function StartsWith(S, Head: string): boolean;
begin
    Result := (1=Pos(Head, S));
end;


function EndsWith(S, Tail: string): boolean;
begin
    Result := SameStr(Tail, Copy(S, Length(S)+1-Length(Tail), Length(Tail)));
end;


function WithoutPathInternal(S, Path: string): string;
var
    Part: string;
    I: integer;
begin
    if SameStr(Uppercase(Path), Uppercase(S)) then Result := ''
    else
    begin
        Result := S;

        Part := ';'+Uppercase(Path)+';';
        repeat
            I := Pos(Part, Uppercase(Result));
            Delete(Result, I, Length(Part)-1);
        until 0=I;

        Part := Uppercase(Path)+';';
        if StartsWith(Uppercase(Result), Part) then
            Delete(Result, 1, Length(Part));

        Part := ';'+Uppercase(Path);
        if EndsWith(Uppercase(Result), Part) then
            Delete(Result, Length(Result)+1-Length(Part), Length(Part));

        if StartsWith(Result, ';') then
            Delete(Result, 1, 1);

        if EndsWith(Result, ';') then
            Delete(Result, Length(Result), 1);
    end;
end;


function WithoutPath(S, Path: string): string;
begin
    Result := WithoutPathInternal(S, Path);
    if EndsWith(Path, '\') then
        Result := WithoutPathInternal(Result, Copy(Path, 1, Length(Path)-1))
    else
        Result := WithoutPathInternal(Result, Path+'\');
end;


var
    Env, Part: string;
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


writeln();
writeln('Short string (must work even without ANSISTRINGS):');
writeln(IsPathInList('C:\Program Files (x86)\Nmap', ''+
        'C:\Users\1\AppData\Local\Microsoft\WindowsApps;C:\Strawberry\perl\bin;C:\Ruby27-x64\msys64\mingw64\bin;'+
        'C:\Program Files\jdk-21.0.1\bin;C:\texlive\2023\bin\windows;C:\Program Files\ffmpeg-6.0-full_build\bin;'+
        'C:\Program Files (x86)\Nmap;'));
writeln(IsPathInList('C:\Program Files (x86)\Nmap', 'C:\Program Files (x86)\Nmap'));


writeln();
writeln('Case insensitive:');
writeln(IsPathInList('C:\TEXLIVE\2023\bin\WinDoWS', ''+
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

writeln(); writeln();
writeln('+++++++++++');
writeln();

writeln('StartsWith: X X');
writeln(StartsWith('X', 'X'));
writeln();

writeln('StartsWith: Abcde Ab');
writeln(StartsWith('Abcde', 'Ab'));
writeln();

writeln('StartsWith: Abcde A');
writeln(StartsWith('Abcde', 'A'));
writeln();

writeln('StartsWith: Abcde de');
writeln(StartsWith('Abcde', 'de'));
writeln();

writeln();

writeln('EndsWith: X X');
writeln(EndsWith('X', 'X'));
writeln();

writeln('EndsWith: Abcde de');
writeln(EndsWith('Abcde', 'de'));
writeln();

writeln('EndsWith: Abcde; ;');
writeln(EndsWith('Abcde;', ';'));
writeln();

writeln('EndsWith: Abcde ;');
writeln(EndsWith('Abcde', ';'));

writeln(); writeln();
writeln('///////////');
writeln();

writeln('Testing WithoutPath function...');
writeln();

Part := 'C:\Abcd';
Env := 'C:\Abcd';
writeln('Removing '+Part);
writeln('From '+Env);
writeln('Result: '+WithoutPath(Env, Part));
writeln();

Env := 'C:\ABCD';
writeln('Removing '+Part);
writeln('From '+Env);
writeln('Result: '+WithoutPath(Env, Part));
writeln();

Env := 'C:\Xyz';
writeln('Removing '+Part);
writeln('From '+Env);
writeln('Result: '+WithoutPath(Env, Part));
writeln();

Part := 'C:\Program Files (x86)\Nmap';
Env := Part+';';
writeln('Removing '+Part);
writeln('From '+Env);
writeln('Result: '+WithoutPath(Env, Part));
writeln();

Env := 'C:\Program Files (x86)\NMAP;C:\Program Files\Meld\;C:\Ruby27-x64\bin';
writeln('Removing '+Part);
writeln('From '+Env);
writeln('Result: '+WithoutPath(Env, Part));
writeln();

Env := 'C:\Program Files\Meld\;C:\Ruby27-x64\bin;C:\Program Files (x86)\NMAP';
writeln('Removing '+Part);
writeln('From '+Env);
writeln('Result: '+WithoutPath(Env, Part));
writeln();

Env := 'C:\Program Files\Meld\;C:\Program Files (x86)\NMAP;C:\Ruby27-x64\bin';
writeln('Removing '+Part);
writeln('From '+Env);
writeln('Result: '+WithoutPath(Env, Part));
writeln();

Env := 'C:\Program Files (x86)\Nmap;C:\Program Files\Meld\;C:\Program Files (x86)\Nmap;C:\Program Files (x86)\NMAP;C:\Ruby27-x64\bin;C:\Program Files (x86)\Nmap;';
writeln('Removing '+Part);
writeln('From '+Env);
writeln('Result: '+WithoutPath(Env, Part));
writeln();

Env := 'C:\Program Files (x86)\Nmap;C:\Program Files\Meld\;C:\Program Files (x86)\Nmap;C:\Program Files (x86)\NMAP;C:\Ruby27-x64\bin;C:\Program Files (x86)\Nmap';
writeln('Removing '+Part);
writeln('From '+Env);
writeln('Result: '+WithoutPath(Env, Part));
writeln();

Env := 'C:\Program Files (x86)\Nmap;C:\Program Files\Meld\;C:\Program Files (x86)\Nmap\;C:\Program Files (x86)\NMAP;C:\Ruby27-x64\bin;C:\Program Files (x86)\Nmap\';
writeln('Removing '+Part);
writeln('From '+Env);
writeln('Result: '+WithoutPath(Env, Part));
writeln();

Part := 'C:\Program Files (x86)\Nmap\';
Env := 'C:\Program Files (x86)\Nmap;C:\Program Files\Meld\;C:\Program Files (x86)\Nmap\;C:\Program Files (x86)\NMAP;C:\Ruby27-x64\bin;C:\Program Files (x86)\Nmap\';
writeln('Removing '+Part);
writeln('From '+Env);
writeln('Result: '+WithoutPath(Env, Part));
writeln();

end.
