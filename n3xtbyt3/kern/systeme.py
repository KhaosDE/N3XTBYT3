"""Die vier Systeme, die N3XTBYT3 simuliert, und ihre festen Eigenschaften."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Shell:
    """Eine Befehlszeile innerhalb eines Systems (z. B. cmd oder PowerShell)."""

    id: str
    name: str            # Anzeigename, z. B. "Windows PowerShell"
    name_admin: str      # Anzeigename mit Administratorrechten


@dataclass(frozen=True)
class System:
    id: str
    name: str
    shells: tuple[Shell, ...]
    start_shell: str
    # Windows unterscheidet bei Befehlen nicht zwischen Groß- und Kleinschreibung,
    # Linux schon.
    gross_klein_egal: bool
    # Zeichen, mit denen Optionen beginnen (Windows: /x und -x, Linux: -x).
    options_zeichen: tuple[str, ...]

    def shell(self, shell_id: str) -> Shell:
        for s in self.shells:
            if s.id == shell_id:
                return s
        raise KeyError(shell_id)

    @property
    def shell_ids(self) -> tuple[str, ...]:
        return tuple(s.id for s in self.shells)


_POWERSHELL = Shell("powershell", "Windows PowerShell", "Administrator: Windows PowerShell")
_CMD = Shell("cmd", "Eingabeaufforderung (cmd)", "Administrator: Eingabeaufforderung (cmd)")
_BASH = Shell("bash", "Terminal (Bash)", "Terminal (Bash, root)")

SYSTEME: dict[str, System] = {
    "windows": System(
        id="windows",
        name="Windows",
        shells=(_POWERSHELL, _CMD),
        start_shell="powershell",
        gross_klein_egal=True,
        options_zeichen=("/", "-"),
    ),
    "windows_server": System(
        id="windows_server",
        name="Windows Server",
        shells=(_POWERSHELL, _CMD),
        start_shell="powershell",
        gross_klein_egal=True,
        options_zeichen=("/", "-"),
    ),
    "linux": System(
        id="linux",
        name="Linux",
        shells=(_BASH,),
        start_shell="bash",
        gross_klein_egal=False,
        options_zeichen=("-",),
    ),
    "linux_server": System(
        id="linux_server",
        name="Linux Server",
        shells=(_BASH,),
        start_shell="bash",
        gross_klein_egal=False,
        options_zeichen=("-",),
    ),
}

REIHENFOLGE = ("windows", "windows_server", "linux", "linux_server")


def system(system_id: str) -> System:
    try:
        return SYSTEME[system_id]
    except KeyError:
        bekannt = ", ".join(REIHENFOLGE)
        raise KeyError(f"Unbekanntes System „{system_id}“. Erlaubt sind: {bekannt}.") from None
