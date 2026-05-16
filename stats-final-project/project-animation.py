import sys
from pathlib import Path

# Scenes in subfolders are not on sys.path; add repo root for local imports.
for _parent in Path(__file__).resolve().parents:
    if (_parent / "mobjects").is_dir():
        sys.path.insert(0, str(_parent))
        break

from manimlib import *
from mobjects import Table
import csv


class MainScene(Scene):
    def construct(self) -> None:

    #region TITLE SLIDE
        datatable = []
        with open(r"stats-final-project\iPhone vs Android Bias Survey.csv", mode='r') as file:
            reader = csv.reader(file)
            for row in reader:
                datatable.append(row)
            

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

        tofade = [apple_logo, android_logo, vs_text, title_text, author_text]
        fadegroup = VGroup()
        for item in tofade:
            fadegroup.add(item)

        self.play(FadeOut(fadegroup))
    #endregion


    #region RESEARCH QUESTION
        q_text_group = VGroup()

        q_text_1 = Text("I've always been interested in this. I've heard\nthat people are really attatched to\ntheir iPhones, but that usually comes from social media.")
        q_text_2 = Text("I wanted to look at how it might show up in the real world.")
        q_text_group.add(q_text_1, q_text_2)
        q_text_group.scale(0.75)
        q_text_1.shift(LEFT * 0.33)
        q_text_2.shift(DOWN)
        q_text_group.align_on_border(LEFT)


        self.play(ShowCreation(q_text_1))
        self.play(ShowCreation(q_text_2))

        self.play(FadeOut(q_text_group))

        """
        knowing that I wanted to look at this, I found a survay talking about this bias in adults,
        and I asked the same questions to the NWS. Now, I'll be able to compare our answers to see if there
        is a significant difference
        """

        ex_text_group = VGroup()
        ex_text_1 = Text("Knowing that I wanted to look at this bias, I found a survay talking about it in adults,")
        ex_text_2 = Text("and asked the same questions to the NWS population. Now, I'll be able to compare the results from NWS")
        ex_text_3 = Text("and see if we have a significant difference from the survay.")
        ex_text_group.add(ex_text_2, ex_text_1, ex_text_3)

        self.play(ShowCreation(ex_text_1))
        self.play(ShowCreation(ex_text_2))
        self.play(ShowCreation(ex_text_3))

        self.play(FadeOut(ex_text_group))

        claim_table = Table(
            [
                ["Claim", "Survay %"],
                ["Android users have been excluded from group chats", "24%"],
                ["Android users have been made fun of for their phone type", "52%"],
                ["iPhone users think less of Android users because of their phone", "22%"],
                ["Android users consider switching to iPhone because of peer presure", "30%"],
                ["iPhone users will switch to another messaging app to accomidate Andriod users", "42%"]
            ],
            header_row=True,
            full_width=True,
            column_width_ratios=(4, 1),
        )

        claim_table.scale(0.5)
        claim_table.align_on_border(LEFT)
        self.play(ShowCreation(claim_table))
    #endregion


    #region HYPOTHESIS
        """
        Because there are 5 claims, I actually have 5 seperate hypothesis tests to run
        """
        test_text_group = VGroup()
        test_text_1 = Text("Because there are 5 different claims, I actaully\nhave 5 seperate hypothesis tests to run.")
        test_text_2 = Text("Because of what I hear around school, all hypothosis\nwill be that there is more bias at NWS than in the survay.")
        test_text_3 = Text("Hypothosis (it's the same for all claims):")
        test_text_4 = Tex(r"H_{0}:\widehat{p}_{1}-\widehat{p}_{2}=0")
        test_text_5 = Tex(r"H_{A}:\widehat{p}_{1}-\widehat{p}_{2}>0")
        test_text_6 = Tex(r"\text{Where }\widehat{p}_{1} \text{ is the proportion from NWS and }\widehat{p}_{2}\text{ is the proportion from the survay.}")
        test_text_group.add(test_text_1, test_text_2, test_text_3, test_text_4, test_text_5, test_text_6)
        test_text_group.scale(0.5)
        test_text_group.align_to(claim_table,RIGHT)

        self.play(ShowCreation(test_text_group))



    #endregion


    #region DATA

    #endregion


    #region DISPLAY

    #endregion


    #region 95 CONFIDENCE

    #endregion


    #region T-TEST

    #endregion

        self.embed()

        

        

        return super().construct()
