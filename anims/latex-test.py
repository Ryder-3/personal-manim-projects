from manimlib import *

class TestLatex(Scene):
    def construct(self):
        tex = Tex(r"\pi")
        self.add(tex)
        self.wait(1)