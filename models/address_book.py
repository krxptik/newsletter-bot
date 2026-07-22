from dataclasses import dataclass


def _normalize(value: str) -> str:
        return value.strip().upper()


def _find_index(items: list[str], value: str) -> int | None:
        normalized = _normalize(value)
        return next((i for i, v in enumerate(items) if v.upper() == normalized), None)


def _resolve(raw: str, names: list[str], offset: int) -> int | None:
    """Resolve a 1-based menu number (accounting for entries listed
    before this one) or a name, to an index into `names`."""
    if raw.isdigit():
        index = int(raw) - 1 - offset
        return index if 0 <= index < len(names) else None
    return _find_index(names, raw)


@dataclass
class Group:
    name: str
    members: list[str]


@dataclass
class AddressBook:
    groups: list[Group]
    ungrouped: list[str]

    @property
    def no_of_groups(self) -> int:
        return len(self.groups)

    @classmethod
    def from_dict(cls, data: dict) -> "AddressBook":
        groups = [Group(name=n, members=m) for n, m in data.get("groups", {}).items()]
        ungrouped = data.get("ungrouped", [])
        return cls(groups=groups, ungrouped=ungrouped)

    def to_dict(self) -> dict:
        return {
            "groups": {g.name: g.members for g in self.groups},
            "ungrouped": self.ungrouped,
        }

    def group_exists(self, name: str) -> bool:
        return _find_index([g.name for g in self.groups], name) is not None

    def ungrouped_exists(self, addr: str) -> bool:
        return _find_index(self.ungrouped, addr) is not None

    def resolve_group(self, raw: str) -> tuple[str, int] | None:
        index = _resolve(raw, [g.name for g in self.groups], 0)
        return (self.groups[index].name, index) if index is not None else None

    def resolve_ungrouped(self, raw: str) -> str | None:
        index = _resolve(raw, self.ungrouped, self.no_of_groups)
        return self.ungrouped[index] if index is not None else None

    def add_group(self, name: str, members: list[str]) -> None:
        self.groups.append(Group(name=name, members=list(members)))

    def remove_group(self, index: int) -> None:
        del self.groups[index]

    def add_ungrouped(self, email: str) -> None:
        self.ungrouped.append(email.lower())

    def remove_ungrouped(self, email: str) -> None:
        self.ungrouped.remove(email)