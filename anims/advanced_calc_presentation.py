from manimlib import *

from manim_slides import Slide 

from matplotlib.pyplot import draw

class MainScene(Slide):
    def construct(self) -> None:

        #Show title
        section_title = Text("Integration in three dimentions")
        self.play(Write(section_title, 1))
        self.next_slide()

        self.play(self.)
        axis = Axes()
        self.play(ShowCreation(axis))


        return super().construct()