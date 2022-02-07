from typing import List

from it.polimi.strategyviz.logging.logger import Logger

LOGGER = Logger('TIGA PARSER')


class TigaState:
    opener = 'State: '
    str_format = '{}{}'

    # E.g.
    # State: ( Kim.GoBack ) retry=1
    def __init__(self, state):
        self.state = state

    @classmethod
    def parse(cls, line: str):
        if not line.__contains__(cls.opener):
            raise ValueError

        fields = line.split(cls.opener)
        return TigaState(fields[1])

    def __str__(self):
        return self.str_format.format(self.opener, self.state)


class TigaEdge:
    opener = 'When you are in '
    middle = ', take transition '
    str_format = '{}{}{}{}'

    # E.g.
    # When you are in (time<=15 && T<=2 && T-time<-3), take transition Kim.GoBack->Kim.Aalborg { 1, tau, 1 }
    def __init__(self, guard: str, edge: str):
        self.guard = guard
        self.edge = edge

    @classmethod
    def parse(cls, line: str):
        if not line.__contains__(cls.opener):
            raise ValueError

        fields = line.split(cls.opener)[1].split(cls.middle)
        return TigaEdge(fields[0], fields[1])

    def __str__(self):
        return self.str_format.format(self.opener, self.guard, self.middle, self.edge)


class TigaWait:
    opener = 'While you are in\t'
    end = ', wait.'
    str_format = '{}{}{}'

    # E.g.
    # While you are in	(time-T<=9 && T<=6 && T-time<-3), wait.
    def __init__(self, guard: str):
        self.guard = guard

    @classmethod
    def parse(cls, line: str):
        if not line.__contains__(cls.opener):
            raise ValueError

        fields = line.split(cls.opener)[1].split(cls.end)
        return TigaWait(fields[0])

    def __str__(self):
        return self.str_format.format(self.opener, self.guard, self.end)


class TigaBlock:
    # E.g.
    # State: ( Kim.GoBack ) retry=1
    # When you are in (time<=15 && T<=2 && T-time<-3), take transition Kim.GoBack->Kim.Aalborg { 1, tau, 1 }
    def __init__(self, state: TigaState, edges: List[TigaEdge], wait: TigaWait):
        self.state = state
        self.edges = edges
        self.wait = wait

    @staticmethod
    def parse(lines: List[str]):
        if len(lines) < 2:
            raise ValueError

        state = TigaState.parse(lines[0])
        edges = []
        for line in lines[1:]:
            try:
                edges.append(TigaEdge.parse(line))
            except ValueError:
                pass

        wait = None
        if len(edges) == 0:
            for line in lines[1:]:
                try:
                    wait = TigaWait.parse(line)
                except ValueError:
                    raise ValueError

        return TigaBlock(state, edges, wait)

    def __str__(self):
        res = str(self.state)
        if len(self.edges) > 0:
            for e in self.edges:
                res += str(e)
        else:
            res += str(self.wait)
        return res + '\n'


def parse_tiga_strategy(file_content: List[str]):
    start_index = file_content.index('Strategy to win:\n')
    block_lines = file_content[start_index + 1:]
    str_blocks = []
    for line in block_lines:
        if line == '\n':
            str_blocks.append([])
        else:
            str_blocks[-1].append(line)

    blocks = []
    for block in str_blocks:
        try:
            blocks.append(TigaBlock.parse(block))
        except ValueError:
            LOGGER.error("An error occurred while parsing the TIGA strategy.")

    [print(b) for b in blocks]