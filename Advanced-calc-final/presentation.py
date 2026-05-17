import numpy as np
from manimlib import *


class main(ThreeDScene):
    def construct(self) -> None:
        frame = self.camera.frame
        frame.set_euler_angles(0,0,0)

        #Types of integration
        
            #IBP
            #Partial Fractions
            #Improper Integrals
        #Average Value
        
        
        #region Integration in 3d

            #region intro

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
            #endregion

            #region Volumes of revolution
        
        SoR_definition = Text("A Solid of Revolution is formed by taking a 2d shape, and revolving \n it about an axis")
        SoR_definition.scale(0.45)
        self.play(Write(SoR_definition))
        #New slide
        self.wait()
        self.play(FadeOut(SoR_definition))

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
        y_eq_x_label = Tex(r"y=x\text{. From }0\le x\le 6", fill_color=YELLOW)
        y_eq_x_label.shift(LEFT*3)

        self.play(ShowCreation(graph))
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

        # Face down the axis of revolution so cylinder slices look solid, not hollow
        self.play(
            frame.animate.set_euler_angles(0, 0, 0),
            run_time=2,
        )
        self.wait()

        def frame_text(mob, buff=0.35, scale=0.45):
            mob.fix_in_frame()
            mob.scale(scale)
            mob.to_edge(UP, buff=buff)
            return mob

        def frame_tex(tex_string, buff=0.35, font_size=48):
            mob = Tex(tex_string, fill_color=WHITE, font_size=font_size)
            return frame_text(mob, buff=buff, scale=0.55)

        text_1 = frame_text(
            Text("To find the volume of this, we do something very similar to integration")
        )
        text_2 = frame_text(
            Text("We slice the solid into a bunch of cylinders."),
            buff=0.75,
        )

        self.play(Write(text_1))
        self.wait()
        self.play(Write(text_2))

        # Show the solid being split into many cylinders
        x_unit = np.linalg.norm(graph.c2p(1, 0, 0) - graph.c2p(0, 0, 0))

        def make_cylinders(n_slices, opacity=0.55, color=TEAL):
            slice_width = (x_b - x_a) / n_slices
            group = Group()
            for i in range(n_slices):
                x_mid = x_a + (i + 0.5) * slice_width
                radius = x_mid  # f(x) = x for y = x
                cyl = Cylinder(
                    height=slice_width * x_unit * 0.95,
                    radius=radius * x_unit,
                    axis=RIGHT,
                    color=color,
                    opacity=opacity,
                    depth_test=True,
                    resolution=(28, 10),
                )
                cyl.move_to(graph.c2p(x_mid, 0, 0))
                group.add(cyl)
            return group, slice_width

        coarse_slices = 10
        cylinders, coarse_width = make_cylinders(coarse_slices)

        self.play(
            FadeOut(revolving_shell),
            FadeOut(cone_mesh),
            LaggedStartMap(FadeIn, cylinders, lag_ratio=0.08),
            run_time=3,
        )
        self.wait()

        text_3 = frame_tex(r"\text{Volume} = w \cdot \pi r^{2}", buff=1.15)
        text_width_explain = frame_text(
            Text(
                "As we use more slices, the width of each cylinder approaches 0, and our approximation of the solid gets better. ",
                alignment="LEFT",
            ),
            buff=1.65,
        )
        text_4 = frame_tex(r"w \to 0", buff=2.15)
        text_5 = frame_tex(r"\text{Volume} = \pi r^{2}", buff=1.15)
        text_6 = frame_tex(r"r = f(x)", buff=2.15)
        text_7 = frame_tex(r"\text{Volume} = \pi f(x)^{2}", buff=2.65)

        self.play(FadeOut(text_1), Write(text_3))
        self.wait()
        self.play(Write(text_width_explain))

        # Thin every cylinder so the visuals match w -> 0
        fine_slices = 48
        thin_cylinders, fine_width = make_cylinders(fine_slices, opacity=0.65)
        self.play(
            FadeOut(cylinders),
            LaggedStartMap(FadeIn, thin_cylinders, lag_ratio=0.02),
            run_time=2.5,
        )
        self.play(Write(text_4))
        self.wait()


        # Transform text_3 into text_5
        self.play(
            FadeOut(text_4),
            TransformMatchingTex(text_3, text_5),
        )

        self.wait()
        self.play(Write(text_6))
        self.wait()
        self.play(Write(text_7))
        self.wait()
        self.play(
            FadeOut(text_2),
            FadeOut(text_5),
            FadeOut(text_width_explain),
            FadeOut(text_6),
            FadeOut(text_7),
        )

        text_8 = frame_text(
            Text("We then sum the volume of all the cylinders", alignment="LEFT"),
            buff=0.75,
        )
        text_9 = frame_tex(
            r"\text{Volume of the solid}=\int_{\text{lower bound}}^{\text{upper bound}}\pi f(x)^{2}\,dx",
            buff=1.15,
        )
        text_10 = frame_tex(
            r"\text{So, our final formula is }\int_{0}^{6}\pi x^{2}\,dx",
            buff=1.15,
        )
        text_11 = frame_tex(r"\pi\int_{0}^{6}x^{2}\,dx", buff=1.15)
        text_12 = frame_tex(r"\pi\left[\frac{1}{3} x^{3}\right]_{0}^{6}", buff=1.15)
        text_13 = frame_tex(
            r"\pi\left[\frac{1}{3} \cdot 6^{3}-\frac{1}{3} \cdot 0^{3}\right]",
            buff=1.15,
        )
        text_14 = frame_tex(r"\pi\left[\frac{1}{3} \cdot 6^{3}\right]", buff=1.15)
        text_15 = frame_tex(r"\pi\left[\frac{216}{3}\right]", buff=1.15)
        text_16 = frame_tex(r"72\pi", buff=1.15)
        

        self.play(Write(text_8))
        self.wait()
        self.play(Write(text_9))
        self.wait()
        self.play(FadeOut(text_9), Write(text_10))
        self.wait()
        self.play(TransformMatchingTex(text_10, text_11))
        self.wait()
        self.play(TransformMatchingTex(text_11, text_12))
        self.wait()
        self.play(TransformMatchingTex(text_12, text_13))
        self.wait()
        self.play(TransformMatchingTex(text_13, text_14))
        self.wait()
        self.play(TransformMatchingTex(text_14, text_15))
        self.wait()
        self.play(TransformMatchingTex(text_15, text_16))
        self.wait()

        answer_box = SurroundingRectangle(text_16, buff=0.2, color=YELLOW)
        self.play(ShowCreation(answer_box))
        self.wait()

        self.play(
            FadeOut(text_8),
            FadeOut(text_16),
            FadeOut(answer_box),
            FadeOut(graph),
            FadeOut(y_eq_x),
            FadeOut(y_eq_x_label),
            FadeOut(thin_cylinders),
        )
        #endregion

            #region Volumes of known cross sections
        frame.to_default_state()
        frame.set_euler_angles(0, 0, 0)

        cross_intro = VGroup()
        cross_text_1 = Text(
            "The next thing we are going to look at is finding the volume of any solid with a known cross-section",
        )
        cross_text_1.scale(0.45)
        cross_text_1.shift(UP * 0.5)
        cross_intro.add(cross_text_1)
        self.play(Write(cross_text_1))
        self.wait()

        cross_text_2 = Text(
            "A solid with a known cross-section is a solid whose base is defined by a function,\n"
            "and whose cross section is a known, unchanging, shape.",
            alignment="LEFT",
        )
        cross_text_2.scale(0.4)
        cross_text_2.shift(DOWN * 0.5)
        cross_intro.add(cross_text_2)
        self.play(Write(cross_text_2))
        self.wait()
        self.play(FadeOut(cross_intro))

        # Shorter y/z unit size keeps the tall solid visible without dominating x
        cross_yz_unit = 0.22
        cross_graph = ThreeDAxes(
            x_range=(-0.5, 5, 1),
            y_range=(0, 17, 4),
            z_range=(0, 17, 4),
            width=5.5,
            height=3.75,
            depth=3.75,
            y_axis_config=dict(unit_size=cross_yz_unit),
            z_axis_config=dict(unit_size=cross_yz_unit),
        )
        cross_graph.add_coordinate_labels()
        cross_a, cross_b = 0.0, 4.0

        base_curve = ParametricCurve(
            lambda t: cross_graph.c2p(t, t ** 2, 0),
            t_range=(cross_a, cross_b, 0.05),
            color=YELLOW,
        )
        top_curve = ParametricCurve(
            lambda t: cross_graph.c2p(t, t ** 2, t ** 2),
            t_range=(cross_a, cross_b, 0.05),
            color=GOLD,
        )

        def square_cross_section(x_val, color=TEAL, opacity=0.55):
            side = x_val ** 2
            return Polygon(
                cross_graph.c2p(x_val, 0, 0),
                cross_graph.c2p(x_val, side, 0),
                cross_graph.c2p(x_val, side, side),
                cross_graph.c2p(x_val, 0, side),
                color=color,
                fill_opacity=opacity,
                stroke_width=1,
                stroke_color=WHITE,
            )

        def cross_surface(u, v, y_fn, z_fn):
            return cross_graph.c2p(u, y_fn(u, v), z_fn(u, v))

        # Solid with square cross sections: 0 <= y,z <= x^2 for each x in [0, 4]
        cross_solid = Group(
            ParametricSurface(
                lambda u, v: cross_surface(u, v, lambda u, v: 0, lambda u, v: u ** 2 * v),
                u_range=(cross_a, cross_b),
                v_range=(0, 1),
                color=BLUE_E,
                opacity=0.82,
                resolution=(36, 18),
            ),
            ParametricSurface(
                lambda u, v: cross_surface(u, v, lambda u, v: u ** 2 * v, lambda u, v: 0),
                u_range=(cross_a, cross_b),
                v_range=(0, 1),
                color=BLUE_D,
                opacity=0.82,
                resolution=(36, 18),
            ),
            ParametricSurface(
                lambda u, v: cross_surface(u, v, lambda u, v: u ** 2, lambda u, v: u ** 2 * v),
                u_range=(cross_a, cross_b),
                v_range=(0, 1),
                color=BLUE_E,
                opacity=0.78,
                resolution=(36, 18),
            ),
            ParametricSurface(
                lambda u, v: cross_surface(u, v, lambda u, v: u ** 2 * v, lambda u, v: u ** 2),
                u_range=(cross_a, cross_b),
                v_range=(0, 1),
                color=BLUE_D,
                opacity=0.78,
                resolution=(36, 18),
            ),
            square_cross_section(cross_b, color=BLUE_E, opacity=0.82),
        )

        n_cross_slices = 16
        cross_slices = Group()
        for i in range(n_cross_slices):
            x_mid = cross_a + (i + 0.5) * (cross_b - cross_a) / n_cross_slices
            cross_slices.add(square_cross_section(x_mid))

        cross_text_3 = frame_tex(
            r"\text{In this example, }f(x)=x^{2}\text{ on }0\le x\le 4"
            r"\text{ and each cross section is a square.}",
            buff=1.15,
        )
        cross_label = Tex(r"f(x)=x^{2}", fill_color=YELLOW)
        cross_label.shift(LEFT * 3 + UP * 0.5)
        cross_label.fix_in_frame()

        self.play(ShowCreation(cross_graph))
        self.play(
            ShowCreation(base_curve),
            ShowCreation(top_curve),
            FadeIn(cross_label),
            Write(cross_text_3),
        )
        self.wait()
        self.play(FadeIn(cross_solid), run_time=2)
        self.wait()

        self.play(
            frame.animate.set_euler_angles(
                theta=0.55,
                phi=0.65,
                gamma=0.25,
            ),
            run_time=2,
        )
        self.wait()

        cross_text_4 = frame_text(
            Text(
                "To find the volume of this solid, we essentially do the same thing we did with the solid of revolution.",
                alignment="LEFT",
            ),
            buff=0.75,
        )
        cross_text_5 = frame_text(
            Text(
                "The only difference is that instead of slicing into cylinders, we slice into whatever shape the cross section is.",
                alignment="LEFT",
            ),
            buff=1.35,
        )
        cross_text_6 = frame_text(
            Text(
                "In our case, the cross section is a square, so we slice the solid into squares.",
                alignment="LEFT",
            ),
            buff=1.95,
        )
        cross_text_7 = frame_tex(
            r"\text{We know that the area of a square is }s^{2}"
            r"\text{ where }s\text{ is the side length.}",
            buff=1.15,
        )
        cross_text_8 = frame_tex(r"s = f(x)", buff=1.65)
        cross_text_9 = frame_tex(
            r"\text{So, the area of the cross section is }f(x)^{2}",
            buff=2.15,
        )
        cross_text_10 = frame_text(
            Text(
                "We then sum the area of all the cross sections on our interval to get the volume.",
                alignment="LEFT",
            ),
            buff=0.75,
        )
        cross_text_11 = frame_tex(
            r"\text{So, our final formula is }\int_{0}^{4}f(x)^{2}\,dx",
            buff=1.15,
        )
        cross_text_13 = frame_tex(
            r"\text{So, our final formula is }\int_{0}^{4}(x^{2})^{2}\,dx",
            buff=1.15,
        )
        cross_text_14 = frame_tex(r"\int_{0}^{4}x^{4}\,dx", buff=1.15)
        cross_text_15 = frame_tex(r"\frac{1}{5}x^{5}\big|_{0}^{4}", buff=1.15)
        cross_text_16 = frame_tex(
            r"\frac{1}{5} \cdot 4^{5}-\frac{1}{5} \cdot 0^{5}",
            buff=1.15,
        )
        cross_text_17 = frame_tex(r"\frac{1}{5} \cdot 4^{5}", buff=1.15)
        cross_text_18 = frame_tex(r"\frac{1024}{5}", buff=1.15)
        
        self.play(FadeOut(cross_text_3))
        self.play(Write(cross_text_4))
        self.wait()
        self.play(Write(cross_text_5))
        self.wait()
        self.play(Write(cross_text_6))
        self.wait()

        self.play(
            FadeOut(cross_solid),
            LaggedStartMap(FadeIn, cross_slices, lag_ratio=0.06),
            run_time=3,
        )
        self.play(
            frame.animate.set_euler_angles(0, 0, 0),
            run_time=2,
        )
        self.wait()

        self.play(
            FadeOut(cross_text_4),
            FadeOut(cross_text_5),
            FadeOut(cross_text_6),
        )
        self.play(Write(cross_text_7))
        self.wait()
        self.play(Write(cross_text_8))
        self.wait()
        self.play(Write(cross_text_9))
        self.wait()

        self.play(
            FadeOut(cross_text_7),
            FadeOut(cross_text_8),
            FadeOut(cross_text_9),
        )
        self.play(Write(cross_text_10))
        self.wait()
        self.play(Write(cross_text_11))
        self.wait()

        cross_label_box = SurroundingRectangle(cross_label, buff=0.15, color=YELLOW)
        self.play(ShowCreation(cross_label_box))
        self.wait()
        self.play(FadeOut(cross_label_box))
        self.play(TransformMatchingTex(cross_text_11, cross_text_13))
        self.wait()
        self.play(TransformMatchingTex(cross_text_13, cross_text_14))
        self.wait()
        self.play(TransformMatchingTex(cross_text_14, cross_text_15))
        self.wait()
        self.play(TransformMatchingTex(cross_text_15, cross_text_16))
        self.wait()
        self.play(TransformMatchingTex(cross_text_16, cross_text_17))
        self.wait()
        self.play(TransformMatchingTex(cross_text_17, cross_text_18))
        self.wait()

        cross_answer_box = SurroundingRectangle(cross_text_18, buff=0.2, color=YELLOW)
        self.play(ShowCreation(cross_answer_box))
        self.wait()

        self.play(
            FadeOut(cross_text_10),
            FadeOut(cross_text_18),
            FadeOut(cross_answer_box),
            FadeOut(cross_label),
            FadeOut(cross_graph),
            FadeOut(base_curve),
            FadeOut(top_curve),
            FadeOut(cross_slices),
        )
        self.wait()

            #endregion

        #endregion