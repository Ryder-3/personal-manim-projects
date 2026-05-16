import numpy as np

from manimlib import *


class main(ThreeDScene):
    def construct(self) -> None:
        frame = self.camera.frame

        #Types of integration
            #IBP
            #Partial Fractions
            #Improper Integrals
        #Average Value
        frame.set_euler_angles(0,0,0)
        
        #Integration in 3d
        part_3_introduction = VGroup()
        part_3_title = Text("Integration in Three Dimentions")
        part_3_title.shift(UP * 2)
        part_3_title.scale(1.25)
        part_3_introduction.add(part_3_title)
        self.play(Write(part_3_title))
        #new slide
        part_3_blurb_1 = Text("Up until now, we've learned how to find the area under a 2D curve")
        part_3_blurb_1.shift(UP)
        part_3_blurb_1.scale(0.5)
        self.play(Write(part_3_blurb_1))
        part_3_introduction.add(part_3_blurb_1)
        #new slide
        part_3_blurb_2 = Text("Now, we are going to learn how to find the volume of a 3d solid")
        part_3_blurb_2.scale(0.5)
        self.play(Write(part_3_blurb_2))
        part_3_introduction.add(part_3_blurb_2)
        #new slide
        part_3_blurb_3 = Text("To start, we are going to learn how to find the volume of a 'Solid of Revolution'")
        part_3_blurb_3.scale(0.5)
        part_3_blurb_3.shift(DOWN)
        self.play(Write(part_3_blurb_3))
        part_3_introduction.add(part_3_blurb_3)
        #new slide
        self.play(FadeOut(part_3_introduction))

            #Volumes of revolution
        
        SoR_definition = Text("A Solid of Revolution is formed by taking a 2d shape, and revolving \n it about an axis")
        self.play(Write(SoR_definition))
        #New slide
        self.remove(SoR_definition)

        text = Text("Like this")
        text.shift(UP * 3)
        text.fix_in_frame()
        self.play(Write(text))

        self.play(
            self.frame.animate.scale(1.85),
            run_time=1.25,
        )

        graph = ThreeDAxes(
            x_range=(-1, 10, 1),
            y_range=(-1, 10, 1),
            z_range=(-5, 5, 1),
        )
        graph.add_coordinate_labels()

        # Segment of y = x in the xy-plane (ThreeDAxes.get_graph is z = f(u, v), not a plane curve)
        x_a, x_b = 0, 6.0
        y_eq_x = ParametricCurve(
            lambda t: graph.c2p(t, t, 0),
            t_range=(x_a, x_b, 0.05),
            color=YELLOW,
        )
        y_eq_x_label = Tex(r"y=x\text{. From }0\le x\le 6", color = YELLOW)

        self.add(graph)
        self.play(ShowCreation(y_eq_x), FadeIn(y_eq_x_label))
        self.wait()
        self.wait()

        # Surface from revolving y = x about the x-axis: (x, y, z) = (u, u cos v, u sin v) in axis coords
        cone_of_revolution = ParametricSurface(
            lambda u, v: graph.c2p(u, u * np.cos(v), u * np.sin(v)),
            u_range=(x_a, x_b),
            v_range=(0, TAU),
            resolution=(31, 49),
            color=BLUE_E,
            opacity=0.85,
        )
        cone_mesh = SurfaceMesh(cone_of_revolution)

        revolving_shell = cone_of_revolution.copy()
        revolving_shell.pointwise_become_partial(cone_of_revolution, 0, 0, axis=1)

        self.play(
            UpdateFromAlphaFunc(
                revolving_shell,
                lambda m, a: m.pointwise_become_partial(cone_of_revolution, 0, a, axis=1),
            ),
            y_eq_x.animate.set_stroke(opacity=0.25),
            self.frame.animate.set_euler_angles(
                theta=0.46691254,
                phi=0.75668624,
                gamma=0.34906585,
            ),
            run_time=4,
        )
        self.add(cone_mesh)
        self.play(ShowCreation(cone_mesh, lag_ratio=0.01), run_time=2)

        volume_find_text = VGroup()
        text_1 = Text("To find the volume of this, we do something very similar to integration")
        text_2 = Text("We slice the solid into a bunch of cylendars.")
        text_3 = Text("First, we make a cylendar with a width of ")

        self.embed()


            #Volumes of known cross sections