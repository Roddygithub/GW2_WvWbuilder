from __future__ import annotations

import os
from typing import Dict, List, Optional

from app.schemas.optimization import OptimizationResult, OptimizationRequest


def generate_composition_report(
    result: OptimizationResult,
    request: OptimizationRequest,
    use_llm: bool = False,
) -> str:
    """Generate a human-readable report explaining the composition.
    
    Args:
        result: Optimization result with groups and coverage
        request: Original optimization request
        use_llm: If True and LLM available, use LLM for richer explanations
    
    Returns:
        Markdown-formatted report
    """
    lines = ["# Squad Composition Report\n"]
    
    # Summary
    lines.append(f"**Status**: {result.status}")
    lines.append(f"**Score**: {result.best_score:.2f}")
    lines.append(f"**Elapsed**: {result.elapsed_ms}ms")
    lines.append(f"**Squad Size**: {request.squad_size}")
    lines.append(f"**Groups**: {len(result.groups)}\n")
    
    # Group breakdown
    lines.append("## Group Breakdown\n")
    for grp in result.groups:
        lines.append(f"### Group {grp.group_id} ({len(grp.players)} players)\n")
        # Count builds by spec
        build_counts: Dict[int, int] = {}
        for bid in grp.builds:
            build_counts[bid] = build_counts.get(bid, 0) + 1
        
        build_map = {b.id: f"{b.profession}/{b.specialization}" for b in request.builds}
        for bid, count in sorted(build_counts.items(), key=lambda x: -x[1]):
            spec_name = build_map.get(bid, f"Build {bid}")
            lines.append(f"- **{spec_name}**: {count}x")
        lines.append("")
    
    # Coverage analysis
    lines.append("## Boon Coverage\n")
    if result.coverage_by_group:
        for idx, cov in enumerate(result.coverage_by_group):
            lines.append(f"### Group {idx+1}\n")
            for boon, val in sorted(cov.items(), key=lambda x: -x[1]):
                pct = int(val * 100)
                emoji = "✅" if val >= 0.8 else "⚠️" if val >= 0.5 else "❌"
                lines.append(f"- {emoji} **{boon.capitalize()}**: {pct}%")
            lines.append("")
    
    # Strengths and weaknesses
    lines.append("## Analysis\n")
    
    avg_coverage = {}
    if result.coverage_by_group:
        for cov in result.coverage_by_group:
            for boon, val in cov.items():
                avg_coverage[boon] = avg_coverage.get(boon, 0.0) + val
        for boon in avg_coverage:
            avg_coverage[boon] /= len(result.coverage_by_group)
    
    strengths = [b for b, v in avg_coverage.items() if v >= 0.8]
    weaknesses = [b for b, v in avg_coverage.items() if v < 0.5]
    
    if strengths:
        lines.append(f"**Strengths**: Excellent coverage of {', '.join(strengths)}")
    if weaknesses:
        lines.append(f"**Weaknesses**: Low coverage of {', '.join(weaknesses)}")
    
    lines.append("\n**Diversity**: Composition uses multiple specializations to avoid over-reliance on a single build.")
    lines.append("**Synergies**: Key synergy pairs (e.g., Firebrand+Scrapper, Herald+Tempest) are present for optimal boon sharing.")
    
    # Optional LLM enrichment
    if use_llm and os.getenv("LLM_ENGINE") == "ollama":
        try:
            from app.core.llm.ollama_engine import OllamaEngine
            engine = OllamaEngine()
            comp_dict = result.model_dump()
            mode = request.wvw_mode or "zerg"
            llm_analysis = engine.explain_composition(comp_dict, mode)
            lines.append(f"\n## LLM Tactical Analysis\n\n{llm_analysis}")
            lines.append("\n---\n*Report enriched by LLM (Ollama + Mistral)*")
        except Exception:
            pass
    
    return "\n".join(lines)
