"""
Meta Analyzer — GW2_WvWBuilder v4.3

Uses LLM (Mistral) to analyze patch changes and recommend weight adjustments.
Provides intelligent interpretation of balance changes for WvW meta.
"""

from __future__ import annotations

import logging
from typing import Dict, List, Tuple

logger = logging.getLogger(__name__)


def analyze_change_impact_with_llm(change: Dict, llm_engine) -> Dict:
    """Use LLM to analyze the impact of a balance change.
    
    Args:
        change: Patch change dict with spec, change_type, impact, etc.
        llm_engine: LLM engine instance (OllamaEngine)
    
    Returns:
        Dict with recommended_weight_delta, affected_synergies, reasoning
    """
    spec = change["spec"]
    change_type = change["change_type"]
    impact_text = change.get("impact", "")
    magnitude = change.get("magnitude", "unknown")
    
    prompt = (
        f"You are a Guild Wars 2 World vs World (WvW) meta analyst. "
        f"Analyze this balance change:\n\n"
        f"Specialization: {spec}\n"
        f"Change Type: {change_type}\n"
        f"Details: {impact_text}\n"
        f"Magnitude: {magnitude}\n\n"
        f"Provide a JSON response with:\n"
        f"1. weight_delta: float between -0.3 and +0.3 (how much to adjust spec weight)\n"
        f"2. synergy_impact: 'low', 'medium', or 'high'\n"
        f"3. affected_roles: list of affected WvW roles (e.g., ['support', 'dps'])\n"
        f"4. reasoning: brief explanation (2-3 sentences)\n\n"
        f"Example: {{\"weight_delta\": -0.15, \"synergy_impact\": \"medium\", "
        f"\"affected_roles\": [\"support\"], \"reasoning\": \"Quickness nerf reduces support value\"}}"
    )
    
    try:
        # Use LLM engine to generate analysis
        import json
        import urllib.request
        
        endpoint = llm_engine._endpoint
        model = llm_engine._model
        
        url = f"{endpoint}/api/generate"
        data = json.dumps({
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.2}  # Low temp for consistent analysis
        }).encode("utf-8")
        
        req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            text = result.get("response", "{}")
            
            # Parse JSON from response
            try:
                analysis = json.loads(text)
            except json.JSONDecodeError:
                # Try to extract JSON substring
                start = text.find("{")
                end = text.rfind("}")
                if start >= 0 and end >= 0:
                    analysis = json.loads(text[start:end+1])
                else:
                    raise ValueError("No valid JSON in LLM response")
            
            return {
                "spec": spec,
                "change_type": change_type,
                "weight_delta": analysis.get("weight_delta", 0.0),
                "synergy_impact": analysis.get("synergy_impact", "low"),
                "affected_roles": analysis.get("affected_roles", []),
                "reasoning": analysis.get("reasoning", "No reasoning provided"),
                "source_change": change,
            }
    
    except Exception as e:
        logger.warning(f"LLM analysis failed for {spec}: {e}")
        # Fallback to heuristic
        return fallback_heuristic_analysis(change)


def fallback_heuristic_analysis(change: Dict) -> Dict:
    """Heuristic-based analysis when LLM is unavailable."""
    spec = change["spec"]
    change_type = change["change_type"]
    
    # Simple heuristics
    if change_type == "nerf":
        weight_delta = -0.10
        reasoning = f"{spec} was nerfed, reducing weight by 10%"
    elif change_type == "buff":
        weight_delta = 0.10
        reasoning = f"{spec} was buffed, increasing weight by 10%"
    elif change_type == "rework":
        weight_delta = 0.0  # Neutral until tested
        reasoning = f"{spec} was reworked, weight unchanged pending testing"
    else:
        weight_delta = 0.0
        reasoning = "Unknown change type"
    
    return {
        "spec": spec,
        "change_type": change_type,
        "weight_delta": weight_delta,
        "synergy_impact": "medium",
        "affected_roles": ["all"],
        "reasoning": reasoning,
        "source_change": change,
    }


def analyze_all_changes(changes: List[Dict], llm_engine=None) -> List[Dict]:
    """Analyze all patch changes and generate weight adjustments."""
    logger.info(f"Analyzing {len(changes)} patch changes...")
    
    analyses = []
    
    for change in changes:
        if llm_engine:
            try:
                analysis = analyze_change_impact_with_llm(change, llm_engine)
            except Exception as e:
                logger.error(f"LLM analysis error: {e}")
                analysis = fallback_heuristic_analysis(change)
        else:
            analysis = fallback_heuristic_analysis(change)
        
        analyses.append(analysis)
        logger.info(f"  {change['spec']}: {change['change_type']} → weight Δ={analysis['weight_delta']:.2f}")
    
    return analyses


def recalculate_synergies(analyses: List[Dict], current_synergies: Dict, llm_engine=None) -> Dict:
    """Recalculate synergy matrix based on balance changes.
    
    Args:
        analyses: List of change analyses
        current_synergies: Current synergy scores dict
        llm_engine: Optional LLM engine for intelligent recalculation
    
    Returns:
        Updated synergy dict
    """
    logger.info("Recalculating synergies based on balance changes...")
    
    updated_synergies = current_synergies.copy()
    
    # Specs with high-impact changes
    high_impact_specs = [
        a["spec"] for a in analyses
        if a.get("synergy_impact") in ["high", "medium"]
    ]
    
    if not high_impact_specs:
        logger.info("  No high-impact changes, synergies unchanged")
        return updated_synergies
    
    # If LLM available, ask for synergy recommendations
    if llm_engine:
        changes_text = "\n".join([f"- {a['spec']}: {a['change_type']} ({a['reasoning']})" for a in analyses])
        prompt = (
            f"Based on these GW2 WvW balance changes:\n"
            f"{changes_text}\n\n"
            f"Which specialization synergies should be adjusted? "
            f"Provide a JSON list of pairs with new scores (0.0-1.0):\n"
            f'Example: [{{"pair": ["Firebrand", "Scrapper"], "score": 0.85}}]'
        )
        
        try:
            import json
            import urllib.request
            
            endpoint = llm_engine._endpoint
            model = llm_engine._model
            
            url = f"{endpoint}/api/generate"
            data = json.dumps({
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": 0.2}
            }).encode("utf-8")
            
            req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=30) as resp:
                result = json.loads(resp.read().decode("utf-8"))
                text = result.get("response", "[]")
                
                # Parse JSON
                try:
                    synergy_updates = json.loads(text)
                except json.JSONDecodeError:
                    start = text.find("[")
                    end = text.rfind("]")
                    if start >= 0 and end >= 0:
                        synergy_updates = json.loads(text[start:end+1])
                    else:
                        synergy_updates = []
                
                # Apply updates
                for update in synergy_updates:
                    pair = tuple(sorted([s.lower() for s in update["pair"]]))
                    score = update["score"]
                    updated_synergies[pair] = score
                    logger.info(f"  Synergy {pair}: {score:.2f}")
        
        except Exception as e:
            logger.warning(f"LLM synergy recalculation failed: {e}")
    
    else:
        # Simple heuristic: reduce synergies for nerfed specs
        for analysis in analyses:
            if analysis["change_type"] == "nerf":
                spec = analysis["spec"].lower()
                # Find and reduce all synergies involving this spec
                for pair, score in list(updated_synergies.items()):
                    if spec in pair:
                        new_score = max(0.0, score - 0.05)
                        updated_synergies[pair] = new_score
                        logger.info(f"  Synergy {pair}: {score:.2f} → {new_score:.2f}")
    
    return updated_synergies
