import math
from dataclasses import dataclass

@dataclass
class LineSegment:
    waypoint: tuple[float, float]
    path: str


def get_polyline_length(coord) -> float:
    length = 0
    for i in range(len(coord) - 1):
        length += get_distance(coord[i], coord[i + 1])

    return length


def get_distance(xy1, xy2) -> float:
    return math.sqrt((xy2[0] - xy1[0]) ** 2 + (xy2[1] - xy1[1]) ** 2)


def get_line_segment(coord, pct) -> LineSegment:
    tgt_dis = get_polyline_length(coord) * pct

    tot_dis = 0
    path = []
    for i in range(len(coord) - 1):
        dis = get_distance(coord[i], coord[i + 1])
        tot_dis += dis
        if tot_dis >= tgt_dis:
            x1, y1 = coord[i]
            x2, y2 = coord[i + 1]
            a = x2 - x1
            b = y2 - y1

            if a == 0 or b == 0:
                waypoint = (x1 + a, y1 + b)
                path = coord[: i + 1]
                break

            a = abs(a)
            b = abs(b)

            c = math.sqrt(a**2 + b**2)

            C = math.pi / 2

            B = math.acos((a**2 + c**2 - b**2) / (2 * a * c))
            A = math.pi - B - C

            X = A
            Y = B
            Z = C

            z = dis - (tot_dis - tgt_dis)

            x = z * math.sin(X) / math.sin(Z)
            y = z * math.sin(Y) / math.sin(Z)

            x_fac = (x2 - x1) / abs(x2 - x1) if abs(x2 - x1) > 0 else 1
            y_fac = (y2 - y1) / abs(y2 - y1) if abs(y2 - y1) > 0 else 1

            waypoint = (x1 + x * x_fac, y1 + y * y_fac)
            path = coord[: i + 1]
            break

    path.append(waypoint)
    line_segment = LineSegment(waypoint=waypoint, path=path)

    return line_segment
