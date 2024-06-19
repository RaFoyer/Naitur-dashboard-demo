# path/src/populate_db.py

import random
import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config.settings import DATABASE_URL
from create_db import Base, Protocol, Client, Form, Question, FormQuestion, Response, QuestionResponse, ClientFormResponse, ProtocolForm

# Create an engine and session
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

# Create Protocols
protocols = [
    ("Basic Protocol Template for Group Ceremony", "Protocol for group ceremonies including various psychological scales."),
    ("PTSD Protocol", "Protocol for assessing PTSD symptoms."),
    ("Depression Protocol", "Protocol for assessing depression symptoms."),
    ("Social Anxiety Protocol", "Protocol for assessing social anxiety symptoms."),
    ("Generalized Anxiety Protocol", "Protocol for assessing generalized anxiety symptoms.")
]

protocol_objects = {}
for name, description in protocols:
    protocol = Protocol(name=name, description=description)
    session.add(protocol)
    session.commit()
    protocol_objects[name] = protocol

# Create Forms
forms = [
    ("Mindfulness Attention Awareness Scale (MAAS)", "MAAS Description", "MAAS"),
    ("Psychedelic Predictor Scale", "PPS Description", "PPS"),
    ("Self Compassion Scale (SCS)", "SCS Description", "SCS"),
    ("Mystical Experiences Questionnaire (MEQ-30)", "MEQ-30 Description", "MEQ-30"),
    ("PTSD Form", "PTSD Form Description", "PTSD"),
    ("Depression Form", "Depression Form Description", "Depression"),
    ("Social Anxiety Form", "Social Anxiety Form Description", "Social Anxiety"),
    ("Generalized Anxiety Form", "Generalized Anxiety Form Description", "Generalized Anxiety")
]

form_objects = {}
for name, description, ftype in forms:
    form = Form(name=name, description=description, type="Likert scale")
    session.add(form)
    session.commit()
    form_objects[ftype] = form

# Create Questions
questions_data = {
    "MAAS": [
        "I could be experiencing some emotion and not be conscious of it until some time later.",
        "I break or spill things because of carelessness, not paying attention, or thinking of something else.",
        "I find it difficult to stay focused on what’s happening in the present.",
        "I tend to walk quickly to get where I’m going without paying attention to what I experience along the way.",
        "I tend not to notice feelings of physical tension or discomfort until they really grab my attention.",
        "I forget a person's name almost as soon as I've been told it for the first time.",
        "It seems I am “running on automatic” without much awareness of what I’m doing.",
        "I rush through activities without being really attentive to them.",
        "I get so focused on the goal I want to achieve that I lose touch with what I'm doing right now to get there.",
        "I do jobs or tasks automatically without being aware of what I'm doing.",
        "I find myself listening to someone with one ear, doing something else at the same time.",
        "I drive places on ‘automatic pilot’ and then wonder why I went there.",
        "I find myself preoccupied with the future or the past.",
        "I find myself doing things without paying attention.",
        "I snack without being aware that I’m eating."
    ],
    "PPS": [
        "I feel ready to surrender to whatever will be.",
        "I feel open to the upcoming experience.",
        "I feel well prepared for the upcoming experience.",
        "I feel comfortable about the upcoming experience.",
        "I am in a good mood.",
        "I feel anxious.",
        "I have a clear intention for the upcoming experience.",
        "I have a good feeling about my relationship with the group/people who will be with me.",
        "I have a good relationship with the main person/people who will look after me."
    ],
    "SCS": [
        "I’m disapproving and judgmental about my own flaws and inadequacies.",
        "When I’m feeling down I tend to obsess and fixate on everything that’s wrong.",
        "When things are going badly for me, I see the difficulties as part of life that everyone goes through.",
        "When I think about my inadequacies, it tends to make me feel more separate and cut off from the rest of the world.",
        "I try to be loving towards myself when I’m feeling emotional pain.",
        "When I fail at something important to me I become consumed by feelings of inadequacy.",
        "When I'm down and out, I remind myself that there are lots of other people in the world feeling like I am.",
        "When times are really difficult, I tend to be tough on myself.",
        "When something upsets me I try to keep my emotions in balance.",
        "When I feel inadequate in some way, I try to remind myself that feelings of inadequacy are shared by most people.",
        "I’m intolerant and impatient towards those aspects of my personality I don't like.",
        "When I’m going through a very hard time, I give myself the caring and tenderness I need.",
        "When I’m feeling down, I tend to feel like most other people are probably happier than I am.",
        "When something painful happens I try to take a balanced view of the situation.",
        "I try to see my failings as part of the human condition.",
        "When I see aspects of myself that I don’t like, I get down on myself.",
        "When I fail at something important to me I try to keep things in perspective.",
        "When I’m really struggling, I tend to feel like other people must be having an easier time of it.",
        "I’m kind to myself when I’m experiencing suffering.",
        "When something upsets me I get carried away with my feelings.",
        "I can be a bit cold-hearted towards myself when I'm experiencing suffering.",
        "When I'm feeling down I try to approach my feelings with curiosity and openness.",
        "I’m tolerant of my own flaws and inadequacies.",
        "When something painful happens I tend to blow the incident out of proportion.",
        "When I fail at something that's important to me, I tend to feel alone in my failure.",
        "I try to be understanding and patient towards those aspects of my personality I don't like."
    ],
    "MEQ-30": [
        "Loss of your usual sense of time.",
        "Experience of amazement.",
        "Sense that the experience cannot be described adequately in words.",
        "Gain of insightful knowledge experienced at an intuitive level.",
        "Feeling that you experienced eternity or infinity.",
        "Experience of oneness or unity with the objects and/or persons perceived in your surroundings.",
        "Loss of your usual sense of space.",
        "Feelings of tenderness and gentleness.",
        "Certainty of encounter with ultimate reality (in the sense of being able to ‘know’ and ‘see’ what is really real at some point during your experience).",
        "Feeling that you could not do justice to your experience by describing it in words.",
        "Loss of your usual sense of where you were.",
        "Feelings of peace and tranquillity.",
        "Sense of being ‘outside of’ time, beyond past and future.",
        "Freedom from the limitations of your personal self and feeling of unity or bond with what was felt to be greater than your personal self.",
        "Sense of being at a spiritual height.",
        "Experience of pure being and pure awareness (beyond the world of sense impressions).",
        "Experience of ecstasy.",
        "Experience of the insight that “all is One”.",
        "Being in a realm with no space boundaries.",
        "Experience of oneness in relation to an “inner world” within.",
        "Sense of reverence.",
        "Experience of timelessness.",
        "You are convinced now, as you look back on your experience, that in it you encountered ultimate reality (that you ‘knew’ and ‘saw’ what was really real).",
        "Feeling that you experienced something profoundly sacred and holy.",
        "Awareness of the life or living presence in all things.",
        "Experience of the fusion of your personal self into a larger whole.",
        "Sense of awe or awesomeness.",
        "Experience of unity with ultimate reality.",
        "Feeling that it would be difficult to communicate your own experience to others who have not had similar experiences.",
        "Feelings of joy."
    ],
    "PTSD": [
        "In the past month, how often have you been bothered by nightmares about the traumatic event?",
        "How often have you had flashbacks, feeling or acting as if the traumatic event were happening again?",
        "When reminded of the traumatic event, how much do you experience physical reactions like sweating or a pounding heart?",
        "How often do you avoid places, activities, or thoughts that remind you of the traumatic event?",
        "How often do you feel emotionally numb or detached from others?"
    ],
    "Depression": [
        "Over the past two weeks, how often have you felt down, depressed, or hopeless?",
        "How often have you felt little interest or pleasure in doing things you usually enjoy?",
        "Have you experienced changes in your appetite or weight (either increase or decrease)?",
        "Have you had trouble falling asleep, staying asleep, or sleeping too much?",
        "How often have you felt tired or had little energy?"
    ],
    "Social Anxiety": [
        "How often do you feel anxious or uncomfortable in social situations where you might be observed or evaluated by others?",
        "How often do you worry about being embarrassed or humiliated in front of others?",
        "How often do you avoid social events or situations because of fear of negative judgment?",
        "How often do you experience physical symptoms (e.g., sweating, blushing, trembling) in social situations?",
        "How often do your fears of negative evaluation interfere with your daily life?"
    ],
    "Generalized Anxiety": [
        "Over the past two weeks, how often have you felt excessive worry or anxiety about a variety of events or activities?",
        "How often have you found it difficult to control your worry?",
        "How often have you been easily fatigued or had difficulty concentrating?",
        "How often have you felt restless, irritable, or on edge?",
        "How often have you experienced muscle tension or sleep disturbances due to worry?"
    ]
}

question_objects = {}
for ftype, questions in questions_data.items():
    for question_text in questions:
        question = Question(text=question_text, description=f"{ftype} Question")
        session.add(question)
        session.commit()
        form_question = FormQuestion(form_id=form_objects[ftype].id, question_id=question.id)
        session.add(form_question)
        session.commit()
        if ftype not in question_objects:
            question_objects[ftype] = []
        question_objects[ftype].append(question)

# Assign forms to protocols
form_protocol_mapping = {
    "Basic Protocol Template for Group Ceremony": ["MAAS", "PPS", "SCS", "MEQ-30"],
    "PTSD Protocol": ["PTSD"],
    "Depression Protocol": ["Depression"],
    "Social Anxiety Protocol": ["Social Anxiety"],
    "Generalized Anxiety Protocol": ["Generalized Anxiety"]
}

for protocol_name, form_types in form_protocol_mapping.items():
    protocol_id = protocol_objects[protocol_name].id
    for form_type in form_types:
        protocol_form = ProtocolForm(protocol_id=protocol_id, form_id=form_objects[form_type].id)
        session.add(protocol_form)
        session.commit()

# Create Clients and Responses
num_clients = 100
time_intervals = ["Baseline", "1-Month", "3-Months", "6-Months", "1-Year"]

for i in range(num_clients):
    client = Client(name=f"Client {i+1}", email=f"client{i+1}@example.com")
    session.add(client)
    session.commit()

    # Ensure each client fills out the "Basic Protocol Template for Group Ceremony"
    selected_protocols = ["Basic Protocol Template for Group Ceremony"]

    # Randomly select 0-2 other protocols for the client to fill out
    other_protocols = random.sample(list(protocol_objects.keys())[1:], random.randint(0, 2))
    selected_protocols.extend(other_protocols)

    for interval in time_intervals:
        for protocol_name in selected_protocols:
            protocol = protocol_objects[protocol_name]
            form_types = form_protocol_mapping[protocol_name]
            for form_type in form_types:
                for question in question_objects[form_type]:
                    if interval == "Baseline":
                        score = random.randint(0, 4)  # Baseline scores in the range 0-4
                    else:
                        baseline_scores = [random.randint(0, 4) for _ in range(5)]  # Generate baseline scores
                        baseline_avg = sum(baseline_scores) / len(baseline_scores)
                        reduction_factor = random.uniform(0.05, 0.8)  # 5-80% reduction
                        score = max(0, int(baseline_avg * reduction_factor))
                    
                    response = Response(text=str(score))
                    session.add(response)
                    session.commit()

                    question_response = QuestionResponse(question=question.id, response=response.id)
                    session.add(question_response)
                    session.commit()

                    client_form_response = ClientFormResponse(
                        client_id=client.id,
                        form_id=form_objects[form_type].id,
                        protocol_id=protocol.id,
                        question_id=question.id,
                        response_id=response.id,
                        time_point=interval
                    )
                    session.add(client_form_response)
                    session.commit()

print("Database populated with synthetic data based on specified patterns.")

