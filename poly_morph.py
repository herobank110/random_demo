from factorygame import GameplayUtilities, GameplayStatics, GameEngine, Loc, MathStat, FColor
from factorygame.core.blueprint import PolygonNode, GeomHelper, GridGismo, WorldGraph
from factorygame.core.input_base import EKeys, EInputEvent
from random import randrange
from tkinter import Label


class PolyMorph(PolygonNode):
    def __init__(self):
        super().__init__()
        self._morph_target = None
        self.target_color = self.fill_color
        self.morph_speed = 0.004
        # Number of vertices in solver.
        self.solver_n = 40

    def __set_target(self, reg_poly_verts):
        is_initial = self._morph_target is None
        self._morph_target = tuple(
            self.solver_nth_point_on_reg_poly(i, reg_poly_verts)
            for i in range(1, self.solver_n + 1))
        if is_initial:
            self.vertices = self._morph_target

    target_vertices = property(None, __set_target)

    def tick(self, dt):
        bias = dt * self.morph_speed
        self.vertices = tuple(
            MathStat.lerp(a, b, bias)
            for a, b in zip(self.vertices, self._morph_target))
        self.fill_color = MathStat.lerp(
            self.fill_color, self.target_color, bias)
        super().tick(dt)

    @staticmethod
    def get_edge_lengths(verts):
        return tuple(
            MathStat.getdist(coords, verts[i + 1 if i + 1 < len(verts) else 0])
            for i, coords in enumerate(verts))

    @staticmethod
    def perimeter_lerp(verts, bias):
        bias = MathStat.clamp(bias)
        edge_lengths = tuple(PolyMorph.get_edge_lengths(verts))
        perimeter = sum(edge_lengths)
        desired_point = perimeter * bias

        current_sum = 0
        for i, length in enumerate(edge_lengths):
            current_sum += length
            if current_sum >= desired_point:
                vert_hi = verts[i]
                vert_lo = verts[i - 1 if i > 0 else -1]
                return MathStat.map_range(
                    desired_point,
                    current_sum - length, current_sum,
                    vert_lo, vert_hi)

    def solver_nth_point_on_reg_poly(self, n, verts):
        corner_needed = self.solver_n / len(verts)
        corner_count = 0
        for i in range(n):
            # add a corner if needed
            if i >= corner_needed * corner_count:
                ended_on_corner = True
                corner_count += 1
            else:
                ended_on_corner = False

        bias = ((corner_count - 1) / len(verts) if ended_on_corner else
                (n - 1) / self.solver_n)
        return PolyMorph.perimeter_lerp(verts, bias)


class MyMorpher(PolyMorph):
    def begin_play(self):
        super().begin_play()
        self.radius = 100
        self.target_color = FColor.cyan()
        self.target_vertices = tuple(
            GeomHelper.generate_reg_poly(3, radius=100))
        GameplayStatics.game_engine.input_mappings.bind_action(
            "Grow", EInputEvent.PRESSED, self.on_grow)
        GameplayStatics.game_engine.input_mappings.bind_action(
            "Shrink", EInputEvent.RELEASED, self.on_shrink)

    def on_grow(self):
        self.radius += 30
        self.randomise()
    def on_shrink(self):
        self.radius = max(1, self.radius - 30)
        self.randomise()

    def on_click(self, event):
        self.randomise()

    def randomise(self):
        self.target_vertices = tuple(GeomHelper.generate_reg_poly(
            randrange(3, 9), radius=self.radius))
        self.target_color = FColor(*map(randrange, (255,)*3))


class MorphWorld(WorldGraph):
    def __init__(self):
        super().__init__()
        self.label = Label(self, font=("Arial", 14))
        self.label.place(relx=0.05, rely=0.95, anchor="sw")

    def begin_play(self):
        super().begin_play()
        self.spawn_actor(GridGismo, Loc(0, 0))
        self.spawn_actor(MyMorpher, Loc(0, 0))
        self.label.config(text="Click to transform\nW to grow\nE to shrink")


class MorphGameEngine(GameEngine):
    def __init__(self):
        super().__init__()
        self._starting_world = MorphWorld
        self._window_title = "Poly Morph"
        self._frame_rate = 90

    def setup_input_mappings(self):
        self.input_mappings.add_action_mapping("Grow", EKeys.W)
        self.input_mappings.add_action_mapping("Shrink", EKeys.E)


GameplayUtilities.create_game_engine(MorphGameEngine)
