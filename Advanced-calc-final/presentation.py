from manimlib import *

class main(ThreeDScene):
    def construct(self) -> None:
        #Types of integration
            #IBP
            #Partial Fractions
            #Improper Integrals
        #Average Value
        self.camera.frame.set_euler_angles(0,0,0)
        
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
        self.play(Write(text))

        RoS_example = VGroup3D()

        graph = ThreeDAxes()

        circle = Circle()
        circle.shift(UR * 2)

        

        self.play(ShowCreation(graph))
        self.play(ShowCreation(circle))
        

            #Volumes of known cross sections
        return super().construct()