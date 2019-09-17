class TextHistory:
    def __init__(self):
        self._text = ''
        self._version = 0
        self._actions = []
        self._pos = len(self._text)

    @property
    def text(self):
        return self._text

    @property
    def version(self):
        return self._version

    def insert(self, text, pos=None):
        pos = self.check(text, pos)
        action = InsertAction(pos, text, self._version, self._version + 1)
        return self.action(action)

    def replace(self, text, pos=None):
        pos = self.check(text, pos)
        action = ReplaceAction(pos, text, self._version, self._version + 1)
        return self.action(action)

    def delete(self, pos, length):
        pos = self.check(self._text, pos, length)
        action = DeleteAction(pos, length, self._version, self._version + 1)
        return self.action(action)

    def action(self, action):
        self._actions.append(action)
        action.version_check()
        self._text = action.apply(self._text)
        self._version = action.to_version
        return self._version

    def optimisation(self, actions_full_list):
        for act in range(len(actions_full_list) - 1):
            pre_act = actions_full_list[len(actions_full_list) - 1]
            if isinstance(pre_act, DeleteAction) and isinstance(act, DeleteAction) and act.pos == pre_act.pos:
                pre_act.length = pre_act.length + act.length
                pre_act.to_version = act.to_version

            if isinstance(pre_act, InsertAction) and isinstance(act, InsertAction):
                if act.pos == pre_act.pos:
                    pre_act.text = act.text + pre_act.text
                elif act.pos - pre_act.pos == len(pre_act.text):
                    pre_act.text = pre_act.text + act.text
        return actions_full_list

    def get_actions(self, from_version=0, to_version=None):
        optimisation_flag = True
        if from_version is None:
            from_version = 0

        if to_version is None:
            to_version = self._version

        if from_version < 0 or from_version > to_version or to_version > self._version:
            raise ValueError

        action_to_return = []
        for action in self._actions:
            if from_version <= action.from_version < to_version != 0:
                action_to_return.append(action)
        if optimisation_flag:
            return self.optimisation(action_to_return)
        else:
            return action_to_return

    def check(self, text, pos, length=None):
        if pos is None:
            pos = len(self._text)
        if not pos < 0 and pos <= len(self._text):
            self._pos = pos
            if length and len(self._text[pos:]) < length:
                raise ValueError
            return pos
        raise ValueError


class Action:
    def __init__(self, pos, text, from_version, to_version):
        self.text = text
        self.pos = pos
        self.from_version = from_version
        self.to_version = to_version

    def version_check(self):
        if not (self.from_version < self.to_version):
            raise ValueError


class InsertAction(Action):
    def apply(self, str):
        str = str[:self.pos] + self.text + str[self.pos:]
        return str

    def __repr__(self):
        return 'Insert({!r}, pos = {!r}, v1 = {!r}, v2 = {!r})'.format(self.text, self.pos, self.from_version, self.to_version)


class ReplaceAction(Action):
    def apply(self, str):
        str = str[:self.pos] + self.text + str[self.pos + len(self.text):]
        return str

    def __repr__(self):
        return 'Replace({!r}, pos = {!r}, v1 = {!r}, v2 = {!r})'.format(self.text, self.pos, self.from_version, self.to_version)


class DeleteAction(Action):
    def __init__(self, pos, length, from_version, to_version):
        self.length = length
        self.pos = pos
        self.from_version = from_version
        self.to_version = to_version

    def apply(self, str):
        str = str[:self.pos] + str[self.pos + self.length:]
        return str

    def __repr__(self):
        return 'Delete(pos = {!r}, length = {!r}, v1 = {!r}, v2 = {!r})'.format(self.pos, self.length, self.from_version, self.to_version)


def main():
    h = TextHistory()

    h.insert("123456")
    h.delete(2, 2)
    h.delete(2, 2)
    h.insert('3')
    print(h.text)
    a = InsertAction(3, '123456', 4, 10)
    h.action(a)
    h.delete(0, 1)
    h.insert('Hello, World')
    print(h.text)
    h.replace('123456', 3)
    h.insert('zxc', 9)
    h.replace('789', 9)
    h.replace('10', 12)
    print(h.text)
    print(h.get_actions())


if __name__ == '__main__':
    main()