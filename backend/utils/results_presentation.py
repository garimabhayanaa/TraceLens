"""
Builds the final, human-readable presentation layer for an analysis run.
Generates:
• Visual Privacy Score (1-10 + colour)        • Inference Categories
• Confidence Levels                           • Data-source attribution
• Mitigation Recommendations
"""

from dataclasses import dataclass, asdict
from typing import Dict, List, Any
import numpy as np
import colours  # tiny helper (r,g,b) → hex you likely already use elsewhere

COLOUR_MAP = {
    1: "#008000",  # dark-green (very safe)
    2: "#19a319",
    3: "#32b432",
    4: "#4cc64c",
    5: "#ffcc00",  # yellow (moderate risk)
    6: "#ffad00",
    7: "#ff8c00",
    8: "#ff5400",
    9: "#ff1e00",
    10: "#cc0000"  # red (critical risk)
}

@dataclass
class VisualPrivacyScore:
    value: int
    colour: str

@dataclass
class InferenceEntry:
    category: str
    inference: str
    confidence: float
    sources: List[str]

@dataclass
class ResultsPresentation:
    privacy_score: VisualPrivacyScore
    inferences: List[InferenceEntry]
    mitigation_recommendations: List[str]

class ResultPresentationBuilder:
    """Creates the public-facing output bundle."""

    def _colour_for_score(self, score: int) -> str:
        return COLOUR_MAP.get(score, "#808080")  # default grey

    # -----  PUBLIC  --------------------------------------------------------
    def build(self, analysis: Dict[str, Any]) -> ResultsPresentation:
        """Accepts full `analysis_results` dict and returns formatted bundle."""

        # 1. Calculate overall privacy score (1-10)
        score_components = [
            analysis["schedule_patterns"].get("overall_schedule_score", 0.0) * 10,
            analysis["economic_indicators"].get("economic_risk_score", 0.0) * 10,
            10 if analysis["mental_state_assessment"].get("crisis_indicators_detected") else 0
        ]
        raw_score = np.clip(np.mean(score_components), 1, 10)
        privacy_score = VisualPrivacyScore(
            value=int(round(raw_score)),
            colour=self._colour_for_score(int(round(raw_score)))
        )

        # 2. Build organised inference entries
        inferences: List[InferenceEntry] = []
        def _add(cat: str, key: str, conf: float, src: List[str]):
            inferences.append(InferenceEntry(category=cat,
                                             inference=key,
                                             confidence=round(conf, 2),
                                             sources=src))

        # Example entries – extend as desired
        _add("Sentiment", analysis["sentiment_analysis"]["overall_sentiment"],
             analysis["sentiment_analysis"]["confidence_score"],
             ["sentiment_analysis"])
        _add("Schedule Risk",
             f"Score {analysis['schedule_patterns'].get('overall_schedule_score',0):.2f}",
             0.90,
             ["schedule_patterns"])
        _add("Economic Risk",
             f"Risk {analysis['economic_indicators'].get('economic_risk_score',0):.2f}",
             0.85,
             ["economic_indicators"])
        _add("Mental State",
             analysis["mental_state_assessment"]
                     .get("mental_state_profile", {})
                     .get("overall_mental_state", "unknown"),
             analysis["mental_state_assessment"]
                     .get("assessment_confidence", 0.0),
             ["mental_state_assessment"])

        # 3. Aggregate mitigation tips (dedup & keep order)
        mitigation = []
        seen: set = set()
        for block in ("schedule_patterns", "economic_indicators", "mental_state_assessment"):
            recs = analysis.get(block, {}).get("privacy_implications",
                                               []) or analysis.get(block, {}).get("recommendations", [])
            for r in recs:
                if r not in seen:
                    mitigation.append(r)
                    seen.add(r)

        return ResultsPresentation(privacy_score, inferences, mitigation)
