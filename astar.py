from utility import *


class Maze:
    def __init__(self, filename):

        with open(filename) as f:
            contents = f.read()

        if contents.count('A') != 1:
            raise Exception('maze must have exactly one start point')
        if contents.count('B') != 1:
            raise Exception('maze must have exactly one goal point')

        contents = contents.splitlines()
        self.height = len(contents)
        self.width = max(len(line) for line in contents)

        self.walls = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                if contents[i][j] == 'A':
                    self.start = (i, j)
                    row.append(False)
                elif contents[i][j] == 'B':
                    self.goal = (i, j)
                    row.append(False)
                elif contents[i][j] == ' ':
                    row.append(False)
                else:
                    row.append(True)
            self.walls.append(row)

        self.solution = None

    def neighbors(self, state):
        # state is a tuple.(location af agent)
        row, col = state
        candidates = [
            ("UP", (row - 1, col)),
            ("Down", (row + 1, col)),
            ("Left", (row, col - 1)),
            ("Right", (row, col + 1))
        ]

        # Which state are available and not wall
        result = []

        for action, (r, c) in candidates:
            if 0 <= r < self.height and 0 <= c < self.width and not self.walls[r][c]:
                result.append((action, (r, c)))

        return result


    def solve_astar(self):
        self.num_explored = 0

        start = Node(state=self.start, parent=None, action=None)
        start.g_score = 0
        start.f_score = manhattan_dis(start.state, self.goal)
        start.h_score = manhattan_dis(start.state, self.goal)
        frontier = QueueFrontier()
        frontier.sort_add(start)

        self.explored = set()
        self.score_of_explored = []

        # keep looping until solution found
        while True:
            if frontier.is_empty():
                raise Exception("no solution")

            # Choose a node from the frontier
            node = frontier.remove()
            self.num_explored += 1

            # If node is the goal, then we have a solution
            if node.state == self.goal:
                actions = []
                cells = []
                f_score = []
                g_score = []
                h_score = []
                while node.parent is not None:
                    actions.append(node.action)
                    cells.append(node.state)
                    f_score.append(node.f_score)
                    g_score.append(node.g_score)
                    h_score.append(node.h_score)
                    node = node.parent
                actions.reverse()
                cells.reverse()
                f_score.reverse()
                g_score.reverse()
                h_score.reverse()

                self.solution = (actions, (cells, f_score, g_score, h_score))

                return

            # Mark node as explored
            self.explored.add(node.state)
            self.score_of_explored .append([node.state, node.f_score, node.g_score, node.h_score])

            # Add neighbors to frontier .(expand nodes )
            for action, state in self.neighbors(node.state):
                if not frontier.contain_state(state) and state not in self.explored:
                    child = Node(state=state, parent=node, action=action)
                    temp_g_score = node.g_score + 1
                    temp_f_score = temp_g_score + manhattan_dis(state, self.goal)
                    if temp_f_score < child.f_score:
                        child.g_score = temp_g_score
                        child.f_score = temp_f_score
                        child.h_score = manhattan_dis(state, self.goal)
                        frontier.sort_add(child)

    def output_image(self, filename, show_solution=True, show_explored=False):
        from PIL import Image, ImageDraw
        cell_size = 50
        cell_border = 2

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.width * cell_size, self.height * cell_size),
            "black"
        )
        draw = ImageDraw.Draw(img)

        solution = self.solution[1] if self.solution is not None else None

        for i, row in enumerate(self.walls):
            for j, col in enumerate(row):

                f_score = float('inf')
                g_score = float('inf')
                h_score = float('inf')
                # Walls
                if col:
                    fill = (40, 40, 40)

                # Start
                elif (i, j) == self.start:
                    fill = (255, 0, 0)

                # Goal
                elif (i, j) == self.goal:
                    fill = (0, 171, 28)

                # Solution
                elif solution is not None and show_solution and (i, j) in solution[0]:
                    fill = (220, 235, 113)
                    ind = solution[0].index((i, j))
                    f_score = solution[1][ind]
                    g_score = solution[2][ind]
                    h_score = solution[3][ind]

                # Explored
                elif solution is not None and show_explored and (i, j) in self.explored:
                    for row in self.score_of_explored :
                        if row[0] == (i, j):
                            f_score = row[1]
                            g_score = row[2]
                            h_score = row[3]

                    fill = (212, 97, 85)

                # Empty cell
                else:
                    fill = (237, 240, 252)

                # Draw cell
                draw.rectangle(
                    ([(j * cell_size + cell_border, i * cell_size + cell_border),
                      ((j + 1) * cell_size - cell_border, (i + 1) * cell_size - cell_border)]),
                    fill=fill
                )
                x = int(((j * cell_size + cell_border) + ((j + 1) * cell_size - cell_border)) / 2)
                y = int(((i * cell_size + cell_border) + ((i + 1) * cell_size - cell_border)) / 2)
                draw.text((x - 15, y), text=f"{h_score}+{g_score}=", fill=(40, 40, 40))
                draw.text((x - 10, y + 10), text=f"{f_score}", fill=(40, 40, 40))

        img.save(filename)


m = Maze('maze2.txt')
print("Maze:")

print("Solving...")
m.solve_astar()
print("States Explored:", m.num_explored)
print("Solution:")

m.output_image("maze2_astar.png", show_explored=True)
