"""
Stats final project presentation (ManimGL + Manim Slides).

From repo root:
    manim-slides render --GL stats-final-project/project-animation.py MainScene

Or cd stats-final-project, then:
    manim-slides render --GL project-animation.py MainScene

Present (after rendering, from stats-final-project/):
    manim-slides MainScene

Requires Qt for present: pip install "manim-slides[pyside6]"

Import order matters: manimlib must load before manim_slides.Slide.
"""
import sys
from collections import Counter
from pathlib import Path

# Scenes in subfolders are not on sys.path; add repo root for local imports.
for _parent in Path(__file__).resolve().parents:
    if (_parent / "customMobjects").is_dir():
        sys.path.insert(0, str(_parent))
        break

from manimlib import *
from manim_slides import Slide
from customMobjects import Table
import json
import math


def proportion_difference_ci_values(
    nws_x: int,
    nws_n: int,
    study_x: int,
    study_n: int,
    z: float = 1.96,
) -> dict:
    """Normal-approximation 95% CI for p̂_1 - p̂_2 (unpooled SE)."""
    p1 = nws_x / nws_n
    p2 = study_x / study_n
    diff = p1 - p2
    se_diff = np.sqrt(p1 * (1 - p1) / nws_n + p2 * (1 - p2) / study_n)
    margin = z * se_diff
    low = diff - margin
    high = diff + margin
    return {
        "nws_x": nws_x,
        "nws_n": nws_n,
        "study_x": study_x,
        "study_n": study_n,
        "p1": p1,
        "p2": p2,
        "p1_pct": round(p1 * 100, 2),
        "p2_pct": round(p2 * 100, 2),
        "diff": diff,
        "diff_pct": round(diff * 100, 2),
        "se_diff": se_diff,
        "margin": margin,
        "margin_pct": round(margin * 100, 2),
        "low_pct": round(low * 100, 2),
        "high_pct": round(high * 100, 2),
    }


def survey_yes_no_counts(survey_data: dict, question_key: str) -> tuple[int, int]:
    yes_count = 0
    n_count = 0
    for answer in survey_data[question_key]:
        if answer == "Yes":
            yes_count += 1
            n_count += 1
        elif answer == "No":
            n_count += 1
    return yes_count, n_count


def survey_option_counts(
    survey_data: dict, question_key: str, option: str
) -> tuple[int, int]:
    option_count = 0
    n_count = 0
    for response in survey_data[question_key]:
        if not response.strip():
            continue
        n_count += 1
        choices = [choice.strip() for choice in response.split(";")]
        if option in choices:
            option_count += 1
    return option_count, n_count


# National device share used to model the external study sample.
NATIONAL_IOS_PCT = 63.0
NATIONAL_ANDROID_PCT = 36.85
ASSUMED_STUDY_TOTAL_N = 1000


def study_counts_from_published_pct(
    published_pct: float,
    platform: str,
    total_n: int = ASSUMED_STUDY_TOTAL_N,
) -> tuple[int, int]:
    """Map a published study % to (x, n) using national iOS/Android split."""
    if platform == "ios":
        platform_n = round(total_n * NATIONAL_IOS_PCT / 100)
    elif platform == "android":
        platform_n = round(total_n * NATIONAL_ANDROID_PCT / 100)
    else:
        raise ValueError(f"Unknown platform: {platform}")
    successes = round(platform_n * published_pct / 100)
    return successes, platform_n


def normal_cdf(z: float) -> float:
    return 0.5 * (1 + math.erf(z / math.sqrt(2)))


def proportion_sampling_conditions_ok(x: int, n: int) -> bool:
    """Check np >= 10 and n(1-p) >= 10 for normal approximation."""
    if n == 0:
        return False
    p = x / n
    return n * p >= 10 and n * (1 - p) >= 10


CLAIM_CONCLUSION_DESCRIPTIONS: dict[str, str] = {
    "Excluded from group chats": (
        "whether Android users were excluded from group chats (study: 24%)"
    ),
    "Made fun for phone type": (
        "whether Android users were made fun of for their phone (study: 52%)"
    ),
    "Judge green bubbles (Q1)": (
        "whether iPhone users judge people for green bubbles (study: 22%)"
    ),
    "Consider switching to iPhone": (
        "whether Android users considered switching to iPhone (study: 30%)"
    ),
    "Missed or misunderstood messages": (
        "whether Android users missed or misunderstood messages (study: 38%)"
    ),
    "Switch messaging app": (
        "whether iPhone users switched messaging apps to accommodate others (study: 42%)"
    ),
}


def two_proportion_z_test(
    nws_x: int,
    nws_n: int,
    study_x: int,
    study_n: int,
) -> dict:
    """Pooled two-proportion z-test for H0: p1 - p2 = 0 (two-tailed p-value)."""
    p1 = nws_x / nws_n
    p2 = study_x / study_n
    p_pool = (nws_x + study_x) / (nws_n + study_n)
    se = np.sqrt(p_pool * (1 - p_pool) * (1 / nws_n + 1 / study_n))
    z = (p1 - p2) / se if se > 0 else 0.0
    p_value = 2 * (1 - normal_cdf(abs(z)))
    return {
        "nws_x": nws_x,
        "nws_n": nws_n,
        "study_x": study_x,
        "study_n": study_n,
        "p1": p1,
        "p2": p2,
        "p1_pct": round(p1 * 100, 2),
        "p2_pct": round(p2 * 100, 2),
        "p_pool": p_pool,
        "se": se,
        "z": z,
        "p_value": p_value,
        "p_value_pct": round(p_value * 100, 2),
    }


class HorizontalBarChart(VGroup):
    """Bar chart with categories on the left and bars extending to the right."""

    def __init__(
        self,
        values,
        height: float = 5,
        width: float = 5,
        n_ticks: int = 4,
        tick_width: float = 0.2,
        tick_height: float = 0.15,
        label_x_axis: bool = True,
        x_axis_label_height: float = 0.25,
        max_value: float = 100,
        bar_colors=(BLUE, YELLOW),
        bar_fill_opacity: float = 0.8,
        bar_stroke_width: float = 3,
        bar_names=None,
        bar_label_scale_val: float = 0.5,
        **kwargs,
    ):
        if bar_names is None:
            bar_names = []
        super().__init__(**kwargs)
        self.height = height
        self.width = width
        self.n_ticks = n_ticks
        self.tick_width = tick_width
        self.tick_height = tick_height
        self.label_x_axis = label_x_axis
        self.x_axis_label_height = x_axis_label_height
        self.max_value = max_value
        self.bar_colors = list(bar_colors)
        self.bar_fill_opacity = bar_fill_opacity
        self.bar_stroke_width = bar_stroke_width
        self.bar_names = bar_names
        self.bar_label_scale_val = bar_label_scale_val

        self.add_axes()
        self.add_bars(values)
        self.center()

    def add_axes(self) -> None:
        y_axis = Line(self.tick_width * DOWN / 2, self.height * UP)
        x_axis = Line(MED_LARGE_BUFF * LEFT, self.width * RIGHT)
        x_ticks = VGroup()
        x_positions = np.linspace(0, self.width, self.n_ticks + 1)
        tick_values = np.linspace(0, self.max_value, self.n_ticks + 1)
        for x, value in zip(x_positions, tick_values):
            x_tick = Line(UP, DOWN)
            x_tick.set_height(self.tick_height)
            x_tick.move_to(x * RIGHT)
            x_ticks.add(x_tick)
        x_axis.add(x_ticks)
        self.add(y_axis, x_axis)
        self.y_axis, self.x_axis = y_axis, x_axis

        if self.label_x_axis:
            labels = VGroup()
            for x_tick, value in zip(x_ticks, tick_values):
                label = Tex(str(np.round(value, 2)))
                label.set_height(self.x_axis_label_height)
                label.next_to(x_tick, DOWN, SMALL_BUFF)
                labels.add(label)
            self.x_axis_labels = labels
            self.add(labels)

    def add_bars(self, values) -> None:
        buff = float(self.height) / (2 * len(values))
        bars = VGroup()
        for i, value in enumerate(values):
            bar = Rectangle(
                width=(value / self.max_value) * self.width,
                height=buff,
                stroke_width=self.bar_stroke_width,
                fill_opacity=self.bar_fill_opacity,
            )
            bar.move_to((2 * i + 0.5) * buff * UP, LEFT)
            bars.add(bar)
        bars.set_color_by_gradient(*self.bar_colors)

        bar_labels = VGroup()
        for bar, name in zip(bars, self.bar_names):
            label = Text(name)
            label.scale(self.bar_label_scale_val)
            label.next_to(bar, LEFT, SMALL_BUFF)
            bar_labels.add(label)

        self.add(bars, bar_labels)
        self.bars = bars
        self.bar_labels = bar_labels


def dice_sum_distribution(n_dice: int) -> tuple[list[int], list[int]]:
    """Return sorted sums and their counts for n fair six-sided dice."""
    counts: Counter[int] = Counter()

    def recurse(remaining: int, total: int) -> None:
        if remaining == 0:
            counts[total] += 1
            return
        for face in range(1, 7):
            recurse(remaining - 1, total + face)

    recurse(n_dice, 0)
    sums = sorted(counts.keys())
    return sums, [counts[s] for s in sums]


def make_die(face_value: int, side_length: float = 0.9) -> VGroup:
    pip_dirs = {
        1: [ORIGIN],
        2: [UL, DR],
        3: [UL, ORIGIN, DR],
        4: [UL, UR, DL, DR],
        5: [UL, UR, ORIGIN, DL, DR],
        6: [LEFT + UP, LEFT, LEFT + DOWN, RIGHT + UP, RIGHT, RIGHT + DOWN],
    }
    die = VGroup()
    face = Square(side_length=side_length)
    face.set_stroke(WHITE, width=2)
    face.set_fill(GREY_E, opacity=1)
    pip_offset = side_length * 0.22
    for direction in pip_dirs[face_value]:
        dot = Dot(radius=side_length * 0.07, color=WHITE)
        dot.move_to(face.get_center() + direction * pip_offset)
        die.add(dot)
    die.add(face)
    die.face_value = face_value
    return die


def set_die_face(die: VGroup, face_value: int) -> VGroup:
    side_length = die[-1].get_width()
    new_die = make_die(face_value, side_length=side_length)
    new_die.move_to(die)
    return new_die


def make_dice_sum_chart(n_dice: int, height: float = 3.5, width: float = 6) -> BarChart:
    sums, counts = dice_sum_distribution(n_dice)
    percents = [100 * c / sum(counts) for c in counts]
    return BarChart(
        percents,
        bar_names=[str(s) for s in sums],
        max_value=max(percents) * 1.15,
        height=height,
        width=width,
        bar_label_scale_val=0.5
    )


class MainScene(Slide):
    def construct(self) -> None:

    #region TITLE SLIDE (title + relevant graphic)
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
        self.next_slide()

        title_text = Text("Bias against Android users in NWS")
        self.play(ShowCreation(title_text))
        self.next_slide()

        author_text = Text(r"-By: Cameron Engrav")
        author_text.shift(DOWN)
        author_text.shift(RIGHT *1.8)
        self.play(ShowCreation(author_text))
        self.next_slide()

        tofade = [apple_logo, android_logo, vs_text, title_text, author_text]
        fadegroup = VGroup()
        for item in tofade:
            fadegroup.add(item)

        self.play(FadeOut(fadegroup))
        #self.next_slide()
    #endregion

    #region PROJECT INTRODUCTION
        intro_title = Text("Project Introduction").scale(0.75)
        intro_title.to_edge(UP, buff=0.4)
        self.play(Write(intro_title))
        self.next_slide()

        q_text_group = VGroup()

        q_text_1 = Text("I've always been interested in this. I've heard\nthat people are really attatched to\ntheir iPhones, but that usually comes from social media.")
        q_text_2 = Text("I wanted to look at how it might show up in the real world.")
        q_text_group.add(q_text_1, q_text_2)
        q_text_group.scale(0.75)
        q_text_1.shift(LEFT * 0.33)
        q_text_2.shift(DOWN)
        q_text_group.align_on_border(LEFT)


        self.play(ShowCreation(q_text_1))
        self.next_slide()
        self.play(ShowCreation(q_text_2))
        self.next_slide()

        self.play(FadeOut(q_text_group))
        #self.next_slide()

        """
        knowing that I wanted to look at this, I found a survay talking about this bias in adults,
        and I asked the same questions to the NWS. Now, I'll be able to compare our answers to see if there
        is a significant difference
        """

        ex_text_group = VGroup()
        ex_text_1 = Text("Knowing that I wanted to look at this bias, I found a survay talking about it in adults,")
        ex_text_2 = Text("and asked the same questions to the NWS population. Now, I'll be able to compare the results from NWS")
        ex_text_3 = Text("and see if we have a significant difference from the survay.")
        ex_text_group.add(ex_text_1, ex_text_2, ex_text_3)
        ex_text_group.arrange(DOWN, aligned_edge=LEFT, buff=0.3)
        ex_text_group.scale(0.5)
        ex_text_group.align_on_border(LEFT)

        self.play(ShowCreation(ex_text_1))
        self.next_slide()
        self.play(ShowCreation(ex_text_2))
        self.next_slide()
        self.play(ShowCreation(ex_text_3))
        self.next_slide()

        self.play(FadeOut(ex_text_group))
        #self.next_slide()

        claim_table = Table(
            [
                ["Claim", "Survay %"],
                ["Android users have been excluded from group chats", "24%"],
                ["Android users have been made fun of for their phone type", "52%"],
                ["iPhone users think less of Android users because of their phone", "22%"],
                ["Android users consider switching to iPhone because of peer presure", "30%"],
                ["Android users missed or could not understand messages (texting app incompatibility)", "38%"],
                ["iPhone users will switch to another messaging app to accomidate Andriod users", "42%"]
            ],
            header_row=True,
            full_width=True,
            column_width_ratios=(4, 1),
        )

        claim_table.scale(0.5)
        claim_table.align_on_border(LEFT)
        self.play(ShowCreation(claim_table))
        self.next_slide()
        self.play(FadeOut(intro_title), FadeOut(claim_table))
    #endregion

    #region HYPOTHESIS TEST
        hypo_title = Text("Hypothesis Test").scale(0.75)
        hypo_title.to_edge(UP, buff=0.4)
        self.play(Write(hypo_title))
        self.next_slide()

        hypo_text_group = VGroup()
        hypo_text_1 = Text("Six claims → six two-proportion z-tests (same setup each time).")
        hypo_text_2 = Text("Significance level:")
        hypo_alpha = Tex(r"\alpha = 0.05")
        hypo_text_3 = Text("Hypotheses (same for every claim):")
        hypo_text_4 = Tex(r"H_{0}:\widehat{p}_{1}-\widehat{p}_{2}=0")
        hypo_text_5 = Tex(r"H_{A}:\widehat{p}_{1}-\widehat{p}_{2}\ne 0")
        hypo_text_6 = Tex(
            r"\text{Where }\widehat{p}_{1}=\text{NWS proportion, "
            r"}\widehat{p}_{2}=\text{published study proportion}"
        )
        hypo_text_group.add(
            hypo_text_1,
            hypo_text_2,
            hypo_alpha,
            hypo_text_3,
            hypo_text_4,
            hypo_text_5,
            hypo_text_6,
        )
        hypo_text_group.arrange(DOWN, aligned_edge=LEFT, buff=0.28)
        hypo_text_group.scale(0.48)
        hypo_text_group.next_to(hypo_title, DOWN, buff=0.35)
        hypo_text_group.align_to(hypo_title, LEFT)

        self.play(Write(hypo_text_group))
        self.next_slide()

        hypo_prediction = Text(
            "Prediction: I expect to reject H₀ for most claims.\n"
            "NWS is mostly students under 18, while the published study sampled adults—\n"
            "phone bias at school may not match the national adult percentages."
        ).scale(0.42)
        hypo_prediction.next_to(hypo_title, DOWN, buff=0.4)
        hypo_prediction.align_to(hypo_title, LEFT)

        self.play(FadeOut(hypo_text_group), Write(hypo_prediction))
        self.next_slide()
        self.play(FadeOut(hypo_title), FadeOut(hypo_prediction))
        #self.next_slide()
    #endregion

    #region INTRO
        intro_txt_1 = Text("For each of the hypothoses, we are comparing two sample proportions")
        intro_txt_2 = Text("We are doing this because we don't know the true proportion, all we know is what we found, and\nwhat the study found")
        intro_txt_3 = Text("We will be testing to see if there is a significant difference between NWS and\nthe findings of the study")
        intro_txt_4 = Text("To do this, we will create a normal distribution around the diferece of the samples")
        intro_txt_5 = Text("If a differece of 0 falls in our normal dist, then we can't know if there is a significant differece")
        intro_txt_6 = Text("If 0 does not fall in our normal dist, then we know there's a significant difference")
        intro_txt_7 = Text("To start, lets look at our data")

        intro_context = VGroup(intro_txt_1, intro_txt_2, intro_txt_3)
        intro_context.arrange(DOWN, aligned_edge=LEFT, buff=0.35)
        intro_context.scale(0.5)
        intro_context.align_on_border(LEFT)

        intro_sampling = VGroup(intro_txt_4, intro_txt_5, intro_txt_6)
        intro_sampling.arrange(DOWN, aligned_edge=LEFT, buff=0.35)
        intro_sampling.scale(0.5)
        intro_sampling.move_to(ORIGIN)

        intro_txt_7.scale(0.55)

        self.play(Write(intro_txt_1))
        self.next_slide()
        self.play(Write(intro_txt_2))
        self.next_slide()
        self.play(Write(intro_txt_3))
        self.next_slide()
        self.play(FadeOut(intro_context))
        #self.next_slide()

        self.play(Write(intro_txt_4))
        self.next_slide()
        self.play(Write(intro_txt_5))
        self.next_slide()
        self.play(Write(intro_txt_6))
        self.next_slide()
        self.play(FadeOut(intro_sampling))
        #self.next_slide()

        self.play(Write(intro_txt_7))
        self.next_slide()
        self.play(FadeOut(intro_txt_7))
        #self.next_slide()
    #endregion

    #region POPULATION AND SAMPLE DATA
        json_path = Path(__file__).parent / "survey_by_question.json"
        with open(json_path, encoding="utf-8") as json_file:
            data = json.load(json_file)

        data_title = Text("Population and Sample Data").scale(0.75)
        data_title.to_edge(UP, buff=0.35)

        pop_sample_txt = Text(
            "Population (comparison data we test against):\n"
            "Published adult phone-bias survey (allaboutcookies.org), modeled with\n"
            f"US device share {NATIONAL_IOS_PCT:.0f}% iOS / {NATIONAL_ANDROID_PCT:.2f}% Android "
            f"(assumed n = {ASSUMED_STUDY_TOTAL_N}).\n\n"
            "Sample (data we collected):\n"
            "NWS students who answered our Google Form survey."
        ).scale(0.38)
        pop_sample_txt.next_to(data_title, DOWN, buff=0.35)
        pop_sample_txt.align_to(data_title, LEFT)

        self.play(Write(data_title), Write(pop_sample_txt))
        self.next_slide()

        method_txt = Text(
            "Methodology: I emailed NWS students and posted the same topics as the study.\n"
            "iPhone users answered Q1–Q3; Android users answered Q4–Q5.\n"
            "Examples: green-bubble judgment, peer pressure to switch, group-chat exclusion, etc."
        ).scale(0.38)
        method_txt.next_to(data_title, DOWN, buff=0.35)
        method_txt.align_to(data_title, LEFT)

        self.play(FadeOut(pop_sample_txt), Write(method_txt))
        self.next_slide()

        #keep this on the bottom for charts in this section
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
        q1_nws_bar_chart = BarChart([q1_y, q1_n], bar_names=["Yes", "No"], max_value=100)
        q1_surv_bar_chart = BarChart([22, 78], bar_names=["Yes", "No"], max_value=100)
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

        q2_nws_bar_chart = HorizontalBarChart(
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
            ],
            max_value=100,
            height=5.5,
            width=4.5,
        )

        q2_surv_bar_chart = HorizontalBarChart(
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
            ],
            max_value=100,
            height=5,
            width=4.5,
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

        q3_nws_bar_chart = BarChart([q3_y, q3_n], bar_names=["Yes","No"], max_value=100)
        q3_surv_bar_chart = BarChart([42, 58], bar_names=["Yes","No"], max_value=100)
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

        q4_nws_bar_chart = HorizontalBarChart(
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
                "Missed or misunderstood messages\n(due to compatibility issues)",
                "Felt negatively judged",
                "Asked a group to use an alternative messaging app",
                "Felt embarrassed",
                "Been excluded from a group chat",
                "None of the above",
            ],
            max_value=100,
            height=5.5,
            width=4.5,
        )

        q4_surv_bar_chart = HorizontalBarChart(
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
                "Missed or misunderstood messages\n(due to compatibility issues)",
                "Felt negatively judged",
                "Asked a group to use an alternative messaging app",
                "Felt embarrassed",
                "Been excluded from a group chat",
            ],
            max_value=100,
            height=5,
            width=4.5,
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

        q5_nws_bar_chart = BarChart([q5_y, q5_n], bar_names=["Yes", "No"], max_value=100)
        q5_surv_bar_chart = BarChart([30, 70], bar_names=["Yes","No"], max_value=100)

        #endregion

        citation.scale(0.35)
        citation.to_edge(DOWN, buff=0.25)
        self.add(citation)

        def layout_comparison_charts(question, nws_chart, surv_chart, note=None, chart_scale=0.7):
            question.scale(0.38)
            question.to_edge(UP, buff=0.35)

            nws_label = Text("NWS").scale(0.55)
            surv_label = Text("External survey").scale(0.55)
            nws_chart.scale(chart_scale)
            surv_chart.scale(chart_scale)

            nws_group = VGroup(nws_label, nws_chart).arrange(DOWN, buff=0.2)
            surv_group = VGroup(surv_label, surv_chart).arrange(DOWN, buff=0.2)
            charts = VGroup(nws_group, surv_group).arrange(
                RIGHT, buff=1.75, aligned_edge=DOWN
            )
            charts.next_to(question, DOWN, buff=0.4)

            slide = VGroup(question, charts)
            if note is not None:
                note.scale(0.35)
                note.next_to(charts, DOWN, buff=0.3)
                slide.add(note)

            self.play(Write(question))
            self.next_slide()
            self.play(
                Write(nws_label),
                Write(surv_label),
                ShowCreation(nws_chart),
                ShowCreation(surv_chart),
            )
            if note is not None:
                self.play(Write(note))
            self.next_slide()
            self.play(FadeOut(slide))

        def show_yes_no_data(question, nws_chart, surv_chart, chart_scale=0.75):
            layout_comparison_charts(
                question, nws_chart, surv_chart, chart_scale=chart_scale
            )

        def show_multi_bar_data(question, nws_chart, surv_chart, note=None):
            layout_comparison_charts(
                question, nws_chart, surv_chart, note=note, chart_scale=0.52
            )

        q1_x_count, q1_n_count = survey_yes_no_counts(
            data, "Do you judge people when they text you with green bubles?"
        )
        _, q5_n_count = survey_yes_no_counts(
            data, "Have you ever considered switching to iPhone due to peer pressure?"
        )
        q4_n_count = sum(
            1
            for r in data[
                "Which of the following have happened to you because you have an "
                "Android phone? (select all that apply)"
            ]
            if r.strip()
        )

        sampling_title = Text("Sampling-distribution conditions (normal approx.)").scale(0.55)
        sampling_title.next_to(data_title, DOWN, buff=0.3)
        sampling_body = Text(
            "For each proportion we need np ≥ 10 and n(1−p) ≥ 10.\n"
            f"Q1 (iPhone): n = {q1_n_count}, np and n(1−p) pass.\n"
            f"Android Q4/Q5: n = {q4_n_count} / {q5_n_count}, checked per claim.\n"
            "Assumed study n₂ from national device split also meets these conditions."
        ).scale(0.36)
        sampling_body.next_to(sampling_title, DOWN, buff=0.25, aligned_edge=LEFT)

        self.play(FadeOut(method_txt), Write(sampling_title), Write(sampling_body))
        self.next_slide()
        self.play(FadeOut(data_title), FadeOut(sampling_title), FadeOut(sampling_body))

        show_yes_no_data(data_txt_1, q1_nws_bar_chart, q1_surv_bar_chart)

        q2_txt = Text(
            'To iPhone users: "Which of the following have you done\n'
            'because someone you know has an Android?"'
        )
        q2_note = Text(
            "Note: NWS included 'None of the above'; the external survey did not."
        )
        show_multi_bar_data(q2_txt, q2_nws_bar_chart, q2_surv_bar_chart, q2_note)

        q3_txt = Text(
            'To iPhone users: "Have you switched to a third-party\n'
            'messaging app to accommodate non-iPhone users?"'
        )
        show_yes_no_data(q3_txt, q3_nws_bar_chart, q3_surv_bar_chart)

        q4_txt = Text(
            'To Android users: "Which of the following have happened\n'
            'to you because you have an Android phone?"'
        )
        q4_note = Text(
            "Note: NWS included 'None of the above'; the external survey did not."
        )
        show_multi_bar_data(q4_txt, q4_nws_bar_chart, q4_surv_bar_chart, q4_note)

        q5_txt = Text(
            'To Android users: "Have you considered switching to iPhone\n'
            'due to peer pressure?"'
        )
        show_yes_no_data(q5_txt, q5_nws_bar_chart, q5_surv_bar_chart)

        self.play(FadeOut(citation))
        #self.next_slide()

    #endregion

    #region POTENTIAL BIAS
        bias_title = Text("Potential Bias").scale(0.75)
        bias_title.to_edge(UP, buff=0.4)

        bias_text_1 = Text(
            "Main bias: the published study sampled adults 18+, while NWS is mostly under 18."
        )
        bias_text_2 = Text(
            "How I addressed it: used the same survey wording as the study so comparisons\n"
            "are about the same behaviors, and cited the external source clearly."
        )
        bias_text_3 = Text(
            "Bias that may still exist: convenience sample (only NWS students),\n"
            "voluntary response, and multi-select questions (Q2/Q4) vs. single-select in the study."
        )

        bias_body = VGroup(bias_text_1, bias_text_2, bias_text_3)
        bias_body.arrange(DOWN, aligned_edge=LEFT, buff=0.35)
        bias_body.scale(0.42)
        bias_body.next_to(bias_title, DOWN, buff=0.45)
        bias_body.align_on_border(LEFT)

        self.play(Write(bias_title))
        self.next_slide()
        for line in bias_body:
            self.play(Write(line))
            self.next_slide()
        self.play(FadeOut(bias_title), FadeOut(bias_body))
        #self.next_slide()
    #endregion

    #region 95% CONFIDENCE INTERVAL
        #region Explain what a normal distribution is (dice example)
        conf_text_1 = Text(
            "One of the most powerful tools in stats is a normal distribution",
            t2s={"normal distribution": ITALIC},
        )
        conf_text_1.scale(0.55)
        conf_text_1.to_edge(UP, buff=0.4)

        dice_example_txt = Text(
            "A familiar example: roll two dice, add the faces, and track the total."
        ).scale(0.48)
        dice_example_txt.next_to(conf_text_1, DOWN, buff=0.35)

        die_left = make_die(1)
        die_right = make_die(1)
        dice_pair = VGroup(die_left, die_right).arrange(RIGHT, buff=0.6)
        dice_pair.next_to(dice_example_txt, DOWN, buff=0.45)

        plus_sign = Tex("+").scale(1.2)
        plus_sign.move_to((die_left.get_right() + die_right.get_left()) / 2)

        sum_label = Tex("= 2").scale(1.1)
        sum_label.next_to(die_right, RIGHT, buff=0.45)

        def roll_die_pair(final_left: int, final_right: int):
            faces = list(range(1, 7))
            for i in range(10):
                left_val = faces[i % 6]
                right_val = faces[(i + 2) % 6]
                if i == 9:
                    left_val, right_val = final_left, final_right
                new_left = set_die_face(die_left, left_val)
                new_right = set_die_face(die_right, right_val)
                new_sum = Tex(f"= {left_val + right_val}").scale(1.1)
                new_sum.next_to(die_right, RIGHT, buff=0.45)
                self.play(
                    Transform(die_left, new_left),
                    Transform(die_right, new_right),
                    Transform(sum_label, new_sum),
                    run_time=0.12,
                )

        hist_caption = Text(
            "Each total has a different number of ways to occur (out of 36 rolls)."
        ).scale(0.42)
        hist_caption.to_edge(UP, buff=0.4)

        two_dice_chart = make_dice_sum_chart(2, height=3.2, width=5.5)
        two_dice_chart.scale(0.7)
        two_dice_chart.next_to(hist_caption, DOWN, buff=0.35)

        more_dice_txt = Text(
            "Add a third or fourth die—the totals cluster more around the middle."
        ).scale(0.48)
        more_dice_txt.to_edge(UP, buff=0.4)

        three_dice_chart = make_dice_sum_chart(3, height=3.0, width=5.5)
        four_dice_chart = make_dice_sum_chart(4, height=3.0, width=5.5)
        for chart in (three_dice_chart, four_dice_chart):
            chart.scale(0.65)
        chart_row = VGroup(
            VGroup(Text("3 dice").scale(0.4), three_dice_chart).arrange(DOWN, buff=0.15),
            VGroup(Text("4 dice").scale(0.4), four_dice_chart).arrange(DOWN, buff=0.15),
        ).arrange(RIGHT, buff=0.6)
        chart_row.next_to(more_dice_txt, DOWN, buff=0.35)

        conf_text_2 = Text("A normal distribution is a smooth bell curve like this")
        conf_text_2.scale(0.5)
        conf_text_2.to_edge(UP, buff=0.4)

        conf_graph = Axes(
            x_range=(-4, 4, 1),
            y_range=(0, 0.45, 0.1),
            height=4.5,
            width=8,
        )
        conf_graph.add_coordinate_labels(num_decimal_places=2)
        conf_graph.next_to(conf_text_2, DOWN, buff=0.35)
        conf_normal_dist = conf_graph.get_graph(
            lambda x: np.exp(-(x**2) / 2) / np.sqrt(2 * np.pi),
            x_range=(-4, 4),
            color=BLUE,
        )
        conf_curve_label = Tex(
            r"f(x)=\frac{e^{-x^2/2}}{\sqrt{2\pi}}",
            color=BLUE
        ).scale(0.55)
        conf_curve_label.next_to(conf_graph, DOWN, buff=0.25)

        conf_text_3 = Text(
            "This normal distribution has an average value of 0"
        )
        conf_text_3.scale(0.48)
        conf_text_3.to_edge(DOWN, buff=0.4)

        conf_text_4 = Tex(r"\text{It also has a Standard Deviation (or }\sigma\text{) of }1")

        self.play(Write(conf_text_1))
        self.next_slide()

        self.play(Write(dice_example_txt))
        self.play(FadeIn(die_left), FadeIn(die_right), FadeIn(plus_sign))
        self.next_slide()

        roll_die_pair(4, 3)
        self.next_slide()

        self.play(
            FadeOut(conf_text_1),
            FadeOut(dice_example_txt),
            FadeOut(dice_pair),
            FadeOut(plus_sign),
            FadeOut(sum_label),
        )
        self.play(Write(hist_caption), ShowCreation(two_dice_chart))
        self.next_slide()

        self.play(
            FadeOut(hist_caption),
            FadeOut(two_dice_chart),
            Write(more_dice_txt),
            FadeIn(chart_row),
        )
        self.next_slide()

        self.play(
            FadeOut(more_dice_txt),
            FadeOut(chart_row),
            Write(conf_text_2),
            ShowCreation(conf_graph),
            ShowCreation(conf_normal_dist),
            Write(conf_curve_label),
        )
        self.next_slide()

        self.play(
            FadeOut(conf_text_2),
            Write(conf_text_3),
        )
        self.next_slide()
        self.play(FadeOut(conf_text_3))

        conf_text_4.scale(0.48)
        conf_text_4.to_edge(DOWN, buff=0.4)
        conf_sigma_brackets = VGroup()
        peak_y = np.exp(-0.5) / np.sqrt(2 * np.pi)
        for x_val, label_tex in ((-1, r"-1\sigma"), (1, r"+1\sigma")):
            bracket = Line(
                conf_graph.coords_to_point(x_val, 0),
                conf_graph.coords_to_point(x_val, peak_y),
                color=GREY_B,
                stroke_width=2,
            )
            label = Tex(label_tex).scale(0.38)
            label.next_to(conf_graph.coords_to_point(x_val, 0), DOWN, buff=0.12)
            conf_sigma_brackets.add(bracket, label)
        self.play(Write(conf_text_4), ShowCreation(conf_sigma_brackets))
        self.next_slide()

        conf_sigma_caption = Text(
            "Standard deviation measures how spread out values are from the average"
        ).scale(0.42)
        conf_sigma_caption.to_edge(UP, buff=0.4)
        conf_sigma_formula = Tex(
            r"\sigma = \sqrt{\frac{1}{N}\sum_{i=1}^{N}(x_i - \mu)^2}"
        ).scale(0.42)
        conf_sigma_formula.next_to(conf_curve_label, LEFT, buff=0.45, aligned_edge=DOWN)

        self.play(Write(conf_sigma_caption), Write(conf_sigma_formula))
        self.next_slide()

        conf_z_caption = Text(
            "A z-score tells us how many standard deviations a value is from the mean"
        ).scale(0.42)
        conf_z_caption.to_edge(UP, buff=0.4)
        conf_z_formula = Tex(r"z = \frac{x - \mu}{\sigma}").scale(0.48)
        conf_z_formula.next_to(conf_curve_label, RIGHT, buff=0.45, aligned_edge=DOWN)
        conf_dist_formulas = VGroup(
            conf_sigma_formula, conf_curve_label, conf_z_formula
        )

        self.play(
            FadeOut(conf_sigma_caption),
            FadeOut(conf_text_4),
            FadeOut(conf_sigma_brackets),
            Write(conf_z_caption),
            Write(conf_z_formula),
        )
        self.next_slide()

        conf_95_caption = Text(
            "About 95% of a normal distribution falls within z = ±1.96"
        ).scale(0.42)
        conf_95_caption.to_edge(UP, buff=0.4)
        conf_95_area = conf_graph.get_area_under_graph(
            conf_normal_dist,
            x_range=(-1.96, 1.96),
            fill_color=YELLOW,
            fill_opacity=0.35,
        )
        z_minus_label = Tex("-1.96").scale(0.4)
        z_plus_label = Tex("1.96").scale(0.4)
        for z_val, label in ((-1.96, z_minus_label), (1.96, z_plus_label)):
            label.next_to(conf_graph.coords_to_point(z_val, 0), DOWN, buff=0.15)

        self.play(
            FadeOut(conf_z_caption),
            Write(conf_95_caption),
            FadeIn(conf_95_area),
            Write(z_minus_label),
            Write(z_plus_label),
        )
        self.next_slide()

        conf_ci_text = Text(
            "A 95% confidence interval uses that same z = 1.96 to build a range\n"
            "around our sample mean—if we repeated sampling many times, about 95%\n"
            "of those intervals would contain the true population value"
        ).scale(0.38)
        conf_ci_text.to_edge(UP, buff=0.35)
        conf_ci_formula = Tex(
            r"\text{95\% CI} \approx \bar{x} \pm 1.96 \cdot \frac{s}{\sqrt{n}}"
        ).scale(0.5)
        conf_ci_formula.next_to(conf_curve_label, DOWN, buff=0.3)

        self.play(
            FadeOut(conf_95_caption),
            Write(conf_ci_text),
            Write(conf_ci_formula),
        )
        self.next_slide()

        conf_dist_group = VGroup(
            conf_graph,
            conf_normal_dist,
            conf_dist_formulas,
            conf_95_area,
            z_minus_label,
            z_plus_label,
        )
        self.play(
            FadeOut(conf_ci_text),
            FadeOut(conf_ci_formula),
            FadeOut(conf_dist_group),
        )
        self.next_slide()
        #endregion

        #region Sample proportions
        prop_text_1 = Text(
            "Our hypothesis tests compare two sample proportions:\n"
            "one from NWS and one from the study survey"
        ).scale(0.45)
        prop_text_1.to_edge(UP, buff=0.4)

        prop_text_2 = Text(
            "To make a sample proportion, count the successes in your sample\n"
            '(for example, how many people answered "Yes"), then divide by n'
        ).scale(0.42)
        prop_text_2.to_edge(UP, buff=0.4)

        prop_hat_formula = Tex(r"\widehat{p} = \frac{x}{n}").scale(0.65)
        prop_hat_labels = Tex(
            r"\text{where } x = \text{successes and } n = \text{sample size}"
        ).scale(0.42)
        prop_hat_block = VGroup(prop_hat_formula, prop_hat_labels).arrange(
            DOWN, buff=0.25
        )

        prop_text_3 = Text(
            "Sample proportions are normally distributed—we use a bell curve\n"
            "to model how those proportions would vary across repeated samples"
        ).scale(0.42)
        prop_text_3.to_edge(UP, buff=0.4)

        prop_graph = Axes(
            x_range=(-4, 4, 1),
            y_range=(0, 0.45, 0.1),
            height=3.8,
            width=7,
        )
        prop_graph.add_coordinate_labels(font_size=20, num_decimal_places=2)
        prop_normal_dist = prop_graph.get_graph(
            lambda x: np.exp(-(x**2) / 2) / np.sqrt(2 * np.pi),
            x_range=(-4, 4),
            color=BLUE,
        )
        prop_graph_group = VGroup(prop_graph, prop_normal_dist)
        prop_graph_group.next_to(prop_text_3, DOWN, buff=0.35)

        prop_se_text_1 = Text(
            "The standard error (SE) measures how much a sample proportion would vary\n"
            "if we repeated the survey many times with the same sample size"
        ).scale(0.42)
        prop_se_text_1.to_edge(UP, buff=0.4)

        prop_se_text_2 = Text(
            "Think of it as the typical spread of sample proportions around the true value—\n"
            "a smaller SE means our estimate is more precise"
        ).scale(0.42)
        prop_se_text_2.to_edge(UP, buff=0.4)

        prop_se_formula = Tex(
            r"SE_{\widehat{p}} = \sqrt{\frac{\widehat{p}(1-\widehat{p})}{n}}"
        ).scale(0.4)
        prop_diff_formula = Tex(
            r"SE_{\widehat{p}_1 - \widehat{p}_2}"
            r" = \sqrt{\widehat{p}(1-\widehat{p})\left(\frac{1}{n_1}+\frac{1}{n_2}\right)}"
        ).scale(0.36)
        prop_hat_formula_small = Tex(r"\widehat{p} = \frac{x}{n}").scale(0.5)
        prop_se_formula.next_to(
            prop_hat_formula_small, LEFT, buff=0.35, aligned_edge=DOWN
        )
        prop_diff_formula.next_to(
            prop_hat_formula_small, RIGHT, buff=0.35, aligned_edge=DOWN
        )
        prop_formula_row = VGroup(
            prop_se_formula, prop_hat_formula_small, prop_diff_formula
        )

        self.play(Write(prop_text_1))
        self.next_slide()

        self.play(FadeOut(prop_text_1), Write(prop_text_2), Write(prop_hat_block))
        self.next_slide()

        self.play(
            FadeOut(prop_text_2),
            FadeOut(prop_hat_block),
            Write(prop_text_3),
            ShowCreation(prop_graph),
            ShowCreation(prop_normal_dist),
        )
        self.next_slide()

        self.play(FadeOut(prop_text_3), Write(prop_se_text_1))
        self.next_slide()

        self.play(FadeOut(prop_se_text_1), Write(prop_se_text_2))
        self.next_slide()

        prop_formula_row.next_to(prop_graph_group, DOWN, buff=0.3)
        self.play(
            FadeOut(prop_se_text_2),
            Write(prop_hat_formula_small),
            Write(prop_se_formula),
            Write(prop_diff_formula),
        )
        self.next_slide()

        prop_section_group = VGroup(
            prop_graph_group,
            prop_formula_row,
        )
        self.play(FadeOut(prop_section_group))
        self.next_slide()
        #endregion

        #region 95% CI for each question
        ci_json_path = Path(__file__).parent / "survey_by_question.json"
        with open(ci_json_path, encoding="utf-8") as ci_file:
            ci_survey = json.load(ci_file)

        q1_key = "Do you judge people when they text you with green bubles?"
        q3_key = (
            "Have you ever switched to a third-party messaging app "
            "(WhatsApp, Discord, etc.) to accommodate non-iPhone users?"
        )
        q4_key = (
            "Which of the following have happened to you because you have an "
            "Android phone? (select all that apply)"
        )
        q5_key = "Have you ever considered switching to iPhone due to peer pressure?"

        # (title, NWS counts, published study %, platform for national split)
        claim_ci_specs = [
            (
                "Excluded from group chats",
                survey_option_counts(
                    ci_survey, q4_key, "Been excluded from a group chat"
                ),
                24.0,
                "android",
            ),
            (
                "Made fun for phone type",
                survey_option_counts(
                    ci_survey, q4_key, "Made fun of by iPhone users"
                ),
                52.0,
                "android",
            ),
            (
                "Judge green bubbles (Q1)",
                survey_yes_no_counts(ci_survey, q1_key),
                22.0,
                "ios",
            ),
            (
                "Consider switching to iPhone",
                survey_yes_no_counts(ci_survey, q5_key),
                30.0,
                "android",
            ),
            (
                "Missed or misunderstood messages",
                survey_option_counts(
                    ci_survey,
                    q4_key,
                    "Missed or misunderstood messages (due to compatibility issues)",
                ),
                38.0,
                "android",
            ),
            (
                "Switch messaging app",
                survey_yes_no_counts(ci_survey, q3_key),
                42.0,
                "ios",
            ),
        ]
        claim_ci_results = []
        for title, (nws_x, nws_n), study_pct, platform in claim_ci_specs:
            study_x, study_n = study_counts_from_published_pct(study_pct, platform)
            claim_ci_results.append(
                (
                    title,
                    proportion_difference_ci_values(nws_x, nws_n, study_x, study_n),
                )
            )

        ci_national_note = Text(
            f"Assume the external study reflects US device share: "
            f"{NATIONAL_IOS_PCT:.0f}% iOS and {NATIONAL_ANDROID_PCT:.2f}% Android "
            f"(total assumed n = {ASSUMED_STUDY_TOTAL_N})"
        ).scale(0.36)
        ci_national_note.to_edge(UP, buff=0.35)

        def walkthrough_q1_ci():
            _, q1 = next(r for r in claim_ci_results if "Q1" in r[0])
            study_ios_n = round(ASSUMED_STUDY_TOTAL_N * NATIONAL_IOS_PCT / 100)

            ci_q1_title = Text(
                '95% CI for Question 1: comparing NWS to the external survey\n'
                '"Do you judge people when they text you with green bubbles?"'
            ).scale(0.36)
            ci_q1_title.next_to(ci_national_note, DOWN, buff=0.25)

            ci_steps = VGroup(
                Tex(
                    rf"\widehat{{p}}_1 = \frac{{{q1['nws_x']}}}{{{q1['nws_n']}}} "
                    rf"\approx {q1['p1']:.3f} "
                    rf"({q1['p1_pct']:.2f}\%)"
                ),
                Tex(
                    rf"\widehat{{p}}_2 \approx {q1['p2']:.3f} "
                    rf"({q1['p2_pct']:.2f}\%), \quad "
                    rf"n_2 \approx {study_ios_n} \text{{ iPhone users}}"
                ),
                Tex(
                    rf"\widehat{{p}}_1 - \widehat{{p}}_2 \approx "
                    rf"{q1['diff_pct']:+.2f} \text{{ percentage points}}"
                ),
                Tex(
                    rf"SE_{{\widehat{{p}}_1 - \widehat{{p}}_2}} = "
                    rf"\sqrt{{\frac{{\widehat{{p}}_1(1-\widehat{{p}}_1)}}{{n_1}} + "
                    rf"\frac{{\widehat{{p}}_2(1-\widehat{{p}}_2)}}{{n_2}}}} "
                    rf"\approx {q1['se_diff']:.3f}"
                ),
                Tex(
                    rf"\text{{margin}} = 1.96 \cdot SE "
                    rf"= 1.96 \times {q1['se_diff']:.3f} "
                    rf"\approx {q1['margin']:.3f} "
                    rf"\;\Rightarrow\; \pm {q1['margin_pct']:.2f} "
                    rf"\text{{ percentage points}}"
                ),
                Tex(
                    rf"\text{{95\% CI for }} \widehat{{p}}_1 - \widehat{{p}}_2: "
                    rf"{q1['diff_pct']:+.2f} \pm {q1['margin_pct']:.2f} "
                    rf"\text{{ pp}} = "
                    rf"[{q1['low_pct']:+.2f},\ {q1['high_pct']:+.2f}] "
                    rf"\text{{ pp}}"
                ),
            )
            for step in ci_steps:
                step.scale(0.58)
            ci_steps.arrange(DOWN, aligned_edge=LEFT, buff=0.28)
            ci_steps.next_to(ci_q1_title, DOWN, buff=0.35)
            ci_steps.align_to(ci_q1_title, LEFT)

            self.play(Write(ci_national_note))
            self.next_slide()
            self.play(Write(ci_q1_title))
            self.next_slide()
            visible_steps = VGroup()
            for step in ci_steps:
                visible_steps.add(step)
                self.play(Write(step))
                self.next_slide()
            self.play(
                FadeOut(ci_national_note),
                FadeOut(ci_q1_title),
                FadeOut(visible_steps),
            )
            self.next_slide()

        walkthrough_q1_ci()

        ci_parallel_title = Tex(
            r"\text{95\% CI for } \widehat{p}_1 - \widehat{p}_2 "
            r"\text{ on all six claims}"
        ).scale(0.48)
        ci_parallel_title.next_to(ci_national_note, DOWN, buff=0.25)

        ci_table_rows = [
            [
                "Claim",
                r"$\widehat{p}_1$",
                r"$\widehat{p}_2$",
                r"$\widehat{p}_1 - \widehat{p}_2$",
                ("tex", r"$SE_{\widehat{p}_1 - \widehat{p}_2}$"),
                "Margin",
                r"95\% CI",
            ],
        ]
        for title, diff_ci in claim_ci_results:
            se_pp = diff_ci["se_diff"] * 100
            ci_table_rows.append(
                [
                    title,
                    f"{diff_ci['p1_pct']:.1f}%",
                    f"{diff_ci['p2_pct']:.1f}%",
                    f"{diff_ci['diff_pct']:+.1f} pp",
                    f"{se_pp:.2f} pp",
                    f"±{diff_ci['margin_pct']:.2f} pp",
                    f"{diff_ci['low_pct']:+.1f} to {diff_ci['high_pct']:+.1f} pp",
                ]
            )

        ci_results_table = Table(
            ci_table_rows,
            header_row=True,
            full_width=True,
            width_margin=0.25,
            h_buff=0.3,
            h_cell_buff=0.5,
            column_width_ratios=(1.55, 0.7, 0.7, 0.75, 0.85, 0.7, 1.2),
            tex_config=dict(scale=0.52),
            header_config=dict(scale=0.55),
            element_config=dict(scale=0.5)
        )
        ci_results_table.scale(0.60)
        ci_results_table.next_to(ci_parallel_title, DOWN, buff=0.35)

        ci_formula_reminder = Tex(
            r"(\widehat{p}_1 - \widehat{p}_2) \pm 1.96 "
            r"\sqrt{\frac{\widehat{p}_1(1-\widehat{p}_1)}{n_1} + "
            r"\frac{\widehat{p}_2(1-\widehat{p}_2)}{n_2}}"
        ).scale(0.44)
        ci_formula_reminder.next_to(ci_results_table, DOWN, buff=0.3)

        self.play(Write(ci_national_note), Write(ci_parallel_title))
        self.next_slide()
        self.play(ShowCreation(ci_results_table))
        self.next_slide()
        self.play(Write(ci_formula_reminder))
        self.next_slide()
        self.play(
            FadeOut(ci_national_note),
            FadeOut(ci_parallel_title),
            FadeOut(ci_results_table),
            FadeOut(ci_formula_reminder),
        )
        self.next_slide()

        ci_interp_q1_x, ci_interp_q1_n = survey_yes_no_counts(ci_survey, q1_key)
        ci_interp_study_x, ci_interp_study_n = study_counts_from_published_pct(22.0, "ios")
        ci_interp_q1 = proportion_difference_ci_values(
            ci_interp_q1_x, ci_interp_q1_n, ci_interp_study_x, ci_interp_study_n
        )

        ci_interp_title = Text("What does the 95% CI mean? (plain language)").scale(0.55)
        ci_interp_title.to_edge(UP, buff=0.4)
        ci_interp_body = Text(
            "For Question 1, the true gap between NWS and the study is probably\n"
            f"between about {ci_interp_q1['low_pct']:+.0f} and {ci_interp_q1['high_pct']:+.0f} "
            "percentage points (NWS higher).\n"
            "If the study's 22% were inside that range, the groups could be similar—\n"
            "but 22% is below our interval, so NWS students report more judgment."
        ).scale(0.38)
        ci_interp_body.next_to(ci_interp_title, DOWN, buff=0.35)
        ci_interp_body.align_to(ci_interp_title, LEFT)

        self.play(Write(ci_interp_title), Write(ci_interp_body))
        self.next_slide()
        self.play(FadeOut(ci_interp_title), FadeOut(ci_interp_body))
        #endregion

    #endregion

    #region Z-SCORE CALCULATION
        z_json_path = Path(__file__).parent / "survey_by_question.json"
        with open(z_json_path, encoding="utf-8") as z_file:
            z_survey = json.load(z_file)

        z_q1_key = "Do you judge people when they text you with green bubles?"
        z_q3_key = (
            "Have you ever switched to a third-party messaging app "
            "(WhatsApp, Discord, etc.) to accommodate non-iPhone users?"
        )
        z_q4_key = (
            "Which of the following have happened to you because you have an "
            "Android phone? (select all that apply)"
        )
        z_q5_key = "Have you ever considered switching to iPhone due to peer pressure?"

        z_claim_specs = [
            (
                "Excluded from group chats",
                survey_option_counts(z_survey, z_q4_key, "Been excluded from a group chat"),
                24.0,
                "android",
            ),
            (
                "Made fun for phone type",
                survey_option_counts(z_survey, z_q4_key, "Made fun of by iPhone users"),
                52.0,
                "android",
            ),
            (
                "Judge green bubbles (Q1)",
                survey_yes_no_counts(z_survey, z_q1_key),
                22.0,
                "ios",
            ),
            (
                "Consider switching to iPhone",
                survey_yes_no_counts(z_survey, z_q5_key),
                30.0,
                "android",
            ),
            (
                "Missed or misunderstood messages",
                survey_option_counts(
                    z_survey,
                    z_q4_key,
                    "Missed or misunderstood messages (due to compatibility issues)",
                ),
                38.0,
                "android",
            ),
            (
                "Switch messaging app",
                survey_yes_no_counts(z_survey, z_q3_key),
                42.0,
                "ios",
            ),
        ]
        z_claim_results = []
        for title, (nws_x, nws_n), study_pct, platform in z_claim_specs:
            study_x, study_n = study_counts_from_published_pct(study_pct, platform)
            z_claim_results.append(
                (title, two_proportion_z_test(nws_x, nws_n, study_x, study_n))
            )

        z_title = Text("Z-Score Calculation").scale(0.75)
        z_title.to_edge(UP, buff=0.35)

        z_vars_txt = Text(
            "Variables for each two-proportion z-test:\n"
            "x₁, n₁ → NWS successes and sample size (p̂₁ = x₁/n₁)\n"
            "x₂, n₂ → study successes and sample size (p̂₂ = x₂/n₂)\n"
            "p̂_pool = (x₁+x₂)/(n₁+n₂) → combine both samples into one overall “yes” rate\n"
            "  (used when H₀ assumes p₁ = p₂: “no difference between NWS and study”)\n"
            "SE_pool = √[p̂_pool(1−p̂_pool)(1/n₁ + 1/n₂)],  z = (p̂₁−p̂₂)/SE_pool"
        ).scale(0.33)
        z_vars_txt.next_to(z_title, DOWN, buff=0.35)
        z_vars_txt.align_to(z_title, LEFT)

        self.play(Write(z_title), Write(z_vars_txt))
        self.next_slide()

        q1z = next(z for t, z in z_claim_results if "Q1" in t)

        def walkthrough_q1_z():
            z_q1_title = Text(
                "Example: Question 1 (judge green bubbles)"
            ).scale(0.5)
            z_q1_title.next_to(z_title, DOWN, buff=0.3)

            z_steps = VGroup(
                Tex(
                    rf"x_1 = {q1z['nws_x']},\; n_1 = {q1z['nws_n']},\;"
                    rf" {{\hat{{p}}}}_1 = {q1z['p1']:.3f}"
                ),
                Tex(
                    rf"x_2 = {q1z['study_x']},\; n_2 = {q1z['study_n']},\;"
                    rf" {{\hat{{p}}}}_2 = {q1z['p2']:.3f}"
                ),
                Text(
                    "p̂_pool: add all “yes” answers from NWS and the study, divide by total n.\n"
                    "If H₀ is true (same true proportion in both groups), this pooled rate is our\n"
                    "best single estimate of that shared proportion—and we use it in SE_pool."
                ).scale(0.36),
                Tex(
                    r"\hat{p}_{\mathrm{pool}} = \frac{x_1+x_2}{n_1+n_2}"
                    + rf" \approx {q1z['p_pool']:.3f}"
                ),
                Tex(
                    rf"\mathrm{{SE}}_{{\mathrm{{pool}}}} \approx {q1z['se']:.3f},\quad "
                    + r"z = \frac{{\hat{p}}_1-{\hat{p}}_2}{\mathrm{SE}_{\mathrm{pool}}}"
                    + rf" \approx {q1z['z']:.2f}"
                ),
                Tex(
                    r"\text{Two-tailed } p\text{-value} \approx "
                    + f"{q1z['p_value']:.4f}"
                    + r",\; p < \alpha"
                ),
                Text(
                    "p-value = area in both tails beyond |z| on the standard normal curve."
                ).scale(0.9),
            )
            for step in z_steps:
                step.scale(0.52)
            z_steps.arrange(DOWN, aligned_edge=LEFT, buff=0.25)
            z_steps.next_to(z_q1_title, DOWN, buff=0.3)
            z_steps.align_to(z_q1_title, LEFT)

            self.play(FadeOut(z_vars_txt), Write(z_q1_title))
            self.next_slide()
            visible = VGroup()
            for step in z_steps:
                visible.add(step)
                self.play(Write(step))
                self.next_slide()
            self.play(FadeOut(z_q1_title), FadeOut(visible))
            self.next_slide()

        walkthrough_q1_z()

        z_table_rows = [
            ["Claim", "z", "p-value", "Reject H₀?"],
        ]
        for title, zr in z_claim_results:
            reject = "Yes" if zr["p_value"] < 0.05 else "No"
            z_table_rows.append(
                [
                    title,
                    f"{zr['z']:+.2f}",
                    f"{zr['p_value']:.4f}",
                    reject,
                ]
            )

        z_parallel_title = Tex(
            r"\text{All six claims: } z\text{-scores and } p\text{-values}"
        ).scale(0.5)
        z_parallel_title.next_to(z_title, DOWN, buff=0.3)

        z_results_table = Table(
            z_table_rows,
            header_row=True,
            full_width=True,
            width_margin=0.25,
            h_buff=0.3,
            column_width_ratios=(1.8, 0.6, 0.7, 0.6),
            header_config=dict(scale=0.58),
            element_config=dict(scale=0.52),
        )
        z_results_table.scale(0.)
        z_results_table.next_to(z_parallel_title, DOWN, buff=0.35)

        self.play(Write(z_parallel_title), ShowCreation(z_results_table))
        self.next_slide()
        self.play(FadeOut(z_title), FadeOut(z_parallel_title), FadeOut(z_results_table))
        self.next_slide()
    #endregion

    #region FORMAL CONCLUSION
        conc_title = Text("Formal Conclusions").scale(0.75)
        conc_title.to_edge(UP, buff=0.4)

        conc_intro = VGroup(
            Tex(r"H_{0}:\widehat{p}_{1}-\widehat{p}_{2}=0 \quad\text{(same for all six claims)}"),
            Tex(r"H_{A}:\widehat{p}_{1}-\widehat{p}_{2}\ne 0"),
            Tex(r"\alpha = 0.05,\quad\text{two-tailed test}"),
            Text("Below: one formal conclusion per claim using our z-test p-values."),
        )
        for mob in conc_intro:
            mob.scale(0.48) if isinstance(mob, Tex) else mob.scale(0.38)
        conc_intro.arrange(DOWN, aligned_edge=LEFT, buff=0.28)
        conc_intro.next_to(conc_title, DOWN, buff=0.35)
        conc_intro.align_to(conc_title, LEFT)

        self.play(Write(conc_title), Write(conc_intro))
        self.next_slide()
        self.play(FadeOut(conc_intro))

        for claim_title, zr in z_claim_results:
            description = CLAIM_CONCLUSION_DESCRIPTIONS[claim_title]
            reject_h0 = zr["p_value"] < 0.05

            claim_heading = Text(claim_title).scale(0.5)
            claim_heading.next_to(conc_title, DOWN, buff=0.35)
            claim_heading.align_to(conc_title, LEFT)

            tex_description = description.replace("%", r"\%")
            claim_stats = VGroup(
                Tex(
                    rf"\widehat{{p}}_1 \approx {zr['p1_pct']:.1f}\% \text{{ (NWS)}},\quad "
                    rf"\widehat{{p}}_2 \approx {zr['p2_pct']:.1f}\% \text{{ (study)}}"
                ),
                Tex(
                    rf"z \approx {zr['z']:+.2f},\quad "
                    rf"p\text{{-value}} \approx {zr['p_value']:.4f},\quad "
                    rf"\alpha = 0.05"
                ),
                Tex(
                    r"H_{A}:\widehat{p}_{1}-\widehat{p}_{2}\ne 0 "
                    rf"\text{{ ({tex_description})}}"
                ),
            )
            for mob in claim_stats:
                mob.scale(0.46)

            if reject_h0:
                decision = Text(
                    "Decision: reject H₀. There is sufficient evidence at the 0.05 level\n"
                    f"that NWS differs from the published study on {description}."
                )
            else:
                decision = Text(
                    "Decision: fail to reject H₀. There is not sufficient evidence at the\n"
                    f"0.05 level that NWS differs from the study on {description}."
                )
            decision.scale(0.36)

            claim_slide = VGroup(claim_heading, claim_stats, decision)
            claim_stats.arrange(DOWN, aligned_edge=LEFT, buff=0.22)
            claim_slide.arrange(DOWN, aligned_edge=LEFT, buff=0.28)
            claim_slide.next_to(conc_title, DOWN, buff=0.3)
            claim_slide.align_to(conc_title, LEFT)

            self.play(Write(claim_heading))
            self.next_slide()
            self.play(Write(claim_stats))
            self.next_slide()
            self.play(Write(decision))
            self.next_slide()
            self.play(FadeOut(claim_slide))

        self.play(FadeOut(conc_title))
        self.next_slide()
    #endregion

    #region SUMMARY
        summary_title = Text("Summary").scale(0.75)
        summary_title.to_edge(UP, buff=0.4)

        summary_body = VGroup(
            Text(
                "Most claims show NWS proportions far from the national study—often higher\n"
                "for negative experiences (e.g., missed messages, judgment of green bubbles)."
            ),
            Text(
                "I was surprised how large some gaps were (like missed messages: ~74% NWS vs. 38% study),\n"
                "but it fits hearing about iMessage culture at school."
            ),
            Text(
                "Implication: teen phone ecosystems may amplify bias beyond what adult surveys suggest—\n"
                "worth discussing accessibility and cross-platform messaging at school."
            ),
        )
        summary_body.arrange(DOWN, aligned_edge=LEFT, buff=0.35)
        summary_body.scale(0.4)
        summary_body.next_to(summary_title, DOWN, buff=0.45)
        summary_body.align_on_border(LEFT)

        self.play(Write(summary_title))
        self.next_slide()
        for line in summary_body:
            self.play(Write(line))
            self.next_slide()
        self.play(FadeOut(summary_title), FadeOut(summary_body))
        self.next_slide()
    #endregion
