; environment.iss
; The code is kindly provided by Wojciech Mleczek in the answer on StackOverflow:
; https://stackoverflow.com/a/46609047/1240328
; Modified to be used at the current user level (if there are no administrator privileges).

[Code]
procedure SelectEnvKeys(var RootKey: integer; var EnvironmentKey: string);
begin
    if IsAdminInstallMode() then
    begin
      RootKey := HKEY_LOCAL_MACHINE;
      EnvironmentKey := 'SYSTEM\CurrentControlSet\Control\Session Manager\Environment';
    end
    else
    begin
      RootKey := HKEY_CURRENT_USER;
      EnvironmentKey := 'Environment';
    end;
end;


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


procedure EnvAddPath(Path: string);
var
    RootKey: integer;
    EnvironmentKey: string;
    Paths: string;
begin
    SelectEnvKeys(RootKey, EnvironmentKey);

    { Retrieve current path (use empty string if entry not exists) }
    if not RegQueryStringValue(RootKey, EnvironmentKey, 'Path', Paths)
    then Paths := '';

    if IsPathInList(Path, Paths) then exit;

    if 0 = Length(Paths) then
        Paths := Path
    else if SameStr(';', Copy(Paths, Length(Paths), 1)) then
        Paths := Paths + Path
    else
        Paths := Paths + ';'+ Path;

    { Overwrite (or create if missing) path environment variable }
    if RegWriteStringValue(RootKey, EnvironmentKey, 'Path', Paths)
    then Log(Format('The [%s] added to PATH: [%s]', [Path, Paths]))
    else Log(Format('Error while adding the [%s] to PATH: [%s]', [Path, Paths]));
end;


procedure EnvRemovePath(Path: string);
var
    RootKey: integer;
    EnvironmentKey: string;
    Paths: string;
    P: integer;
begin
    SelectEnvKeys(RootKey, EnvironmentKey);

    { Skip if registry entry not exists }
    if not RegQueryStringValue(RootKey, EnvironmentKey, 'Path', Paths) then
        exit;

    if not IsPathInList(Path, Paths) then exit;
    P := Pos(';' + Uppercase(Path) + ';', ';' + Uppercase(Paths) + ';');

    { Update path variable }
    Delete(Paths, P - 1, Length(Path) + 1);

    { Overwrite path environment variable }
    if RegWriteStringValue(RootKey, EnvironmentKey, 'Path', Paths)
    then Log(Format('The [%s] removed from PATH: [%s]', [Path, Paths]))
    else Log(Format('Error while removing the [%s] from PATH: [%s]', [Path, Paths]));
end;
