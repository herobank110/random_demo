"""Forward And Backwards Reaching Inverse Kinematics (FABRIK) solver.
Author: David Kanekanian
"""

from factorygame import GameEngine, GameplayUtilities, Loc, MathStat
from factorygame.core.blueprint import FColor, GeomHelper, WorldGraph, PolygonNode, GridGismo, GeomHelper
from tkinter import Button


def get_edge_lengths_open(verts):
    """Get edge lengths between vertices in a poly line.
    """
    return tuple(
        MathStat.getdist(verts[i], verts[i - 1])
        for i in range(1, len(verts)))


def get_mouse_viewport_position(context):
    """Not in latest official factorygame release."""
    return Loc(
        context.winfo_pointerx() - context.winfo_rootx(),
        context.winfo_pointery() - context.winfo_rooty()
    )


def get_mouse_world_position(world_graph):
    return world_graph.canvas_to_view(
        get_mouse_viewport_position(world_graph))


class FabrikSolver:

    class _SolveData:
        def __init__(self, solver):
            # in terms of coordinates
            self.verts = tuple(map(lambda p: p.location, solver.points))
            self.lengths = get_edge_lengths_open(self.verts)
            # Copy the first point into the start.
            self.start = Loc(solver.points[0].location)
            self.goal = solver.end_effector.location

    def __init__(self):
        # in terms of actors (with locations)
        self.points = []
        self.tolerance = 0.1
        self.max_iterations = 10
        self.end_effector = None
        self._last_verts = None

    def solve(self):
        if len(self.points) < 2 or self.end_effector is None:
            return

        data = self._SolveData(self)

        if abs(data.goal - data.start) > sum(data.lengths):
            # The effector is beyond joint capability.
            FabrikSolver._straighten_towards(data, data.goal)
        else:
            # The effector is within reach.
            if self._last_verts is None:
                # Cannot solve if last verts not valid.
                # Prepare last verts for the next iteration.
                self._last_verts = data.verts
                return
            FabrikSolver._do_solve(data, data.goal)

        # Save the new locations to the actors.
        FabrikSolver._apply_to_actors(data.verts, self.points)

        # Save for the next solve.
        self._last_verts = data.verts

    @staticmethod
    def _apply_to_actors(verts, actors):
        for vert, actor in zip(verts, actors):
            actor.location = vert

    @staticmethod
    def _straighten_towards(data, goal):
        direction = goal - data.start
        direction /= abs(direction)

        verts = list(data.verts)
        for i, length_to_previous in zip(range(1, len(verts)), data.lengths):
            verts[i] = verts[i - 1] + direction * length_to_previous
        data.verts = tuple(verts)

    @staticmethod
    def _do_solve(data: _SolveData, goal, **kw):
        """
        Available keywords:
        iterations: maximum number of forward and backward iterations
        tolerance: maximum distance from goal to stop iterations
        """
        tolerance = kw.get("tolerance", 0.01)
        iterations = kw.get("iterations", 10)

        # Start at the end.
        verts = list(data.verts)

        for _ in range(iterations):
            # Put the end vertex at the goal
            verts[-1] = goal

            # Iterate backwards to solve in place.
            for i in range(len(verts) - 1, 0, -1):
                direction = verts[i - 1] - verts[i]
                direction /= abs(direction)
                verts[i - 1] = verts[i] + direction * data.lengths[i - 1]

            # Put the first point at the original start.
            verts[0] = data.start

            # Iterate backwards to solve in place.
            for i in range(len(verts) - 1):
                direction = verts[i + 1] - verts[i]
                direction /= abs(direction)
                verts[i + 1] = verts[i] + direction * data.lengths[i]

            if abs(verts[-1] - data.goal) <= tolerance:
                # Stop early if within tolerance.
                break

        # Save back as a tuple.
        data.verts = tuple(verts)


class DraggablePoint(PolygonNode):
    """Point in the joint chain

    Can be dragged around the graph.
    """

    def __init__(self):
        super().__init__()
        self.is_dragged = False
        self.is_hovered = False
        # Which order this point is in the chain.
        self.point_index = 0
        self.normal_color = FColor.from_hex("#cc9999")
        self.hover_color = FColor.from_hex("#d4777e")
        self.held_color = FColor.from_hex("#d4777e")

    def begin_play(self):
        super().begin_play()
        self.vertices = tuple(GeomHelper.generate_reg_poly(
            3 + self.point_index, radius=100))
        self.fill_color = self.normal_color

    def on_begin_cursor_over(self, event):
        self.is_hovered = True
        self.fill_color = self.hover_color

    def on_end_cursor_over(self, event):
        self.is_hovered = False
        self.fill_color = self.normal_color

    def on_click(self, event):
        self.is_dragged = not self.is_dragged
        if self.is_dragged:
            self.fill_color = self.held_color
            self.vertices = tuple(GeomHelper.generate_reg_poly(
                3 + self.point_index, radius=75))
        else:
            self.fill_color = self.hover_color if self.is_hovered else self.normal_color
            self.vertices = tuple(GeomHelper.generate_reg_poly(
                3 + self.point_index, radius=100))

            # IK needs to be resolved when a point has finished moving.
            self.world.fabrik_solver.solve()

    def tick(self, delta_time):
        if self.is_dragged:
            self.location = get_mouse_world_position(self.world)
        # This is optional in the latest factorygame.
        self.vertices = tuple(GeomHelper.generate_reg_poly(
            3 + self.point_index, radius=75))
        super().tick(delta_time)


class EndEffector(DraggablePoint):
    def __init__(self):
        super().__init__()
        self.point_index = 20
        self.normal_color = FColor(128)
        self.hover_color = FColor(110)
        self.held_color = FColor(100)

    def tick(self, delta_time):
        if self.is_dragged:
            self.world.fabrik_solver.solve()
        super().tick(delta_time)


class FabrikWorld(WorldGraph):
    def begin_play(self):
        super().begin_play()
        self.zoom_ratio = 9
        self.spawn_actor(GridGismo, Loc(0, 0))
        self.fabrik_solver = FabrikSolver()
        self.fabrik_solver.end_effector = self.spawn_actor(
            EndEffector, Loc(0, 0))
        Button(self, text="Add Point", command=self.add_point
               ).place(relx=0.05, rely=0.05, anchor="nw")

    def add_point(self):
        center = self.canvas_to_view(self.get_canvas_dim() / 2)
        new_point = self.deferred_spawn_actor(DraggablePoint, center)
        new_point.point_index = len(self.fabrik_solver.points)
        self.fabrik_solver.points.append(new_point)
        self.finish_deferred_spawn_actor(new_point)


class FabrikEngine(GameEngine):
    def __init__(self):
        super().__init__()
        self._frame_rate = 90
        self._window_title = "FABRIK IK Solver"
        self._starting_world = FabrikWorld


GameplayUtilities.create_game_engine(FabrikEngine)
