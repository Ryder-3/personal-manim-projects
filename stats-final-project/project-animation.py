from manimlib import *
from manim_slides import Slide
import csv


class MainScene(Slide):
    def construct(self) -> None:
        with open(r"stats-final-project\iPhone vs Android Bias Survey.csv", mode='r') as file:
            reader = csv.reader(file)

        #create apple logo
        apple_logo = SVGMobject(r"assets\svg\Apple_logo_black.svg")
        logos = VGroup()
        
        logos.add(apple_logo)

        #create android logo
        android_logo = SVGMobject(r"assets\svg\android-icon.svg")

        vs_text = Text('vs.')
        vs_text.scale(2)
        logos.add(vs_text)
        
        logos.add(android_logo)
        android_logo.shift(RIGHT * 3)
        apple_logo.shift(LEFT * 3)
        logos.shift(UP * 2)
        self.play(ShowCreation(logos))
        self.wait(1)

        title_text = Text("Bias against Android users in NWS")
        self.play(ShowCreation(title_text))

        author_text = Text(r"-By: Cameron Engrav")
        author_text.shift(DOWN)
        author_text.shift(RIGHT *1.8)
        self.play(ShowCreation(author_text))

        self.embed()

        

        

        return super().construct()
