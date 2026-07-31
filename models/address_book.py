from dataclasses import dataclass


@dataclass
class Group:
    name: str
    members: list[str]


@dataclass
class AddressBook:
    groups: list[Group]

    @property
    def no_of_groups(self) -> int:
        return len(self.groups)

    @classmethod
    def from_dict(cls, data: dict) -> "AddressBook":
        # --- Old format: groups and ungrouped split ---
        if "groups" in data or "ungrouped" in data:
            groups = [Group(name=n, members=m) for n, m in data.get("groups", {}).items()]
            return cls(groups=groups)

        # --- Current format ---
        return cls(groups=[Group(name=n, members=m) for n, m in data.items()])

    def to_dict(self) -> dict:
        return {g.name: g.members for g in self.groups}

    def get_group_by_name(self, name: str) -> Group | None:
        for g in self.groups:
            if g.name.upper() == name.upper():
                return g
        return None

    def get_group_by_index(self, idx: int) -> Group | None:
        if 0 <= idx < self.no_of_groups:
            return self.groups[idx]
        return None

    def group_exists(self, name: str) -> bool:
        return self.get_group_by_name(name) is not None

    def add_group(self, name: str, members: list[str]) -> None:
        self.groups.append(Group(name=name, members=list(members)))

    def remove_group(self, group: Group) -> None:
        self.groups.remove(group)