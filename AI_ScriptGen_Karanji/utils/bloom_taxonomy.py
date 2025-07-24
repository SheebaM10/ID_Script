 # utils/bloom_taxonomy.py

import re

# Bloom’s levels mapped to action verbs (can be expanded)
BLOOMS_VERBS = {
    "Remember": [
        "define", "list", "name", "identify", "recall", "recognize", "label", "match"
    ],
    "Understand": [
        "explain", "describe", "discuss", "summarize", "interpret", "classify", "restate"
    ],
    "Apply": [
        "use", "demonstrate", "implement", "solve", "illustrate", "execute", "practice"
    ],
    "Analyze": [
        "analyze", "differentiate", "distinguish", "compare", "contrast", "examine", "investigate"
    ],
    "Evaluate": [
        "evaluate", "judge", "defend", "critique", "justify", "appraise", "recommend"
    ],
    "Create": [
        "create", "design", "assemble", "construct", "develop", "formulate", "compose"
    ]
}


def classify_blooms_level(text: str) -> str:
    """Detect the Bloom’s taxonomy level of a given sentence using key action verbs."""
    text = text.lower()
    for level, verbs in BLOOMS_VERBS.items():
        for verb in verbs:
            # match verb as a word (not substring), e.g., "describe" not "undescribed"
            if re.search(rf'\b{verb}\b', text):
                return level
    return "Understand"  # Default fallback level


# Example usage
if __name__ == "__main__":
    samples = [
        "List the steps in the digestive process.",
        "Explain how nutrients are absorbed in the small intestine.",
        "Create a nutrition plan based on the six food groups.",
        "Differentiate between mechanical and chemical digestion.",
        "Evaluate the importance of fiber in gut health."
    ]
    for s in samples:
        print(f"{s} → {classify_blooms_level(s)}")
