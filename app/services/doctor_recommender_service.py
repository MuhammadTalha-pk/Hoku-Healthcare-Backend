from app.schemas.doctor_recommender import (
    DoctorRecommendationRequest,
    DoctorRecommendationResponse,
)


SPECIALTY_RULES = {
    "General Physician": {
        "fever",
        "headache",
        "body pain",
        "weakness",
        "fatigue",
        "cold",
        "flu",
        "cough",
        "vomiting",
    },
    "Cardiologist": {
        "chest pain",
        "heart pain",
        "irregular heartbeat",
        "palpitations",
        "high blood pressure",
        "shortness of breath",
    },
    "Dermatologist": {
        "rash",
        "itching",
        "acne",
        "skin allergy",
        "hair loss",
        "dry skin",
        "skin infection",
    },
    "Neurologist": {
        "severe headache",
        "migraine",
        "seizure",
        "numbness",
        "memory loss",
        "dizziness",
        "tremor",
    },
    "Orthopedic Specialist": {
        "back pain",
        "joint pain",
        "knee pain",
        "bone pain",
        "fracture",
        "shoulder pain",
        "neck pain",
    },
    "Gastroenterologist": {
        "stomach pain",
        "abdominal pain",
        "constipation",
        "diarrhea",
        "acid reflux",
        "indigestion",
        "blood in stool",
    },
    "ENT Specialist": {
        "ear pain",
        "hearing loss",
        "sore throat",
        "sinus",
        "blocked nose",
        "nose bleeding",
        "tonsils",
    },
    "Pulmonologist": {
        "breathing difficulty",
        "persistent cough",
        "asthma",
        "wheezing",
        "lung pain",
        "shortness of breath",
    },
    "Gynecologist": {
        "pregnancy",
        "period pain",
        "irregular periods",
        "vaginal bleeding",
        "pelvic pain",
        "menstrual problem",
    },
    "Pediatrician": {
        "child fever",
        "child cough",
        "child weakness",
        "baby vomiting",
        "baby rash",
    },
    "Psychiatrist": {
        "anxiety",
        "depression",
        "panic attack",
        "insomnia",
        "suicidal thoughts",
        "stress",
    },
    "Ophthalmologist": {
        "eye pain",
        "blurred vision",
        "red eye",
        "vision loss",
        "eye infection",
    },
    "Urologist": {
        "urine pain",
        "blood in urine",
        "kidney pain",
        "frequent urination",
        "urinary infection",
    },
}



EMERGENCY_SYMPTOMS = {
    "severe chest pain",
    "difficulty breathing",
    "breathing difficulty",
    "unconsciousness",
    "severe bleeding",
    "stroke symptoms",
    "face drooping",
    "sudden weakness",
    "suicidal thoughts",
    "seizure",
    "vision loss",
}


def recommend_doctor(
    request: DoctorRecommendationRequest,
) -> DoctorRecommendationResponse:
    user_symptoms = set(request.symptoms)

    emergency_matches = sorted(
        symptom
        for symptom in user_symptoms
        if symptom in EMERGENCY_SYMPTOMS
    )

    if emergency_matches:
        return DoctorRecommendationResponse(
            recommended_specialty="Emergency Department",
            matched_symptoms=emergency_matches,
            urgency="Emergency",
            reason=(
                "One or more reported symptoms may require immediate "
                "medical attention."
            ),
            advice=(
                "Go to the nearest emergency department or contact local "
                "emergency services immediately."
            ),
            emergency_warning=(
                "Do not rely only on an online recommendation for these symptoms."
            ),
            disclaimer=(
                "This recommendation is for general guidance only and is not "
                "a medical diagnosis."
            ),
        )

    specialty_scores: dict[str, list[str]] = {}

    for specialty, known_symptoms in SPECIALTY_RULES.items():
        matched = sorted(user_symptoms.intersection(known_symptoms))

        if matched:
            specialty_scores[specialty] = matched

    if not specialty_scores:
        return DoctorRecommendationResponse(
            recommended_specialty="General Physician",
            matched_symptoms=[],
            urgency="Routine",
            reason=(
                "The entered symptoms do not strongly match a specific specialty."
            ),
            advice=(
                "Start with a General Physician for an initial examination "
                "and referral if needed."
            ),
            disclaimer=(
                "This recommendation is for general guidance only and is not "
                "a medical diagnosis."
            ),
        )

    recommended_specialty = max(
        specialty_scores,
        key=lambda specialty: len(specialty_scores[specialty]),
    )

    matched_symptoms = specialty_scores[recommended_specialty]

    urgency = "Routine"

    if request.duration_days is not None and request.duration_days >= 7:
        urgency = "Priority"

    if len(matched_symptoms) >= 3:
        urgency = "Priority"

    return DoctorRecommendationResponse(
        recommended_specialty=recommended_specialty,
        matched_symptoms=matched_symptoms,
        urgency=urgency,
        reason=(
            f"The reported symptoms match common cases handled by a "
            f"{recommended_specialty}."
        ),
        advice=(
            f"Book an appointment with a {recommended_specialty}. "
            "Seek urgent help if symptoms become severe."
        ),
        disclaimer=(
            "This recommendation is for general guidance only and is not "
            "a medical diagnosis. Consult a qualified healthcare professional."
        ),
    )


def get_specialties() -> list[str]:
    return sorted(SPECIALTY_RULES.keys())