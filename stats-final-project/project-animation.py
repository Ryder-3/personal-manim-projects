import sys
from pathlib import Path

from matplotlib.pyplot import bar

# Scenes in subfolders are not on sys.path; add repo root for local imports.
for _parent in Path(__file__).resolve().parents:
    if (_parent / "mobjects").is_dir():
        sys.path.insert(0, str(_parent))
        break

from manimlib import *
from mobjects import Table
import json


class MainScene(Scene):
    def construct(self) -> None:

    #region TITLE SLIDE
    

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
        test_text_5 = Tex(r"H_{A}:\widehat{p}_{1}-\widehat{p}_{2}\ne 0")
        test_text_6 = Tex(r"\text{Where }\widehat{p}_{1} \text{ is the proportion from NWS and }\widehat{p}_{2}\text{ is the proportion from the survay.}")
        test_text_group.add(test_text_1, test_text_2, test_text_3, test_text_4, test_text_5, test_text_6)
        test_text_group.scale(0.5)
        test_text_group.align_to(claim_table,RIGHT)

        self.play(ShowCreation(test_text_group))
    #endregion

    #region INTRO
        intro_txt_1 = Text("For each of the hypothoses, we are comparing two sample proportions")
        intro_txt_2 = Text("We are doing this because we don't know the truo proportion, all we know is what we found, and what the study found")
        intro_txt_3 = Text("We will be testing to see if there is a significant difference between NWS and the findings of the study")
        intro_txt_4 = Text("To do this, we will create a normal distribution around the diferece of the samples")
        intro_txt_5 = Text("If a differece of 0 falls in our normal dist, then we can't know if there is a significant differece")
        intro_txt_6 = Text("If 0 does not fall in our normal dist, then we know there's a significant difference")
        intro_txt_7 = Text("To start, lets look at our data")
    #endregion

    #region DATA
        json_path = Path(__file__).parent / "survey_by_question.json"
        with open(json_path, encoding="utf-8") as json_file:
            data = json.load(json_file)
        

        # Show Each question, the survay responce, and our responce

        #keep this on the bottom for this entire section
        citation = Text("Source for outside data: https://allaboutcookies.org/apple-vs-android")

        #region q1 (to iphone users), do you think less of people who have Andriods
        data_txt_1 = Text('The first question I asked iPhone users was "Do you judge people when they text you with green bubbles?"')
        q1_data = data["Do you judge people when they text you with green bubles?"]

        #get q1 data
        q1_y = 0
        q1_n = 0
        q1_answers = 0

        for answer in q1_data:
            if answer == "Yes":
                q1_y += 1
                q1_answers += 1
            elif answer == "No":
                q1_n += 1
                q1_answers += 1
            

        #convert answer num into %
        q1_y = (q1_y/q1_answers) * 100
        q1_n = (q1_n/q1_answers) * 100

        q1_y = round(q1_y, 2)
        q1_n = round(q1_n, 2)

        #display        
        q1_nws_bar_chart = BarChart([q1_y, q1_n], bar_names=["Yes", "No"])
        q1_surv_bar_chart = BarChart([22, 78], bar_names=["Yes", "No"])
        #endregion
    
        #region q2 (to iphone users), which of the following have you done because someone you know has an android?
        q2_data = data["Which of the following have you done because someone you know has an Android? (select all that apply)"]
        q2_counts: dict[str, float] = {}
        q2_answers = 0
        for response in q2_data:
            if not response.strip():
                continue
            q2_answers += 1
            for choice in response.split(";"):
                choice = choice.strip()
                if choice:
                    q2_counts[choice] = q2_counts.get(choice, 0) + 1

        for choice in q2_counts:
            q2_counts[choice] = (q2_counts[choice] / q2_answers) * 100
            q2_counts[choice] = round(q2_counts[choice], 2)

        q2_nws_bar_chart = BarChart(
            values=[
                q2_counts["Only used non-texting platforms to communicate"],
                q2_counts["Moved group chats to WhatsApp or similar apps"],
                q2_counts["Texted them less frequently"],
                q2_counts["Excluded them from group chats"],
                q2_counts["Removed them from group chats"],
                q2_counts["Stopped texting them entirely"],
                q2_counts["None of the above"]
            ],
            bar_names=[
                "Only used non-texting platforms to communicate",
                "Moved group chats to WhatsApp or similar apps",
                "Texted them less frequently",
                "Excluded them from group chats",
                "Removed them from group chats",
                "Stopped texting them entirely",
                "None of the above",
            ]
        )

        q2_surv_bar_chart = BarChart(
            values=[
                35,
                30,
                23,
                21,
                17,
                15
            ],
            bar_names=[
                "Only used non-texting platforms to communicate",
                "Moved group chats to WhatsApp or similar apps",
                "Texted them less frequently",
                "Excluded them from group chats",
                "Removed them from group chats",
                "Stopped texting them entirely",
            ]
        )

        #Note that I gave a none of the above, the other survay didn't

        #endregion

        #region q3 (to iphone users), Have you ever switched to a third-party messaging app (WhatsApp, Discord, etc.) to accommodate non-iPhone users?
        q3_data = data["Have you ever switched to a third-party messaging app (WhatsApp, Discord, etc.) to accommodate non-iPhone users?"]
        
        q3_y = 0
        q3_n = 0
        q3_a = 0

        for answer in q3_data:
            if answer == "Yes":
                q3_y += 1
                q3_a += 1
            elif answer == "No":
                q3_n += 1
                q3_a += 1

        #convert to %
        q3_y = (q3_y/q3_a) * 100
        q3_n = (q3_n/q3_a) * 100

        q3_y = round(q3_y, 2)
        q3_n = round(q3_n, 2)

        q3_nws_bar_chart = BarChart([q3_y, q3_n], bar_names=["Yes","No"])
        q3_surv_bar_chart = BarChart([42, 58], bar_names=["Yes","No"])
        #endregion

        #region q4 (to android users) Which of the following have happened to you because you have an Android phone? (select all that apply)
        q4_data = data["Which of the following have happened to you because you have an Android phone? (select all that apply)"]

        q4_counts: dict[str, float] = {}
        q4_answers = 0
        for response in q4_data:
            if not response.strip():
                continue
            q4_answers += 1
            for choice in response.split(";"):
                choice = choice.strip()
                if choice:
                    q4_counts[choice] = q4_counts.get(choice, 0) + 1

        for choice in q4_counts:
            q4_counts[choice] = (q4_counts[choice] / q4_answers) * 100
            q4_counts[choice] = round(q4_counts[choice], 2)

        q4_nws_bar_chart = BarChart(
            values = [
                q4_counts['Made fun of by iPhone users'],
                q4_counts["Missed or misunderstood messages (due to compatibility issues)"],
                q4_counts["Felt negatively judged"],
                q4_counts["Asked a group to use an alternative messaging app"],
                q4_counts["Felt embarrassed"],
                q4_counts["Been excluded from a group chat"],
                q4_counts["None of the above"],
            ],
            bar_names = [
                "Made fun of by iPhone users",
                "Missed or misunderstood messages (due to compatibility issues)",
                "Felt negatively judged",
                "Asked a group to use an alternative messaging app",
                "Felt embarrassed",
                "Been excluded from a group chat",
                "None of the above",
            ]
        )

        q4_surv_bar_chart = BarChart(
            values = [
                52,
                38,
                36,
                33,
                26,
                24,
            ],
            bar_names = [
                "Made fun of by iPhone users",
                "Missed or misunderstood messages (due to compatibility issues)",
                "Felt negatively judged",
                "Asked a group to use an alternative messaging app",
                "Felt embarrassed",
                "Been excluded from a group chat",
                "None of the above",
            ]
        )
        #Note that I gave a none of the above, the other survay didn't  


        #endregion

        #region q5 (to android users), Have you ever considered switching to iPhone due to peer pressure
        q5_data = data["Have you ever considered switching to iPhone due to peer pressure?"]

        q5_y = 0
        q5_n = 0
        q5_a = 0

        for answer in q5_data:
            if answer == "Yes":
                q5_y += 1
                q5_a += 1
            elif answer == "No":
                q5_n += 1
                q5_a += 1
        
        #convert to %
        q5_y = (q5_y/q5_a) * 100
        q5_n = (q5_n/q5_a) * 100

        q5_y = round(q5_y, 2)
        q5_n = round(q5_n, 2)

        q5_nws_bar_chart = BarChart([q5_y, q5_n], bar_names=["Yes", "No"])
        q5_surv_bar_chart = BarChart([30, 70], bar_names=["Yes","No"])

        #endregion

        #region q6 (to iphone users), have you ever switched to a third-party messaging app to accomodate non-ios users?
        q6_data = data["Have you ever switched to a third-party messaging app (WhatsApp, Discord, etc.) to accommodate non-iPhone users?"]

        q6_y = 0
        q6_n = 0
        q6_a = 0

        for answer in q6_data:
            if answer == "Yes":
                q6_y += 1
                q6_a += 1
            elif answer == "No":
                q6_n += 1
                q6_a += 1
        
        #convert to %
        q6_y = (q6_y/q6_a) * 100
        q6_n = (q6_n/q6_a) * 100

        q6_y = round(q6_y, 2)
        q6_n = round(q6_n, 2)

        q6_nws_bar_chart = BarChart([q5_y, q5_n], bar_names=["Yes", "No"])
        q6_surv_bar_chart = BarChart([42, 58], bar_names=["Yes","No"])

        #endregion

    #endregion


    #region DISPLAY

    #endregion


    #region 95 CONFIDENCE

    #endregion


    #region T-TEST

    #endregion

        self.embed()

        

        

        return super().construct()
